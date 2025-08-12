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
        file = request.files.get('file')  # Handle the file upload

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
            file.seek(0, 2)  # Move to the end of the file
            file_size = file.tell()  # Get the file size in bytes
            file.seek(0)  # Reset file pointer to the start
            
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
                new_student = Students(idNumber, firstName, lastName, courseCode, year, gender, "Enrolled", ImageURL=image_url)
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
    student = Students.find_by_id(idNumber)
    if student:
        # Manually delete using the student IDNumber
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE IDNumber = %s", (student['IDNumber'],))
        conn.commit()
        cursor.close()
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
        file = request.files.get('file')  # Get the uploaded file

        student = Students.find_by_id(idNumber)
        if student:
            # Check if the new ID already exists
            existing_student = Students.find_by_id(new_idNumber)
            if existing_student and existing_student['IDNumber'] != idNumber:
                flash(f"ID Number {new_idNumber} is already in use.", "error")
                return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

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
                    return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

                try:
                    # Upload the image using Cloudinary (or your chosen image storage service)
                    upload_result = cloudinary.uploader.upload(file)
                    image_url = upload_result.get('secure_url')  # Get the URL of the uploaded image
                except Exception as e:
                    flash(f"Error uploading image: {str(e)}", "error")
                    return redirect(url_for('student_bp.edit_student', idNumber=idNumber))

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
            return redirect(url_for('student_bp.view_students'))

    student = Students.find_by_id(conn, idNumber)
    return render_template('edit_student.html', student=student)

# Search student
# Search student
@student_bp.route('/search_student', methods=['GET'])
def search_student():
    search_field = request.args.get('searchField')
    search_value = request.args.get('searchValue')

    field_map = {
        'idNumber': 'IDNumber',
        'firstName': 'firstName',
        'lastName': 'lastName',
        'course': 'CourseCode',  # We will handle the CourseDetails separately
        'yearLevel': 'Year',
        'gender': 'Gender',
        'status': 'Status'
    }

    if search_field not in field_map:
        flash("Invalid search field!", "danger")
        return redirect(url_for('student_bp.view_students'))

    # Pagination parameters for search
    page = request.args.get('page', 1, type=int)  # Current page, default to 1
    per_page = 50  # Number of students per page
    offset = (page - 1) * per_page  # Calculate the offset

    # Build the SQL query for gender with length check and exact matching
    if search_field == 'gender':
        query = f"""
            SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
            FROM student s 
            LEFT JOIN program p ON s.CourseCode = p.programCode
            LEFT JOIN college c ON p.programCollege = c.collegeCode
            WHERE LENGTH({field_map[search_field]}) = LENGTH(TRIM(%s)) 
            AND LOWER({field_map[search_field]}) = LOWER(TRIM(%s))
            LIMIT {per_page} OFFSET {offset}
        """
        params = [search_value, search_value]  # Use the search_value for both length and matching check
    elif search_field == 'course':
        # If searching for course, show the combined CourseDetails
        query = f"""
            SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
            FROM student s
            LEFT JOIN program p ON s.CourseCode = p.programCode
            LEFT JOIN college c ON p.programCollege = c.collegeCode
            WHERE CONCAT(p.programCode, ' (', c.collegeName, ')') LIKE LOWER(%s)
            LIMIT {per_page} OFFSET {offset}
        """
        params = [f"%{search_value}%"]  # Use LIKE to match CourseDetails
    else:
        query = f"""
            SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
            FROM student s
            LEFT JOIN program p ON s.CourseCode = p.programCode
            LEFT JOIN college c ON p.programCollege = c.collegeCode
            WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)
            LIMIT {per_page} OFFSET {offset}
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

        # Query to get the total count of search results
        cursor.execute(f"""
            SELECT COUNT(*) FROM student s
            LEFT JOIN program p ON s.CourseCode = p.programCode
            LEFT JOIN college c ON p.programCollege = c.collegeCode
            WHERE CONCAT(p.programCode, ' (', c.collegeName, ')') LIKE LOWER(%s)
        """, [f"%{search_value}%"])
        total_results = cursor.fetchone()[0]

        # Calculate total pages for search results
        total_pages = (total_results + per_page - 1) // per_page  # Ceiling division
        cursor.close()
    except Exception as e:
        flash(f"An error occurred while searching: {e}", "danger")
        return redirect(url_for('student_bp.view_students'))

    if len(results) > 0:
        return render_template(
            'search_results.html',  # Render a different template for search results
            students=results, 
            search_field=search_field, 
            search_value=search_value,
            page=page,
            total_pages=total_pages
        )  # Display paginated results
    else:
        flash("No students found.", "warning")
        return redirect(url_for('student_bp.view_students'))