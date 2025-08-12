from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Students, Programs, Colleges
from .. import mysql  # Import Flask-MySQLdb
import cloudinary.uploader

program_bp = Blueprint("program_bp", __name__)

# Home page
@program_bp.route("/")
@program_bp.route("/home")
def home():
    return render_template("home.html")

# Programs page
@program_bp.route('/programs', methods=['GET'])
def view_programs():
    conn = mysql.connection
    programs = Programs.get_all_programs(conn)
    colleges = Colleges.get_all_colleges(conn)
    return render_template('program.html', programs=programs, colleges=colleges)

# Add program
@program_bp.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        conn = mysql.connection
        if Programs.check_program_exists(programCode):
            flash(f"Program with code {programCode} already exists!", "error")
            return redirect(url_for('program_bp.view_programs'))

        new_program = Programs(programCode, programTitle, programCollege)
        new_program.save_program()
        flash("Program added successfully!", "success")
        return redirect(url_for('program_bp.view_programs'))

    return render_template('program.html')

# Delete program
@program_bp.route('/delete_program/<program_code>', methods=['POST'])
def delete_program(program_code):
    conn = mysql.connection
    try:
        Programs.delete_program(program_code)
        flash("Program deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while trying to delete the program: {e}", "error")
    return redirect(url_for('program_bp.view_programs'))

# Edit program
@program_bp.route('/edit_program/<originalProgramCode>', methods=['GET', 'POST'])
def edit_program(originalProgramCode):
    conn = mysql.connection

    if request.method == 'POST':
        new_programCode = request.form.get("courseCode")
        new_programTitle = request.form.get("courseTitle")
        new_collegeCode = request.form.get("collegeCode")

        program = Programs.find_by_program(originalProgramCode)
        if program:
            program.update_program(new_programCode, new_programTitle, new_collegeCode)
            conn.commit()
            flash("Program updated successfully!", "success")
        return redirect(url_for('program_bp.view_programs'))

    program = Programs.find_by_program(originalProgramCode)
    colleges = Colleges.get_all_colleges(conn)  # Fixed: Added conn parameter
    return render_template('edit_program.html', program=program, colleges=colleges)

# Search program
@program_bp.route('/search_program', methods=['GET'])
def search_program():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'programCode': 'programCode',
        'programTitle': 'programTitle',
        'programCollege': 'programCollege'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('program_bp.view_programs'))  # Fixed: Changed to view_programs

    try:
        conn = mysql.connection
        # Use model method instead of direct query
        results = Programs.search_programs(conn, search_field, search_value)
        
    except Exception as e:
        flash(f"An error occurred while searching: {e}", "danger")
        return redirect(url_for('program_bp.view_programs'))  # Fixed: Changed to view_programs

    if len(results) == 1:
        return render_template('program.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('program.html', programs=results)  # Multiple results
    else:
        flash("No programs found.", "warning")
        return redirect(url_for('program_bp.view_programs'))  # Fixed: Changed to view_programs