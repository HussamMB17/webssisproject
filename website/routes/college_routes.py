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

    query = f"SELECT * FROM college WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
    params = [f"%{search_value}%"]

    try:
        conn = mysql.connection  # Use the established connection
        cursor = conn.cursor()  # Using default cursor without MySQLdb import
        cursor.execute(query, params)
        # Fetch the results and convert them into a list of dictionaries
        columns = [desc[0] for desc in cursor.description]  # Get column names
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]  # Convert rows to dictionaries
        cursor.close()
    except Exception as e:
        flash(f"An error occurred while searching: {e}", "danger")
        return redirect(url_for('college_bp.college_page'))

    if len(results) == 1:
        return render_template('college.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('college.html', colleges=results)  # Multiple results
    else:
        flash("No colleges found.", "warning")
        return redirect(url_for('college_bp.college_page'))
    
    