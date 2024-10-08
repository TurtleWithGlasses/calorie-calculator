from tkcalendar import Calendar
import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, edit_meal_in_db, delete_meal_from_db, add_new_meal, save_daily_calories, fetch_meals_for_date, fetch_meals_from_db
from datetime import datetime


# Function to open the Manage Meals window
def open_manage_meals_window(self):
    print("open_manage_meals_window is running")
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
    print(f"Meal data fetched: {meal_data}")
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
        print("save_new_meal is running")
        meal_name = meal_name_entry.get().strip()
        meal_calories = meal_calories_entry.get().strip()
        if meal_name and meal_calories.isdigit():
            print(f"Adding new meal: {meal_name} with {meal_calories} calories")
            add_new_meal(meal_name, int(meal_calories))
            self.refresh_meal_options()
            meal_listbox.insert(tk.END, f"{meal_name} - {meal_calories} calories")
            meal_name_entry.delete(0, tk.END)
            meal_calories_entry.delete(0, tk.END)
        else:
            print("Input error: Meal name or calorie count is invalid")
            messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")

    def edit_meal():
        print("edit_meal is running")
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
                print(f"save_edited_meal is running for {meal_name}")
                new_name = new_meal_name_entry.get().strip()
                new_calories = new_meal_calories_entry.get().strip()

                if new_name and new_calories.isdigit():
                    print(f"Editing meal to: {new_name} with {new_calories} calories")
                    edit_meal_in_db(meal_name, new_name, int(new_calories))
                    self.refresh_meal_options()
                    meal_listbox.delete(selected_index)
                    meal_listbox.insert(selected_index, f"{new_name} - {new_calories} calories")
                    edit_window.destroy()
                else:
                    print("Input error: Meal name or calorie count is invalid")
                    messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")
            
            ok_button = tk.Button(edit_window, text="OK", command=save_edited_meal)
            ok_button.pack(side=tk.LEFT, padx=15, pady=10)
            
            cancel_button = tk.Button(edit_window, text="Cancel", command=edit_window.destroy)
            cancel_button.pack(side=tk.RIGHT, padx=15, pady=10)

    def delete_meal():
        print("delete_meal is running")
        selected_index = meal_listbox.curselection()
        if selected_index:
            selected_meal = meal_listbox.get(selected_index).split(" - ")[0]
            print(f"Deleting meal: {selected_meal}")
            delete_meal_from_db(selected_meal)
            self.refresh_meal_options()
            meal_listbox.delete(selected_index)
        else:
            print("No meal selected for deletion")

    save_button = tk.Button(manage_meal_window, text="Add Meal", command=save_new_meal)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    edit_button = tk.Button(manage_meal_window, text="Edit Meal", command=edit_meal)
    edit_button.pack(side=tk.LEFT, padx=10, pady=10)

    delete_button = tk.Button(manage_meal_window, text="Delete Meal", command=delete_meal)
    delete_button.pack(side=tk.LEFT, padx=10, pady=10)

def refresh_meal_options(self):
    print("refresh_meal_options is running")
    meal_data = fetch_meal_data()
    print(f"Meal data refreshed: {meal_data}")
    self.meal_options = [meal[0] for meal in meal_data]

    for section in self.sections:
        section.meal_options = self.meal_options
        section.refresh_combo_boxes()

def validate_quantity(quantity):
    print(f"validate_quantity is running: {quantity}")
    return quantity.isdigit()

class MealSection:
    def __init__(self, app, root, title, meal_options, row_counter, selected_meal_calories, section_index):
        print(f"MealSection initialized for {title} with section index {section_index}")
        self.app = app
        self.root = root
        self.title = title
        self.meal_options = meal_options
        self.filtered_options = meal_options  # Stores filtered options dynamically
        self.row_counter = row_counter
        self.total_calories = 0
        self.meal_rows = []
        self.selected_meal_calories = selected_meal_calories
        self.section_index = section_index
        self.empty_row_count = 4

        # Create the section UI
        self.create_section()

    def create_section(self):
        print(f"Creating section for {self.title}")
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

        # self.total_calorie_label = tk.Label(button_frame, text="Total: 0", font=("Arial", 10))
        # self.total_calorie_label.pack(side=tk.LEFT, padx=5)

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
                print(f"Searching meals in db for: {current_text}")
                matched_meals = fetch_meals_from_db(current_text)
                print(f"Matched meals: {matched_meals}")
                combobox['values'] = matched_meals
                combobox.event_generate("<Down>")
            except Exception as e:
                print(f"Error fetching meals: {e}")
    
    def add_meal_row(self):
        print("Adding meal row")
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

    def delete_meal_row(self, row_widgets):
        print("delete_meal_row is running")
        for widget in row_widgets.values():
            widget.grid_forget()

        self.meal_rows.remove(row_widgets)
        self.update_total_calories()

    def add_meal_row_with_data(self, meal_name, grams, total_calories):
        print(f"Adding meal row with data: {meal_name}, {grams}, {total_calories}")
        row_widgets = {}

        meal_combobox = ttk.Combobox(self.meal_input_frame)
        meal_combobox.grid(row=self.row_counter[0], column=0, padx=5, pady=5)
        meal_combobox.set(meal_name)
        row_widgets['meal_combobox'] = meal_combobox

        quantity_entry = tk.Entry(self.meal_input_frame, width=5)
        quantity_entry.grid(row=self.row_counter[0], column=1, padx=5, pady=5)
        quantity_entry.insert(0, grams)
        row_widgets['quantity_entry'] = quantity_entry

        calories_label = tk.Label(self.meal_input_frame, text=f"Total Calories: {int(total_calories)}")
        calories_label.grid(row=self.row_counter[0], column=2, padx=5, pady=5)
        row_widgets['calories_label'] = calories_label

        delete_btn = tk.Button(self.meal_input_frame, text="Delete", command=lambda: self.delete_meal_row(row_widgets))
        delete_btn.grid(row=self.row_counter[0], column=3, padx=5, pady=5)
        row_widgets['delete_btn'] = delete_btn

        self.meal_rows.append(row_widgets)

        # self.total_calories += total_calories
        # self.total_calorie_label.config(text=f"Total: {self.total_calories}")

        self.row_counter[0] += 1

    def update_total_calories(self, row_widgets=None):
        print("update_total_calories is running")
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

        self.app.update_total_daily_calories()

    def update_total_daily_calories(self):
        print(f"update_total_daily_calories is running for {self.app.selected_date}")
        total_daily_calories = 0
        meals_for_date = []

        for section in self.app.sections:
            section_index = section.section_index

            for row in section.meal_rows:
                meal_combobox = row['meal_combobox']
                quantity_entry = row['quantity_entry']
                calories_label = row['calories_label']

                meal = meal_combobox.get().strip()
                grams = quantity_entry.get().strip()

                if validate_quantity(grams):
                    grams = int(grams)
                    calories = float(calories_label.cget("text").replace("Total Calories: ", ""))
                    meals_for_date.append((self.app.selected_date, meal, grams, calories, section_index))
                    total_daily_calories += calories
                    print(f"Meals being saved: {meals_for_date}")

        self.app.total_calories_label.config(text=f"Total Calories for {self.app.selected_date}: {total_daily_calories}")
        save_daily_calories(self.app.selected_date, total_daily_calories, meals_for_date)

    def reset_section(self):
        print(f"reset_section is running for {self.title}")
        for row in self.meal_rows:
            for widget in row.values():
                widget.grid_forget()

        self.meal_rows.clear()
        self.total_calories = 0
        # self.total_calorie_label.config(text="")

    def on_meal_selected(self, row_widgets):
        print("on_meal_selected is running")
        meal_combobox = row_widgets['meal_combobox']
        meal = meal_combobox.get().strip()
        if meal:
            meal_calories = get_meal_calories(meal)
            print(f"Meal selected: {meal} with {meal_calories} calories")
            self.selected_meal_calories[meal] = meal_calories
            self.update_total_calories(row_widgets)

    def count_empty_rows(self):
        print("count_empty_rows is running")
        empty_rows = 0
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            quantity_entry = row['quantity_entry']
            
            meal = meal_combobox.get().strip()
            quantity = quantity_entry.get().strip()

            if not meal and not quantity:
                empty_rows += 1
        print(f"Empty rows counted: {empty_rows}")
        return empty_rows

    def load_calories_for_date(self):
        print(f"Loading meals for date: {self.app.selected_date}")
        num_empty_rows = self.count_empty_rows()

        meals_for_date = fetch_meals_for_date(self.app.selected_date)
        print(f"Fetched meals: {meals_for_date}")

        for section in self.app.sections:
            section.reset_section()

        for meal_name, grams, calories, section_index in meals_for_date:
            self.app.sections[section_index].add_meal_row_with_data(meal_name, grams, calories)

        for _ in range(num_empty_rows):
            self.app.sections[0].add_meal_row()

        self.app.update_total_daily_calories()

class MealCalorieTrackerApp:
    def __init__(self, root):
        print("MealCalorieTrackerApp initialized")
        self.root = root
        self.total_daily_calories = 0
        self.sections = []
        self.selected_meal_calories = {}
        self.selected_date = datetime.now().strftime("%Y-%m-%d")

        init_db()
        meal_data = fetch_meal_data()
        self.meal_options = [meal[0] for meal in meal_data]
        print(f"Meal options initialized: {self.meal_options}")

        self.setup_ui()
        self.load_calories_for_date()

    def setup_ui(self):
        print("Setting up UI")
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.select_date_btn = tk.Button(top_frame, text=f"Select Date: {self.selected_date}", command=self.open_calendar)
        self.select_date_btn.pack(side=tk.LEFT, padx=10)

        self.current_date_time_label = tk.Label(top_frame, text="", font=("Arial", 12))
        self.current_date_time_label.pack(side=tk.LEFT, padx=10)

        manage_meal_btn = tk.Button(top_frame, text="Manage Meals", command=self.open_manage_meals_window)
        manage_meal_btn.pack(side=tk.RIGHT, padx=10)

        self.create_section("09:00 AM - 12:00 PM", 0)
        self.create_section("12:00 PM - 06:00 PM", 1)
        self.create_section("06:00 PM - 12:00 AM", 2)

        self.total_calories_label = tk.Label(self.root, text="Total Calories for Today: 0", font=("Arial", 12))
        self.total_calories_label.pack(side=tk.LEFT, padx=10)

        self.update_date_time()

    def open_calendar(self):
        self.cal_win = tk.Toplevel(self.root)
        self.cal_win.title("Select Date")

        current_date = datetime.strptime(self.selected_date, "%Y-%m-%d")

        today_date = datetime.today()

        cal = Calendar(self.cal_win, selectmode="day", year=current_date.year, month=current_date.month, day=current_date.day)
        cal.pack(pady=20)

        cal.calevent_create(today_date, 'Today', 'today')
        cal.tag_config('today', background='gray', foreground='white')

        def on_date_selected():
            print("Date selected from calendar")
            self.selected_date = cal.get_date()
            self.selected_date = datetime.strptime(self.selected_date, "%m/%d/%y").strftime("%Y-%m-%d")
            self.select_date_btn.config(text=f"Selected Date: {self.selected_date}")
            self.cal_win.destroy()
            self.load_calories_for_date()

        select_btn = tk.Button(self.cal_win, text="Select", command=on_date_selected)
        select_btn.pack(pady=10)

    def load_calories_for_date(self):
        print(f"load_calories_for_date is running for {self.selected_date}")
        meals_for_date = fetch_meals_for_date(self.selected_date)
        print(f"Fetched meals for {self.selected_date}: {meals_for_date}")

        for section in self.sections:
            section.reset_section()

        for meal_name, grams, calories, section_index in meals_for_date:
            self.sections[section_index].add_meal_row_with_data(meal_name, grams, calories)

        self.update_total_daily_calories()

    def update_total_daily_calories(self):
        print(f"update_total_daily_calories is running for {self.selected_date}")
        total_daily_calories = 0
        meals_for_date = []

        for section_index, section in enumerate(self.sections):
            for row in section.meal_rows:
                meal_combobox = row['meal_combobox']
                quantity_entry = row['quantity_entry']
                calories_label = row['calories_label']

                meal = meal_combobox.get().strip()
                grams = quantity_entry.get().strip()

                if validate_quantity(grams):
                    grams = int(grams)
                    calories = float(calories_label.cget("text").replace("Total Calories: ", ""))
                    meals_for_date.append((self.selected_date, meal, grams, calories, section_index))
                    total_daily_calories += calories

        print(f"Total daily calories for {self.selected_date}: {total_daily_calories}")
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
        print(f"Meal options refreshed: {self.meal_options}")
        for section in self.sections:
            section.meal_options = self.meal_options
            section.refresh_combo_boxes()

    def create_section(self, title, section_index):
        print(f"Creating section: {title}")
        row_counter = [1]
        section = MealSection(self, self.root, title, self.meal_options, row_counter, self.selected_meal_calories, section_index)
        self.sections.append(section)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meal Calorie Tracker")
    root.geometry("500x1200")

    app = MealCalorieTrackerApp(root)
    root.mainloop()
