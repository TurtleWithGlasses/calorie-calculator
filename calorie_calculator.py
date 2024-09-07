import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, add_new_meal

class MealSection:
    def __init__(self, root, title, meal_options, row_counter):
        self.root = root
        self.title = title
        self.meal_options = meal_options
        self.row_counter = row_counter
        self.total_calories = 0
        self.meal_rows = []

        # Create the section UI
        self.create_section()

    def create_section(self):
        # Create a frame with a thin border
        section_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        section_frame.pack(fill=tk.X, padx=5, pady=5)

        # Canvas for scrollable content
        canvas = tk.Canvas(section_frame)
        canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(section_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Configure canvas scroll
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        frame_title_label = tk.Label(self.inner_frame, text=self.title)
        frame_title_label.grid(row=0, column=0, columnspan=4, pady=10)

        self.meal_input_frame = tk.Frame(self.inner_frame)
        self.meal_input_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=5)

        tk.Label(self.meal_input_frame, text="Meal").grid(row=0, column=0)
        tk.Label(self.meal_input_frame, text="Quantity").grid(row=0, column=1)
        tk.Label(self.meal_input_frame, text="Total Calories").grid(row=0, column=2)

        # Add initial meal rows
        for _ in range(3):
            self.add_meal_row()

        # Buttons and total in a separate frame (below meal entries)
        button_frame = tk.Frame(self.inner_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        # Total calories label for the section
        self.total_calorie_label = tk.Label(button_frame, text="Total: 0")
        self.total_calorie_label.pack(side=tk.RIGHT, padx=10)

        add_more_btn = tk.Button(button_frame, text="Add More", command=self.add_meal_row)
        add_more_btn.pack(side=tk.LEFT, padx=10)

        reset_btn = tk.Button(button_frame, text="Reset", command=self.reset_section)
        reset_btn.pack(side=tk.LEFT, padx=10)

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
            selected_meal_calories[meal] = meal_calories
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
                meal_cal = selected_meal_calories.get(meal, 0) * int(quantity)
                calories_label.config(text=f"Total Calories: {meal_cal}")
                self.total_calories += meal_cal

        self.total_calorie_label.config(text=f"Total: {self.total_calories}")
        self.update_total_daily_calories()

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

    def update_total_daily_calories(self):
        self.root.update_total_daily_calories()


#### Main Application Class
class MealCalorieTrackerApp:
    def __init__(self, root):
        self.root = root
        self.total_daily_calories = 0
        self.sections = []  # Store all meal sections

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
        section = MealSection(self.root, title, self.meal_options, row_counter)
        self.sections.append(section)

    def update_total_daily_calories(self):
        total_daily_calories = sum(section.total_calories for section in self.sections)
        self.total_calories_label.config(text=f"Total Calories for Today: {total_daily_calories}")

    def open_add_meal_window(self):
        # Implementation to add a new meal (similar to the original logic)
        pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Meal Calorie Tracker")
    root.geometry("440x1200")

    app = MealCalorieTrackerApp(root)
    root.mainloop()
