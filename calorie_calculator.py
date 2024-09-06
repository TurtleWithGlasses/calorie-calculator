import tkinter as tk
from tkinter import ttk


# Function to reset the details (e.g., reset meal, quantity, and total cal)
def reset_frame(frame):
    for widget in frame.winfo_children():
        if isinstance(widget, tk.Entry) or isinstance(widget, ttk.Combobox):
            widget.delete(0, tk.END)
        elif isinstance(widget, tk.Label) and "Total Calories" in widget.cget("text"):
            widget.config(text="Total Calories: 0")

# Function to delete a specific meal row without reconfiguring the entire grid
def delete_meal_row(meal_row, frame, row_counter):
    for widget in meal_row:
        widget.grid_forget()  # Remove all widgets in that row from the grid
    row_counter[0] -= 1  # Decrement the row counter after deletion

# Function to dynamically add a new meal row to the frame
def add_meal_row(scroll_frame, row_counter):
    # Meal selection (ComboBox)
    meal_combobox = ttk.Combobox(scroll_frame, values=["Meal 1", "Meal 2", "Meal 3"])
    meal_combobox.grid(row=row_counter[0], column=0, padx=5, pady=5)

    # Quantity input (Entry)
    quantity_entry = tk.Entry(scroll_frame, width=5)
    quantity_entry.grid(row=row_counter[0], column=1, padx=5, pady=5)

    # Calories label (to be updated dynamically)
    calories_label = tk.Label(scroll_frame, text="Total Calories: 0")
    calories_label.grid(row=row_counter[0], column=2, padx=5, pady=5)

    # Delete button to remove the row
    delete_btn = tk.Button(scroll_frame, text="Delete", command=lambda: delete_meal_row([meal_combobox, quantity_entry, calories_label, delete_btn], scroll_frame, row_counter))
    delete_btn.grid(row=row_counter[0], column=3, padx=5, pady=5)

    # Increment row_counter for the next row
    row_counter[0] += 1

# main window
root = tk.Tk()
root.title("Meal Calorie Tracher")
root.geometry("410x1200")

# top section of date selection and add meal button
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

select_date_btn = tk.Button(top_frame, text="Select Date")
select_date_btn.pack(side=tk.LEFT, padx=10)

current_date_time_label = tk.Label(top_frame, text="Current date & time")
current_date_time_label.pack(side=tk.LEFT, padx=10)

add_meal_btn = tk.Button(top_frame, text="Add Meal")
add_meal_btn.pack(side=tk.RIGHT, padx=10)

# function to create a scrollable frame for meal entries and add/reset buttons
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

    for _ in range(3):
        add_meal_row(meal_input_frame, row_counter)
    
    button_frame = tk.Frame(container_frame)
    button_frame.pack(pady=5)

    add_more_btn = tk.Button(button_frame, text="Add More", command= lambda: add_meal_row(meal_input_frame,row_counter))
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



root.mainloop()