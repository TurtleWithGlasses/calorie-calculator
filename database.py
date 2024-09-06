import sqlite3

# Initialize database and create table if it doesn't exist
def init_db():
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS meals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        calories INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

# Insert some meal data into the database for testing
def insert_meal_data():
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    meals = [("Meal 1", 150), ("Meal 2", 250), ("Meal 3", 100)]
    cursor.executemany('INSERT INTO meals (name, calories) VALUES (?, ?)', meals)
    conn.commit()
    conn.close()

# Fetch meal data from the database
def fetch_meal_data():
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, calories FROM meals")
    data = cursor.fetchall()
    conn.close()
    return data

# Get the calories of a meal from the database
def get_meal_calories(meal_name):
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    cursor.execute("SELECT calories FROM meals WHERE name=?", (meal_name,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Insert a new meal into the database
def add_new_meal(name, calories):
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    
    # Check if the meal already exists
    cursor.execute('SELECT COUNT(*) FROM meals WHERE name=?', (name,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False  # Meal already exists
    
    # Insert new meal if it doesn't exist
    cursor.execute('INSERT INTO meals (name, calories) VALUES (?, ?)', (name, calories))
    conn.commit()
    conn.close()
    return True  # Successfully added

