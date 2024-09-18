DROP DATABASE IF EXISTS sanad;
CREATE DATABASE sanad;
USE sanad;

CREATE TABLE IF NOT EXISTS Parent (
    Parent_ID INT AUTO_INCREMENT PRIMARY KEY,
    SSN INT,
    Parent_Name VARCHAR(32),
    Email VARCHAR(32),
    E_Password VARCHAR(32)
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Contact_Info (
    ContactInfo_ID INT AUTO_INCREMENT PRIMARY KEY,
    Info1 VARCHAR(32),
    Info2 VARCHAR(32),
    Info3 VARCHAR(32),
    Parent_ID INT,
    FOREIGN KEY (Parent_ID) REFERENCES Parent(Parent_ID) ON DELETE CASCADE
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Child (
    Child_ID INT AUTO_INCREMENT PRIMARY KEY,
    Child_Name VARCHAR(32),
    DateOfBirth DATE,
    Gender VARCHAR(32),
    Parent_ID INT,
    FOREIGN KEY (Parent_ID) REFERENCES Parent(Parent_ID) ON DELETE CASCADE
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Courses (
    Course_ID INT AUTO_INCREMENT PRIMARY KEY,
    Course_Name VARCHAR(32),
    Disability VARCHAR(32)
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Administrator (
    Administrator_ID INT AUTO_INCREMENT PRIMARY KEY,
    Admin_Name VARCHAR(32),
    Admin_Role VARCHAR(32),
    Email VARCHAR(32),
    E_Password VARCHAR(32)
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Specialist (
    Specialist_ID INT AUTO_INCREMENT PRIMARY KEY,
    Specialist_Name VARCHAR(32),
    SSN INT,
    Salary DOUBLE,
    Email VARCHAR(32),
    E_Password VARCHAR(32)
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Payments (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    PaymentDate DATE,
    Amount DOUBLE,
    Parent_ID INT,
    Administrator_ID INT,
    PaymentStatus ENUM('Paid', 'Not Yet'),
    FOREIGN KEY (Parent_ID) REFERENCES Parent(Parent_ID) ON DELETE CASCADE,
    FOREIGN KEY (Administrator_ID) REFERENCES Administrator(Administrator_ID) ON DELETE CASCADE
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Test (
    Treatment_NUM INT AUTO_INCREMENT PRIMARY KEY,
    TestName VARCHAR(32),
    Course_ID INT,
    FOREIGN KEY (Course_ID) REFERENCES Courses(Course_ID) ON DELETE CASCADE
) AUTO_INCREMENT=1;

CREATE TABLE IF NOT EXISTS Supervision (
    Child_ID INT,
    Specialist_ID INT,
    Course_ID INT,
    Reservation_Days VARCHAR(255),
    Reservation_Start_Time TIME,
    Reservation_End_Time TIME,
    PRIMARY KEY (Child_ID, Course_ID, Specialist_ID),
    FOREIGN KEY (Child_ID) REFERENCES Child(Child_ID) ON DELETE CASCADE,
    FOREIGN KEY (Course_ID) REFERENCES Courses(Course_ID) ON DELETE CASCADE,
    FOREIGN KEY (Specialist_ID) REFERENCES Specialist(Specialist_ID) ON DELETE CASCADE
);

INSERT INTO Administrator (Admin_Name, Admin_Role, Email, E_Password) VALUES
('Rola Ahmad', 'Finance Manager', 'rola@gmail.com', 'rola1'),
('Ahmad Mostafa', 'General Manager', 'ahmad@gmail.com', '234'),
('Hussein Dar Ali', 'Public Relations Manager', 'husain@gmail.com', 'h88');

INSERT INTO Specialist (Specialist_Name, SSN, Salary, Email, E_Password) VALUES
('Israa', 123456789, 2500,  'israa@gmail.com', 'israa'), 
('Tuleen', 123456789, 2500,  'tuleen@gmail.com', 'tuleen'), 
('Sama', 123456789, 2500, 'sama@gmail.com', 's44');  

INSERT INTO Parent (SSN, Parent_Name, Email, E_Password) VALUES
(123456789, 'Sami', 'Sami@gmail.com', 's123'),
(234567890, 'Farah', 'Farah@gmail.com', 'farah88'),
(345678901, 'Fadi', 'Fadi@gmail.com', 'fadi9'),
(456789012, 'Layla', 'layla@gmail.com', 'layla123'),
(567890123, 'Nader', 'nader@gmail.com', 'nader99'),
(678901234, 'Rami', 'rami@gmail.com', 'rami111'),
(789012345, 'Zain', 'zain@gmail.com', 'zain333'),
(890123456, 'Lara', 'lara@gmail.com', 'lara777');

INSERT INTO Contact_Info (Info1, Info2, Info3, Parent_ID) VALUES
('07982234', '0982311', '0987644', 1),
('079987234', '0980001', '01117644', 2),
('07922234', '98912311', '0981117644', 3),
('079999234', '0987771', '0989994', 4),
('079888234', '0988881', '0988884', 5),
('079777234', '0981111', '0981114', 6),
('079666234', '0986661', '0986664', 7),
('079555234', '0985551', '0985554', 8);

INSERT INTO Child (Child_Name, DateOfBirth, Gender, Parent_ID) VALUES
('Milad', '2012-02-06', 'Male', 1),
('Farah', '2009-04-07', 'Female', 2),
('Adam', '2014-09-11', 'Male', 3),
('Lina', '2011-05-21', 'Female', 4),
('Rami', '2013-12-13', 'Male', 5),
('Tamer', '2010-01-22', 'Male', 1),
('Dana', '2008-11-30', 'Female', 2),
('Kareem', '2013-03-17', 'Male', 3),
('Hala', '2012-06-25', 'Female', 4),
('Sami', '2015-10-19', 'Male', 5),
('Nour', '2011-08-18', 'Female', 6),
('Zaid', '2012-11-20', 'Male', 7),
('Sara', '2013-05-14', 'Female', 8);

INSERT INTO Courses (Course_Name, Disability) VALUES
('Autism Therapy', 'Autism'),
('Speech Learning', 'Speech Difficulties'),
('Rehabilitation', 'Down Syndrome'),
('Occupational Therapy', 'Physical Disabilities'),
('Behavioral Therapy', 'Behavioral Issues'),
('Music Therapy', 'Emotional Issues'),
('Art Therapy', 'Creative Expression'),
('Physical Education', 'Physical Development');

INSERT INTO Payments (PaymentDate, Amount, Parent_ID, Administrator_ID, PaymentStatus) VALUES
('2024-01-10', 500.00, 1, 1, 'Paid'),
('2024-02-15', 100.00, 2, 1, 'Paid'),
('2024-03-20', 100.00, 3, 1, 'Not Yet'),
('2024-04-25', 50.00, 4, 1, 'Paid'),
('2024-05-30', 350.00, 5, 1, 'Paid'),
('2024-06-05', 100.00, 6, 1, 'Not Yet'),
('2024-07-10', 550.00, 7, 1, 'Paid'),
('2024-08-15', 400.00, 8, 1, 'Paid'),
('2024-04-25', 350.00, 4, 1, 'Paid'),
('2024-05-30', 450.00, 5, 1, 'Paid'),
('2024-06-05', 300.00, 6, 1, 'Not Yet'),
('2024-07-10', 250.00, 7, 1, 'Paid'),
('2024-08-15', 300.00, 8, 1, 'Paid'),
('2024-06-05', 100.00, 6, 1, 'Not Yet'),
('2024-07-10', 550.00, 7, 1, 'Paid'),
('2024-08-15', 400.00, 8, 1, 'Paid'),
('2024-04-25', 350.00, 4, 1, 'Paid'),
('2024-05-30', 450.00, 1, 1, 'Paid'),
('2024-06-05', 300.00, 1, 1, 'Not Yet'),
('2024-07-10', 250.00, 1, 1, 'Paid'),
('2024-08-15', 300.00, 8, 1, 'Paid'),
('2024-05-30', 350.00, 5, 1, 'Paid'),
('2024-06-05', 100.00, 6, 1, 'Not Yet'),
('2024-07-10', 550.00, 7, 1, 'Paid'),
('2024-08-15', 400.00, 8, 1, 'Paid'),
('2024-04-25', 350.00, 4, 1, 'Paid'),
('2024-05-30', 450.00, 5, 1, 'Paid'),
('2024-06-05', 300.00, 6, 1, 'Not Yet'),
('2024-07-10', 250.00, 7, 1, 'Paid'),
('2024-08-15', 300.00, 8, 1, 'Paid'),
('2024-06-05', 100.00, 6, 1, 'Not Yet');

INSERT INTO Test (TestName, Course_ID) VALUES
('Initial Assessment', 1),
('Progress Evaluation', 2),
('Final Exam', 3),
('Midterm Exam', 4),
('Diagnostic Test', 5),
('Skill Test', 6),
('Performance Test', 7),
('Physical Fitness Test', 8);

INSERT INTO Supervision (Child_ID, Specialist_ID, Course_ID, Reservation_Days, Reservation_Start_Time, Reservation_End_Time) VALUES
(1, 1, 1, 'Monday,Wednesday', '11:00:00', '12:00:00'),
(1, 2, 2, 'Tuesday,Thursday', '10:00:00', '11:00:00'),
(2, 2, 2, 'Monday,Wednesday', '11:00:00', '12:00:00'),
(2, 3, 3, 'Monday,Wednesday', '13:00:00', '14:00:00'),
(3, 3, 3, 'Tuesday,Thursday', '11:00:00', '12:00:00'),
(3, 1, 4, 'Monday,Wednesday', '10:00:00', '11:00:00'),
(4, 1, 4, 'Tuesday,Thursday', '12:00:00', '13:00:00'),
(5, 3, 1, 'Monday,Wednesday', '10:00:00', '11:00:00'),
(6, 1, 1, 'Tuesday,Thursday', '9:00:00', '10:00:00'),
(7, 2, 2, 'Monday,Wednesday', '9:00:00', '10:00:00'),
(8, 3, 3, 'Tuesday,Thursday', '12:00:00', '13:00:00'),
(9, 1, 4, 'Monday,Wednesday', '13:00:00', '14:00:00'),
(10, 2, 5, 'Monday,Wednesday', '12:00:00', '13:00:00'),
(10, 3, 1, 'Tuesday,Thursday', '9:00:00', '10:00:00'),
(11, 1, 6, 'Monday,Wednesday', '9:00:00', '10:00:00'),
(12, 2, 7, 'Tuesday,Thursday', '12:00:00', '13:00:00'),
(13, 3, 8, 'Monday,Wednesday', '11:00:00', '12:00:00');

SELECT * FROM Specialist;
SELECT * FROM Administrator;
SELECT * FROM Child;
SELECT * FROM Courses;
SELECT * FROM Parent;
SELECT * FROM Contact_Info;
SELECT * FROM Payments;
SELECT * FROM Test;
SELECT * FROM Supervision;
SELECT PaymentDate, Amount, PaymentStatus FROM Payments WHERE Parent_ID = 1;
