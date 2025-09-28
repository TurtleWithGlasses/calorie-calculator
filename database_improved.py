"""
Improved database manager with better error handling, security, and features.
"""

import psycopg2
import json
import csv
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple, Any
from contextlib import contextmanager
import logging

from config import DB_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Enhanced database manager with improved error handling and security."""
    
    def __init__(self):
        self.config = DB_CONFIG
        self.init_database()
        
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
                
    def init_database(self):
        """Initialize database and create tables if they don't exist."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create meals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS meals (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        calories INTEGER NOT NULL,
                        protein REAL DEFAULT 0,
                        carbs REAL DEFAULT 0,
                        fat REAL DEFAULT 0,
                        fiber REAL DEFAULT 0,
                        sugar REAL DEFAULT 0,
                        sodium REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create daily_calories table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_calories (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL UNIQUE,
                        total_calories REAL NOT NULL,
                        protein REAL DEFAULT 0,
                        carbs REAL DEFAULT 0,
                        fat REAL DEFAULT 0,
                        fiber REAL DEFAULT 0,
                        sugar REAL DEFAULT 0,
                        sodium REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create daily_meals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_meals (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        meal_name TEXT NOT NULL,
                        grams REAL NOT NULL,
                        calories REAL NOT NULL,
                        protein REAL DEFAULT 0,
                        carbs REAL DEFAULT 0,
                        fat REAL DEFAULT 0,
                        fiber REAL DEFAULT 0,
                        sugar REAL DEFAULT 0,
                        sodium REAL DEFAULT 0,
                        section_index INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create user_goals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_goals (
                        id SERIAL PRIMARY KEY,
                        date DATE NOT NULL,
                        daily_calories INTEGER NOT NULL,
                        protein_goal REAL DEFAULT 0,
                        carbs_goal REAL DEFAULT 0,
                        fat_goal REAL DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_meals_date ON daily_meals(date)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_meals_section ON daily_meals(section_index)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_name ON meals(name)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except psycopg2.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
            
    def add_meal(self, name: str, calories: int, **macros) -> bool:
        """Add a new meal to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if meal already exists
                cursor.execute('SELECT id FROM meals WHERE name = %s', (name,))
                if cursor.fetchone():
                    logger.warning(f"Meal '{name}' already exists")
                    return False
                
                # Insert new meal
                cursor.execute('''
                    INSERT INTO meals (name, calories, protein, carbs, fat, fiber, sugar, sodium)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (name, calories, 
                     macros.get('protein', 0),
                     macros.get('carbs', 0),
                     macros.get('fat', 0),
                     macros.get('fiber', 0),
                     macros.get('sugar', 0),
                     macros.get('sodium', 0)))
                
                conn.commit()
                logger.info(f"Added meal: {name}")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"Failed to add meal: {e}")
            return False
            
    def get_meal(self, name: str) -> Optional[Dict]:
        """Get meal information by name."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, calories, protein, carbs, fat, fiber, sugar, sodium
                    FROM meals WHERE name = %s
                ''', (name,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'name': result[0],
                        'calories': result[1],
                        'protein': result[2],
                        'carbs': result[3],
                        'fat': result[4],
                        'fiber': result[5],
                        'sugar': result[6],
                        'sodium': result[7]
                    }
                return None
                
        except psycopg2.Error as e:
            logger.error(f"Failed to get meal: {e}")
            return None
            
    def search_meals(self, query: str, limit: int = 50) -> List[Dict]:
        """Search meals by name."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, calories, protein, carbs, fat
                    FROM meals 
                    WHERE LOWER(name) LIKE LOWER(%s)
                    ORDER BY name
                    LIMIT %s
                ''', (f'%{query}%', limit))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'name': row[0],
                        'calories': row[1],
                        'protein': row[2],
                        'carbs': row[3],
                        'fat': row[4]
                    })
                return results
                
        except psycopg2.Error as e:
            logger.error(f"Failed to search meals: {e}")
            return []
            
    def update_meal(self, old_name: str, new_name: str, calories: int, **macros) -> bool:
        """Update an existing meal."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE meals 
                    SET name = %s, calories = %s, protein = %s, carbs = %s, 
                        fat = %s, fiber = %s, sugar = %s, sodium = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE name = %s
                ''', (new_name, calories,
                     macros.get('protein', 0),
                     macros.get('carbs', 0),
                     macros.get('fat', 0),
                     macros.get('fiber', 0),
                     macros.get('sugar', 0),
                     macros.get('sodium', 0),
                     old_name))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Updated meal: {old_name} -> {new_name}")
                    return True
                return False
                
        except psycopg2.Error as e:
            logger.error(f"Failed to update meal: {e}")
            return False
            
    def delete_meal(self, name: str) -> bool:
        """Delete a meal from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM meals WHERE name = %s', (name,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Deleted meal: {name}")
                    return True
                return False
                
        except psycopg2.Error as e:
            logger.error(f"Failed to delete meal: {e}")
            return False
            
    def save_daily_meals(self, date: str, meals: List[Dict]) -> bool:
        """Save daily meals for a specific date."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Delete existing meals for the date
                cursor.execute('DELETE FROM daily_meals WHERE date = %s', (date,))
                
                # Insert new meals
                for meal in meals:
                    cursor.execute('''
                        INSERT INTO daily_meals 
                        (date, meal_name, grams, calories, protein, carbs, fat, 
                         fiber, sugar, sodium, section_index)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (date, meal['name'], meal['grams'], meal['calories'],
                         meal.get('protein', 0), meal.get('carbs', 0), meal.get('fat', 0),
                         meal.get('fiber', 0), meal.get('sugar', 0), meal.get('sodium', 0),
                         meal['section_index']))
                
                # Update daily totals
                total_calories = sum(meal['calories'] for meal in meals)
                total_protein = sum(meal.get('protein', 0) for meal in meals)
                total_carbs = sum(meal.get('carbs', 0) for meal in meals)
                total_fat = sum(meal.get('fat', 0) for meal in meals)
                
                cursor.execute('''
                    INSERT INTO daily_calories (date, total_calories, protein, carbs, fat)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (date) DO UPDATE SET
                        total_calories = EXCLUDED.total_calories,
                        protein = EXCLUDED.protein,
                        carbs = EXCLUDED.carbs,
                        fat = EXCLUDED.fat,
                        updated_at = CURRENT_TIMESTAMP
                ''', (date, total_calories, total_protein, total_carbs, total_fat))
                
                conn.commit()
                logger.info(f"Saved {len(meals)} meals for {date}")
                return True
                
        except psycopg2.Error as e:
            logger.error(f"Failed to save daily meals: {e}")
            return False
            
    def get_daily_meals(self, date: str) -> List[Dict]:
        """Get meals for a specific date."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT meal_name, grams, calories, protein, carbs, fat, section_index
                    FROM daily_meals
                    WHERE date = %s
                    ORDER BY section_index, created_at
                ''', (date,))
                
                meals = []
                for row in cursor.fetchall():
                    meals.append({
                        'name': row[0],
                        'grams': row[1],
                        'calories': row[2],
                        'protein': row[3],
                        'carbs': row[4],
                        'fat': row[5],
                        'section_index': row[6]
                    })
                return meals
                
        except psycopg2.Error as e:
            logger.error(f"Failed to get daily meals: {e}")
            return []
            
    def get_daily_totals(self, date: str) -> Optional[Dict]:
        """Get daily totals for a specific date."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT total_calories, protein, carbs, fat
                    FROM daily_calories
                    WHERE date = %s
                ''', (date,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'calories': result[0],
                        'protein': result[1],
                        'carbs': result[2],
                        'fat': result[3]
                    }
                return None
                
        except psycopg2.Error as e:
            logger.error(f"Failed to get daily totals: {e}")
            return None
            
    def get_analytics_data(self, start_date: str, end_date: str) -> Dict:
        """Get analytics data for a date range."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get daily totals
                cursor.execute('''
                    SELECT date, total_calories, protein, carbs, fat
                    FROM daily_calories
                    WHERE date BETWEEN %s AND %s
                    ORDER BY date
                ''', (start_date, end_date))
                
                daily_data = []
                for row in cursor.fetchall():
                    daily_data.append({
                        'date': row[0].strftime('%Y-%m-%d'),
                        'calories': row[1],
                        'protein': row[2],
                        'carbs': row[3],
                        'fat': row[4]
                    })
                
                # Get meal frequency
                cursor.execute('''
                    SELECT meal_name, COUNT(*) as frequency
                    FROM daily_meals
                    WHERE date BETWEEN %s AND %s
                    GROUP BY meal_name
                    ORDER BY frequency DESC
                    LIMIT 10
                ''', (start_date, end_date))
                
                meal_frequency = []
                for row in cursor.fetchall():
                    meal_frequency.append({
                        'name': row[0],
                        'frequency': row[1]
                    })
                
                return {
                    'daily_data': daily_data,
                    'meal_frequency': meal_frequency
                }
                
        except psycopg2.Error as e:
            logger.error(f"Failed to get analytics data: {e}")
            return {'daily_data': [], 'meal_frequency': []}
            
    def export_data(self, file_path: str) -> bool:
        """Export data to CSV or JSON file."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if file_path.endswith('.csv'):
                    self._export_csv(cursor, file_path)
                elif file_path.endswith('.json'):
                    self._export_json(cursor, file_path)
                else:
                    raise ValueError("Unsupported file format")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False
            
    def _export_csv(self, cursor, file_path: str):
        """Export data to CSV format."""
        # Export meals
        cursor.execute('SELECT * FROM meals')
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([desc[0] for desc in cursor.description])
            writer.writerows(cursor.fetchall())
            
    def _export_json(self, cursor, file_path: str):
        """Export data to JSON format."""
        data = {}
        
        # Export meals
        cursor.execute('SELECT * FROM meals')
        meals = []
        for row in cursor.fetchall():
            meals.append({
                'id': row[0],
                'name': row[1],
                'calories': row[2],
                'protein': row[3],
                'carbs': row[4],
                'fat': row[5],
                'fiber': row[6],
                'sugar': row[7],
                'sodium': row[8]
            })
        data['meals'] = meals
        
        # Export daily data
        cursor.execute('SELECT * FROM daily_calories ORDER BY date')
        daily_data = []
        for row in cursor.fetchall():
            daily_data.append({
                'date': row[1].strftime('%Y-%m-%d'),
                'total_calories': row[2],
                'protein': row[3],
                'carbs': row[4],
                'fat': row[5]
            })
        data['daily_data'] = daily_data
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def import_data(self, file_path: str) -> bool:
        """Import data from CSV or JSON file."""
        try:
            if file_path.endswith('.json'):
                self._import_json(file_path)
            else:
                raise ValueError("Only JSON import is currently supported")
            return True
        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            return False
            
    def _import_json(self, file_path: str):
        """Import data from JSON format."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Import meals
            if 'meals' in data:
                for meal in data['meals']:
                    cursor.execute('''
                        INSERT INTO meals (name, calories, protein, carbs, fat, fiber, sugar, sodium)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (name) DO UPDATE SET
                            calories = EXCLUDED.calories,
                            protein = EXCLUDED.protein,
                            carbs = EXCLUDED.carbs,
                            fat = EXCLUDED.fat,
                            fiber = EXCLUDED.fiber,
                            sugar = EXCLUDED.sugar,
                            sodium = EXCLUDED.sodium
                    ''', (meal['name'], meal['calories'], meal.get('protein', 0),
                         meal.get('carbs', 0), meal.get('fat', 0), meal.get('fiber', 0),
                         meal.get('sugar', 0), meal.get('sodium', 0)))
            
            conn.commit()
            logger.info("Data imported successfully")
