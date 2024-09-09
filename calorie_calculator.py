import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, edit_meal_in_db, delete_meal_from_db, add_new_meal

# Function to open the Manage Meals window
def open_manage_meals_window(self):
    manage_meal_window = tk.Toplevel(self.root)
    manage_meal_window.title("Manage Meals")
    manage_meal_window.geometry("400x600")

    # List of existing meals for editing and deleting
    meal_listbox = tk.Listbox(manage_meal_window)
    meal_listbox.pack(pady=10, fill=tk.BOTH, expand=True)
    
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
            # Extract the meal name and calories
            selected_meal = meal_listbox.get(selected_index)
            meal_name, meal_calories = selected_meal.split(" - ")[0], selected_meal.split(" - ")[1].split(" ")[0]
            
            # Open a new window for editing
            edit_window = tk.Toplevel(manage_meal_window)
            edit_window.title("Edit Meal")
            edit_window.geometry("300x200")
            
            # Meal Name Label and Entry
            tk.Label(edit_window, text="Meal Name:").pack(pady=5)
            new_meal_name_entry = tk.Entry(edit_window)
            new_meal_name_entry.pack(pady=5)
            new_meal_name_entry.insert(0, meal_name)

            # Meal Calories Label and Entry
            tk.Label(edit_window, text="Calories:").pack(pady=5)
            new_meal_calories_entry = tk.Entry(edit_window)
            new_meal_calories_entry.pack(pady=5)
            new_meal_calories_entry.insert(0, meal_calories)

            # OK button to save changes
            def save_edited_meal():
                new_name = new_meal_name_entry.get().strip()
                new_calories = new_meal_calories_entry.get().strip()

                # Validate input and update meal in the database
                if new_name and new_calories.isdigit():
                    edit_meal_in_db(meal_name, new_name, int(new_calories))
                    self.refresh_meal_options()
                    meal_listbox.delete(selected_index)
                    meal_listbox.insert(selected_index, f"{new_name} - {new_calories} calories")
                    edit_window.destroy()
                else:
                    messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")
            
            # Cancel button to discard changes
            def cancel_edit():
                edit_window.destroy()

            # Buttons for OK and Cancel
            ok_button = tk.Button(edit_window, text="OK", command=save_edited_meal)
            ok_button.pack(side=tk.LEFT, padx=10, pady=10)
            
            cancel_button = tk.Button(edit_window, text="Cancel", command=cancel_edit)
            cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def delete_meal():
        selected_index = meal_listbox.curselection()
        if selected_index:
            selected_meal = meal_listbox.get(selected_index).split(" - ")[0]
            delete_meal_from_db(selected_meal)  # Delete meal from DB
            self.refresh_meal_options()
            meal_listbox.delete(selected_index)

    # Buttons for Adding, Editing, and Deleting
    save_button = tk.Button(manage_meal_window, text="Add Meal", command=save_new_meal)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    edit_button = tk.Button(manage_meal_window, text="Edit Meal", command=edit_meal)
    edit_button.pack(side=tk.LEFT, padx=10, pady=10)

    delete_button = tk.Button(manage_meal_window, text="Delete Meal", command=delete_meal)
    delete_button.pack(side=tk.LEFT, padx=10, pady=10)

# Function to refresh the meal options in combo boxes after adding a new meal
def refresh_meal_options(self):
    meal_data = fetch_meal_data()
    self.meal_options = [meal[0] for meal in meal_data]

    # Refresh the combo boxes for all sections
    for section in self.sections:
        section.meal_options = self.meal_options  # Update meal options in the section
        section.refresh_combo_boxes()

# Validation function to check quantity (since meal is now a combo box)
def validate_quantity(quantity):
    if not quantity.isdigit():
        return False
    return True


class MealSection:
    def __init__(self, app, root, title, meal_options, row_counter, selected_meal_calories):
        self.app = app
        self.root = root
        self.title = title
        self.meal_options = meal_options
        self.row_counter = row_counter
        self.total_calories = 0
        self.meal_rows = []
        self.selected_meal_calories = selected_meal_calories

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
        tk.Label(self.meal_input_frame, text="Quantity").grid(row=0, column=1, padx=5)
        tk.Label(self.meal_input_frame, text="Total Calories").grid(row=0, column=2, padx=5)

        for _ in range(3):
            self.add_meal_row()

        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        add_more_btn = tk.Button(button_frame, text="Add More", command=self.add_meal_row)
        add_more_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_section)
        reset_btn.pack(side=tk.LEFT, padx=5)

        self.total_calorie_label = tk.Label(button_frame, text="Total: 0", font=("Arial", 10))
        self.total_calorie_label.pack(side=tk.LEFT, padx=5)

    def add_meal_row(self):
        row_widgets = {}

        meal_combobox = ttk.Combobox(self.meal_input_frame, values=self.meal_options)
        meal_combobox.grid(row=self.row_counter[0], column=0, padx=5, pady=5)
        row_widgets['meal_combobox'] = meal_combobox

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

        meal_combobox.bind("<<ComboboxSelected>>", lambda e: self.on_meal_selected(row_widgets))
        quantity_entry.bind("<KeyRelease>", lambda e: self.update_total_calories(row_widgets))

        self.row_counter[0] += 1

    def bind_mouse_wheel(self, widget):
        widget.bind("<Enter>", lambda _: widget.bind_all("<MouseWheel>", self.on_mouse_wheel))
        widget.bind("<Leave>", lambda _: widget.unbind_all("<MouseWheel>"))
    
    def on_mouse_wheel(self, event):
        widget = event.widget
        if isinstance(widget, tk.Canvas):
            widget.yview_scroll(int(-1*(event.delta/120)), "units")

    def delete_meal_row(self, row_widgets):
        for widget in row_widgets.values():
            widget.grid_forget()
        self.meal_rows.remove(row_widgets)
        self.update_total_calories()

    def on_meal_selected(self, row_widgets):
        meal_combobox = row_widgets['meal_combobox']
        meal = meal_combobox.get().strip()
        if meal:
            meal_calories = get_meal_calories(meal)
            self.selected_meal_calories[meal] = meal_calories

    def update_total_calories(self, row_widgets=None):
        self.total_calories = 0
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            quantity_entry = row['quantity_entry']
            calories_label = row['calories_label']

            meal = meal_combobox.get().strip()
            quantity = quantity_entry.get().strip()

            if validate_quantity(quantity):
                meal_cal = self.selected_meal_calories.get(meal, 0) * int(quantity)
                calories_label.config(text=f"Total Calories: {meal_cal}")
                self.total_calories += meal_cal

        self.total_calorie_label.config(text=f"Total: {self.total_calories}")
        self.app.update_total_daily_calories()

    def reset_section(self):
        for row in self.meal_rows:
            for widget in row.values():
                if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
                    widget.delete(0, tk.END)
                elif isinstance(widget, tk.Label) and "Total Calories" in widget.cget("text"):
                    widget.config(text="Total Calories: 0")

        self.total_calories = 0
        self.total_calorie_label.config(text="Total: 0")
    
    def refresh_combo_boxes(self):
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            meal_combobox.config(values=self.meal_options)


class MealCalorieTrackerApp:
    def __init__(self, root):
        self.root = root
        self.total_daily_calories = 0
        self.sections = []
        self.selected_meal_calories = {}

        init_db()
        meal_data = fetch_meal_data()
        self.meal_options = [meal[0] for meal in meal_data]

        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        select_date_btn = tk.Button(top_frame, text="Select Date")
        select_date_btn.pack(side=tk.LEFT, padx=10)

        current_date_time_label = tk.Label(top_frame, text="Current date & time")
        current_date_time_label.pack(side=tk.LEFT, padx=10)

        manage_meal_btn = tk.Button(top_frame, text="Manage Meals", command=self.open_manage_meals_window)
        manage_meal_btn.pack(side=tk.RIGHT, padx=10)

        self.create_section("09:00 AM - 12:00 PM")
        self.create_section("12:00 PM - 06:00 PM")
        self.create_section("06:00 PM - 12:00 AM")

        self.total_calories_label = tk.Label(self.root, text="Total Calories for Today: 0", font=("Arial", 12))
        self.total_calories_label.pack()

    def create_section(self, title):
        row_counter = [1]
        section = MealSection(self, self.root, title, self.meal_options, row_counter, self.selected_meal_calories)
        self.sections.append(section)

    def update_total_daily_calories(self):
        total_daily_calories = sum(section.total_calories for section in self.sections)
        self.total_calories_label.config(text=f"Total Calories for Today: {total_daily_calories}")

    def open_manage_meals_window(self):
        open_manage_meals_window(self)
    
    def refresh_meal_options(self):
        refresh_meal_options(self)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meal Calorie Tracker")
    root.geometry("440x1200")

    app = MealCalorieTrackerApp(root)
    root.mainloop()
