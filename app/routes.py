from flask import Flask, jsonify, render_template, request, flash, Blueprint, current_app, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from .objs import *
from . import db
from .models import *
import os
import statistics as stat
from datetime import datetime
from werkzeug.utils import secure_filename
from .tasks import *


main_bp = Blueprint('main', __name__)

login_manager = LoginManager()


@main_bp.route('/gcr', methods=['POST'])
def generate_custom_report():
    data = request.get_json()
    pro_id = data.get('pro_id')

    task = export_service_csv.apply_async(args=[pro_id])

    # Do something with pro_id (e.g., generate a report)
    return jsonify({"message": f"Report generation started for Professional ID: {pro_id}"}), 200


@main_bp.route('/get_csv_report', methods=["GET", "POST"])
def csv_report():
    data = request.json
    firstName = data.get("firstName", "<<No First Name Provided>>")
    lastName = data.get("lastName", "<<No Last Name Provide>>")
    task = get_csv_report.apply_async(args=[firstName, lastName])
    return jsonify({"task_id": task.id}), 202


@main_bp.route("/hello", methods=["GET", "POST"])
def hello():
    job = just_say_hello.delay("Shekhar")
    return str(job), 200


@main_bp.post('/v_add_service')
@login_required
def v_add_service():
    data = request.get_json()
    service_id = data['service_id']
    description = data['des']
    price = data['price']
    pro_id = Professionals.query.filter_by(user_id=current_user.id).first().id
    name = data['name']
    cs_id = CompanyServices.query.filter_by(name=name).first().id

    professional = Professionals.query.get(pro_id)
    professional.ServiceOffered[name] = [price, description]

    ser = Services(service=name, description=description,
                   price=price, serviceProvider=pro_id, cs_id=cs_id)

    db.session.add(ser)
    db.session.commit()

    data2 = {
        "id": service_id,
        "service": name,
        "price": price,
        "description": description,
    }
    return jsonify(data2)


@main_bp.post('/v_delete_pro_service')
@login_required
def deleteProService():
    data = request.get_json()
    # ser_id = data['service_id']
    service = data['serviceName']
    pro_id = Professionals.query.filter_by(user_id=current_user.id).first().id
    Services.query.filter_by(service=service, serviceProvider=pro_id).delete()
    db.session.commit()
    return jsonify({"message": "ok"})


@main_bp.post('/v_close_order')
@login_required
def v_close_order():
    data = request.get_json()
    order_id = data['order_id']
    cusRating = data['cusRating']
    cusFeedback = data['cusFeedback']
    order = Order.query.filter_by(order_id=order_id).first()
    order.rating = cusRating
    order.remark_by_customer = cusFeedback
    order.status = "closed"
    order.closed_by = "customer"
    t = order.closed_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": f"{order_id} has been closed", "time": t.isoformat()})


@main_bp.post('/v_reject_it')
@login_required
def v_reject_it():
    data = request.get_json()
    oid = data["order_id"]
    order = Order.query.filter_by(order_id=oid).first()
    order.status = "rejected"
    order.closed_by = "professional"
    order.closed_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "ok"})


@main_bp.post('/v_accept_it')
@login_required
def v_accept_it():
    data = request.get_json()
    oid = data["order_id"]
    order = Order.query.filter_by(order_id=oid).first()
    order.status = "accepted"
    order.accepted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "ok"})


@main_bp.post('/v_pro_orders')
@login_required
def getProOrder():
    data = request.get_json()
    user_id = data['user_id']
    pro_id = Professionals.query.filter_by(user_id=user_id).first().id
    orders = Order.query.filter_by(professional_id=pro_id).order_by(
        Order.booked_at.desc()).all()

    OrderList = [
        {
            "order_id": order.order_id,
            "customer_name": order.user.name,
            "customer_address": f"{order.user.address}\n\
            Contact: {order.user.phone}\n\
            E-mail: {order.user.email}",
            "status": order.status,
            "rating": order.rating,
            "booked_at": order.booked_at.isoformat() if order.booked_at else None,
            "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
            "remark_by_customer": order.remark_by_customer,
            "services": order.service,
            "closed_by": order.closed_by,
        } for order in orders
    ]

    serviceOffered = Services.query.filter_by(serviceProvider=pro_id).all()

    serviceOfferedList = [{
        "id": service.id,
        "service": service.service,
        "price": service.price,
        "description": service.description,
    } for service in serviceOffered]

    companyService = CompanyServices.query.all()

    CompanyServicesList = [{
        "id": cs.id,
        "name": cs.name
    } for cs in companyService]

    finalJason = {
        "OrderList": OrderList,
        "serviceOfferedByPro": serviceOfferedList,
        "companyService": CompanyServicesList
    }
    return jsonify(finalJason)


@main_bp.get('/sep')
@login_required
def sep():
    professional = Professionals.query.filter_by(
        user_id=current_user.id).first()

    if professional.status == "blocked":
        return "<p>Your Services are blocked. Contact Admin</p>"

    professional_id = professional.id
    orders = Order.query.filter_by(professional_id=professional_id).order_by(
        Order.booked_at.desc()).all()
    ratingList = []
    for order in orders:
        if order.rating != None:
            ratingList.append(order.rating)
        if len(ratingList) == 0:
            ratingList = [0]

    return render_template('v_pro_dash.html')


@main_bp.post('/v_cancel_order')
@login_required
def v_cancel_order():
    data = request.get_json()
    order_id = data.get('order_id')
    order = Order.query.get(order_id)
    order.status = "cancelled"
    db.session.commit()
    return jsonify({"message": f"{order_id} is cancelled by the customer"})


@main_bp.post('/v_place_order')
@login_required
def v_place_order():
    data = request.get_json()

    user_id = data.get('user_id')
    professional_id = data.get('professional_id')
    service = data.get('service')

    new_order = Order(user_id=user_id, professional_id=professional_id,
                      status="requested", rating=0.0, service=service,

                      )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "order created"})


@main_bp.post('/v_find_service')
@login_required
def v_find_service():
    data = request.get_json()  # Get JSON data from Vue request
    input_value = data.get('value', '')  # Extract the 'value' field

    req_service = input_value
    avlbleService = Services.query.join(Professionals, Services.serviceProvider == Professionals.id) \
        .filter(
        Services.service.like(f'%{req_service}%'),
        Professionals.status == 'active'
    ).all()

    finalList = []

    for service in avlbleService:
        tempDict = {}
        tempDict['Service Name'] = service.service
        tempDict['Price'] = service.price
        tempDict['Service Provider'] = service.professional.business_name
        tempDict['Service Description'] = service.description
        tempDict['Professional ID'] = service.professional.id
        tempDict['Address'] = service.professional.address + \
            f'.\nPIN: {service.professional.pin}.\nContact: {service.professional.user.phone}'
        tempRatingList = []
        # rating decided by all the orders
        for order in Professionals.query.filter_by(id=service.professional.id).first().orders:

            if order.rating != None:
                tempRatingList.append(order.rating)
        try:
            tempDict['Rating'] = round(stat.mean(tempRatingList), 2)
        except:
            tempDict['Rating'] = 0
        finalList.append(tempDict)

    return jsonify(sorted(finalList, key=lambda x: x['Rating'], reverse=True))


@main_bp.get('/get_orders_of_user_id/<int:comp_id>')
@login_required
def get_orders_of_user_id(comp_id):

    ThisUsersOrders = Order.query.filter_by(user_id=comp_id).order_by(
        Order.booked_at.desc()).all()
    OrderList = [
        {
            "order_id": order.order_id,
            "professional_id": order.professional_id,
            "pro_name": order.professional.business_name,
            "pro_add": f"{order.professional.address}\nPIN: {order.professional.pin}\nCont: {order.professional.user.phone}",
            "status": order.status,
            "rating": order.rating,
            "booked_at": order.booked_at.isoformat() if order.booked_at else None,
            "closed_at": order.closed_at.isoformat() if order.closed_at else None,
            "accepted_at": order.accepted_at.isoformat() if order.accepted_at else None,
            "remark_by_customer": order.remark_by_customer,
            "services": order.service,
            "closed_by": order.closed_by,
        } for order in ThisUsersOrders
    ]

    return jsonify(OrderList)


@main_bp.route('/se')
def se():
    return render_template('v_c_dash.html', current_user=current_user)


@main_bp.get('/all_user')
def allUser():
    user_list = User.query.all()
    return {"users": [user.to_json() for user in user_list]}

################################################################## old code ################################################


@main_bp.route('/pro_add_service', methods=['POST'])
@login_required
def proAddService():
    service = request.form["service"]
    if service not in ServiceList:
        flash("Service is not in master list.", "error")
        return redirect(url_for('main.dashboard'))
    price = request.form["price"]
    description = request.form["description"]
    id = request.form["id"]

    professional = Professionals.query.get(
        id)
    professional.ServiceOffered[service] = [price, description]

    ser = Services(service=service, description=description,
                   price=price, serviceProvider=id)

    db.session.add(ser)
    db.session.commit()
    flash("Service created", "success")
    return redirect(url_for('main.dashboard'))


@main_bp.route('/pro_delete_service', methods=['POST'])
@login_required
def proDeleteService():
    service = request.form["service"]
    id = request.form["id"]

    professional = Professionals.query.get(
        id)
    if professional:
        ServiceOfferedDict = professional.ServiceOffered

        if service in ServiceOfferedDict:
            del ServiceOfferedDict[service]

        Services.query.filter_by(service=service, serviceProvider=id).delete()

        db.session.commit()

    return redirect(url_for('main.dashboard'))


@main_bp.route('/admin/delete_service', methods=["POST"])
@login_required
def deleteService():
    if current_user.role == "admin":
        item = request.form["service"]
        CompanyServices.query.filter_by(name=item).delete()
        Services.query.filter_by(service=item).delete()
        # Services.query.filter_by(service=item).delete()
        db.session.commit()
        flash("Service deleted from the database.", "success")
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.dashboard'))


@main_bp.route('/add_service', methods=['POST'])
@login_required
def addService():
    if current_user.role == "admin":
        service = request.form["service"]
        inCompService = CompanyServices.query.filter_by(name=service).first()
        if inCompService:
            flash("Service is already present in the database.", "error")
            return redirect(url_for('main.dashboard'))
        ser = CompanyServices(name=service)
        db.session.add(ser)
        db.session.commit()
        return redirect(url_for('main.dashboard'))

    else:
        return redirect(url_for('main.dashboard'))


@main_bp.route('/admin/activate_pro', methods=['POST'])
@login_required
def ActivatePro():
    b_value = request.form["b_value"]
    pro_id = request.form["pro_id"]

    pro = Professionals.query.filter_by(id=pro_id).first()

    user_id = pro.user_id
    user = User.query.filter_by(id=user_id).first()

    if b_value == "Approve":
        pro.status = "active"
        user.role = "professional"

        db.session.commit()

        return redirect(url_for('main.dashboard'))
    else:
        user.role == "customer"

        db.session.delete(pro)
        db.session.commit()
        return redirect(url_for('main.dashboard'))


@main_bp.route('/')
def home():
    if not current_user.is_authenticated:
        return render_template('login.html')
    else:
        return redirect(url_for('main.dashboard'))


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and (user.password == password):
            if user.status != "active":
                return "Your account is deactivated. Please contact admin."
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials!', 'error')
            return render_template('login.html')
    else:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html')


@main_bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        return render_template('login.html')
    elif current_user.role == "customer":
        ThisUsersOrders = Order.query.filter_by(user_id=current_user.id).order_by(
            Order.booked_at.desc()).all()
        # return render_template('c_dash.html', orders=ThisUsersOrders)
        return render_template('v_c_dash.html')
    elif current_user.role == "professional":
        professional = Professionals.query.filter_by(
            user_id=current_user.id).first()
        if professional.status == "blocked":
            return "<p>Your Services are blocked. Contact Admin</p>"
        professional_id = professional.id
        orders = Order.query.filter_by(professional_id=professional_id).order_by(
            Order.booked_at.desc()).all()
        ratingList = []
        for order in orders:
            if order.rating != None:
                ratingList.append(order.rating)
        if len(ratingList) == 0:
            ratingList = [0]

        # return render_template('pro_dash.html', professional=professional, orders=orders, rating=round(stat.mean(ratingList), 2),
            #    ServiceList=ServiceList)
        return render_template('v_pro_dash.html')
    elif current_user.role == "admin":
        return redirect(url_for('main.admin'))


@main_bp.route('/admin')
@login_required
def admin():
    pros = Professionals.query.all()
    users = User.query.all()
    notClosedOrders = Order.query.filter_by(status="accepted").order_by(
        Order.booked_at.desc()).all()
    sl = [u[0] for u in db.session.query(CompanyServices.name).all()]
    return render_template('admin/index.html', pros=pros, users=users, ServiceList=sl,
                           notClosedOrders=notClosedOrders)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        role = "customer"
        status = "active"
        new_user = User(username=username, password=password,
                        name=name, email=email, role=role, phone=phone, address=address, status=status)

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully! Please log in.', 'success')
            return redirect(url_for('main.login'))

        except IntegrityError:
            db.session.rollback()  # Rollback the transaction
            flash('Username already exists, please choose another one.', 'error')
            return redirect(url_for('main.register'))

    else:
        return render_template('reg_customer.html')


@main_bp.route('/userInfo', methods=['GET'])
@login_required
def userInfo():
    return render_template("user_info.html")


@main_bp.route('/user_info_edit', methods=["POST"])
@login_required  # Ensure the user is logged in
def userInfoEdit():
    formData = request.form

    for key, value in formData.items():
        if value:  # Only update if there's a value
            if key == "username":
                # Check if the username is already taken
                if User.query.filter_by(username=value).first():
                    flash("The username is not available. Try something else", "error")
                    return redirect(url_for('main.userInfo'))

            # Update the user's attribute
            # Use setattr to set the attribute
            setattr(current_user, key, value)

    db.session.commit()  # Save changes to the database

    flash("Data updated successfully!", "success")
    return redirect(url_for('main.userInfo'))


@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', "success")
    return redirect(url_for('main.login'))


@main_bp.route('/reg_professional', methods=['GET', 'POST'])
def reg_professional():
    if current_user.role == "customer":
        if request.method == "GET":
            return render_template("reg_professional.html", ServiceList=sorted(ServiceList))
        # Gather data from the form
        YoE = request.form["exp"]
        Bname = request.form["b_name"]
        UpFile = request.files['file']
        pin = request.form["pin"]
        address = request.form["address"]
        user_id = current_user.id
        orders = []
        services = {}

        for service in request.form.getlist('service'):
            price = request.form.get(f'price_{service}')
            description = request.form.get(f'description_{service}')
            services[service] = [price, description]

        UpFile = request.files['file']

        if UpFile and UpFile.filename.endswith('.pdf'):
            filename = secure_filename(
                f"user_id-{current_user.id}__{UpFile.filename}")
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)

            UpFile.save(file_path)

            file_url = f'/uploads/{filename}'

        NewPro = Professionals(user_id=user_id, business_name=Bname,
                               pin=pin, address=address, orders=orders,
                               ServiceOffered=services, YoE=YoE,
                               status="review", doc=file_url)

        db.session.add(NewPro)
        db.session.commit()

        serviceProvider = Professionals.query.filter_by(
            user_id=user_id).first().id

        for item in services.keys():
            ser = item
            price = services[item][0]
            description = services[item][1]

            newService = Services(service=ser, price=price,
                                  description=description,
                                  serviceProvider=serviceProvider)
            db.session.add(newService)

        db.session.commit()

        return "<p>Your application is received and waiting for admin's approval.</p>"

    elif current_user.role in ["professional", "admin"]:
        return redirect(url_for('main.dashboard'))
    else:
        flash("You must be a user and logged in to register as a professional", "error")
        return redirect(url_for('main.login'))


@main_bp.route('/accept_reject_it', methods=['POST'])
def AcceptRejectIt():
    val = request.form.get("b_value")
    order_id = request.form.get("order_id")

    if not val or not order_id:
        return redirect(url_for('main.dashboard'))

    order = Order.query.filter_by(order_id=order_id).first()

    if order:
        if val == "Accept":
            order.status = "accepted"
            order.accepted_at = datetime.utcnow()
        elif val == "Reject":
            order.status = "rejected"
            order.closed_by = "professional"
            order.closed_at = datetime.utcnow()

        db.session.commit()

    return redirect(url_for('main.dashboard'))


@main_bp.route('/close_it', methods=['POST'])
def closeIt():
    order_id = request.form["if_close"]
    rating = request.form["rating"]
    remark = request.form["remark"]
    order = Order.query.get(order_id)
    order.status = "closed"
    order.rating = float(rating)
    order.remark_by_customer = remark
    order.closed_at = datetime.utcnow()
    order.closed_by = "customer"
    db.session.commit()

    return redirect(url_for('main.dashboard'))


@main_bp.route('/FindService', methods=['POST'])
@login_required
def FindService():
    req_service = request.form["req_service"]
    avlbleService = Services.query.join(Professionals, Services.serviceProvider == Professionals.id) \
        .filter(
        Services.service.like(f'%{req_service}%'),
        Professionals.status == 'active'
    ).all()

    finalList = []

    for service in avlbleService:
        tempDict = {}
        tempDict['Service Name'] = service.service
        tempDict['Price'] = service.price
        tempDict['Service Provider'] = service.professional.business_name
        tempDict['Service Description'] = service.description
        tempDict['Professional ID'] = service.professional.id
        tempDict['Address'] = service.professional.address + \
            f'.\nPIN: {service.professional.pin}.\nContact: {service.professional.user.phone}'
        tempRatingList = []
        # rating decided by all the orders
        for order in Professionals.query.filter_by(id=service.professional.id).first().orders:

            if order.rating != None:
                tempRatingList.append(order.rating)
        try:
            tempDict['Rating'] = round(stat.mean(tempRatingList), 2)
        except:
            tempDict['Rating'] = 0
        finalList.append(tempDict)

    return render_template('find_service_result.html', req_service=req_service, services=sorted(finalList, key=lambda x: x['Rating'], reverse=True))


@main_bp.route('/PlaceOrder', methods=['POST'])
@login_required
def PlaceOrder():
    user_id = request.form["customer"]
    professional_id = request.form["professional_id"]
    service = request.form["service"]

    new_order = Order(user_id=user_id, professional_id=professional_id,
                      status="requested", rating=0.0, service=service
                      )
    db.session.add(new_order)
    db.session.commit()

    return redirect(url_for('main.dashboard'))
