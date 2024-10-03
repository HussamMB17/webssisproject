from flask import Flask, render_template, redirect, url_for, request, jsonify
from forms import StudentForm
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

app = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

app.config['SECRET_KEY'] = 'mysecretkey'
# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

mysql = MySQL(app)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Logic to handle form data goes here
        return redirect(url_for('home'))
    return render_template('add_student.html', form=form)
# Get form data
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')

    # Here you would typically save the data to your database
    # For example:
    # new_student = Student(firstname=firstname, lastname=lastname)
    # db.session.add(new_student)
    # db.session.commit()

    # Return a JSON response (you can customize the response as needed)
    return jsonify({"message": "Student added successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
