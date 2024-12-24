DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS program;
DROP TABLE IF EXISTS college;


-- Create the 'college' table
CREATE TABLE IF NOT EXISTS college (
    collegeCode VARCHAR(255) PRIMARY KEY,
    collegeName VARCHAR(255) NOT NULL
);

-- Create the 'program' table with both ON DELETE CASCADE and ON UPDATE CASCADE
CREATE TABLE IF NOT EXISTS program (
    programCode VARCHAR(255) PRIMARY KEY,
    programTitle VARCHAR(255) NOT NULL,
    programCollege VARCHAR(255),
    FOREIGN KEY (programCollege) REFERENCES college(collegeCode)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- Create the 'student' table with foreign key to 'program' table
CREATE TABLE IF NOT EXISTS student (
    IDNumber VARCHAR(255) PRIMARY KEY,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    CourseCode VARCHAR(255),
    Status VARCHAR(255) NOT NULL,
    Year VARCHAR(255) NOT NULL,
    Gender VARCHAR(255) NOT NULL,
    imageURL VARCHAR(255),
    FOREIGN KEY (CourseCode) REFERENCES program(programCode)
    ON DELETE SET NULL  -- Set CourseCode to NULL when a program is deleted
    ON UPDATE CASCADE   -- Update CourseCode when programCode is updated
);

-- Insert data into 'college' table
INSERT INTO college (collegeCode, collegeName) VALUES
('CCS', 'College of Computer Studies'),
('CASS', 'College of Arts and Social Sciences'),
('COE', 'College of Engineering'),
('CHS', 'College of Health and Sciences'),
('CSM', 'College of Science and Mathematics'),
('CEBA', 'College of Economics, Business and Accountancy');

-- Insert data into 'program' table
INSERT INTO program (programCode, programTitle, programCollege) VALUES
('BSCS', 'Bachelor of Science in Computer Science', 'CCS'),
('BSIT', 'Bachelor of Science in Information Technology', 'CCS'),
('BSCE', 'Bachelor of Science in Civil Engineering', 'COE'),
('BSEE', 'Bachelor of Science in Electrical Engineering', 'COE'),
('BSA', 'Bachelor of Science in Accountancy', 'CEBA'),
('BSBA', 'Bachelor of Science in Business Administration', 'CEBA'),
('BSBio', 'Bachelor of Science in Biology', 'CSM'),
('BSMath', 'Bachelor of Science in Mathematics', 'CSM'),
('BSPsych', 'Bachelor of Science in Psychology', 'CASS'),
('BSEd', 'Bachelor of Science in Education', 'CASS');

-- Insert data into 'student' table
INSERT INTO student (IDNumber, firstName, lastName, CourseCode, Status, Year, Gender, imageURL) VALUES
('2022-001', 'Alice', 'Smith', 'BSCS', 'Active', '4th Year', 'Female', 'https://example.com/image1.jpg'),
('2022-002', 'Bob', 'Brown', 'BSIT', 'Active', '3rd Year', 'Male', 'https://example.com/image2.jpg'),
('2022-003', 'Charlie', 'Davis', 'BSCE', 'Active', '2nd Year', 'Male', 'https://example.com/image3.jpg'),
('2022-004', 'Diana', 'Evans', 'BSEE', 'Active', '1st Year', 'Female', 'https://example.com/image4.jpg'),
('2022-005', 'Eve', 'Johnson', 'BSA', 'Active', '4th Year', 'Female', 'https://example.com/image5.jpg'),
('2022-006', 'Frank', 'Miller', 'BSBA', 'Active', '3rd Year', 'Male', 'https://example.com/image6.jpg'),
('2022-007', 'Grace', 'Wilson', 'BSBio', 'Active', '4th Year', 'Female', 'https://example.com/image7.jpg'),
('2022-008', 'Hank', 'Taylor', 'BSMath', 'Active', '3rd Year', 'Male', 'https://example.com/image8.jpg'),
('2022-009', 'Ivy', 'Anderson', 'BSPsych', 'Active', '2nd Year', 'Female', 'https://example.com/image9.jpg'),
('2022-010', 'Jack', 'Thomas', 'BSEd', 'Active', '1st Year', 'Male', 'https://example.com/image10.jpg'),
('2022-011', 'Kate', 'Harris', 'BSCS', 'Active', '3rd Year', 'Female', 'https://example.com/image11.jpg'),
('2022-012', 'Leo', 'Clark', 'BSIT', 'Active', '2nd Year', 'Male', 'https://example.com/image12.jpg'),
('2022-013', 'Mia', 'Lewis', 'BSCE', 'Active', '1st Year', 'Female', 'https://example.com/image13.jpg'),
('2022-014', 'Noah', 'Walker', 'BSEE', 'Active', '4th Year', 'Male', 'https://example.com/image14.jpg'),
('2022-015', 'Olivia', 'Hall', 'BSA', 'Active', '3rd Year', 'Female', 'https://example.com/image15.jpg'),
('2022-016', 'Paul', 'Allen', 'BSBA', 'Active', '2nd Year', 'Male', 'https://example.com/image16.jpg'),
('2022-017', 'Quinn', 'Young', 'BSBio', 'Active', '1st Year', 'Female', 'https://example.com/image17.jpg'),
('2022-018', 'Rose', 'King', 'BSMath', 'Active', '4th Year', 'Female', 'https://example.com/image18.jpg'),
('2022-019', 'Sam', 'Scott', 'BSPsych', 'Active', '3rd Year', 'Male', 'https://example.com/image19.jpg'),
('2022-020', 'Tina', 'Adams', 'BSEd', 'Active', '2nd Year', 'Female', 'https://example.com/image20.jpg'),
('2022-021', 'Uma', 'Parker', 'BSCS', 'Active', '1st Year', 'Female', 'https://example.com/image21.jpg'),
('2022-022', 'Victor', 'Collins', 'BSIT', 'Active', '4th Year', 'Male', 'https://example.com/image22.jpg'),
('2022-023', 'Wendy', 'Mitchell', 'BSCE', 'Active', '3rd Year', 'Female', 'https://example.com/image23.jpg'),
('2022-024', 'Xavier', 'Perez', 'BSEE', 'Active', '2nd Year', 'Male', 'https://example.com/image24.jpg'),
('2022-025', 'Yvonne', 'Hughes', 'BSA', 'Active', '1st Year', 'Female', 'https://example.com/image25.jpg');