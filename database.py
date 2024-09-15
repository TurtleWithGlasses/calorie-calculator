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
    cursor.execute("SELECT name, calories FROM meals ORDER BY name ASC")
    data = cursor.fetchall()
    conn.close()
    
    print(f"Fetched meal data: {data}")  # Debug print to show the meal data fetched
    return data

def get_meal_calories(meal_name):
    print(f"Fetching calories for meal: {meal_name}")  # Debugging print
    conn = sqlite3.connect("meals.db")
    cursor = conn.cursor()
    cursor.execute("SELECT calories FROM meals WHERE name=?", (meal_name,))
    result = cursor.fetchone()
    conn.close()

    if result:
        print(f"Calories fetched for {meal_name}: {result[0]}")  # Debugging print
        return result[0]
    else:
        print(f"No calories found for {meal_name}")  # Debugging print
        return 0


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

# Edit a meal in the database
def edit_meal_in_db(old_name, new_name, new_calories):
    conn = sqlite3.connect('meals.db')  # Adjust according to your DB
    cursor = conn.cursor()
    cursor.execute("UPDATE meals SET name=?, calories=? WHERE name=?", (new_name, new_calories, old_name))
    conn.commit()
    conn.close()

# Delete a meal from the database
def delete_meal_from_db(meal_name):
    conn = sqlite3.connect('meals.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE name=?", (meal_name,))
    conn.commit()
    conn.close()
