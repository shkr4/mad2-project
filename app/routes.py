from flask import Flask, render_template, request, flash, Blueprint, current_app, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from .objs import *
from . import db
from .models import *
import os
import json
import statistics as stat
from datetime import datetime
from werkzeug.utils import secure_filename


main_bp = Blueprint('main', __name__)

login_manager = LoginManager()


@main_bp.route('/se')
def se():
    return render_template('some_ex.html')


@main_bp.get('/all_user')
def allUser():
    user_list = User.query.all()
    return {"users": [user.to_json() for user in user_list]}


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
    print(ser.service, ser.price)
    print(professional.ServiceOffered)

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
        id)  # Fetch the professional directly
    if professional:
        ServiceOfferedDict = professional.ServiceOffered

        # Check if the service exists before deleting
        if service in ServiceOfferedDict:
            del ServiceOfferedDict[service]
        else:
            print(f"Service '{service}' not found in offered services.")

        # Delete from Services table
        Services.query.filter_by(service=service, serviceProvider=id).delete()

        # Commit changes to the database
        db.session.commit()
    else:
        print("Professional not found.")

    return redirect(url_for('main.dashboard'))


@main_bp.route('/admin/delete_service', methods=["POST"])
@login_required
def deleteService():
    if current_user.role == "admin":
        item = request.form["service"]
        ServiceList.remove(item)
        Services.query.filter_by(service=item).delete()
        db.session.commit()
        flash("Service deleted from the Service List.", "success")
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('main.dashboard'))


@main_bp.route('/add_service', methods=['POST'])
@login_required
def addService():
    if current_user.role == "admin":
        service = request.form["service"]
        if service in ServiceList:
            flash("Service is already present in the Service List.", "error")
            return redirect(url_for('main.dashboard'))
        ServiceList.append(service)
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
        return render_template('c_dash.html', orders=ThisUsersOrders)
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

        return render_template('pro_dash.html', professional=professional, orders=orders, rating=round(stat.mean(ratingList), 2),
                               ServiceList=ServiceList)
    elif current_user.role == "admin":
        return redirect(url_for('main.admin'))


@main_bp.route('/admin')
@login_required
def admin():
    pros = Professionals.query.all()
    users = User.query.all()
    notClosedOrders = Order.query.filter_by(status="accepted").order_by(
        Order.booked_at.desc()).all()
    return render_template('admin/index.html', pros=pros, users=users, ServiceList=sorted(ServiceList),
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

        # Update user role in user table to "professional"

        # current_user.role = "professional"

        UpFile = request.files['file']

        # Check for allowed file type
        if UpFile and UpFile.filename.endswith('.pdf'):
            # Generate a secure filename
            filename = secure_filename(
                f"user_id-{current_user.id}__{UpFile.filename}")
            print(filename)
            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)

            print(file_path)
            # Save the file
            UpFile.save(file_path)

            # Generate a URL for the uploaded file
            file_url = f'/uploads/{filename}'

        # Add the this user as a professional in professional database

        NewPro = Professionals(user_id=user_id, business_name=Bname,
                               pin=pin, address=address, orders=orders,
                               ServiceOffered=services, YoE=YoE,
                               status="review", doc=file_url)
        # current_user.hasAppliedForPro = True

        db.session.add(NewPro)
        db.session.commit()

        # services in the Services Table

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

        # return render_template("pro_dash.html", professional=Professionals.query.filter_by(user_id=user_id).first())
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

    order = Order.query.filter_by(order_id=order_id).first()  # Fetch the order

    if order:  # Ensure the order exists
        if val == "Accept":
            order.status = "accepted"
            order.accepted_at = datetime.utcnow()  # Correct usage
        elif val == "Reject":
            order.status = "rejected"
            order.closed_by = "professional"
            order.closed_at = datetime.utcnow()  # Correct usage

        db.session.commit()  # Commit changes to the database

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
    # Search for services that match the requested service
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
        for order in Professionals.query.filter_by(id=service.professional.id).first().orders:

            if order.rating != None:
                tempRatingList.append(order.rating)
        try:
            tempDict['Rating'] = round(stat.mean(tempRatingList), 2)
        except:
            tempDict['Rating'] = 0
        finalList.append(tempDict)
    # Services.query.filter(
    #     Services.service.like(f'%{req_service}%')).all()  # Get all matches

    # Pass both the requested service and the results to the template
    return render_template('find_service_result.html', req_service=req_service, services=sorted(finalList, key=lambda x: x['Rating'], reverse=True))


@ main_bp.route('/PlaceOrder', methods=['POST'])
@ login_required
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
