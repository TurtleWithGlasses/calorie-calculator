from tkcalendar import Calendar
import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, edit_meal_in_db, delete_meal_from_db, add_new_meal, save_daily_calories, fetch_meals_for_date, fetch_meals_from_db
from datetime import datetime


# Function to open the Manage Meals window
def open_manage_meals_window(self):
    manage_meal_window = tk.Toplevel(self.root)
    manage_meal_window.title("Manage Meals")
    manage_meal_window.geometry("400x600")

    # Create a frame to hold the Listbox and the scrollbar
    listbox_frame = tk.Frame(manage_meal_window)
    listbox_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Create a scrollbar for the Listbox
    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # List of existing meals for editing and deleting
    meal_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set)
    meal_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Configure the scrollbar to control the Listbox
    scrollbar.config(command=meal_listbox.yview) 
    # Populate listbox with existing meals
    meal_data = fetch_meal_data()  # Get current meals from DB
    for meal in meal_data:
        meal_listbox.insert(tk.END, f"{meal[0]} - {meal[1]} calories")

    # Meal Name Label and Entry (for adding/editing meals)
    tk.Label(manage_meal_window, text="Meal Name:").pack(pady=5)
    meal_name_entry = tk.Entry(manage_meal_window)
    meal_name_entry.pack(pady=5)

    # Meal Calories Label and Entry (for adding/editing meals)
    tk.Label(manage_meal_window, text="Calories:").pack(pady=5)
    meal_calories_entry = tk.Entry(manage_meal_window)
    meal_calories_entry.pack(pady=5)

    # Add, Edit, and Delete Buttons
    def save_new_meal():
        meal_name = meal_name_entry.get().strip()
        meal_calories = meal_calories_entry.get().strip()
        if meal_name and meal_calories.isdigit():
            add_new_meal(meal_name, int(meal_calories))
            self.refresh_meal_options()
            meal_listbox.insert(tk.END, f"{meal_name} - {meal_calories} calories")
            meal_name_entry.delete(0, tk.END)
            meal_calories_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")

    def edit_meal():
        selected_index = meal_listbox.curselection()
        if selected_index:
            selected_meal = meal_listbox.get(selected_index)
            meal_name, meal_calories = selected_meal.split(" - ")[0], selected_meal.split(" - ")[1].split(" ")[0]
            edit_window = tk.Toplevel(manage_meal_window)
            edit_window.title("Edit Meal")
            edit_window.geometry("300x200")
            
            tk.Label(edit_window, text="Meal Name:").pack(pady=5)
            new_meal_name_entry = tk.Entry(edit_window)
            new_meal_name_entry.pack(pady=5)
            new_meal_name_entry.insert(0, meal_name)

            tk.Label(edit_window, text="Calories:").pack(pady=5)
            new_meal_calories_entry = tk.Entry(edit_window)
            new_meal_calories_entry.pack(pady=5)
            new_meal_calories_entry.insert(0, meal_calories)

            def save_edited_meal():
                new_name = new_meal_name_entry.get().strip()
                new_calories = new_meal_calories_entry.get().strip()

                if new_name and new_calories.isdigit():
                    edit_meal_in_db(meal_name, new_name, int(new_calories))
                    self.refresh_meal_options()
                    meal_listbox.delete(selected_index)
                    meal_listbox.insert(selected_index, f"{new_name} - {new_calories} calories")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")
            
            ok_button = tk.Button(edit_window, text="OK", command=save_edited_meal)
            ok_button.pack(side=tk.LEFT, padx=15, pady=10)
            
            cancel_button = tk.Button(edit_window, text="Cancel", command=edit_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=15, pady=10)

    def delete_meal():
        selected_index = meal_listbox.curselection()
        if selected_index:
            selected_meal = meal_listbox.get(selected_index).split(" - ")[0]
            delete_meal_from_db(selected_meal)
            self.refresh_meal_options()
            meal_listbox.delete(selected_index)

    save_button = tk.Button(manage_meal_window, text="Add Meal", command=save_new_meal)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    edit_button = tk.Button(manage_meal_window, text="Edit Meal", command=edit_meal)
    edit_button.pack(side=tk.LEFT, padx=10, pady=10)

    delete_button = tk.Button(manage_meal_window, text="Delete Meal", command=delete_meal)
    delete_button.pack(side=tk.LEFT, padx=10, pady=10)

def refresh_meal_options(self):
    meal_data = fetch_meal_data()
    self.meal_options = [meal[0] for meal in meal_data]

    for section in self.sections:
        section.meal_options = self.meal_options
        section.refresh_combo_boxes()

def validate_quantity(quantity):
    return quantity.isdigit()

class MealSection:
    def __init__(self, app, root, title, meal_options, row_counter, selected_meal_calories):
        self.app = app
        self.root = root
        self.title = title
        self.meal_options = meal_options
        self.filtered_options = meal_options  # Stores filtered options dynamically
        self.row_counter = row_counter
        self.total_calories = 0
        self.meal_rows = []
        self.selected_meal_calories = selected_meal_calories
        self.empty_row_count = 4

        # Create the section UI
        self.create_section()

    def create_section(self):
        section_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE, padx=10, pady=5)
        section_frame.pack(fill=tk.X, padx=5, pady=5)

        frame_title_label = tk.Label(section_frame, text=self.title, font=("Arial", 12, "bold"))
        frame_title_label.pack(anchor="w", pady=5)

        canvas = tk.Canvas(section_frame)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = tk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.meal_input_frame = tk.Frame(canvas)
        self.meal_input_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.meal_input_frame, anchor="nw")

        self.bind_mouse_wheel(canvas)

        tk.Label(self.meal_input_frame, text="Meal").grid(row=0, column=0, padx=5)
        tk.Label(self.meal_input_frame, text="Quantity (100g)").grid(row=0, column=1, padx=5)
        tk.Label(self.meal_input_frame, text="Total Calories").grid(row=0, column=2, padx=5)

        for _ in range(self.empty_row_count):
            self.add_meal_row()

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        add_more_btn = tk.Button(button_frame, text="Add More", command=self.add_meal_row)
        add_more_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_section)
        reset_btn.pack(side=tk.LEFT, padx=5)

        self.total_calorie_label = tk.Label(button_frame, text="Total: 0", font=("Arial", 10))
        self.total_calorie_label.pack(side=tk.LEFT, padx=5)

    def bind_mouse_wheel(self, widget):
        widget.bind("<Enter>", lambda _: widget.bind_all("<MouseWheel>", self.on_mouse_wheel))
        widget.bind("<Leave>", lambda _: widget.unbind_all("<MouseWheel>"))

    def on_mouse_wheel(self, event):
        widget = event.widget
        if isinstance(widget, tk.Canvas):
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def search_meals_in_db(self, combobox):
        current_text = combobox.get().lower()
        if len(current_text) >= 3:
         try:
             matched_meals = fetch_meals_from_db(current_text)
             combobox['values'] = matched_meals
             combobox.event_generate("<Down>")
         except Exception as e:
             print(f"Error fetching meals: {e}")
    
    def add_meal_row(self):
        row_widgets = {}

        meal_combobox = ttk.Combobox(self.meal_input_frame)
        meal_combobox.grid(row=self.row_counter[0], column=0, padx=5, pady=5)
        row_widgets['meal_combobox'] = meal_combobox

        meal_combobox.bind("<KeyRelease>", lambda e: self.search_meals_in_db(meal_combobox))
        meal_combobox.bind("<Return>", lambda e: self.select_meal_and_close(meal_combobox, row_widgets))

        quantity_entry = tk.Entry(self.meal_input_frame, width=5)
        quantity_entry.grid(row=self.row_counter[0], column=1, padx=5, pady=5)
        row_widgets['quantity_entry'] = quantity_entry

        calories_label = tk.Label(self.meal_input_frame, text="Total Calories: 0")
        calories_label.grid(row=self.row_counter[0], column=2, padx=5, pady=5)
        row_widgets['calories_label'] = calories_label

        delete_btn = tk.Button(self.meal_input_frame, text="Delete", command=lambda: self.delete_meal_row(row_widgets))
        delete_btn.grid(row=self.row_counter[0], column=3, padx=5, pady=5)
        row_widgets['delete_btn'] = delete_btn

        self.meal_rows.append(row_widgets)
        self.row_counter[0] += 1

        meal_combobox.bind("<<ComboboxSelected>>", lambda e: self.on_meal_selected(row_widgets))
        quantity_entry.bind("<KeyRelease>", lambda e: self.update_total_calories(row_widgets))

        self.row_counter[0] += 1

    def add_meal_row_with_data(self, meal_name, grams, calories):
        row_widgets = {}

        meal_combobox = ttk.Combobox(self.meal_input_frame)
        meal_combobox.grid(row=self.row_counter[0], column=0, padx=5, pady=5)
        meal_combobox.set(meal_name)  # Set the predefined meal name
        row_widgets['meal_combobox'] = meal_combobox

        quantity_entry = tk.Entry(self.meal_input_frame, width=5)
        quantity_entry.grid(row=self.row_counter[0], column=1, padx=5, pady=5)
        quantity_entry.insert(0, grams)  # Set the predefined grams
        row_widgets['quantity_entry'] = quantity_entry

        calories_label = tk.Label(self.meal_input_frame, text=f"Total Calories: {int(calories)}")
        calories_label.grid(row=self.row_counter[0], column=2, padx=5, pady=5)
        row_widgets['calories_label'] = calories_label

        delete_btn = tk.Button(self.meal_input_frame, text="Delete", command=lambda: self.delete_meal_row(row_widgets))
        delete_btn.grid(row=self.row_counter[0], column=3, padx=5, pady=5)
        row_widgets['delete_btn'] = delete_btn

        self.meal_rows.append(row_widgets)

        self.total_calories += calories
        self.total_calorie_label.config(text=f"Total: {self.total_calories}")

        self.row_counter[0] += 1

    def update_total_calories(self, row_widgets=None):
        self.total_calories = 0
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            quantity_entry = row['quantity_entry']
            calories_label = row['calories_label']

            meal = meal_combobox.get().strip()
            grams = quantity_entry.get().strip()

            if validate_quantity(grams):
                meal_cal = self.selected_meal_calories.get(meal, 0)
                grams = int(grams)

                calculated_calories = (meal_cal * grams) / 100

                calories_label.config(text=f"Total Calories: {int(calculated_calories)}")
                self.total_calories += calculated_calories

        self.total_calorie_label.config(text=f"Total: {self.total_calories}")
        self.app.update_total_daily_calories()

    def reset_section(self):
        # Remove all widgets associated with each row
        for row in self.meal_rows:
            for widget in row.values():
                widget.grid_forget()  # Remove widget from the grid layout

        # Clear the meal rows list and reset total calories
        self.meal_rows.clear()
        self.total_calories = 0
        self.total_calorie_label.config(text="")

    def on_meal_selected(self, row_widgets):
        meal_combobox = row_widgets['meal_combobox']
        meal = meal_combobox.get().strip()
        if meal:
            meal_calories = get_meal_calories(meal)
            self.selected_meal_calories[meal] = meal_calories
            # Optionally update the calories label
            self.update_total_calories(row_widgets)

    def count_empty_rows(self):
        empty_rows = 0
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            quantity_entry = row['quantity_entry']
            
            meal = meal_combobox.get().strip()
            quantity = quantity_entry.get().strip()

            if not meal and not quantity:  # If both are empty, consider the row empty
                empty_rows += 1
        return empty_rows

    def load_calories_for_date(self):
        if self.selected_date:
            # Track the number of empty rows before resetting
            num_empty_rows = self.sections[0].count_empty_rows()

            # Fetch meals for the selected date from the database
            meals_for_date = fetch_meals_for_date(self.selected_date)
            
            # Reset all sections (clear existing rows)
            for section in self.sections:
                section.reset_section()

            # Add meals from the database for the selected date
            for meal_name, grams, calories in meals_for_date:
                self.sections[0].add_meal_row_with_data(meal_name, grams, calories)

            # Add back the number of empty rows previously tracked
            for _ in range(num_empty_rows):
                self.sections[0].add_meal_row()

            # Update the total daily calories based on the loaded meals
            self.update_total_daily_calories()

    def set_empty_rows_count(self, count):
        # Set the number of empty rows to be used when reloading the date
        self.empty_rows_count = count

class MealCalorieTrackerApp:
    def __init__(self, root):
        self.root = root
        self.total_daily_calories = 0
        self.sections = []
        self.selected_meal_calories = {}
        self.selected_date = datetime.now().strftime("%Y-%m-%d")

        init_db()
        meal_data = fetch_meal_data()
        self.meal_options = [meal[0] for meal in meal_data]

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.select_date_btn = tk.Button(top_frame, text=f"Select Date: {self.selected_date}", command=self.open_calendar)
        self.select_date_btn.pack(side=tk.LEFT, padx=10)

        self.current_date_time_label = tk.Label(top_frame, text="", font=("Arial", 12))
        self.current_date_time_label.pack(side=tk.LEFT, padx=10)

        manage_meal_btn = tk.Button(top_frame, text="Manage Meals", command=self.open_manage_meals_window)
        manage_meal_btn.pack(side=tk.RIGHT, padx=10)

        self.create_section("09:00 AM - 12:00 PM")
        self.create_section("12:00 PM - 06:00 PM")
        self.create_section("06:00 PM - 12:00 AM")

        self.total_calories_label = tk.Label(self.root, text="Total Calories for Today: 0", font=("Arial", 12))
        self.total_calories_label.pack()

        self.update_date_time()

    def open_calendar(self):
        self.cal_win = tk.Toplevel(self.root)
        self.cal_win.title("Select Date")

        cal = Calendar(self.cal_win, selectmode="day", year=2024, month=9, day=15)
        cal.pack(pady=20)

        def on_date_selected():
            self.selected_date = cal.get_date()

            self.selected_date = datetime.strptime(self.selected_date, "%m/%d/%y").strftime("%Y-%m-%d")
            self.select_date_btn.config(text=f"Selected Date: {self.selected_date}")
            self.cal_win.destroy()

            self.load_calories_for_date()

        select_btn = tk.Button(self.cal_win, text="Select", command=on_date_selected)
        select_btn.pack(pady=10)

    def load_calories_for_date(self):
        if self.selected_date:
            # Fetch meals for the selected date from the database
            meals_for_date = fetch_meals_for_date(self.selected_date)
            
            # Track the number of empty rows before resetting
            num_empty_rows = self.sections[0].count_empty_rows()

            # Reset all sections (clear existing rows)
            for section in self.sections:
                section.reset_section()

            # Add meals from the database for the selected date
            for meal_name, grams, calories in meals_for_date:
                self.sections[0].add_meal_row_with_data(meal_name, grams, calories)

            # Re-add the previously tracked number of empty rows
            self.sections[0].set_empty_rows_count(num_empty_rows)
            for _ in range(num_empty_rows):
                self.sections[0].add_meal_row()

            # Update the total daily calories based on the loaded meals
            self.update_total_daily_calories()

    def update_total_daily_calories(self):
        total_daily_calories = 0
        meals_for_date = []

        for section in self.sections:
            for row in section.meal_rows:
                meal_combobox = row['meal_combobox']
                quantity_entry = row['quantity_entry']
                calories_label = row['calories_label']

                meal = meal_combobox.get().strip()
                grams = quantity_entry.get().strip()

                if validate_quantity(grams):
                    grams = int(grams)
                    calories = float(calories_label.cget("text").replace("Total Calories: ", ""))

                    meals_for_date.append((self.selected_date, meal, grams, calories))
                    total_daily_calories += calories

        self.total_calories_label.config(text=f"Total Calories for {self.selected_date}: {total_daily_calories}")
        save_daily_calories(self.selected_date, total_daily_calories, meals_for_date)

    def update_date_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d\n%H:%M:%S")
        self.current_date_time_label.config(text=f"{current_time}")
        self.root.after(1000, self.update_date_time)

    def open_manage_meals_window(self):
        open_manage_meals_window(self)

    def refresh_meal_options(self):
        meal_data = fetch_meal_data()
        self.meal_options = [meal[0] for meal in meal_data]
        for section in self.sections:
            section.meal_options = self.meal_options
            section.refresh_combo_boxes()

    def create_section(self, title):
        row_counter = [1]
        section = MealSection(self, self.root, title, self.meal_options, row_counter, self.selected_meal_calories)
        self.sections.append(section)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meal Calorie Tracker")
    root.geometry("500x1200")

    app = MealCalorieTrackerApp(root)
    root.mainloop()
