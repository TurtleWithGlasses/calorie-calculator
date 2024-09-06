import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, fetch_meal_data, get_meal_calories, add_new_meal

# Function to reset the details (e.g., reset meal, quantity, and total cal)
def reset_frame(frame):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
            widget.delete(0, tk.END)
        elif isinstance(widget, tk.Label) and "Total Calories" in widget.cget("text"):
            widget.config(text="Total Calories: 0")

# Function to delete a specific meal row without reconfiguring the entire grid
def delete_meal_row(meal_row, frame, row_counter, total_calorie_label):
    for widget in meal_row:
        widget.grid_forget()  # Remove all widgets in that row from the grid
    row_counter[0] -= 1  # Decrement the row counter after deletion
    update_total_calories(frame, total_calorie_label)

def update_total_calories(meal_input_frame, total_calorie_label):
    total_calories = 0
    print("update_total_calories() triggered")  # Debug print

    meal = None  # Initialize meal to None
    quantity = None  # Initialize quantity to None

    for child in meal_input_frame.winfo_children():
        # Check if the widget is a Combobox for meal selection
        if isinstance(child, ttk.Combobox):
            meal_combobox = child
            meal = meal_combobox.get()
            print(f"Meal selected: {meal}")  # Debug print

        # Check if the widget is an Entry for quantity input
        if isinstance(child, tk.Entry):
            quantity_entry = child
            quantity = quantity_entry.get()
            print(f"Quantity entered: {quantity}")  # Debug print

        # After getting both meal and quantity, fetch the calories and update labels
        if meal and quantity and quantity.isdigit():
            meal_calories = get_meal_calories(meal)  # Fetch calories from DB
            print(f"Calories fetched for {meal}: {meal_calories}")  # Debug print
            meal_cal = meal_calories * int(quantity)  # Calculate total for this meal
            total_calories += meal_cal  # Add to the frame's total

            # Find the next label for the calorie count and update it
            for next_widget in meal_input_frame.winfo_children():
                if isinstance(next_widget, tk.Label) and "Total Calories" in next_widget.cget("text"):
                    next_widget.config(text=f"Total Calories: {meal_cal}")  # Display per-row total
                    break

    total_calorie_label.config(text=f"Total: {total_calories}")  # Update the total for the frame
    update_total_daily_calories()  # Update the total for the entire day




# Function to calculate the total calories for the entire day across all frames
def update_total_daily_calories():
    total = 0
    for total_label in total_calorie_labels:
        total_text = total_label.cget("text")
        if total_text.startswith("Total:"):
            total += int(total_text.split(": ")[1])
    total_calories_label.config(text=f"Total Calories for Today: {total}")

# Function to dynamically add a new meal row to the frame
def add_meal_row(scroll_frame, row_counter, total_calorie_label, meal_options):
    # Meal selection (ComboBox)
    meal_combobox = ttk.Combobox(scroll_frame, values=meal_options)
    meal_combobox.grid(row=row_counter[0], column=0, padx=5, pady=5)

    # Quantity input (Entry)
    quantity_entry = tk.Entry(scroll_frame, width=5)
    quantity_entry.grid(row=row_counter[0], column=1, padx=5, pady=5)

    # Calories label (to be updated dynamically)
    calories_label = tk.Label(scroll_frame, text="Total Calories: 0")
    calories_label.grid(row=row_counter[0], column=2, padx=5, pady=5)

    # Delete button to remove the row
    delete_btn = tk.Button(scroll_frame, text="Delete", command=lambda: delete_meal_row([meal_combobox, quantity_entry, calories_label, delete_btn], scroll_frame, row_counter, total_calorie_label))
    delete_btn.grid(row=row_counter[0], column=3, padx=5, pady=5)

    # Add event to update the total calories when the user enters the meal or quantity
    meal_combobox.bind("<<ComboboxSelected>>", lambda e: print(f"Meal selected: {meal_combobox.get()}") or update_total_calories(scroll_frame, total_calorie_label))

    quantity_entry.bind("<KeyRelease>", lambda e: print(f"Quantity entered: {quantity_entry.get()}") or update_total_calories(scroll_frame, total_calorie_label))


    # Increment row_counter for the next row
    row_counter[0] += 1

# Function to open the "Add Meal" window
def open_add_meal_window():
    # Create a new window
    add_meal_window = tk.Toplevel(root)
    add_meal_window.title("Add New Meal")
    add_meal_window.geometry("300x150")

    # Meal Name Label and Entry
    tk.Label(add_meal_window, text="Meal Name:").pack(pady=5)
    meal_name_entry = tk.Entry(add_meal_window)
    meal_name_entry.pack(pady=5)

    # Meal Calories Label and Entry
    tk.Label(add_meal_window, text="Calories:").pack(pady=5)
    meal_calories_entry = tk.Entry(add_meal_window)
    meal_calories_entry.pack(pady=5)

    # Save button
    def save_new_meal():
        meal_name = meal_name_entry.get().strip()
        meal_calories = meal_calories_entry.get().strip()

        # Validate the inputs
        if meal_name == "" or not meal_calories.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid meal name and calorie count.")
            return

        # Add meal to the database
        add_new_meal(meal_name, int(meal_calories))

        # Update the combo boxes in the main app
        refresh_meal_options()

        # Close the add meal window
        add_meal_window.destroy()

    save_button = tk.Button(add_meal_window, text="Save", command=save_new_meal)
    save_button.pack(pady=10)

def refresh_combo_boxes(meal_input_frame):
    for widget in meal_input_frame.winfo_children():
        if isinstance(widget, ttk.Combobox):
            widget.config(values=meal_options)

# Function to refresh the meal options in combo boxes after adding a new meal
def refresh_meal_options():
    global meal_options
    meal_data = fetch_meal_data()  # Fetch updated meal data
    meal_options = [meal[0] for meal in meal_data]  # Extract just the meal names
    print("Meal options loaded:", meal_options)  # Debugging line
    refresh_combo_boxes(meal_input_frame1)
    refresh_combo_boxes(meal_input_frame2)
    refresh_combo_boxes(meal_input_frame3)



# Main window
root = tk.Tk()
root.title("Meal Calorie Tracker")
root.geometry("440x1200")

# Initialize the database
init_db()

# Fetch meals and their calories from the database
meal_data = fetch_meal_data()
meal_options = [meal[0] for meal in meal_data]  # Extract just the meal names

# Top section of date selection and add meal button
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

select_date_btn = tk.Button(top_frame, text="Select Date")
select_date_btn.pack(side=tk.LEFT, padx=10)

current_date_time_label = tk.Label(top_frame, text="Current date & time")
current_date_time_label.pack(side=tk.LEFT, padx=10)

add_meal_btn = tk.Button(top_frame, text="Add Meal", command=open_add_meal_window)
add_meal_btn.pack(side=tk.RIGHT, padx=10)

total_calorie_labels = []  # To store calorie labels for each part of the day

# Function to create a scrollable frame for meal entries and add/reset buttons
def create_meal_frame(root, frame_title):
    container_frame = tk.Frame(root)
    container_frame.pack(fill=tk.X, padx=5, pady=5)

    row_frame = tk.Frame(container_frame)
    row_frame.pack(fill=tk.X)

    canvas = tk.Canvas(row_frame)
    scroll_frame = tk.Frame(canvas)

    scrollbar = tk.Scrollbar(row_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill="both", expand=True)
    canvas.create_window((0,0), window=scroll_frame, anchor="nw")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    frame_title_label = tk.Label(scroll_frame, text=frame_title)
    frame_title_label.grid(row=0, column=0, columnspan=4, pady=10)

    meal_input_frame = tk.Frame(scroll_frame)
    meal_input_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=5)

    tk.Label(meal_input_frame, text="Meal").grid(row=0, column=0)
    tk.Label(meal_input_frame, text="Quantity").grid(row=0, column=1)
    tk.Label(meal_input_frame, text="Total Calories").grid(row=0, column=2)

    row_counter = [1]

    
    button_frame = tk.Frame(container_frame)
    button_frame.pack(pady=5)

    total_calorie_label_for_single_part = tk.Label(button_frame, text="Total: 0")
    total_calorie_label_for_single_part.pack(side=tk.RIGHT, padx=10)
    total_calorie_labels.append(total_calorie_label_for_single_part)


    for _ in range(3):
        add_meal_row(meal_input_frame, row_counter, total_calorie_label_for_single_part, meal_options)

    add_more_btn = tk.Button(button_frame, text="Add More", command= lambda: add_meal_row(meal_input_frame, row_counter, total_calorie_label_for_single_part, meal_options))
    add_more_btn.pack(side=tk.LEFT, padx=10)

    reset_btn = tk.Button(button_frame, text="Reset", command=lambda f=meal_input_frame: reset_frame(f))
    reset_btn.pack(side=tk.LEFT, padx=10)

    return container_frame, meal_input_frame, button_frame


frame1, meal_input_frame1, button_frame1 = create_meal_frame(root, "09:00 AM - 12:00 PM")
frame2, meal_input_frame2, button_frame2 = create_meal_frame(root, "12:00 PM - 06:00 PM")
frame3, meal_input_frame3, button_frame3 = create_meal_frame(root, "06:00 PM - 12:00 AM")

frame4 = tk.Frame(root)
frame4.pack(fill=tk.X, padx=5, pady=5)

total_calories_label = tk.Label(frame4, text="Calculation of total Calories You Get Today: 0", font=("Arial", 12))
total_calories_label.pack()

meal_options = [meal[0] for meal in fetch_meal_data()]  # Fetch initial meal data


root.mainloop()
