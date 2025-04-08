from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from .workers import celery, make_celery  # Import celery and make_celery
from celery.schedules import crontab
from flask_mail import Mail, Message

load_dotenv()
mailPort = int(os.environ.get('port'))
mailServer = os.environ.get('server')
mailUsername = os.environ.get('sender_email')
mailPassword = os.environ.get('mailpasswd')

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "secretkey"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static/uploads")
    app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
    app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
    app.config["CELERYBEAT_SCHEDULE"] = {
        "send-daily-reminder": {
            "task": "app.tasks.send_daily_reminder",  # Full path to the task
            # 6 PM daily (18:00 in 24-hour format)
            "schedule": crontab(minute="*"),
        },
        "send-monthly-reminder": {
            "task": "app.tasks.send_monthly_report",  # Full path to the task
            # "schedule": crontab(day_of_month=1, hour=0, minute=0),  # 6 PM daily (18:00 in 24-hour format)
            "schedule": crontab(minute="*")
        },
    }

    app.config['MAIL_SERVER'] = mailServer
    app.config['MAIL_PORT'] = mailPort
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = mailUsername
    app.config['MAIL_PASSWORD'] = mailPassword
    app.config['MAIL_DEFAULT_SENDER'] = mailUsername

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    mail.init_app(app)
    # socketio.init_app(app, async_mode="eventlet", message_queue="redis://localhost:6379/0", cors_allowed_origins="*")

    from .models import User, Professionals, Order, Services, CompanyServices

    with app.app_context():
        db.create_all()

    from .routes import main_bp
    app.register_blueprint(main_bp)

    admin = Admin(app, name="My Admin Panel", template_mode="bootstrap3")
    from .adminClass import UserAdmin, ProfessionalsAdmin, OrderAdmin, ServicesAdmin, CompanyServicesAdmin
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(ProfessionalsAdmin(Professionals, db.session))
    admin.add_view(OrderAdmin(Order, db.session))
    admin.add_view(ServicesAdmin(Services, db.session))
    admin.add_view(CompanyServicesAdmin(CompanyServices, db.session))

    celery_instance = make_celery(app)
    celery_instance.conf.update(
        # Apply the beat schedule
        beat_schedule=app.config["CELERYBEAT_SCHEDULE"]
    )

    return app, celery_instance


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
