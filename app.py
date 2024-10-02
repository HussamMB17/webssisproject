from flask import Flask, render_template, redirect, url_for
from webssisproject.forms import StudentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Logic to handle form data goes here
        return redirect(url_for('home'))
    return render_template('add_student.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
