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
    def find_by_id(idNumber):
        conn = mysql.connection  # Access the MySQL connection from Flask
        cursor = conn.cursor()  # Use a regular cursor (not dictionary=True)
        cursor.execute("SELECT * FROM student WHERE IDNumber = %s", (idNumber,))
        row = cursor.fetchone()  # Fetch the single row

        if row:
            # Manually create a dictionary using column names
            columns = [desc[0] for desc in cursor.description]  # Get column names
            result = dict(zip(columns, row))  # Convert row to a dictionary
            cursor.close()
            return result  # Return the dictionary

        cursor.close()
        return None  # Return None if no row is found


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
