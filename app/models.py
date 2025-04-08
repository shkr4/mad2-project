from . import db
from flask_login import UserMixin
from sqlalchemy.ext.mutable import MutableDict
from flask_admin import Admin
from sqlalchemy.sql import func
# Custom index view


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String)
    phone = db.Column(db.Integer)
    role = db.Column(db.String)
    address = db.Column(db.Text)
    status = db.Column(db.String)
    # Set default to the current timestamp
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now())

    orders = db.relationship('Order', backref='user', lazy=True)

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'address': self.address,
            'status': self.status,
            'orders': [order.to_json() for order in self.orders]
        }

    def __repr__(self):
        return f'{self.name}'


class Professionals(db.Model):
    __tablename__ = "professionals"

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # FK to User
    business_name = db.Column(db.String)
    YoE = db.Column(db.Integer)
    address = db.Column(db.Text)
    pin = db.Column(db.Integer)
    status = db.Column(db.String)
    ServiceOffered = db.Column(MutableDict.as_mutable(db.PickleType))
    # Set default to the current timestamp
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now())

    orders = db.relationship('Order', backref='professional', lazy=True)
    services = db.relationship('Services', backref='professional', lazy=True)
    user = db.relationship('User', backref='professional')
    doc = db.Column(db.String)

    def to_json(self):
        return {
            "id": self.id,
            "orders": [x.to_json() for x in self.orders],
            "business_name": self.business_name, "YoE": self.YoE, "address": self.address,
            "pin": self.pin, "status": self.status, "service_offered": [x for x in self.ServiceOffered]
        }

    def __repr__(self):
        return f'{self.business_name}'


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey(
        'professionals.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    rating = db.Column(db.Float(precision=2, decimal_return_scale=2))
    # Set default to the current timestamp
    booked_at = db.Column(db.DateTime, default=func.now())
    accepted_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    closed_by = db.Column(db.String)
    remark_by_customer = db.Column(db.Text)

    service = db.Column(db.String(100), nullable=False)

    def to_json(self):
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "professional_id": self.professional_id,
            "status": self.status,
            "rating": self.rating,
            "booked_at": self.booked_at,
            "closed_at": self.closed_at,
            "remark_by_customer": self.remark_by_customer,
            "service": self.service
        }

    # No need for explicit relationship definition here as 'backref' handles it


# This Model is to only record available srvices and display on the HTML. Do not connect it with other models
class Services(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    cs_id = db.Column(db.Integer, db.ForeignKey(
        'compServices.id'), nullable=True)
    service = db.Column(db.String, nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Integer)
    serviceProvider = db.Column(db.Integer, db.ForeignKey('professionals.id'))
    created_at = db.Column(db.DateTime, default=func.now())

    # order = db.relationship('Services', backref="service")

    # 'backref' allows easy access to related professionals in the relationship


# user = User(name = name, password = password, email = email, YoE = YoE, services = service, UpFile = UpFile, pin = pin,
#     address = address)
class CompanyServices(db.Model):
    __tablename__ = "compServices"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
