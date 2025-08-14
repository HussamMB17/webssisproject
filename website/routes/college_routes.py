from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Students, Programs, Colleges
from .. import mysql  # Import Flask-MySQLdb
import cloudinary.uploader

college_bp = Blueprint("college_bp", __name__)

# Home page
@college_bp.route("/")
@college_bp.route("/home")
def home():
    return render_template("home.html")

# Colleges page
@college_bp.route('/colleges/', methods=['GET'])
def college_page():
    conn = mysql.connection
    colleges = Colleges.get_all_colleges(conn)  # Query colleges from DB
    return render_template('college.html', colleges=colleges)

# Add college
@college_bp.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        conn = mysql.connection  # Get the DB connection

        if Colleges.check_college_exists(collegeCode):
            flash(f"College with code {collegeCode} already exists!", "error")
            return redirect(url_for('college_bp.college_page'))

        new_college = Colleges(collegeCode, collegeName)
        new_college.save_college()
        flash("College added successfully!", "success")
        return redirect(url_for('college_bp.college_page'))

    return render_template('college.html')

# Delete college
@college_bp.route('/delete_college/<collegeCode>', methods=['POST'])
def delete_college(collegeCode):
    conn = mysql.connection
    college = Colleges.find_by_college(collegeCode)

    if college:
        college.delete_college()
        conn.commit()
        flash(f"College with code {collegeCode} deleted successfully.", "success")
    else:
        flash(f"No college found with code {collegeCode}.", "error")

    return redirect(url_for('college_bp.college_page'))

# Edit college
@college_bp.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    print(f"Original College Code: {originalCollegeCode}")  # Debugging line

    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    # Make sure the form is properly filled out
    if not new_collegeCode or not new_collegeName:
        flash("Please provide both college code and name.", "error")
        return redirect(url_for('college_bp.college_page'))

    # Call update_college with both the original and new codes
    Colleges.update_college(originalCollegeCode, new_collegeCode, new_collegeName)
    
    flash("College updated successfully!", "success")
    return redirect(url_for('college_bp.college_page'))

# Search college
@college_bp.route('/search_college', methods=['GET'])
def search_college():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'collegeCode': 'collegeCode',
        'collegeName': 'collegeName'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('college_bp.college_page'))

    try:
        conn = mysql.connection
        # Use model method instead of direct query
        results = Colleges.search_colleges(conn, search_field, search_value)
        
    except Exception as e:
        flash(f"An error occurred while searching: {e}", "danger")
        return redirect(url_for('college_bp.college_page'))

    # Always render the college template with search context
    return render_template(
        'college.html',
        colleges=results if len(results) > 0 else [],
        search_field=search_field,
        search_value=search_value,
        no_results=(len(results) == 0)
    )