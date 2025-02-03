# Standard library imports
import os
import re
from datetime import datetime

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import pymysql

# Initialize Flask app
app = Flask(__name__)

# Install PyMySQL as a drop-in replacement for MySQLdb
pymysql.install_as_MySQLdb()

# Configure the app
app.secret_key = 'dfdgtdygrytedydtreyueyrytseyrtdyftrtyftftyftftyftfrtyd'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/vincentchieyinelawfirm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Mail
mail = Mail(app)

# Configure the email settings (Gmail SMTP settings)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'vinchieyine66@gmail.com'  # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'chieyine#@1866'  # Replace with your Gmail app password
app.config['MAIL_DEFAULT_SENDER'] = 'vinchieyine66@gmail.com'  # Replace with your Gmail

mail.init_app(app)

# Define the Testimonials model
class Testimonial(db.Model):
    __tablename__ = 'testimonials'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(200))  # For the file path or URL
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    appointment_date = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Appointment {self.fullname}, {self.email}>'
# Define the Contact model

class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False)

# Define the SubscriberActions model to store the logs
class SubscriberActions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), db.ForeignKey('newsletter.email'), nullable=False)  # Foreign key to Newsletter
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())

# Route to display and handle the form submission
@app.route('/vincentchieyinelawfirm-homepage', methods=['GET', 'POST'])
def submit_testimonial():
    testimonials = Testimonial.query.all()  # Fetch all testimonials from the database

    if request.method == 'POST':
        # Get form data
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Handle the profile picture file upload
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file:
                # Save the file (here we save it to an 'uploads' folder)
                upload_folder = 'uploads'
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, file.filename)
                file.save(file_path)
                profile_picture = file_path  # Save the file path to the database

        # Validate the required fields
        if not fullname or not email or not phone or not subject or not message:
            flash("All fields are required", "error")
            return redirect(url_for('submit_testimonial'))

        # Create and save the new testimonial to the database
        testimonial = Testimonial(
            fullname=fullname,
            email=email,
            phone=phone,
            profile_picture=profile_picture,
            subject=subject,
            message=message
        )
        db.session.add(testimonial)
        db.session.commit()

        # Flash a success message
        flash("Thank you for your testimonial!", "success")
        return redirect(url_for('submit_testimonial'))

    return render_template('index.html', testimonials=testimonials)



@app.route('/make_appointment', methods=['GET', 'POST'])
def submit_appointment():
    if request.method == 'POST':
        # Get form data
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        appointment_date = request.form['appointment_date']
        message = request.form['message']

        # Server-side validation (additional)
        if not fullname or not email or not phone or not appointment_date or not message:
            flash('All fields are required!')
            return redirect(url_for('submit_appointment'))

        # Create new appointment record
        new_appointment = Appointment(
            fullname=fullname,
            email=email,
            phone=phone,
            appointment_date=appointment_date,
            message=message
        )

        try:
            # Save the appointment to the database
            db.session.add(new_appointment)
            db.session.commit()
            flash('Your appointment has been successfully booked!')

            # Send confirmation email to the user
            user_message = Message(
                subject="Appointment Confirmation",
                recipients=[email],
                body=f"Hello {fullname},\n\nYour appointment has been successfully booked for {appointment_date}.\n\nMessage: {message}\n\nThank you for booking with us."
            )
            mail.send(user_message)

            # Send email to the admin (vinchieyine66@gmail.com)
            admin_message = Message(
                subject="New Appointment Booking",
                recipients=['vinchieyine66@gmail.com'],
                body=f"New appointment booked by {fullname}.\n\nDetails:\nFull Name: {fullname}\nEmail: {email}\nPhone: {phone}\nAppointment Date: {appointment_date}\nMessage: {message}"
            )
            mail.send(admin_message)

            # Redirect to the same page after successful booking
            return redirect(url_for('submit_appointment'))
        except Exception as e:
            # Rollback in case of error and show a flash message
            db.session.rollback()
            flash(f'An error occurred while saving your appointment: {e}')
            return redirect(url_for('submit_appointment'))

    return render_template('index.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Collect form data
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Validate form fields
        if not fullname or not email or not subject or not message:
            flash("All fields are required!", "danger")
            return redirect(url_for('contact'))

        # Validate email format
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash("Invalid email address!", "danger")
            return redirect(url_for('contact'))

        # Save to database
        try:
            # Save contact details
            contact_entry = ContactUs(
                fullname=fullname,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(contact_entry)
            db.session.commit()

        except Exception as db_error:
            db.session.rollback()  # Rollback database transaction
            flash(f"Failed to save your message to the database. Error: {db_error}", "danger")
            return redirect(url_for('contact'))

        try:
            # Send confirmation email
            msg = Message(
                subject=f"Contact Form: {subject}",
                recipients=['youradminemail@example.com'],  # Admin email
                body=f"Message from {fullname} ({email}):\n\n{message}"
            )
            mail.send(msg)

        except Exception as email_error:
            flash(f"Message sent successfully we will get bak to you as soon as possible but if we don't ,please do not hesitate to send us a Gmail message,  failed to send email. Error: {email_error}", "warning")
            return render_template('contacts.html', success_message="Your message has been saved successfully, but email delivery failed.")

        # Flash and send success message
        success_message = "Your message has been sent and saved successfully!"
        flash(success_message, "success")
        return render_template('contacts.html', success_message=success_message)

    return render_template('contacts.html')

# Route for the Form
@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form.get('email')

        # Email validation
        if not email:
            flash('Email is required!', 'error')
            return redirect(url_for('subscribe'))
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            flash('Invalid email format!', 'error')
            return redirect(url_for('subscribe'))

        # Save to the database
        try:
            new_subscription = Newsletter(email=email)
            db.session.add(new_subscription)
            db.session.commit()
            flash('Thank you for subscribing!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Email already subscribed or an error occurred.', 'error')

        return redirect(url_for('subscribe'))

    return render_template('index.html')
# Route to display subscribers with their actions
@app.route('/subscribers')
def subscribers():
    # Fetch all subscribers from the Newsletter model
    subscribers_list = Newsletter.query.all()  # This will fetch all records from the Newsletter table
    return render_template('subscribers.html', subscribers=subscribers_list)

# Send message route
@app.route('/send_message', methods=['POST'])
def send_message():
    topic = request.form['topic']
    message = request.form['message']
    selected_emails = request.form.getlist('emails')

    # Log action in SubscriberActions table
    for email in selected_emails:
        action_log = SubscriberActions(email=email, action=f"Message sent: {topic}")
        db.session.add(action_log)
    db.session.commit()  # Save actions in the SubscriberActions table

    # Process sending the message logic here, e.g., send via email
    print(f'Sending message to: {selected_emails}')
    print(f'Subject: Updates from VINCENT CHIEYINE & CO')
    print(f'Message: {message}')

    return jsonify({'status': 'success', 'message': 'Message sent successfully!'})

# Update subscriber route
@app.route('/update_subscriber', methods=['POST'])
def update_subscriber():
    email = request.form['email']
    new_email = request.form['new_email']
    
    # Update subscriber logic here (database update)
    subscriber = Newsletter.query.filter_by(email=email).first()
    if subscriber:
        subscriber.email = new_email
        db.session.commit()  # Save changes to the Newsletter table
        
        # Log action in SubscriberActions table
        action_log = SubscriberActions(email=new_email, action=f"Updated email to {new_email}")
        db.session.add(action_log)
        db.session.commit()  # Save action to the SubscriberActions table
        
        print(f'Updating {email} to {new_email}')
        return jsonify({'status': 'success', 'message': f'Email for {email} updated to {new_email}'})
    else:
        return jsonify({'status': 'error', 'message': 'Subscriber not found'})
# Delete subscriber route (updated to use deleted flag)
@app.route('/delete_subscriber', methods=['POST'])
def delete_subscriber():
    email = request.form['email']
    
    # Update subscriber logic here (set 'deleted' flag)
    subscriber = Newsletter.query.filter_by(email=email).first()
    if subscriber:
        subscriber.deleted = True  # Mark as deleted
        db.session.commit()  # Save changes
        
        # Log action in SubscriberActions table
        action_log = SubscriberActions(email=email, action="Deleted subscriber")
        db.session.add(action_log)
        db.session.commit()  # Save action to the SubscriberActions table
        
        print(f'Marking subscriber {email} as deleted')
        return jsonify({'status': 'success', 'message': f'{email} has been deleted.'})
    else:
        return jsonify({'status': 'error', 'message': 'Subscriber not found'})

@app.route('/about')
def about():
    return render_template('about.html')

# Route to display the thank-you message
@app.route('/thank_you')
def thank_you():
    return "Thank you for your testimonial!"

# Ensure you create tables inside the app context
with app.app_context():
    db.create_all()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
