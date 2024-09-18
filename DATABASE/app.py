from flask import Flask, render_template, request, redirect, url_for, flash, session, json, jsonify
import pymysql
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret'


def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='sanad',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('login'))

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO Parent (Parent_Name, Email, E_Password) VALUES (%s, %s, %s)",
                           (username, email, password))
            conn.commit()
        conn.close()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('login'))


@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            if user_type == 'parent':
                cursor.execute("SELECT * FROM Parent WHERE Email=%s AND E_Password=%s", (username, password))
                user = cursor.fetchone()
                if user:
                    session['user'] = user
                    session['user_type'] = user_type
                    session['parent_id'] = user['Parent_ID']
            elif user_type == 'administrator':
                cursor.execute("SELECT * FROM Administrator WHERE Email=%s AND E_Password=%s", (username, password))
                user = cursor.fetchone()
                if user:
                    session['user'] = user
                    session['user_type'] = user_type
                    session['administrator_id'] = user['Administrator_ID']
            elif user_type == 'specialist':
                cursor.execute("SELECT * FROM Specialist WHERE Email=%s AND E_Password=%s", (username, password))
                user = cursor.fetchone()
                if user:
                    session['user'] = user
                    session['user_type'] = user_type

            if user:
                flash('Login successful!', 'success')
                if user_type == 'parent':
                    return redirect(url_for('parent_dashboard'))
                elif user_type == 'administrator':
                    return redirect(url_for('admin_dashboard'))
                elif user_type == 'specialist':
                    return redirect(url_for('specialist_dashboard'))
            else:
                flash('Invalid credentials', 'danger')
                return redirect(url_for('login'))
        conn.close()
    except Exception as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


################################################################
# new
@app.route('/specialists')
def specialists():
    specialists, total_salary, max_salary, avg_salary = get_specialist_data()

    # Debugging Statements
    print(f"Specialists: {specialists}")
    print(f"Total Salary: {total_salary}, Max Salary: {max_salary}, Avg Salary: {avg_salary}")

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Course_ID, Course_Name FROM Courses")
        courses = cursor.fetchall()
    conn.close()

    return render_template('specialists.html', specialists=specialists, total_salary=total_salary,
                           max_salary=max_salary, avg_salary=avg_salary, courses=courses)


def get_specialist_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Specialist")
            result = cursor.fetchall()

            print(f"Fetched Specialists: {result}")

            cursor.execute("SELECT SUM(Salary), MAX(Salary), AVG(Salary) FROM Specialist")
            total_salary, max_salary, avg_salary = cursor.fetchone()

            print(f"Total Salary: {total_salary}, Max Salary: {max_salary}, Avg Salary: {avg_salary}")

        conn.close()
        return result, total_salary, max_salary, avg_salary
    except Exception as e:
        print(f"Error: {e}")
        return [], 0, 0, 0


def get_course_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Courses")
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_specialist', methods=['GET', 'POST'])
def add_specialist():
    if request.method == 'POST':
        name = request.form['name']
        ssn = request.form['ssn']
        salary = request.form['salary']
        email = request.form['email']
        password = request.form['password']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Specialist (Specialist_Name, SSN, Salary, Email, E_Password) VALUES (%s, %s, %s, %s, %s)",
                    (name, ssn, salary, email, password))
                conn.commit()
            conn.close()
            flash('Specialist added successfully!', 'success')
            return redirect(url_for('specialists'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('add_specialist.html')


@app.route('/update_specialist/<int:specialist_id>', methods=['POST'])
def update_specialist(specialist_id):
    name = request.form['name']
    salary = request.form['salary']
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE Specialist SET Specialist_Name=%s, Salary=%s WHERE Specialist_ID=%s",
                (name, salary, specialist_id))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/delete_specialist/<int:specialist_id>', methods=['POST'])
def delete_specialist(specialist_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Supervision WHERE Specialist_ID = %s", (specialist_id,))
            cursor.execute("DELETE FROM Specialist WHERE Specialist_ID = %s", (specialist_id,))
            conn.commit()
        conn.close()
        return jsonify(success=True, message='Specialist deleted successfully!')
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/search_specialist', methods=['GET'])
def search_specialist():
    query = request.args.get('query')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Specialist WHERE Specialist_Name LIKE %s", ('%' + query + '%',))
            specialists = cursor.fetchall()
        conn.close()
        return jsonify(success=True, specialists=specialists)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/sort_specialists', methods=['GET'])
def sort_specialists():
    column = request.args.get('column')
    direction = request.args.get('direction')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM Specialist ORDER BY {column} {direction}"
            cursor.execute(query)
            specialists = cursor.fetchall()
        conn.close()
        return jsonify(success=True, specialists=specialists)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/filter_specialists', methods=['GET'])
def filter_specialists():
    course_id = request.args.get('course_id')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT Specialist.* 
                FROM Specialist
                JOIN Supervision ON Specialist.Specialist_ID = Supervision.Specialist_ID
                WHERE Supervision.Course_ID = %s
            """, (course_id,))
            specialists = cursor.fetchall()
        conn.close()
        return jsonify(success=True, specialists=specialists)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Child
@app.route('/children')
def children():
    children_data = get_child_data()
    return render_template('children.html', children=children_data)


def get_child_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Child")
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_child', methods=['GET', 'POST'])
def add_child():
    if request.method == 'POST':
        name = request.form['name']
        birthDate = request.form['birthDate']
        gender = request.form['gender']
        parent_id = request.form['parent_id']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Child (Child_Name, DateOfBirth, Gender, Parent_ID) VALUES (%s, %s, %s, %s)",
                               (name, birthDate, gender, parent_id))
                conn.commit()
            conn.close()
            flash('Child added successfully!', 'success')
            return redirect(url_for('children'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('add_child.html')


@app.route('/update_child/<int:child_id>', methods=['POST'])
def update_child(child_id):
    name = request.form.get('name')
    birthDate = request.form.get('birthDate')
    gender = request.form.get('gender')
    parent_id = request.form.get('parent_id')

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Child 
                SET Child_Name = %s, DateOfBirth = %s, Gender = %s, Parent_ID = %s 
                WHERE Child_ID = %s
                """, (name, birthDate, gender, parent_id, child_id))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/search_child', methods=['GET'])
def search_child():
    query = request.args.get('query', '')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Child WHERE Child_Name LIKE %s", ('%' + query + '%',))
            children = cursor.fetchall()
        conn.close()
        return jsonify(success=True, children=children)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/delete_child/<int:child_id>', methods=['POST'])
def delete_child(child_id):
    logging.debug(f"Deleting child: {child_id}")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            # First, get the parent_id of the child to be deleted
            cursor.execute("SELECT Parent_ID FROM Child WHERE Child_ID = %s", (child_id,))
            result = cursor.fetchone()
            if result:
                parent_id = result['Parent_ID']
                
                cursor.execute("DELETE FROM Supervision WHERE Child_ID = %s", (child_id,))
                cursor.execute("DELETE FROM Child WHERE Child_ID = %s", (child_id,))
                cursor.execute("SELECT COUNT(*) AS child_count FROM Child WHERE Parent_ID = %s", (parent_id,))
                child_count = cursor.fetchone()['child_count']
                
                if child_count == 0:
                    cursor.execute("DELETE FROM Parent WHERE Parent_ID = %s", (parent_id,))
                
                conn.commit()
            else:
                logging.error(f"No child found with ID: {child_id}")
                return jsonify(success=False, message='Child not found!')

        conn.close()
        logging.debug("Deletion successful")
        return jsonify(success=True, message='Child deleted successfully!')
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify(success=False, error=str(e))



@app.route('/sort_children', methods=['GET'])
def sort_children():
    column = request.args.get('column', 'Child_Name')
    direction = request.args.get('direction', 'ASC')

    valid_columns = ['Child_Name', 'DateOfBirth', 'Gender', 'Parent_ID']
    if column not in valid_columns:
        column = 'Child_Name'
    if direction.upper() not in ['ASC', 'DESC']:
        direction = 'ASC'

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM Child ORDER BY {column} {direction}"
            cursor.execute(query)
            children = cursor.fetchall()
        conn.close()

        formatted_children = []
        for child in children:
            formatted_child = dict(child)
            formatted_child['DateOfBirth'] = child['DateOfBirth'].strftime('%Y-%m-%d')
            formatted_children.append(formatted_child)

        return jsonify(success=True, children=formatted_children)
    except Exception as e:
        return jsonify(success=False, error=str(e))


# Courses
@app.route('/courses')
def courses():
    courses = get_Course_data()
    return render_template('courses.html', courses=courses)


def get_Course_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Courses")
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        disability = request.form['disability']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Courses (Course_Name, Disability) VALUES (%s, %s)", (name, disability))
                conn.commit()
            conn.close()
            flash('Course added successfully!', 'success')
            return redirect(url_for('courses'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('add_course.html')


@app.route('/delete_course/<int:course_id>', methods=['POST'])
def delete_course(course_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Supervision WHERE Course_ID = %s", (course_id,))
            cursor.execute("DELETE FROM Test WHERE Course_ID = %s", (course_id,))
            cursor.execute("DELETE FROM Courses WHERE Course_ID = %s", (course_id,))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        print(f"Error deleting course: {e}")
        return jsonify(success=False, error=str(e))


@app.route('/update_course/<int:course_id>', methods=['POST'])
def update_course(course_id):
    name = request.form['name']
    disability = request.form['disability']
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE Courses SET Course_Name = %s, Disability = %s WHERE Course_ID = %s", (name, disability, course_id))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        print(f"Error updating course: {e}")
        return jsonify(success=False, error=str(e))


@app.route('/search_course', methods=['GET'])
def search_course():
    query = request.args.get('query')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Courses WHERE Course_Name LIKE %s", ('%' + query + '%',))
            courses = cursor.fetchall()
        conn.close()
        return jsonify(success=True, courses=courses)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/sort_courses', methods=['GET'])
def sort_courses():
    column = request.args.get('column', 'Course_Name')
    direction = request.args.get('direction', 'ASC')

    valid_columns = ['Course_Name', 'Disability']
    if column not in valid_columns:
        column = 'Course_Name'
    if direction.upper() not in ['ASC', 'DESC']:
        direction = 'ASC'

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT * FROM Courses ORDER BY {column} {direction}"
            cursor.execute(query)
            courses = cursor.fetchall()
        conn.close()

        return jsonify(success=True, courses=courses)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/parents')
def parents():
    parents = get_Parent_data()
    return render_template('parents.html', parents=parents)


def get_Parent_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Parent")
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []


@app.route('/add_parent', methods=['GET', 'POST'])
def add_parent():
    if request.method == 'POST':
        ssn = request.form['ssn']
        name = request.form['name']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Parent (SSN, Parent_Name) VALUES (%s, %s)", (ssn, name))
                conn.commit()
            conn.close()
            flash('Parent added successfully!', 'success')
            return redirect(url_for('parents'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('add_parent.html')


@app.route('/update_parent/<int:parent_id>', methods=['POST'])
def update_parent(parent_id):
    print(request.form)  
    ssn = request.form.get('ssn')
    name = request.form.get('name')
    print(f"Received Data - SSN: {ssn}, Name: {name}, Parent ID: {parent_id}")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE Parent SET SSN = %s, Parent_Name = %s WHERE Parent_ID = %s",
                           (ssn, name, parent_id))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))


@app.route('/delete_parent/<int:parent_id>', methods=['POST'])
def delete_parent(parent_id):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Child WHERE Parent_ID = %s", (parent_id,))
            cursor.execute("DELETE FROM Contact_Info WHERE parent_id = %s", (parent_id,))
            cursor.execute("DELETE FROM Parent WHERE Parent_ID = %s", (parent_id,))
            conn.commit()
        conn.close()
        print(f"Successfully deleted parent with ID: {parent_id}")
        return jsonify(success=True)
    except Exception as e:
        print(f"Error deleting parent: {e}")
        return jsonify(success=False, error=str(e))


@app.route('/search_parent', methods=['GET'])
def search_parent():
    query = request.args.get('query', '')
    print(f"Search Query: {query}")  
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Parent WHERE Parent_Name LIKE %s", ('%' + query + '%',))
            parents = cursor.fetchall()
        conn.close()
        print(f"Search Results: {parents}")  
        return jsonify(success=True, parents=parents)
    except Exception as e:
        print(f"Error: {e}")  
        return jsonify(success=False, error=str(e))


########################################################################################################################
@app.route('/parent_dashboard')
def parent_dashboard():
    if 'user' in session and session['user_type'] == 'parent':
        user = session['user']
        parent_id = user['Parent_ID']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Parent WHERE Parent_ID=%s", (parent_id,))
                parent = cursor.fetchone()
                cursor.execute("SELECT Info1, Info2, Info3 FROM Contact_Info WHERE parent_id=%s", (parent_id,))
                contact_info = cursor.fetchone()
                cursor.execute("SELECT * FROM Child WHERE Parent_ID=%s", (parent_id,))
                children = cursor.fetchall()
                cursor.execute("SELECT * FROM Payments WHERE parent_id=%s", (parent_id,))
                payments = cursor.fetchall()
            conn.close()
            contact_list = [contact_info['Info1'], contact_info['Info2'], contact_info['Info3']]
            return render_template('parent_dashboard.html', parent=parent, contact_list=contact_list, children=children,
                                   payments=payments)
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/my_children')
def my_children():
    if 'user' in session and session['user_type'] == 'parent':
        parent_id = session['parent_id']
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT c.Child_ID, c.Child_Name, co.Course_Name, s.Reservation_Days, s.Reservation_Start_Time, sp.Specialist_Name
                    FROM Child c
                    LEFT JOIN Supervision s ON c.Child_ID = s.Child_ID
                    LEFT JOIN Courses co ON s.Course_ID = co.Course_ID
                    LEFT JOIN Specialist sp ON s.Specialist_ID = sp.Specialist_ID
                    WHERE c.Parent_ID = %s
                """
                cursor.execute(sql, (parent_id,))
                children = cursor.fetchall()
        finally:
            connection.close()
        return render_template('my_children.html', children=children)
    else:
        return redirect(url_for('login'))


@app.route('/parent_payments')
def parent_payments():
    if 'user' in session and session['user_type'] == 'parent':
        parent_id = session['parent_id']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # Fetch all payments for the parent
                cursor.execute("SELECT PaymentDate, Amount, PaymentStatus FROM Payments WHERE Parent_ID=%s",
                               (parent_id,))
                payments = cursor.fetchall()

                total_paid = sum(
                    payment['Amount'] for payment in payments if payment['PaymentStatus'].lower() == 'paid')
                total_unpaid = sum(
                    payment['Amount'] for payment in payments if payment['PaymentStatus'].lower() != 'paid')

            conn.close()
            return render_template('parent_payments.html', payments=payments, total_paid=total_paid,
                                   total_unpaid=total_unpaid)
        except Exception as e:
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('parent_dashboard'))
    else:
        return redirect(url_for('login'))


@app.route('/child_profile/<int:child_id>')
def child_profile(child_id):
    if 'user' in session and session['user_type'] == 'parent':
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT c.Child_Name,c.Child_ID, c.DateOfBirth, c.Gender, p.Email as Parent_Email, p.Parent_Name
                    FROM Child c
                    LEFT JOIN Parent p ON c.Parent_ID = p.Parent_ID
                    WHERE c.Child_ID = %s
                """, (child_id,))
                child = cursor.fetchone()

                cursor.execute("""
                    SELECT co.Course_Name, s.Reservation_Days, s.Reservation_Start_Time, s.Reservation_End_Time, sp.Specialist_Name
                    FROM Supervision s
                    LEFT JOIN Courses co ON s.Course_ID = co.Course_ID
                    LEFT JOIN Specialist sp ON s.Specialist_ID = sp.Specialist_ID
                    WHERE s.Child_ID = %s
                """, (child_id,))
                courses = cursor.fetchall()

            if child:
                dob = child['DateOfBirth']
                today = datetime.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                child['Age'] = age

        finally:
            connection.close()

        return render_template('child_profile.html', child=child, courses=courses)
    else:
        return redirect(url_for('login'))


################################################################################################
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' not in session or session.get('user_type') != 'administrator':
        flash('Please log in as an administrator to access this page.', 'danger')
        return redirect(url_for('login'))

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Administrator WHERE Administrator_ID=%s", (session['administrator_id'],))
            admin_data = cursor.fetchone()

        return render_template('administrator_dashboard.html', admin=admin_data)
    except Exception as e:
        flash(f"Error: {e}", 'danger')
        return redirect(url_for('login'))
    finally:
        conn.close()


@app.route('/organization_statistics')
def organization_statistics():
    if 'user' in session:
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                # Total Profit
                cursor.execute("SELECT SUM(Amount) AS Total_Profit FROM Payments;")
                total_profit = cursor.fetchone()['Total_Profit']

                # Total Children
                cursor.execute("SELECT COUNT(*) AS Total_Children FROM Child;")
                total_children = cursor.fetchone()['Total_Children']

                # Total Specialists
                cursor.execute("SELECT COUNT(*) AS Total_Specialists FROM Specialist;")
                total_specialists = cursor.fetchone()['Total_Specialists']

                # Total Courses
                cursor.execute("SELECT COUNT(*) AS Total_Courses FROM Courses;")
                total_courses = cursor.fetchone()['Total_Courses']

                # Parents who have not paid yet
                cursor.execute("""
                    SELECT Parent.Parent_ID, Parent.Parent_Name, Contact_Info.Info1 AS Contact
                    FROM Parent
                    LEFT JOIN Payments ON Parent.Parent_ID = Payments.Parent_ID AND Payments.PaymentStatus = 'Paid'
                    LEFT JOIN Contact_Info ON Parent.Parent_ID = Contact_Info.Parent_ID
                    WHERE Payments.Parent_ID IS NULL;
                """)
                parents_not_paid = cursor.fetchall()

                # Parents who have more than one child
                cursor.execute("""
                    SELECT Parent.*, ChildCount.num_children
                    FROM Parent
                    INNER JOIN (
                        SELECT Parent_ID, COUNT(*) AS num_children
                        FROM Child
                        GROUP BY Parent_ID
                        HAVING COUNT(*) > 1
                    ) AS ChildCount ON Parent.Parent_ID = ChildCount.Parent_ID
                """)
                parents_with_multiple_children = cursor.fetchall()

                # Children who have more than one disability or attend more than one course
                cursor.execute("""
                    SELECT Child.Child_ID, Child.Child_Name, Child.DateOfBirth, Child.Gender, Parent.Parent_Name
                    FROM Child
                    INNER JOIN Parent ON Child.Parent_ID = Parent.Parent_ID
                    INNER JOIN Supervision ON Child.Child_ID = Supervision.Child_ID
                    INNER JOIN Courses ON Supervision.Course_ID = Courses.Course_ID
                    GROUP BY Child.Child_ID
                    HAVING COUNT(DISTINCT Supervision.Course_ID) > 1 OR COUNT(DISTINCT Courses.Disability) > 1
                """)
                children_multiple_disabilities_courses = cursor.fetchall()

                # Count courses per specialist
                cursor.execute("""
                    SELECT Specialist.Specialist_ID, Specialist.Specialist_Name, COUNT(Supervision.Course_ID) AS num_courses
                    FROM Specialist
                    LEFT JOIN Supervision ON Specialist.Specialist_ID = Supervision.Specialist_ID
                    GROUP BY Specialist.Specialist_ID
                """)
                course_count_per_specialist = cursor.fetchall()

                # Total salary for each specialist
                cursor.execute("""
                    SELECT Specialist.Specialist_ID, Specialist.Specialist_Name, Specialist.Salary
                    FROM Specialist
                    ORDER BY Specialist.Salary DESC;
                """)
                total_salary_per_specialist = cursor.fetchall()
                # Total salary for each specialist
                cursor.execute("""
                    SELECT Specialist.Specialist_ID, Specialist.Specialist_Name, Specialist.Salary
                    FROM Specialist
                    ORDER BY Specialist.Salary DESC;
                """)
                total_salary_per_specialist = cursor.fetchall()

        finally:
            connection.close()

        return render_template(
            'organization_statistics.html',
            total_profit=total_profit,
            total_children=total_children,
            total_specialists=total_specialists,
            total_courses=total_courses,
            parents_not_paid=parents_not_paid,
            parents_with_multiple_children=parents_with_multiple_children,
            children_multiple_disabilities_courses=children_multiple_disabilities_courses,
            course_count_per_specialist=course_count_per_specialist,
            total_salary_per_specialist=total_salary_per_specialist
        )
    else:
        return redirect(url_for('login'))


@app.route('/add_parent_and_child', methods=['GET', 'POST'])
def add_parent_and_child():
    if request.method == 'POST':
        ssn = request.form['ssn']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        child_name = request.form['child_name']
        birth_date = request.form['birth_date']
        gender = request.form['gender']
        selected_courses = request.form.getlist('course_ids')

        print(f"Data Received: SSN={ssn}, Name={name}, Email={email}, Password={password}")
        print(f"Child Data: Name={child_name}, Birth Date={birth_date}, Gender={gender}")
        print(f"Selected Courses: {selected_courses}")

        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # Insert into Parent table
                cursor.execute(
                    "INSERT INTO Parent (SSN, Parent_Name, Email, E_Password) VALUES (%s, %s, %s, %s)",
                    (ssn, name, email, password)
                )
                parent_id = cursor.lastrowid  # Get the inserted Parent ID
                print(f"Parent ID: {parent_id}")

                # Insert into Child table
                cursor.execute(
                    "INSERT INTO Child (Child_Name, DateOfBirth, Gender, Parent_ID) VALUES (%s, %s, %s, %s)",
                    (child_name, birth_date, gender, parent_id)
                )
                child_id = cursor.lastrowid  # Get the inserted Child ID
                print(f"Child ID: {child_id}")

                # Insert into Supervision table
                for course_id in selected_courses:
                    specialist_id = request.form.get(f'specialists[{course_id}]')
                    selected_date = request.form.get(f'dates[{course_id}]')
                    print(f"Processing Course: {course_id}, Specialist: {specialist_id}, Date: {selected_date}")

                    if specialist_id and selected_date:
                        parts = selected_date.split('-')
                        if len(parts) == 3:
                            reservation_days, start_time, end_time = parts
                            print ("rexss",reservation_days,"start_time",start_time,"endtime",end_time)
                            print(f"Parsed Dates: Days={reservation_days}, Start={start_time}, End={end_time}")

                            # Check if the specialist is already booked at this time
                            cursor.execute(
                                "SELECT * FROM Supervision WHERE Specialist_ID=%s AND Reservation_Days=%s AND Reservation_Start_Time=%s AND Reservation_End_Time=%s",
                                (specialist_id, reservation_days, start_time, end_time)
                            )
                            if cursor.fetchone():
                                flash(
                                    f'Specialist {specialist_id} is already reserved for course {course_id} at the selected time.',
                                    'danger')
                            else:
                                cursor.execute(
                                    "INSERT INTO Supervision (Child_ID, Specialist_ID, Course_ID, Reservation_Days, Reservation_Start_Time, Reservation_End_Time) VALUES (%s, %s, %s, %s, %s, %s)",
                                    (child_id, specialist_id, course_id, reservation_days, start_time, end_time)
                                )
                                print(
                                    f"Inserted into Supervision: Child ID: {child_id}, Specialist ID: {specialist_id}, Course ID: {course_id}, Days: {reservation_days}, Start: {start_time}, End: {end_time}")
                        else:
                            flash(
                                f'Invalid date format for course {course_id}. Expected format is "Days,StartTime,EndTime".',
                                'danger')
                            print(f"Invalid date format: {selected_date}")

                conn.commit()
                print("Transaction committed")

            conn.close()
            flash('Parent and Child added successfully!', 'success')
            return redirect(url_for('add_parent_and_child'))
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Error: {e}", 'danger')

    # Fetch courses and specialists to display in the form
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Course_ID, Course_Name FROM Courses")
        courses = cursor.fetchall()
        cursor.execute("SELECT Specialist_ID as id, Specialist_Name as name FROM Specialist")
        specialists = cursor.fetchall()
    conn.close()

    return render_template('add_parent_and_child.html', courses=courses, specialists=specialists)


@app.route('/available_dates', methods=['GET'])
def available_dates():
    specialist_id = request.args.get('specialist_id')
    course_id = request.args.get('course_id')

    predefined_slots = [
        ('Monday,Wednesday', '08:00:00', '09:00:00'),
        ('Monday,Wednesday', '09:00:00', '10:00:00'),
        ('Monday,Wednesday', '10:00:00', '11:00:00'),
        ('Monday,Wednesday', '11:00:00', '12:00:00'),
        ('Monday,Wednesday', '12:00:00', '13:00:00'),
        ('Monday,Wednesday', '13:00:00', '14:00:00'),
        ('Monday,Wednesday', '14:00:00', '15:00:00'),
        ('Tuesday,Thursday', '08:00:00', '09:00:00'),
        ('Tuesday,Thursday', '09:00:00', '10:00:00'),
        ('Tuesday,Thursday', '10:00:00', '11:00:00'),
        ('Tuesday,Thursday', '11:00:00', '12:00:00'),
        ('Tuesday,Thursday', '12:00:00', '13:00:00'),
        ('Tuesday,Thursday', '13:00:00', '14:00:00'),
        ('Tuesday,Thursday', '14:00:00', '15:00:00')
    ]

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Reservation_Days, Reservation_Start_Time, Reservation_End_Time 
                FROM Supervision 
                WHERE Specialist_ID = %s
            """, (specialist_id,))
            reserved_slots = cursor.fetchall()

        conn.close()

        reserved_set = set(
            (slot['Reservation_Days'], str(slot['Reservation_Start_Time']), str(slot['Reservation_End_Time'])) for slot
            in reserved_slots)

        available_slots = [slot for slot in predefined_slots if slot not in reserved_set]

        return jsonify(success=True, slots=[(f"{slot[0]},{slot[1]},{slot[2]}") for slot in available_slots])
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/fetch_available_slots', methods=['GET'])
def fetch_available_slots():
    specialist_id = request.args.get('specialist_id')
    course_id = request.args.get('course_id')

    predefined_slots = [
        ('Monday,Wednesday', '08:00:00', '09:00:00'),
        ('Monday,Wednesday', '09:00:00', '10:00:00'),
        ('Monday,Wednesday', '10:00:00', '11:00:00'),
        ('Monday,Wednesday', '11:00:00', '12:00:00'),
        ('Monday,Wednesday', '12:00:00', '13:00:00'),
        ('Monday,Wednesday', '13:00:00', '14:00:00'),
        ('Monday,Wednesday', '14:00:00', '15:00:00'),
        ('Tuesday,Thursday', '08:00:00', '09:00:00'),
        ('Tuesday,Thursday', '09:00:00', '10:00:00'),
        ('Tuesday,Thursday', '10:00:00', '11:00:00'),
        ('Tuesday,Thursday', '11:00:00', '12:00:00'),
        ('Tuesday,Thursday', '12:00:00', '13:00:00'),
        ('Tuesday,Thursday', '13:00:00', '14:00:00'),
        ('Tuesday,Thursday', '14:00:00', '15:00:00')
    ]

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Reservation_Days, Reservation_Start_Time, Reservation_End_Time 
                FROM Supervision 
                WHERE Specialist_ID = %s
            """, (specialist_id,))
            reserved_slots = cursor.fetchall()
        conn.close()
        reserved_set = set(
            (slot['Reservation_Days'], str(slot['Reservation_Start_Time']), str(slot['Reservation_End_Time'])) for slot
            in reserved_slots)
        available_slots = [slot for slot in predefined_slots if slot not in reserved_set]
        return jsonify(success=True, slots=available_slots)
    except Exception as e:
        return jsonify(success=False, error=str(e))
    

@app.route('/add_new_child', methods=['GET', 'POST'])
def add_new_child():
    parent_id = request.args.get('parent_id')

    if request.method == 'POST':
        name = request.form['name']
        birthDate = request.form['birthDate']
        gender = request.form['gender']
        selected_courses = request.form.getlist('course_ids')
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                # Insert the child
                cursor.execute(
                    "INSERT INTO Child (Child_Name, DateOfBirth, Gender, Parent_ID) VALUES (%s, %s, %s, %s)",
                    (name, birthDate, gender, parent_id)
                )
                child_id = cursor.lastrowid  # Get the inserted Child ID

                for course_id in selected_courses:
                    specialist_id = request.form.get(f'specialists[{course_id}]')
                    selected_date = request.form.get(f'dates[{course_id}]')

                    if specialist_id and selected_date:
                        parts = selected_date.split('-')
                        if len(parts) == 3:
                            reservation_days, start_time, end_time = parts
                            print("res",reservation_days,"strt time",start_time, "enddd",end_time)
                            # Ensure reservation_days format is correct
                            if reservation_days in ['Monday,Wednesday', 'Tuesday,Thursday']:
                                cursor.execute(
                                    "SELECT * FROM Supervision WHERE Specialist_ID=%s AND Reservation_Days=%s AND Reservation_Start_Time=%s AND Reservation_End_Time=%s",
                                    (specialist_id, reservation_days, start_time, end_time)
                                ) 
                                if cursor.fetchone():
                                    flash(
                                        f'Specialist {specialist_id} is already reserved for course {course_id} at the selected time.',
                                        'danger')
                                else:
                                    cursor.execute(
                                        "INSERT INTO Supervision (Child_ID, Specialist_ID, Course_ID, Reservation_Days, Reservation_Start_Time, Reservation_End_Time) VALUES (%s, %s, %s, %s, %s, %s)",
                                        (child_id, specialist_id, course_id, reservation_days, start_time, end_time)
                                    )
                            else:
                                flash(
                                    f'Invalid reservation days format for course {course_id}. Expected format is "Days".',
                                    'danger')
                        else:
                            flash(
                                f'Invalid date format for course {course_id}. Expected format is "Days,StartTime,EndTime".',
                                'danger')

                conn.commit()

            conn.close()
            return redirect(url_for('parents'))
        except Exception as e:
            print(f"Error: {e}")
            flash(f"Error: {e}", 'danger')

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT Course_ID, Course_Name FROM Courses")
        courses = cursor.fetchall()
        cursor.execute("SELECT Specialist_ID as id, Specialist_Name as name FROM Specialist")
        specialists = cursor.fetchall()
    conn.close()
    return render_template('add_new_child.html', parent_id=parent_id, courses=courses, specialists=specialists)



######################################################################################################
# Specialist section
@app.route('/specialist_dashboard')
def specialist_dashboard():
    if 'user' in session and session['user_type'] == 'specialist':
        user = session['user']
        specialist_id = user['Specialist_ID']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Specialist WHERE Specialist_ID=%s", (specialist_id,))
                specialist = cursor.fetchone()
                cursor.execute("""
                    SELECT DISTINCT Courses.Course_Name
                    FROM Courses
                    JOIN Supervision ON Courses.Course_ID = Supervision.Course_ID
                    WHERE Supervision.Specialist_ID = %s
                """, (specialist_id,))
                courses = cursor.fetchall()
                cursor.execute("""
                    SELECT c.Child_ID, c.Child_Name, s.Reservation_Days, s.Reservation_Start_Time, s.Reservation_End_Time, co.Course_Name
                    FROM Supervision s
                    JOIN Child c ON s.Child_ID = c.Child_ID
                    JOIN Courses co ON s.Course_ID = co.Course_ID
                    WHERE s.Specialist_ID=%s
                """, (specialist_id,))
                supervisions = cursor.fetchall()
            conn.close()
            return render_template('specialist_dashboard.html', specialist=specialist, courses=courses,
                                   supervisions=supervisions)
        except Exception as e:
            logging.error(f"Error in specialist_dashboard: {e}")
            flash(f"Error: {e}", 'danger')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@app.route('/my_supervisions')
def my_supervisions():
    if 'user' in session and session['user_type'] == 'specialist':
        print(session)
        specialist_id = session['user']['Specialist_ID']

        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT Child.Child_Name, Courses.Course_Name, Supervision.Reservation_Days, 
                    Supervision.Reservation_Start_Time, Supervision.Reservation_End_Time
                    FROM Supervision
                    JOIN Child ON Supervision.Child_ID = Child.Child_ID
                    JOIN Courses ON Supervision.Course_ID = Courses.Course_ID
                    WHERE Supervision.Specialist_ID = %s
                """
                cursor.execute(sql, (specialist_id,))
                supervisions = cursor.fetchall()
        finally:
            connection.close()
        return render_template('my_supervisions.html', supervisions=supervisions)
    else:
        return redirect(url_for('login'))


# Display schedule
@app.route('/todays_schedule')
def todays_schedule():
    if 'user' in session and session['user_type'] == 'specialist':
        specialist_id = session['user']['Specialist_ID']
        today = datetime.today().strftime('%A')  
        print(f"Today's day: {today}")  
        connection = get_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT Child.Child_Name, Courses.Course_Name, 
                    Supervision.Reservation_Start_Time, Supervision.Reservation_End_Time
                    FROM Supervision
                    JOIN Child ON Supervision.Child_ID = Child.Child_ID
                    JOIN Courses ON Supervision.Course_ID = Courses.Course_ID
                    WHERE Supervision.Specialist_ID = %s AND FIND_IN_SET(%s, Supervision.Reservation_Days)
                """
                cursor.execute(sql, (specialist_id, today))
                todays_supervisions = cursor.fetchall()

                print(f"Today's supervisions: {todays_supervisions}")  # Debug: Print fetched data
        finally:
            connection.close()

        return render_template('todays_schedule.html', supervisions=todays_supervisions)
    else:
        return redirect(url_for('login'))


@app.route('/payments')
def payments():
    payments_data = get_payment_data()
    return render_template('payments.html', payments=payments_data)

from datetime import datetime
def get_payment_data():
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.Parent_Name, p.Parent_ID, py.* 
                FROM Payments py 
                INNER JOIN Parent p ON py.Parent_ID = p.Parent_ID 
                ORDER BY py.Parent_ID
            """)
            result = cursor.fetchall()
        conn.close()

        grouped_payments = {}
        seen_payment_ids = set()

        for payment in result:
            payment_id = payment['PaymentID']
            if payment_id not in seen_payment_ids:
                parent_name = payment['Parent_Name']
                payment['PaymentDate'] = payment['PaymentDate'].strftime('%Y-%m-%d')
                if parent_name not in grouped_payments:
                    grouped_payments[parent_name] = []
                grouped_payments[parent_name].append(payment)
                seen_payment_ids.add(payment_id)

        return grouped_payments
    except Exception as e:
        print(f"Error: {e}")
        return {}


@app.route('/add_payment', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        paymentDate = request.form['paymentDate']
        amount = request.form['amount']
        parent_id = request.form['parent_id']
        paymentStatus = request.form['paymentStatus']
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO Payments (PaymentDate, Amount, Parent_ID, PaymentStatus) VALUES (%s, %s, %s, %s)",
                               (paymentDate, amount, parent_id, paymentStatus))
                conn.commit()
            conn.close()
            flash('Payment added successfully!', 'success')
            return redirect(url_for('payments'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('add_payment.html')


@app.route('/update_payment/<int:payment_id>', methods=['POST'])
def update_payment(payment_id):
    paymentDate = request.form.get('paymentDate')
    amount = request.form.get('amount')
    parent_id = request.form.get('parent_id')
    paymentStatus = request.form.get('status')

    print(f'Updating payment {payment_id} with status: {paymentStatus}')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Payments 
                SET PaymentDate = %s, Amount = %s, Parent_ID = %s, PaymentStatus = %s
                WHERE PaymentID = %s
                """, (paymentDate, amount, parent_id, paymentStatus, payment_id))
            conn.commit()
        conn.close()
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e))



@app.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    logging.debug(f"Deleting payment: {payment_id}")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Payments WHERE PaymentID = %s", (payment_id,))
            conn.commit()
        conn.close()
        logging.debug("Deletion successful")
        return jsonify(success=True, message='Payment deleted successfully!')
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify(success=False, error=str(e))

@app.route('/search_payment', methods=['GET'])
def search_payment():
    query = request.args.get('query', '')
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT Payments.*, Parent.Parent_Name
                FROM Payments
                JOIN Parent ON Payments.Parent_ID = Parent.Parent_ID
                WHERE Parent.Parent_Name LIKE %s
            """, ('%' + query + '%',))
            payments = cursor.fetchall()
        conn.close()
        return jsonify(success=True, payments=payments)
    except Exception as e:
        return jsonify(success=False, error=str(e))


if __name__ == '__main__':
    app.run(debug=True)
