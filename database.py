import psycopg2
# from psycopg2 import sql
import time

postgresg_user="postgres"
postgresg_pw="mehmetsoylu"


# Initialize database and create table if it doesn't exist
def init_db():
    conn = psycopg2.connect(
        host="localhost",
        database="calorie_tracker_db",
        user=postgresg_user,
        password=postgresg_pw
    )
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS meals (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        calories INTEGER NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_calories (
                        id SERIAL PRIMARY KEY,
                        date TEXT NOT NULL,
                        total_calories REAL NOT NULL)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_meals (
                        id SERIAL PRIMARY KEY,
                        date TEXT NOT NULL,
                        meal_name TEXT NOT NULL,
                        grams INTEGER NOT NULL,
                        calories REAL NOT NULL,
                        section_index INTEGER NOT NULL
                   )''')
    
    conn.commit()
    cursor.close()
    conn.close()

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="calorie_tracker_db",
        user=postgresg_user,
        password=postgresg_pw
    )
    return conn


# Insert some meal data into the database for testing
def insert_meal_data():
    conn = psycopg2.connect(host="localhost",
                            database="calorie_tracker_db",
                            user=postgresg_user,
                            password=postgresg_pw)
    cursor = conn.cursor()
    meals = [("Meal 1", 150), ("Meal 2", 250), ("Meal 3", 100)]
    cursor.executemany('INSERT INTO meals (name, calories) VALUES (%s, %s)', meals)
    conn.commit()
    conn.close()

# Fetch meal data from the database
def fetch_meal_data():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="calorie_tracker_db",
            user=postgresg_user,
            password=postgresg_pw
        )
        cursor = conn.cursor()
        cursor.execute("SELECT name, calories FROM meals ORDER BY name ASC")
        data = cursor.fetchall()
    except psycopg2.DatabaseError as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()
    return data

def get_meal_calories(meal_name):
    try:
        conn = psycopg2.connect(host="localhost",
                                database="calorie_tracker_db",
                                user=postgresg_user,
                                password=postgresg_pw)
        cursor = conn.cursor()
        cursor.execute("SELECT calories FROM meals WHERE name=%s", (meal_name,))
        result = cursor.fetchone()
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        result = None
    finally:
        conn.close()

    if result:
        return result[0]
    return 0


# Insert a new meal into the database
def add_new_meal(name, calories):
    conn = psycopg2.connect(host="localhost",
                            database="calorie_tracker_db",
                            user=postgresg_user,
                            password=postgresg_pw)
    cursor = conn.cursor()
    
    # Check if the meal already exists
    cursor.execute('SELECT COUNT(*) FROM meals WHERE name=%s', (name,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False  # Meal already exists
    
    # Insert new meal if it doesn't exist
    cursor.execute('INSERT INTO meals (name, calories) VALUES (%s, %s)', (name, calories))
    conn.commit()
    conn.close()
    return True  # Successfully added

# Edit a meal in the database
def edit_meal_in_db(old_name, new_name, new_calories):
    conn = psycopg2.connect(host="localhost",
                            database="calorie_tracker_db",
                            user=postgresg_user,
                            password=postgresg_pw)  # Adjust according to your DB
    cursor = conn.cursor()
    cursor.execute("UPDATE meals SET name=%s, calories=%s WHERE name=%s", (new_name, new_calories, old_name))
    conn.commit()
    conn.close()

# Delete a meal from the database
def delete_meal_from_db(meal_name):
    conn = psycopg2.connect(host="localhost",
                            database="calorie_tracker_db",
                            user=postgresg_user,
                            password=postgresg_pw)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE name=%s", (meal_name,))
    conn.commit()
    conn.close()

def save_daily_calories(selected_date, total_calories, meals):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO daily_calories (date, total_calories)
                          VALUES (%s, %s)
                          ON CONFLICT (date) DO UPDATE
                          SET total_calories = EXCLUDED.total_calories''',
                       (selected_date, total_calories))
        save_meals_for_date(conn, selected_date, meals)
        conn.commit()
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def save_meals_for_date(conn, selected_date, meals):
    cursor = conn.cursor()
    
    # First, remove the old meals for the selected date
    cursor.execute('DELETE FROM daily_meals WHERE date = %s', (selected_date,))
    
    # Insert the new meals for the selected date
    cursor.executemany('INSERT INTO daily_meals (date, meal_name, grams, calories, section_index) VALUES (%s, %s, %s, %s, %s)', meals)

def fetch_meals_for_date(selected_date):
    conn = psycopg2.connect(
        host="localhost",
        database="calorie_tracker_db",
        user=postgresg_user,
        password=postgresg_pw
    )
    cursor = conn.cursor()

    # Query to fetch meals for a date and include the section index (0, 1, 2)
    cursor.execute('''
        SELECT meal_name, grams, calories, section_index
        FROM daily_meals
        WHERE date = %s
    ''', (selected_date,))
    
    meals = cursor.fetchall()
    conn.close()
    
    print(f"Fetched meals for {selected_date}: {meals}")
    return meals

def save_meals_with_retry(selected_date, meals, retries=5):
    for i in range(retries):
        try:
            conn = psycopg2.connect(host="localhost",
                            database="calorie_tracker_db",
                            user=postgresg_user,
                            password=postgresg_pw)
            cursor = conn.cursor()

            # First, remove the old meals for the selected date
            cursor.execute('DELETE FROM daily_meals WHERE date = %s', (selected_date,))
            cursor.executemany('INSERT INTO daily_meals (date, meal_name, grams, calories) VALUES (%s, %s, %s, %s)', meals)
            conn.commit()
            conn.close()
            break  # If successful, break out of the retry loop
        except psycopg2.OperationalError as e:
            if "locked" in str(e):
                print(f"Database is locked, retrying... ({i+1}/{retries})")
                time.sleep(1)  # Wait for 1 second before retrying
            else:
                raise  # If it's another kind of error, raise it

def fetch_meals_from_db(search_text):
        query = "SELECT name FROM meals WHERE LOWER(name) LIKE %s ORDER BY name ASC"
        search_param = f"%{search_text}%"
        conn = psycopg2.connect(
            host="localhost",
            database="calorie_tracker_db",
            user=postgresg_user,
            password=postgresg_pw
        )
        cursor = conn.cursor()
        cursor.execute(query, (search_param,))
        matched_meals = [row[0] for row in cursor.fetchall()]
        conn.close()
        return matched_meals