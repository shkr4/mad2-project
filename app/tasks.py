from celery import shared_task
from .workers import celery  # Import from workers.py directly
import time
from datetime import datetime
from app import mail, mailUsername
from flask_mail import Message
from .models import User, Professionals, Order


from flask import current_app as app


@shared_task
def send_daily_reminder():
    with app.app_context():
        professionals = Professionals.query.all()
        for pro in professionals:
            pending_requests = Order.query.filter_by(
                professional_id=pro.id, status='requested').count()
            if pending_requests > 0:
                email = User.query.filter_by(id=pro.user_id).first().email
                msg = Message(subject="Service Reminder",
                              sender=mailUsername,
                              recipients=[email])
                msg.body = f"Hello {pro.business_name}, you have {pending_requests} pending service requests."
                mail.send(msg)


@shared_task
def send_monthly_report():
    with app.app_context():
        customers = User.query.filter_by(role="customer").all()
        for cust in customers:
            services = Order.query.filter_by(user_id=cust.id).all()

            report = f"Dear {cust.name}, you had {len(services)} service requests this month."

            msg = Message("Monthly Service Report",
                          sender=mailUsername,
                          recipients=[cust.email])
            msg.body = report
            mail.send(msg)


@celery.task(bind=True)
def export_service_csv(self, professional_id):
    with app.app_context():
        from io import StringIO
        import csv
        from flask import current_app

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["Service ID", "Customer ID",
                        "Date of Request", "Remarks"])

        services = Order.query.filter_by(
            professional_id=professional_id, status='closed').all()
        for service in services:
            writer.writerow([service.order_id, service.user_id,
                            service.booked_at, service.remark_by_customer])

        output.seek(0)
        file_path = f"{app.config['UPLOAD_FOLDER']}/service_report/service_export_pro_id_{professional_id}_{datetime.utcnow()}.csv"

        with open(file_path, "w") as f:
            f.write(output.getvalue())

        return f"CSV file created at {file_path}"
