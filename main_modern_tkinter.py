#!/usr/bin/env python3
"""
Modern Calorie Tracker - Enhanced Tkinter Version
A modernized version of the original calorie calculator with improved UI and features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import Calendar
from datetime import datetime, timedelta
import json
import csv
from typing import List, Dict, Optional
import logging

# Import your existing database module
from database import init_db, fetch_meal_data, get_meal_calories, edit_meal_in_db, delete_meal_from_db, add_new_meal, save_daily_calories, fetch_meals_for_date, fetch_meals_from_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModernCalorieTracker:
    """Modernized calorie tracker with improved UI and features."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_styles()
        self.init_database()
        self.setup_ui()
        self.load_data()
        
    def setup_window(self):
        """Setup the main window."""
        self.root.title("Calorie Tracker Pro - Modern Edition")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_styles(self):
        """Setup modern styling."""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2E86AB')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495E')
        style.configure('Modern.TButton', font=('Arial', 10, 'bold'))
        style.configure('Success.TButton', font=('Arial', 10, 'bold'), foreground='white')
        style.configure('Danger.TButton', font=('Arial', 10, 'bold'), foreground='white')
        
        # Configure colors
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72', 
            'success': '#27AE60',
            'warning': '#F39C12',
            'danger': '#E74C3C',
            'light': '#ECF0F1',
            'dark': '#2C3E50'
        }
        
    def init_database(self):
        """Initialize database."""
        try:
            init_db()
            self.meal_data = fetch_meal_data()
            self.meal_options = [meal[0] for meal in self.meal_data]
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.create_header(main_frame)
        
        # Content section with notebook
        self.create_content(main_frame)
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self, parent):
        """Create the header section."""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="Calorie Tracker Pro", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # Date selection
        date_frame = ttk.Frame(header_frame)
        date_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        self.calendar_btn = ttk.Button(date_frame, text="📅", command=self.open_calendar, width=3)
        self.calendar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick date buttons
        ttk.Button(date_frame, text="Today", command=self.set_today).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Yesterday", command=self.set_yesterday).pack(side=tk.LEFT, padx=2)
        ttk.Button(date_frame, text="Tomorrow", command=self.set_tomorrow).pack(side=tk.LEFT, padx=2)
        
        # Action buttons
        action_frame = ttk.Frame(header_frame)
        action_frame.grid(row=0, column=2, sticky="e", padx=(10, 0))
        
        ttk.Button(action_frame, text="Manage Meals", command=self.open_meal_manager).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(action_frame, text="Refresh", command=self.refresh_data).pack(side=tk.LEFT, padx=2)
        
    def create_content(self, parent):
        """Create the main content area."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        # Daily tracking tab
        self.daily_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.daily_frame, text="Daily Tracking")
        self.create_daily_tracking()
        
        # Analytics tab
        self.analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analytics_frame, text="Analytics")
        self.create_analytics()
        
        # Goals tab
        self.goals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.goals_frame, text="Goals")
        self.create_goals()
        
    def create_daily_tracking(self):
        """Create the daily tracking interface."""
        # Create scrollable frame
        canvas = tk.Canvas(self.daily_frame)
        scrollbar = ttk.Scrollbar(self.daily_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Meal sections
        self.meal_sections = []
        section_titles = ["Breakfast (6:00-11:00)", "Lunch (11:00-16:00)", "Dinner (16:00-21:00)", "Snacks (21:00-6:00)"]
        
        for i, title in enumerate(section_titles):
            section = MealSectionModern(scrollable_frame, title, i, self)
            self.meal_sections.append(section)
            section.pack(fill="x", pady=5, padx=10)
            
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Total calories display
        self.create_total_display(scrollable_frame)
        
    def create_total_display(self, parent):
        """Create the total calories display."""
        total_frame = ttk.LabelFrame(parent, text="Daily Summary", padding="10")
        total_frame.pack(fill="x", pady=10, padx=10)
        
        # Total calories
        self.total_calories_var = tk.StringVar(value="Total Calories: 0")
        total_label = ttk.Label(total_frame, textvariable=self.total_calories_var, 
                              font=('Arial', 14, 'bold'), foreground=self.colors['primary'])
        total_label.pack()
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(total_frame, variable=self.progress_var, 
                                          maximum=3000, length=400)
        self.progress_bar.pack(pady=5)
        
        # Goal info
        self.goal_var = tk.StringVar(value="Goal: 2000 calories")
        goal_label = ttk.Label(total_frame, textvariable=self.goal_var, 
                             font=('Arial', 10), foreground=self.colors['dark'])
        goal_label.pack()
        
    def create_analytics(self):
        """Create the analytics tab."""
        analytics_frame = ttk.Frame(self.analytics_frame)
        analytics_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Analytics content
        ttk.Label(analytics_frame, text="Analytics Dashboard", style='Title.TLabel').pack(pady=10)
        
        # Placeholder for analytics
        ttk.Label(analytics_frame, text="Analytics features coming soon!", 
                 font=('Arial', 12)).pack(pady=50)
        
        # Simple statistics
        stats_frame = ttk.LabelFrame(analytics_frame, text="Quick Stats", padding="10")
        stats_frame.pack(fill="x", pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=10, width=60)
        self.stats_text.pack(fill="both", expand=True)
        
        self.update_analytics()
        
    def create_goals(self):
        """Create the goals tab."""
        goals_frame = ttk.Frame(self.goals_frame)
        goals_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(goals_frame, text="Goals & Settings", style='Title.TLabel').pack(pady=10)
        
        # Daily calorie goal
        goal_frame = ttk.LabelFrame(goals_frame, text="Daily Calorie Goal", padding="10")
        goal_frame.pack(fill="x", pady=10)
        
        ttk.Label(goal_frame, text="Target Calories:").grid(row=0, column=0, sticky="w", padx=5)
        self.goal_calories_var = tk.StringVar(value="2000")
        goal_entry = ttk.Entry(goal_frame, textvariable=self.goal_calories_var, width=10)
        goal_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(goal_frame, text="Update Goal", command=self.update_goal).grid(row=0, column=2, padx=10)
        
    def create_status_bar(self):
        """Create the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.grid(row=1, column=0, sticky="ew")
        
    def open_calendar(self):
        """Open calendar for date selection."""
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("300x300")
        cal_window.transient(self.root)
        cal_window.grab_set()
        
        # Center the window
        cal_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        cal = Calendar(cal_window, selectmode="day")
        cal.pack(pady=20)
        
        def on_date_select():
            selected_date = cal.get_date()
            self.date_var.set(selected_date)
            cal_window.destroy()
            self.load_data()
            
        ttk.Button(cal_window, text="Select", command=on_date_select).pack(pady=10)
        
    def set_today(self):
        """Set date to today."""
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.load_data()
        
    def set_yesterday(self):
        """Set date to yesterday."""
        yesterday = datetime.now() - timedelta(days=1)
        self.date_var.set(yesterday.strftime("%Y-%m-%d"))
        self.load_data()
        
    def set_tomorrow(self):
        """Set date to tomorrow."""
        tomorrow = datetime.now() + timedelta(days=1)
        self.date_var.set(tomorrow.strftime("%Y-%m-%d"))
        self.load_data()
        
    def load_data(self):
        """Load data for the selected date."""
        try:
            date_str = self.date_var.get()
            for section in self.meal_sections:
                section.load_meals_for_date(date_str)
            self.update_totals()
            self.status_var.set(f"Data loaded for {date_str}")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            
    def update_totals(self):
        """Update total calories display."""
        total = sum(section.get_total_calories() for section in self.meal_sections)
        self.total_calories_var.set(f"Total Calories: {total}")
        
        # Update progress bar
        goal = int(self.goal_calories_var.get())
        self.progress_var.set(total)
        self.progress_bar.configure(maximum=goal)
        
        # Update goal display
        self.goal_var.set(f"Goal: {goal} calories ({total}/{goal})")
        
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()
        self.status_var.set("Data refreshed")
        
    def open_meal_manager(self):
        """Open meal management window."""
        MealManagerModern(self.root, self)
        
    def export_data(self):
        """Export data to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    self.export_json(file_path)
                else:
                    self.export_csv(file_path)
                messagebox.showinfo("Success", "Data exported successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
                
    def export_json(self, file_path):
        """Export data to JSON format."""
        data = {
            'meals': [{'name': meal[0], 'calories': meal[1]} for meal in self.meal_data],
            'daily_data': self.get_daily_data()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            
    def export_csv(self, file_path):
        """Export data to CSV format."""
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Calories'])
            for meal in self.meal_data:
                writer.writerow([meal[0], meal[1]])
                
    def get_daily_data(self):
        """Get daily meal data."""
        daily_data = []
        for section in self.meal_sections:
            for meal in section.get_meals():
                daily_data.append({
                    'section': section.title,
                    'name': meal['name'],
                    'quantity': meal['quantity'],
                    'calories': meal['calories']
                })
        return daily_data
        
    def update_analytics(self):
        """Update analytics display."""
        # Simple analytics for now
        total_meals = len(self.meal_data)
        total_calories = sum(section.get_total_calories() for section in self.meal_sections)
        
        stats = f"""Database Statistics:
Total Meals in Database: {total_meals}
Current Day Calories: {total_calories}
Average Calories per Meal: {total_calories / max(1, sum(len(section.get_meals()) for section in self.meal_sections)):.1f}

Recent Activity:
- Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Active sections: {len([s for s in self.meal_sections if s.get_meals()])}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
    def update_goal(self):
        """Update daily calorie goal."""
        try:
            goal = int(self.goal_calories_var.get())
            self.update_totals()
            messagebox.showinfo("Success", f"Goal updated to {goal} calories")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")


class MealSectionModern(ttk.LabelFrame):
    """Modern meal section widget."""
    
    def __init__(self, parent, title, section_index, app):
        super().__init__(parent, text=title, padding="10")
        self.app = app
        self.section_index = section_index
        self.meal_rows = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the section UI."""
        # Header with controls
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(header_frame, text="+ Add Meal", command=self.add_meal_row).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(header_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Total for this section
        self.section_total_var = tk.StringVar(value="Total: 0 calories")
        ttk.Label(header_frame, textvariable=self.section_total_var, 
                 font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Meals container
        self.meals_frame = ttk.Frame(self)
        self.meals_frame.pack(fill="both", expand=True)
        
        # Add initial empty row
        self.add_meal_row()
        
    def add_meal_row(self):
        """Add a new meal row."""
        row_frame = ttk.Frame(self.meals_frame)
        row_frame.pack(fill="x", pady=2)
        
        # Meal selection
        meal_var = tk.StringVar()
        meal_combo = ttk.Combobox(row_frame, textvariable=meal_var, width=25)
        meal_combo['values'] = self.app.meal_options
        meal_combo.bind('<KeyRelease>', lambda e: self.search_meals(meal_combo))
        meal_combo.bind('<<ComboboxSelected>>', lambda e: self.on_meal_selected(meal_combo, quantity_spin, calories_label))
        meal_combo.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quantity
        quantity_var = tk.StringVar(value="100")
        quantity_spin = ttk.Spinbox(row_frame, from_=1, to=10000, textvariable=quantity_var, width=8)
        quantity_spin.bind('<KeyRelease>', lambda e: self.calculate_calories(meal_combo, quantity_spin, calories_label))
        quantity_spin.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row_frame, text="g").pack(side=tk.LEFT, padx=(0, 5))
        
        # Calories display
        calories_label = ttk.Label(row_frame, text="0 cal", width=10)
        calories_label.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_btn = ttk.Button(row_frame, text="×", command=lambda: self.delete_row(row_frame), width=3)
        delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Store row data
        self.meal_rows.append({
            'frame': row_frame,
            'meal_combo': meal_combo,
            'quantity_spin': quantity_spin,
            'calories_label': calories_label,
            'meal_var': meal_var,
            'quantity_var': quantity_var
        })
        
    def delete_row(self, row_frame):
        """Delete a meal row."""
        row_frame.destroy()
        self.meal_rows = [row for row in self.meal_rows if row['frame'] != row_frame]
        self.update_section_total()
        
    def clear_all(self):
        """Clear all meals in this section."""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all meals in this section?"):
            for row in self.meal_rows:
                row['frame'].destroy()
            self.meal_rows = []
            self.add_meal_row()
            self.update_section_total()
            
    def search_meals(self, combo):
        """Search for meals as user types."""
        search_text = combo.get().lower()
        if len(search_text) >= 2:
            try:
                matched_meals = fetch_meals_from_db(search_text)
                combo['values'] = matched_meals
                combo.event_generate('<Down>')
            except Exception as e:
                logger.error(f"Search error: {e}")
                
    def on_meal_selected(self, combo, quantity_spin, calories_label):
        """Handle meal selection."""
        self.calculate_calories(combo, quantity_spin, calories_label)
        
    def calculate_calories(self, combo, quantity_spin, calories_label):
        """Calculate calories for a meal."""
        try:
            meal_name = combo.get().strip()
            quantity = int(quantity_spin.get())
            
            if meal_name:
                calories_per_100g = get_meal_calories(meal_name)
                total_calories = (calories_per_100g * quantity) / 100
                calories_label.config(text=f"{total_calories:.0f} cal")
            else:
                calories_label.config(text="0 cal")
                
            self.update_section_total()
        except (ValueError, TypeError):
            calories_label.config(text="0 cal")
            self.update_section_total()
            
    def update_section_total(self):
        """Update section total calories."""
        total = 0
        for row in self.meal_rows:
            try:
                calories_text = row['calories_label'].cget('text')
                if calories_text and calories_text != "0 cal":
                    total += float(calories_text.replace(' cal', ''))
            except (ValueError, AttributeError):
                continue
                
        self.section_total_var.set(f"Total: {total:.0f} calories")
        
        # Update app totals
        if hasattr(self.app, 'update_totals'):
            self.app.update_totals()
            
    def get_total_calories(self):
        """Get total calories for this section."""
        total = 0
        for row in self.meal_rows:
            try:
                calories_text = row['calories_label'].cget('text')
                if calories_text and calories_text != "0 cal":
                    total += float(calories_text.replace(' cal', ''))
            except (ValueError, AttributeError):
                continue
        return total
        
    def get_meals(self):
        """Get meals data for this section."""
        meals = []
        for row in self.meal_rows:
            meal_name = row['meal_var'].get().strip()
            quantity = row['quantity_var'].get()
            
            if meal_name and quantity:
                try:
                    quantity = int(quantity)
                    calories_text = row['calories_label'].cget('text')
                    calories = float(calories_text.replace(' cal', '')) if calories_text != "0 cal" else 0
                    
                    meals.append({
                        'name': meal_name,
                        'quantity': quantity,
                        'calories': calories
                    })
                except (ValueError, TypeError):
                    continue
        return meals
        
    def load_meals_for_date(self, date_str):
        """Load meals for a specific date."""
        try:
            # Clear existing meals
            for row in self.meal_rows:
                row['frame'].destroy()
            self.meal_rows = []
            
            # Load meals from database
            meals_for_date = fetch_meals_for_date(date_str)
            section_meals = [meal for meal in meals_for_date if meal[3] == self.section_index]
            
            # Add meals to section
            for meal_name, grams, calories, section_index in section_meals:
                self.add_meal_row()
                if self.meal_rows:
                    row = self.meal_rows[-1]
                    row['meal_var'].set(meal_name)
                    row['quantity_var'].set(str(grams))
                    self.calculate_calories(row['meal_combo'], row['quantity_spin'], row['calories_label'])
                    
            # If no meals, add one empty row
            if not section_meals:
                self.add_meal_row()
                
        except Exception as e:
            logger.error(f"Failed to load meals for date: {e}")
            if not self.meal_rows:
                self.add_meal_row()


class MealManagerModern:
    """Modern meal management dialog."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.window = tk.Toplevel(parent)
        self.setup_window()
        self.setup_ui()
        self.load_meals()
        
    def setup_window(self):
        """Setup the meal manager window."""
        self.window.title("Meal Manager")
        self.window.geometry("800x600")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center the window
        self.window.geometry("+%d+%d" % (self.parent.winfo_rootx() + 50, self.parent.winfo_rooty() + 50))
        
    def setup_ui(self):
        """Setup the meal manager UI."""
        # Header
        header_frame = ttk.Frame(self.window, padding="10")
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text="Meal Manager", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)
        
        # Search
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))
        search_entry.bind('<KeyRelease>', lambda e: self.filter_meals())
        
        # Main content
        content_frame = ttk.Frame(self.window, padding="10")
        content_frame.pack(fill="both", expand=True)
        
        # Meals list
        self.create_meals_list(content_frame)
        
        # Add meal section
        self.create_add_meal_section(content_frame)
        
        # Buttons
        button_frame = ttk.Frame(self.window, padding="10")
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Refresh", command=self.load_meals).pack(side=tk.RIGHT, padx=5)
        
    def create_meals_list(self, parent):
        """Create the meals list."""
        list_frame = ttk.LabelFrame(parent, text="Existing Meals", padding="5")
        list_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Treeview for meals
        columns = ('Name', 'Calories')
        self.meals_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.meals_tree.heading(col, text=col)
            self.meals_tree.column(col, width=200)
            
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.meals_tree.yview)
        self.meals_tree.configure(yscrollcommand=scrollbar.set)
        
        self.meals_tree.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        
        # Bind selection
        self.meals_tree.bind('<Double-1>', self.edit_selected_meal)
        
    def create_add_meal_section(self, parent):
        """Create the add meal section."""
        add_frame = ttk.LabelFrame(parent, text="Add New Meal", padding="5")
        add_frame.pack(fill="x")
        
        # Form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill="x")
        
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Calories (per 100g):").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.calories_var = tk.StringVar()
        calories_entry = ttk.Entry(form_frame, textvariable=self.calories_var, width=10)
        calories_entry.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Button(form_frame, text="Add Meal", command=self.add_meal).grid(row=0, column=4, padx=10, pady=2)
        
    def load_meals(self):
        """Load meals from database."""
        try:
            # Clear existing items
            for item in self.meals_tree.get_children():
                self.meals_tree.delete(item)
                
            # Load meals
            meals = fetch_meal_data()
            for meal in meals:
                self.meals_tree.insert('', 'end', values=(meal[0], meal[1]))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load meals: {str(e)}")
            
    def filter_meals(self):
        """Filter meals based on search."""
        search_text = self.search_var.get().lower()
        
        # Clear existing items
        for item in self.meals_tree.get_children():
            self.meals_tree.delete(item)
            
        # Filter and add meals
        meals = fetch_meal_data()
        for meal in meals:
            if search_text in meal[0].lower():
                self.meals_tree.insert('', 'end', values=(meal[0], meal[1]))
                
    def edit_selected_meal(self, event):
        """Edit the selected meal."""
        selection = self.meals_tree.selection()
        if selection:
            item = self.meals_tree.item(selection[0])
            meal_name = item['values'][0]
            self.edit_meal(meal_name)
            
    def edit_meal(self, meal_name):
        """Edit a specific meal."""
        # Get current meal data
        calories = get_meal_calories(meal_name)
        
        # Create edit dialog
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Edit Meal")
        edit_window.geometry("300x150")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        # Form
        ttk.Label(edit_window, text="Name:").pack(pady=5)
        name_var = tk.StringVar(value=meal_name)
        name_entry = ttk.Entry(edit_window, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="Calories (per 100g):").pack(pady=5)
        calories_var = tk.StringVar(value=str(calories))
        calories_entry = ttk.Entry(edit_window, textvariable=calories_var, width=10)
        calories_entry.pack(pady=5)
        
        def save_meal():
            new_name = name_var.get().strip()
            new_calories = calories_var.get().strip()
            
            if new_name and new_calories.isdigit():
                if edit_meal_in_db(meal_name, new_name, int(new_calories)):
                    messagebox.showinfo("Success", "Meal updated successfully!")
                    edit_window.destroy()
                    self.load_meals()
                    self.app.meal_options = [meal[0] for meal in fetch_meal_data()]
                else:
                    messagebox.showerror("Error", "Failed to update meal!")
            else:
                messagebox.showerror("Error", "Please enter valid data!")
                
        ttk.Button(edit_window, text="Save", command=save_meal).pack(pady=10)
        
    def add_meal(self):
        """Add a new meal."""
        name = self.name_var.get().strip()
        calories = self.calories_var.get().strip()
        
        if name and calories.isdigit():
            if add_new_meal(name, int(calories)):
                messagebox.showinfo("Success", "Meal added successfully!")
                self.name_var.set("")
                self.calories_var.set("")
                self.load_meals()
                self.app.meal_options = [meal[0] for meal in fetch_meal_data()]
            else:
                messagebox.showerror("Error", "Failed to add meal! It may already exist.")
        else:
            messagebox.showerror("Error", "Please enter valid name and calories!")


def main():
    """Main application entry point."""
    root = tk.Tk()
    app = ModernCalorieTracker(root)
    root.mainloop()


if __name__ == '__main__':
    main()
