from flask import Blueprint, render_template, request, redirect, flash, url_for
from website.models import Students, Programs, Colleges
from .. import mysql  # Import Flask-MySQLdb
import cloudinary.uploader

student_bp = Blueprint("student_bp", __name__)

# Home page
@student_bp.route("/")
@student_bp.route("/home")
def home():
    return render_template("home.html")

# Students page
@student_bp.route('/students', methods=['GET'])
def view_students():
    conn = mysql.connection

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Get data using model methods instead of direct queries
    students = Students.get_students_paginated(conn, page, per_page)
    total_students = Students.get_total_student_count(conn)
    
    # Calculate total pages
    total_pages = (total_students + per_page - 1) // per_page

    # Fetch programs for the dropdown
    programs = Programs.get_all_programs(conn)

    # Update status for each student
    for student in students:
        student_id = student['IDNumber']
        Students.check_and_update_status(conn, student_id)

    # Pass pagination data to the template
    return render_template(
        'student.html',
        students=students,
        programs=programs,
        page=page,
        total_pages=total_pages
    )


@student_bp.route('/students/', methods=['GET'])
def students_redirect():
    return redirect('/students')

# Add student
@student_bp.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == "POST":
        # Get form data
        idNumber = request.form.get("idNumber")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        courseCode = request.form.get("courseCode")
        year = request.form.get("year")
        gender = request.form.get("gender")
        file = request.files.get('file')

        # Allowed file extensions and MIME types
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        allowed_mime_types = {'image/jpeg', 'image/png'}
        max_file_size = 2 * 1024 * 1024  # 2 MB

        # Validate ID format
        if not Students.validate_id_format(idNumber):
            flash("ID Number must be in the format YYYY-NNNN (e.g., 2024-0001)", "error")
            return redirect(url_for('student_bp.view_students'))

        # Validate other input fields
        if not all([idNumber, firstName, lastName, courseCode, year, gender]):
            flash("Please fill out all the fields.", "error")
            return redirect(url_for('student_bp.view_students'))

        # Handle image upload
        image_url = None
        if file and file.filename != '':
            # Validate file size
            file.seek(0, 2)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > max_file_size:
                flash("The uploaded file is too large. Maximum allowed size is 2 MB.", "error")
                return redirect(url_for('student_bp.view_students'))
            
            # Extract the file extension and MIME type
            file_extension = file.filename.rsplit('.', 1)[-1].lower()
            file_mime_type = file.mimetype

            if file_extension not in allowed_extensions or file_mime_type not in allowed_mime_types:
                flash("Only image files (JPG, PNG) are allowed.", "error")
                return redirect(url_for('student_bp.view_students'))

            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"An error occurred during image upload: {str(e)}", "error")
                return redirect(url_for('student_bp.view_students'))

        try:
            conn = mysql.connection
            # Check if student ID already exists
            if Students.check_id_exists(idNumber):
                flash(f"Student with ID {idNumber} already exists!", "error")
            else:
                # Add new student with image URL
                new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, "Enrolled", image_url=image_url)
                new_student.save_student()
                flash("Student added successfully!", "success")
                # Check and update status if necessary
                Students.check_and_update_status(conn, idNumber)

        except Exception as e:
            flash(f"An error occurred: {str(e)}", "error")

        return redirect(url_for('student_bp.view_students'))

    return render_template('student.html')


# Delete student
@student_bp.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    conn = mysql.connection
    student = Students.find_by_id(conn, idNumber)
    if student:
        # Use model method instead of direct query
        Students.delete_by_id(conn, student['IDNumber'])
        flash("Student deleted successfully!", "success")
    return redirect(url_for('student_bp.view_students'))

# Edit student
@student_bp.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
def edit_student(idNumber):
    conn = mysql.connection

    if request.method == 'POST':
        # Get updated data from the form
        new_idNumber = request.form.get("idNumber")
        new_firstName = request.form.get("firstName")
        new_lastName = request.form.get("lastName")
        new_courseCode = request.form.get("courseCode")
        new_year = request.form.get("year")
        new_gender = request.form.get("gender")
        file = request.files.get('file')

        student = Students.find_by_id(conn, idNumber)
        if student:
            # Check if the new ID already exists
            existing_student = Students.find_by_id(conn, new_idNumber)
            if existing_student and existing_student['IDNumber'] != idNumber:
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

            # Handle the photo update if a new file is uploaded
            image_url = student['imageURL']  # Keep the current image URL as default
            if file and file.filename != '':
                # Validate file extension
                allowed_extensions = {'jpg', 'jpeg', 'png'}
                allowed_mime_types = {'image/jpeg', 'image/png'}

                file_extension = file.filename.rsplit('.', 1)[-1].lower()
                file_mime_type = file.mimetype

                if file_extension not in allowed_extensions or file_mime_type not in allowed_mime_types:
                    flash("Only image files (JPG, PNG) are allowed.", "error")
                    return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

                # Check file size (2MB = 2 * 1024 * 1024 bytes)
                MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB in bytes
                
                # Create a BytesIO object from the file
                from io import BytesIO
                file_content = file.read()
                file_size = len(file_content)
                
                print(f"DEBUG: File size is {file_size} bytes ({file_size / (1024*1024):.2f} MB)")  # Debug line
                
                if file_size > MAX_FILE_SIZE:
                    flash(f"File size ({file_size / (1024*1024):.2f} MB) exceeds the 2MB limit.", "error")
                    return redirect(url_for('student_bp.view_students', idNumber=idNumber))
                
                # Create a new file-like object for Cloudinary upload
                file_for_upload = BytesIO(file_content)
                file_for_upload.name = file.filename  # Preserve filename

                try:
                    upload_result = cloudinary.uploader.upload(file_for_upload)
                    image_url = upload_result.get('secure_url')
                except Exception as e:
                    flash(f"Error uploading image: {str(e)}", "error")
                    return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

            # Use model method instead of direct query
            Students.update_student_by_id(conn, idNumber, new_idNumber, new_firstName, new_lastName, 
                                        new_courseCode, new_year, new_gender, image_url)

            # Check and update status if necessary
            Students.check_and_update_status(conn, new_idNumber)

            flash(f"Student ID {new_idNumber} updated successfully!", "success")
            return redirect(url_for('student_bp.view_students'))

    student = Students.find_by_id(conn, idNumber)
    return render_template('edit_student.html', student=student)

# Search student
@student_bp.route('/search_student', methods=['GET'])
def search_student():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'idNumber': 'IDNumber',
        'firstName': 'firstName',
        'lastName': 'lastName',
        'course': 'CourseCode',
        'yearLevel': 'Year',
        'gender': 'Gender',
        'status': 'Status'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('student_bp.view_students'))

    # Pagination parameters for search
    page = request.args.get('page', 1, type=int)
    per_page = 50

    try:
        conn = mysql.connection
        
        # Use model methods instead of direct queries
        results = Students.search_students(conn, search_field, search_value, page, per_page)
        total_results = Students.get_search_count(conn, search_field, search_value)

        # Calculate total pages for search results
        total_pages = (total_results + per_page - 1) // per_page if total_results > 0 else 1

        # Get programs for the dropdown in the modals
        programs = Programs.get_all_programs(conn)

    except Exception as e:
        flash(f"An error occurred while searching: {e}", "danger")
        return redirect(url_for('student_bp.view_students'))

    # Convert results to the format expected by the template
    formatted_students = []
    if results:
        for result in results:
            formatted_student = {
                'IDNumber': result.get('IDNumber'),
                'firstName': result.get('firstName'),
                'lastName': result.get('lastName'),
                'CourseCode': result.get('programCode'),  # Use programCode from the search results
                'Year': result.get('Year'),
                'Gender': result.get('Gender'),
                'Status': result.get('Status'),
                'imageURL': result.get('imageURL'),
                'CourseDetails': f"{result.get('programCode')} ({result.get('collegeName')})" if result.get('programCode') and result.get('collegeName') else result.get('programCode')
            }
            formatted_students.append(formatted_student)

    # Always render the student template with search context
    # Change 'students.html' to match your actual template name
    return render_template(
        'student.html',  # or whatever your student template is actually named
        students=formatted_students,
        search_field=search_field,
        search_value=search_value,
        no_results=(len(formatted_students) == 0),
        page=page,
        total_pages=total_pages,
        programs=programs  # Pass programs for the add/edit form
    )