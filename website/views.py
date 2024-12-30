from flask import Blueprint, render_template, request, redirect, flash, url_for
from .models import Students, Programs, Colleges
from . import mysql  # Import Flask-MySQLdb
import cloudinary.uploader

views = Blueprint("views", __name__)

# Home page
@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")

# Students page
@views.route('/students', methods=['GET'])
def view_students():
    conn = mysql.connection  # Access the MySQL connection from Flask

    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # Current page, default to 1
    per_page = 50  # Number of students per page
    offset = (page - 1) * per_page  # Calculate the offset

    # Query total count of students
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM student")  # Adjust if needed
    total_students = cursor.fetchone()[0]

    # Calculate total pages
    total_pages = (total_students + per_page - 1) // per_page  # Ceiling division

    # Fetch paginated students
    cursor.execute(f"SELECT * FROM student LIMIT {per_page} OFFSET {offset}")
    results = cursor.fetchall()

    # Fetch column names for building manual dictionaries
    column_names = [desc[0] for desc in cursor.description]
    cursor.close()

    # Manually build a dictionary for each row
    students = []
    for row in results:
        row_dict = dict(zip(column_names, row))
        students.append({
            "IDNumber": row_dict['IDNumber'],
            "firstName": row_dict['firstName'],
            "lastName": row_dict['lastName'],
            "Year": row_dict['Year'],
            "Gender": row_dict['Gender'],
            "Status": row_dict['Status'],
            "imageURL": row_dict['imageURL'],
            "CourseCode": row_dict['CourseCode']
        })

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



@views.route('/students/', methods=['GET'])
def students_redirect():
    return redirect('/students')


# Programs page
@views.route('/programs', methods=['GET'])
def view_programs():
    conn = mysql.connection
    programs = Programs.get_all_programs(conn)
    colleges = Colleges.get_all_colleges(conn)
    return render_template('program.html', programs=programs, colleges=colleges)

# Colleges page
@views.route('/colleges', methods=['GET'])
def college_page():
    conn = mysql.connection
    colleges = Colleges.get_all_colleges(conn)  # Query colleges from DB
    return render_template('college.html', colleges=colleges)

# Add student
@views.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == "POST":
        # Get form data
        idNumber = request.form.get("idNumber")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        courseCode = request.form.get("courseCode")
        year = request.form.get("year")
        gender = request.form.get("gender")
        file = request.files.get('file')  # Handle the file upload

        # Allowed file extensions and MIME types
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        allowed_mime_types = {'image/jpeg', 'image/png'}
        max_file_size = 2 * 1024 * 1024  # 2 MB

        # Validate ID format
        if not Students.validate_id_format(idNumber):
            flash("ID Number must be in the format YYYY-NNNN (e.g., 2024-0001)", "error")
            return redirect(url_for('views.view_students'))

        # Validate other input fields
        if not all([idNumber, firstName, lastName, courseCode, year, gender]):
            flash("Please fill out all the fields.", "error")
            return redirect(url_for('views.view_students'))

        # Handle image upload
        image_url = None
        if file and file.filename != '':
            # Validate file size
            file.seek(0, 2)  # Move to the end of the file
            file_size = file.tell()  # Get the file size in bytes
            file.seek(0)  # Reset file pointer to the start
            
            if file_size > max_file_size:
                flash("The uploaded file is too large. Maximum allowed size is 2 MB.", "error")
                return redirect(url_for('views.view_students'))
            # Extract the file extension and MIME type
            file_extension = file.filename.rsplit('.', 1)[-1].lower()
            file_mime_type = file.mimetype

            if file_extension not in allowed_extensions or file_mime_type not in allowed_mime_types:
                flash("Only image files (JPG, PNG) are allowed.", "error")
                return redirect(url_for('views.view_students'))

            try:
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"An error occurred during image upload: {str(e)}", "error")
                return redirect(url_for('views.view_students'))

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

        return redirect(url_for('views.view_students'))

    return render_template('student.html')


# Delete student
@views.route('/delete_student/<idNumber>', methods=['POST'])
def delete_student(idNumber):
    conn = mysql.connection
    student = Students.find_by_id(idNumber)
    if student:
        # Manually delete using the student IDNumber
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE IDNumber = %s", (student['IDNumber'],))
        conn.commit()
        cursor.close()
        flash("Student deleted successfully!", "success")
    return redirect(url_for('views.view_students'))

# Edit student
@views.route('/edit_student/<idNumber>', methods=['GET', 'POST'])
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
        file = request.files.get('file')  # Get the uploaded file

        student = Students.find_by_id(idNumber)
        if student:
            # Check if the new ID already exists
            existing_student = Students.find_by_id(new_idNumber)
            if existing_student and existing_student['IDNumber'] != idNumber:
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('views.edit_student', idNumber=idNumber))

            # Handle the photo update if a new file is uploaded
            image_url = student['imageURL']  # Keep the current image URL as default
            if file and file.filename != '':  # Check if a new file is uploaded
                # Validate file extension
                allowed_extensions = {'jpg', 'jpeg', 'png'}
                allowed_mime_types = {'image/jpeg', 'image/png'}

                file_extension = file.filename.rsplit('.', 1)[-1].lower()
                file_mime_type = file.mimetype

                if file_extension not in allowed_extensions or file_mime_type not in allowed_mime_types:
                    flash("Only image files (JPG, PNG) are allowed.", "error")
                    return redirect(url_for('views.edit_student', idNumber=idNumber))

                try:
                    # Upload the image using Cloudinary (or your chosen image storage service)
                    upload_result = cloudinary.uploader.upload(file)
                    image_url = upload_result.get('secure_url')  # Get the URL of the uploaded image
                except Exception as e:
                    flash(f"Error uploading image: {str(e)}", "error")
                    return redirect(url_for('views.edit_student', idNumber=idNumber))

            # Proceed with updating the student record in the database
            cursor = conn.cursor()
            cursor.execute("""UPDATE student 
                              SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, imageURL = %s
                              WHERE IDNumber = %s""",
                           (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, image_url, idNumber))
            conn.commit()
            cursor.close()

            # Check and update status if necessary
            Students.check_and_update_status(conn, new_idNumber)

            flash(f"Student ID {new_idNumber} updated successfully!", "success")
            return redirect(url_for('views.view_students'))

    student = Students.find_by_id(conn, idNumber)
    return render_template('edit_student.html', student=student)

# Add program
@views.route('/add_program', methods=['GET', 'POST'])
def add_program():
    if request.method == "POST":
        programCode = request.form.get("courseCode")
        programTitle = request.form.get("courseTitle")
        programCollege = request.form.get("collegeCode")

        conn = mysql.connection
        if Programs.check_program_exists(programCode):
            flash(f"Program with code {programCode} already exists!", "error")
            return redirect(url_for('views.view_programs'))

        new_program = Programs(programCode, programTitle, programCollege)
        new_program.save_program()
        flash("Program added successfully!", "success")
        return redirect(url_for('views.view_programs'))

    return render_template('program.html')

# Delete program
@views.route('/delete_program/<program_code>', methods=['POST'])
def delete_program(program_code):
    conn = mysql.connection
    try:
        Programs.delete_program(program_code)
        flash("Program deleted successfully!", "success")
    except Exception as e:
        flash(f"An error occurred while trying to delete the program: {e}", "error")
    return redirect(url_for('views.view_programs'))


# Edit program
@views.route('/edit_program/<originalProgramCode>', methods=['GET', 'POST'])
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
        return redirect(url_for('views.view_programs'))

    program = Programs.find_by_program(originalProgramCode)
    colleges = Colleges.get_all_colleges()
    return render_template('edit_program.html', program=program, colleges=colleges)

# Add college
@views.route('/add_college', methods=['GET', 'POST'])
def add_college():
    if request.method == "POST":
        collegeCode = request.form.get("collegeCode")
        collegeName = request.form.get("collegeName")

        conn = mysql.connection  # Get the DB connection

        if Colleges.check_college_exists(collegeCode):
            flash(f"College with code {collegeCode} already exists!", "error")
            return redirect(url_for('views.college_page'))

        new_college = Colleges(collegeCode, collegeName)
        new_college.save_college()
        flash("College added successfully!", "success")
        return redirect(url_for('views.college_page'))

    return render_template('college.html')


# Delete college
@views.route('/delete_college/<collegeCode>', methods=['POST'])
def delete_college(collegeCode):
    conn = mysql.connection
    college = Colleges.find_by_college(collegeCode)

    if college:
        college.delete_college()
        conn.commit()
        flash(f"College with code {collegeCode} deleted successfully.", "success")
    else:
        flash(f"No college found with code {collegeCode}.", "error")

    return redirect(url_for('views.college_page'))

# Edit college
@views.route('/edit_college/<originalCollegeCode>', methods=['POST'])
def edit_college(originalCollegeCode):
    print(f"Original College Code: {originalCollegeCode}")  # Debugging line

    new_collegeCode = request.form.get('collegeCode')
    new_collegeName = request.form.get('collegeName')

    # Make sure the form is properly filled out
    if not new_collegeCode or not new_collegeName:
        flash("Please provide both college code and name.", "error")
        return redirect(url_for('views.college_page'))

    # Call update_college with both the original and new codes
    Colleges.update_college(originalCollegeCode, new_collegeCode, new_collegeName)
    
    flash("College updated successfully!", "success")
    return redirect(url_for('views.college_page'))

# Search college
@views.route('/search_college', methods=['GET'])
def search_college():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'collegeCode': 'collegeCode',
        'collegeName': 'collegeName'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('views.college_page'))

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
        return redirect(url_for('views.college_page'))

    if len(results) == 1:
        return render_template('college.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('college.html', colleges=results)  # Multiple results
    else:
        flash("No colleges found.", "warning")
        return redirect(url_for('views.college_page'))


# Search program
@views.route('/search_program', methods=['GET'])
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
        return redirect(url_for('views.program_page'))

    query = f"SELECT * FROM program WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
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
        return redirect(url_for('views.program_page'))

    if len(results) == 1:
        return render_template('program.html', search_result=results[0])  # Single result
    elif len(results) > 1:
        return render_template('program.html', programs=results)  # Multiple results
    else:
        flash("No programs found.", "warning")
        return redirect(url_for('views.program_page'))


# Search student
# Search student
@views.route('/search_student', methods=['GET'])
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
        return redirect(url_for('views.view_students'))

    # Build the SQL query for gender with length check and exact matching
    if search_field == 'gender':
        query = f"""
            SELECT * FROM student 
            WHERE LENGTH({field_map[search_field]}) = LENGTH(TRIM(%s)) 
            AND LOWER({field_map[search_field]}) = LOWER(TRIM(%s))
        """
        params = [search_value, search_value]  # Use the search_value for both length and matching check
    else:
        query = f"""
            SELECT * FROM student 
            WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)
        """
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
        return redirect(url_for('views.view_students'))

    if len(results) > 0:
        return render_template(
            'search_results.html',  # Render a different template for search results
            students=results, 
            search_field=search_field, 
            search_value=search_value
        )  # Display all results without pagination
    else:
        flash("No students found.", "warning")
        return redirect(url_for('views.view_students'))
