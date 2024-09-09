import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, add_new_meal

# Function to open the Add Meal window
def open_add_meal_window(self):
    # Create a new window
    add_meal_window = tk.Toplevel(self.root)
    add_meal_window.title("Add New Meal")
    add_meal_window.geometry("300x200")

    # Meal Name Label and Entry
    tk.Label(add_meal_window, text="Meal Name:").pack(pady=5)
    meal_name_entry = tk.Entry(add_meal_window)
    meal_name_entry.pack(pady=5)

    # Meal Calories Label and Entry
    tk.Label(add_meal_window, text="Calories:").pack(pady=5)
    meal_calories_entry = tk.Entry(add_meal_window)
    meal_calories_entry.pack(pady=5)

    # Save Button
    def save_new_meal():
        meal_name = meal_name_entry.get().strip()
        meal_calories = meal_calories_entry.get().strip()

        # Validate the inputs
        if meal_name == "" or not meal_calories.isdigit():
            messagebox.showerror("Input Error", "Please enter a valida meal name and calorie count.")
            return
        
        # Add meal to the database
        add_new_meal(meal_name, int(meal_calories)) #Assuming that we have a function that adds the meal to the database

        # Update the combo boxes in the main app
        self.refresh_meal_options()

        # Close the add meal window
        add_meal_window.destroy()
    
    save_button = tk.Button(add_meal_window, text="Save", command=save_new_meal)
    save_button.pack(pady=10)

# Function to refresh the meal options in combo boxes after adding a new meal
def refresh_meal_options(self):
    # Fetch the updated meal data
    meal_data = fetch_meal_data()
    self.meal_options = [meal[0] for meal in meal_data]  # Extract meal names

    # Refresh the combo boxes for all sections
    for section in self.sections:
        section.meal_options = self.meal_options  # Update meal options in the section
        section.refresh_combo_boxes()  # Call the method to refresh combo boxes



# Validation function to check meal and quantity
def validate_meal_and_quantity(meal, quantity):
    if not meal:
        print("Meal is not selected or invalid")
        return False
    if not quantity.isdigit():
        print("Quantity is not valid")
        return False
    print("Meals and quantity are valid.")
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
        # Main Frame for the section (Frame 1, Frame 2, Frame 3)
        section_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE, padx=10, pady=5)
        section_frame.pack(fill=tk.X, padx=5, pady=5)

        # Title for the section
        frame_title_label = tk.Label(section_frame, text=self.title, font=("Arial", 12, "bold"))
        frame_title_label.pack(anchor="w", pady=5)

        # Create canvas for scrolling
        canvas = tk.Canvas(section_frame)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # Scrollbar for the canvas
        scrollbar = tk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the meal rows
        self.meal_input_frame = tk.Frame(canvas)
        self.meal_input_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.meal_input_frame, anchor="nw")

        # Bind the mouse wheel to the canvas scroll event
        self.bind_mouse_wheel(canvas)

        tk.Label(self.meal_input_frame, text="Meal").grid(row=0, column=0, padx=5)
        tk.Label(self.meal_input_frame, text="Quantity").grid(row=0, column=1, padx=5)
        tk.Label(self.meal_input_frame, text="Total Calories").grid(row=0, column=2, padx=5)

        # Add initial meal rows
        for _ in range(3):
            self.add_meal_row()

        # Frame for "Add More", "Reset", and total calories, placed **after** meal rows
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        add_more_btn = tk.Button(button_frame, text="Add More", command=self.add_meal_row)
        add_more_btn.pack(side=tk.LEFT, padx=5)

        reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_section)
        reset_btn.pack(side=tk.LEFT, padx=5)

        # Total calories label for the section
        self.total_calorie_label = tk.Label(button_frame, text="Total: 0", font=("Arial", 10))
        self.total_calorie_label.pack(side=tk.LEFT, padx=5)

    def add_meal_row(self):
        row_widgets = {}

        # Meal selection (ComboBox)
        meal_combobox = ttk.Combobox(self.meal_input_frame, values=self.meal_options)
        meal_combobox.grid(row=self.row_counter[0], column=0, padx=5, pady=5)
        row_widgets['meal_combobox'] = meal_combobox

        # Quantity input (Entry)
        quantity_entry = tk.Entry(self.meal_input_frame, width=5)
        quantity_entry.grid(row=self.row_counter[0], column=1, padx=5, pady=5)
        row_widgets['quantity_entry'] = quantity_entry

        # Calories label (to be updated dynamically)
        calories_label = tk.Label(self.meal_input_frame, text="Total Calories: 0")
        calories_label.grid(row=self.row_counter[0], column=2, padx=5, pady=5)
        row_widgets['calories_label'] = calories_label

        # Delete button to remove the row
        delete_btn = tk.Button(self.meal_input_frame, text="Delete", command=lambda: self.delete_meal_row(row_widgets))
        delete_btn.grid(row=self.row_counter[0], column=3, padx=5, pady=5)
        row_widgets['delete_btn'] = delete_btn

        # Add this row's widgets to the list of rows
        self.meal_rows.append(row_widgets)

        # Event to handle meal selection and fetch calories
        meal_combobox.bind("<<ComboboxSelected>>", lambda e: self.on_meal_selected(row_widgets))

        # Event to handle quantity entry and update total calories
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
        # Remove widgets from the grid
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
            print(f"Selected {meal}, Calories fetched: {meal_calories}")

    def update_total_calories(self, row_widgets=None):
        self.total_calories = 0  # Reset section total calories
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            quantity_entry = row['quantity_entry']
            calories_label = row['calories_label']

            meal = meal_combobox.get().strip()
            quantity = quantity_entry.get().strip()

            if validate_meal_and_quantity(meal, quantity):
                meal_cal = self.selected_meal_calories.get(meal, 0) * int(quantity)
                calories_label.config(text=f"Total Calories: {meal_cal}")
                self.total_calories += meal_cal

        self.total_calorie_label.config(text=f"Total: {self.total_calories}")
        self.app.update_total_daily_calories()  # Update the total calories in the main app

    def reset_section(self):
        # Reset all rows
        for row in self.meal_rows:
            for widget in row.values():
                if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
                    widget.delete(0, tk.END)
                elif isinstance(widget, tk.Label) and "Total Calories" in widget.cget("text"):
                    widget.config(text="Total Calories: 0")

        self.total_calories = 0
        self.total_calorie_label.config(text="Total: 0")
    
    def refresh_combo_boxes(self):
        """Refresh the meal options in the combo boxes for this section."""
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            meal_combobox.config(values=self.meal_options)  # Update meal options


class MealCalorieTrackerApp:
    def __init__(self, root):
        self.root = root
        self.total_daily_calories = 0
        self.sections = []  # Store all meal sections
        self.selected_meal_calories = {}  # Store meal calorie data for each selected meal

        # Initialize the database
        init_db()

        # Fetch meal options from the database
        meal_data = fetch_meal_data()
        self.meal_options = [meal[0] for meal in meal_data]

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        select_date_btn = tk.Button(top_frame, text="Select Date")
        select_date_btn.pack(side=tk.LEFT, padx=10)

        current_date_time_label = tk.Label(top_frame, text="Current date & time")
        current_date_time_label.pack(side=tk.LEFT, padx=10)

        add_meal_btn = tk.Button(top_frame, text="Add Meal", command=self.open_add_meal_window)
        add_meal_btn.pack(side=tk.RIGHT, padx=10)

        # Sections for different times of the day
        self.create_section("09:00 AM - 12:00 PM")
        self.create_section("12:00 PM - 06:00 PM")
        self.create_section("06:00 PM - 12:00 AM")

        self.total_calories_label = tk.Label(self.root, text="Total Calories for Today: 0", font=("Arial", 12))
        self.total_calories_label.pack()

    def create_section(self, title):
        row_counter = [1]  # Use list to allow mutability across methods
        section = MealSection(self, self.root, title, self.meal_options, row_counter, self.selected_meal_calories)
        self.sections.append(section)

    def update_total_daily_calories(self):
        total_daily_calories = sum(section.total_calories for section in self.sections)
        self.total_calories_label.config(text=f"Total Calories for Today: {total_daily_calories}")

    def open_add_meal_window(self):
        # Implementation to add a new meal (similar to the original logic)
        open_add_meal_window(self)
    
    def refresh_meal_options(self):
        refresh_meal_options(self)
    
    def refresh_combo_boxes(self):
        for row in self.meal_rows:
            meal_combobox = row['meal_combobox']
            meal_combobox.config(values=self.meal_options)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meal Calorie Tracker")
    root.geometry("440x1200")

    app = MealCalorieTrackerApp(root)
    root.mainloop()
