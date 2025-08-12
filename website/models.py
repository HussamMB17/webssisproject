from . import mysql
import re


class Students:
    def __init__(self, idNumber, firstName, lastName, courseCode, year, gender, status, image_url=None):
        self.idNumber = idNumber
        self.firstName = firstName
        self.lastName = lastName
        self.courseCode = courseCode
        self.year = year
        self.gender = gender
        self.status = status
        self.imageURL = image_url  # New field for the image URL

    def save_student(self):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        sql = """
            INSERT INTO student (IDNumber, firstName, lastName, CourseCode, Year, Gender, Status, imageURL)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (self.idNumber, self.firstName, self.lastName, self.courseCode, self.year, self.gender, self.status, self.imageURL))
        conn.commit()
        cursor.close()

    @staticmethod
    def get_all_students(conn):
        # Create a cursor object from the connection
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute("SELECT * FROM student")
        
        # Get column names from the cursor description
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all rows from the executed query
        students = cursor.fetchall()
        
        # Convert each row into a dictionary using column names
        students_dict = [dict(zip(columns, row)) for row in students]
        
        # Close the cursor
        cursor.close()
        
        # Return the list of student dictionaries
        return students_dict

    @staticmethod
    def get_students_paginated(conn, page=1, per_page=50):
        """Get paginated students with course and college details"""
        offset = (page - 1) * per_page
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                s.IDNumber, 
                s.firstName, 
                s.lastName, 
                s.Year, 
                s.Gender, 
                s.Status, 
                s.imageURL, 
                p.programCode, 
                c.collegeName
            FROM 
                student s
            LEFT JOIN 
                program p ON s.CourseCode = p.programCode
            LEFT JOIN 
                college c ON p.programCollege = c.collegeCode
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        cursor.close()

        # Build student dictionaries
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
                "CourseDetails": f"{row_dict['programCode']} ({row_dict['collegeName']})" if row_dict['programCode'] and row_dict['collegeName'] else row_dict['programCode']
            })
        
        return students

    @staticmethod
    def get_total_student_count(conn):
        """Get total count of students"""
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student")
        total_students = cursor.fetchone()[0]
        cursor.close()
        return total_students

    def update_student(self, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender,
                       new_status, new_image_url=None):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE student 
            SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, Status = %s, imageURL = %s
            WHERE IDNumber = %s""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, new_status, new_image_url, self.idNumber))
        conn.commit()
        cursor.close()

    @staticmethod
    def update_student_by_id(conn, old_id, new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, image_url):
        """Update student by ID - moved from routes"""
        cursor = conn.cursor()
        cursor.execute("""UPDATE student 
                          SET IDNumber = %s, firstName = %s, lastName = %s, CourseCode = %s, Year = %s, Gender = %s, imageURL = %s
                          WHERE IDNumber = %s""",
                       (new_idNumber, new_firstName, new_lastName, new_courseCode, new_year, new_gender, image_url, old_id))
        conn.commit()
        cursor.close()

    @staticmethod
    def check_id_exists(idNumber):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM student WHERE IDNumber = %s", (idNumber,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Returns True if the ID exists, otherwise False

    @staticmethod
    def validate_id_format(idNumber):
        """
        Validate if the idNumber is in the format YYYY-NNNN.
        """
        pattern = r'^\d{4}-\d{4}$'
        return re.match(pattern, idNumber) is not None

    def delete_student(self):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute('DELETE FROM student WHERE IDNumber = %s', (self.idNumber,))
        conn.commit()
        cursor.close()

    @staticmethod
    def delete_by_id(conn, idNumber):
        """Delete student by ID - moved from routes"""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM student WHERE IDNumber = %s", (idNumber,))
        conn.commit()
        cursor.close()

    @staticmethod
    def find_by_id(conn, idNumber):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student WHERE IDNumber = %s", (idNumber,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            cursor.close()
            return result

        cursor.close()
        return None

    @staticmethod
    def search_students(conn, search_field, search_value, page=1, per_page=50):
        """Search students with pagination - moved from routes"""
        offset = (page - 1) * per_page
        
        field_map = {
            'idNumber': 'IDNumber',
            'firstName': 'firstName',
            'lastName': 'lastName',
            'course': 'CourseCode',
            'yearLevel': 'Year',
            'gender': 'Gender',
            'status': 'Status'
        }

        cursor = conn.cursor()

        # Build the SQL query based on search field
        if search_field == 'gender':
            query = f"""
                SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
                FROM student s 
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE LENGTH({field_map[search_field]}) = LENGTH(TRIM(%s)) 
                AND LOWER({field_map[search_field]}) = LOWER(TRIM(%s))
                LIMIT %s OFFSET %s
            """
            params = [search_value, search_value, per_page, offset]
        elif search_field == 'course':
            query = """
                SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
                FROM student s
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE CONCAT(p.programCode, ' (', c.collegeName, ')') LIKE LOWER(%s)
                LIMIT %s OFFSET %s
            """
            params = [f"%{search_value}%", per_page, offset]
        else:
            query = f"""
                SELECT s.IDNumber, s.firstName, s.lastName, s.Year, s.Gender, s.Status, s.imageURL, p.programCode, c.collegeName
                FROM student s
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)
                LIMIT %s OFFSET %s
            """
            params = [f"%{search_value}%", per_page, offset]

        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()

        return results

    @staticmethod
    def get_search_count(conn, search_field, search_value):
        """Get total count of search results - moved from routes"""
        cursor = conn.cursor()
        
        field_map = {
            'idNumber': 'IDNumber',
            'firstName': 'firstName',
            'lastName': 'lastName',
            'course': 'CourseCode',
            'yearLevel': 'Year',
            'gender': 'Gender',
            'status': 'Status'
        }

        if search_field == 'gender':
            query = f"""
                SELECT COUNT(*) FROM student s
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE LENGTH({field_map[search_field]}) = LENGTH(TRIM(%s)) 
                AND LOWER({field_map[search_field]}) = LOWER(TRIM(%s))
            """
            params = [search_value, search_value]
        elif search_field == 'course':
            query = """
                SELECT COUNT(*) FROM student s
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE CONCAT(p.programCode, ' (', c.collegeName, ')') LIKE LOWER(%s)
            """
            params = [f"%{search_value}%"]
        else:
            query = f"""
                SELECT COUNT(*) FROM student s
                LEFT JOIN program p ON s.CourseCode = p.programCode
                LEFT JOIN college c ON p.programCollege = c.collegeCode
                WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)
            """
            params = [f"%{search_value}%"]

        cursor.execute(query, params)
        total_results = cursor.fetchone()[0]
        cursor.close()
        return total_results

    @staticmethod
    def check_and_update_status(conn, idNumber):
        print(f"Checking status for student ID: {idNumber}")

        try:
            cursor = conn.cursor()

            # Fetch the student's course code
            cursor.execute("SELECT CourseCode FROM student WHERE IDNumber = %s", (idNumber,))
            student = cursor.fetchone()

            if student:  # Check if a student record was found
                course_code = student[0]  # Fetch the CourseCode
                print(f"Found course code for student {idNumber}: {course_code}")

                # Check if the program exists
                cursor.execute("SELECT * FROM program WHERE programCode = %s", (course_code,))
                program_exists = cursor.fetchone()

                if not program_exists:  # If no program found, update status to 'Unenrolled'
                    print(f"Program code {course_code} does not exist. Updating status to 'Unenrolled'.")
                    cursor.execute("UPDATE student SET Status = 'Unenrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()
                    print(f"Student ID {idNumber} status updated to 'Unenrolled'.")
                else:  # If program exists, update status to 'Enrolled'
                    print(f"Program code {course_code} exists. Updating status to 'Enrolled'.")
                    cursor.execute("UPDATE student SET Status = 'Enrolled' WHERE IDNumber = %s", (idNumber,))
                    conn.commit()
                    print(f"Student ID {idNumber} status updated to 'Enrolled'.")
            else:
                print(f"Student ID {idNumber} not found.")

        except Exception as err:
            print(f"Error: {err}")
        finally:
            cursor.close()



class Programs:
    def __init__(self, programCode, programTitle, programCollege):
        self.programCode = programCode
        self.programTitle = programTitle
        self.programCollege = programCollege

    def save_program(self):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO program (programCode, programTitle, programCollege) VALUES (%s, %s, %s)
        ''', (self.programCode, self.programTitle, self.programCollege))
        conn.commit()
        cursor.close()

    @staticmethod
    def get_all_programs(conn):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()  # Use a regular cursor
        
        try:
            cursor.execute('SELECT * FROM program')
            rows = cursor.fetchall()  # Fetch all rows from the query
            
            # Get column names before closing the cursor
            columns = [column[0] for column in cursor.description]  # Extract column names
            
            # Convert rows into a list of dictionaries
            result = [dict(zip(columns, row)) for row in rows]
            
            return result  # Return the list of dictionaries

        except Exception as e:
            print(f"Error retrieving programs: {e}")
            return []

        finally:
            cursor.close()  # Ensure the cursor is closed after execution

    @staticmethod
    def search_programs(conn, search_field, search_value):
        """Search programs - moved from routes"""
        field_map = {
            'programCode': 'programCode',
            'programTitle': 'programTitle',
            'programCollege': 'programCollege'
        }
        
        query = f"SELECT * FROM program WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
        params = [f"%{search_value}%"]
        
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return results
        except Exception as e:
            print(f"Error searching programs: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def find_by_program(programCode):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM program WHERE programCode = %s', (programCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Programs(row[0], row[1], row[2])
        return None

    def update_program(self, new_programCode, new_programTitle, new_collegeCode):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute(''' 
            UPDATE program 
            SET programCode = %s, programTitle = %s, programCollege = %s 
            WHERE programCode = %s 
        ''', (new_programCode, new_programTitle, new_collegeCode, self.programCode))
        conn.commit()
        cursor.close()

    @classmethod
    def delete_program(cls, program_code):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("DELETE FROM program WHERE programCode = %s", (program_code,))
        conn.commit()
        cursor.close()

    @staticmethod
    def check_program_exists(programCode):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM program WHERE programCode = %s", (programCode,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0


class Colleges:
    def __init__(self, collegeCode, collegeName):
        self.collegeCode = collegeCode
        self.collegeName = collegeName

    def save_college(self):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute(''' 
            INSERT INTO college (collegeCode, collegeName) VALUES (%s, %s)
        ''', (self.collegeCode, self.collegeName))
        conn.commit()
        cursor.close()

    @staticmethod
    def get_all_colleges(conn):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()  # Use a regular cursor

        try:
            cursor.execute('SELECT * FROM college')
            rows = cursor.fetchall()  # Fetch all rows from the query
            
            # Manually convert rows into a list of dictionaries
            columns = [column[0] for column in cursor.description]  # Extract column names
            result = [dict(zip(columns, row)) for row in rows]
            
            return result  # Return the list of dictionaries

        except Exception as e:
            print(f"Error retrieving colleges: {e}")
            return []

        finally:
            cursor.close()  # Ensure the cursor is closed

    @staticmethod
    def search_colleges(conn, search_field, search_value):
        """Search colleges - moved from routes"""
        field_map = {
            'collegeCode': 'collegeCode',
            'collegeName': 'collegeName'
        }
        
        query = f"SELECT * FROM college WHERE LOWER({field_map[search_field]}) LIKE LOWER(%s)"
        params = [f"%{search_value}%"]
        
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return results
        except Exception as e:
            print(f"Error searching colleges: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def check_college_exists(collegeCode):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM college WHERE collegeCode = %s", (collegeCode,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0  # Returns True if the college exists, otherwise False

    @staticmethod
    def find_by_college(collegeCode):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM college WHERE collegeCode = %s', (collegeCode,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            return Colleges(row[0], row[1])
        return None

    @staticmethod
    def update_college(original_college_code, new_college_code, new_college_name):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute("""UPDATE college 
                        SET collegeCode = %s, collegeName = %s 
                        WHERE collegeCode = %s""",
                    (new_college_code, new_college_name, original_college_code))
        conn.commit()
        cursor.close()

    def delete_college(self):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()
        cursor.execute('DELETE FROM college WHERE collegeCode = %s', (self.collegeCode,))
        conn.commit()
        cursor.close()