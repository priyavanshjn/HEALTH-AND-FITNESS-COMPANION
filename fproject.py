import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import os


# --- GLOBAL DATA LOADING & CLEANING (CALORIE MODE) ---
def load_and_clean_data(file_name="Combined_Food_and_Calories.csv"):
    """Loads food data, cleans calories, and prepares for searching."""
    try:
        df = pd.read_csv(file_name)
    except FileNotFoundError:
        return None

    # Clean the 'Calories' column
    df['Calories_Clean'] = df['Calories'].str.replace(r'\s*cal\s*', '', regex=True)
    df['Calories_Clean'] = df['Calories_Clean'].str.replace(r'\s*kJ\s*', '', regex=True)
    df['Calories_Clean'] = pd.to_numeric(df['Calories_Clean'], errors='coerce')

    # Drop rows where calorie conversion failed
    df_cleaned = df.dropna(subset=['Calories_Clean']).copy()

    # Create the lowercase column for case-insensitive searching
    df_cleaned['Food_Lower'] = df_cleaned['Food'].str.lower()

    return df_cleaned


FOOD_DATA = load_and_clean_data()


# --- 1. BMI & FITNESS CALCULATOR LOGIC (User's Code Refactored) ---

def calculate_fitness(name, gender, age, height, weight, goal, diet_type):
    """Calculates BMI, BMR, Fat%, and provides fitness recommendations."""
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    # Body Fat Percentage calculation (simplified formula)
    fat_percentage = (1.20 * bmi) + (0.23 * age) - (10.8 if gender == 'Male' else 0) - 5.4
    # BMR calculation (Mifflin-St Jeor)
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == 'Male' else -161)

    # Activity Multiplier (1.55 is Moderate Activity)
    calories_needed = bmr * 1.55

    # Simple adjustment based on goal
    if goal == 'Weight Loss':
        calories_needed -= 500  # Deficit
        burned_calories = 500  # Suggestion for daily burn
    elif goal == 'Weight Gain':
        calories_needed += 500  # Surplus
        burned_calories = 200  # Focus on recovery
    else:  # Maintain Fitness
        burned_calories = 300

    workout = {
        "Weight Loss": "Cardio + HIIT (Running, Cycling, Jump Rope)\nMuscle focus: Full body",
        "Weight Gain": "Strength training (Squats, Deadlifts, Bench Press)\nMuscle focus: Upper & Lower body",
        "Maintain Fitness": "Balanced: Yoga + Weights\nMuscle focus: Core and flexibility"
    }[goal]

    diet = {
        "Veg": {
            "Weight Loss": "Oats, dal-salad, paneer soup",
            "Weight Gain": "Banana shake, paneer, nuts",
            "Maintain Fitness": "Balanced veg meals"
        },
        "Non-Veg": {
            "Weight Loss": "Eggs, grilled chicken, soup",
            "Weight Gain": "Meat curry, biryani, eggs",
            "Maintain Fitness": "Lean meat, fruits, veggies"
        }
    }[diet_type][goal]

    return {
        "Name": name, "Gender": gender, "Age": age, "Height": height, "Weight": weight,
        "Goal": goal, "BMI": round(bmi, 2), "Fat%": round(fat_percentage, 2),
        "BMR": int(bmr), "Calories Needed": int(calories_needed), "Burned Calories": int(burned_calories),
        "Workout": workout, "Diet": diet
    }


def generate_report_window(data1, data2=None):
    """Displays the fitness report in a new Tkinter window."""

    report_window = Toplevel()
    report_window.title("Fitness Report")
    report_window.grab_set()

    ttk.Label(report_window, text="--- Detailed Fitness Analysis ---", font=('Arial', 14, 'bold')).pack(pady=10)

    report_text = tk.Text(report_window, height=30, width=80, wrap='word', padx=10, pady=10)
    report_text.pack(expand=True, fill='both')

    weekly_plan = {
        "Day 1": "Chest + Cardio: Push-ups, Bench Press, Running 20min",
        "Day 2": "Back + Cardio: Pull-ups, Dumbbell Rows, Cycling 25min",
        "Day 3": "Legs: Squats, Lunges, Step-ups, Jump Rope",
        "Day 4": "Shoulders: Overhead Press, Lateral Raises",
        "Day 5": "Arms + Cardio: Biceps, Triceps, HIIT",
        "Day 6": "Core: Planks, Crunches, Russian Twists",
        "Day 7": "Rest / Yoga: Light yoga"
    }

    def write_person(person, label):
        content = f"--- {label}: {person['Name']} ---\n"
        content += f"Goal: {person['Goal']}\n"
        content += f"BMI: {person['BMI']} (Under 18.5: Underweight, 18.5–24.9: Healthy, 25.0–29.9: Overweight, 30.0+: Obese)\n"
        content += f"Body Fat %: {person['Fat%']}%\n"
        content += f"BMR: {person['BMR']} cal\n"
        content += f"Daily Calories for Goal: {person['Calories Needed']} cal\n"
        content += f"Recommended Burn: {person['Burned Calories']} cal\n\n"

        content += f"Workout Plan:\n{person['Workout']}\n\n"
        content += f"Diet Recommendation ({person['Diet']}):\n{person['Diet']}\n\n"

        content += "7-Day Workout Schedule:\n"
        for day, ex in weekly_plan.items():
            content += f"- {day}: {ex}\n"
        content += "\n" + "=" * 40 + "\n\n"
        return content

    report_content = write_person(data1, "PERSON 1")
    if data2:
        report_content += write_person(data2, "PERSON 2 (Comparison)")

    report_text.insert(tk.END, report_content)
    report_text.config(state='disabled')


class BmiFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="10")

        self.vars = {
            'name1': tk.StringVar(), 'gender1': tk.StringVar(value="Male"), 'age1': tk.StringVar(),
            'height1': tk.StringVar(), 'weight1': tk.StringVar(), 'goal1': tk.StringVar(value="Maintain Fitness"),
            'diet1': tk.StringVar(value="Veg"),
            'name2': tk.StringVar(), 'gender2': tk.StringVar(value="Male"), 'age2': tk.StringVar(),
            'height2': tk.StringVar(), 'weight2': tk.StringVar(), 'goal2': tk.StringVar(value="Maintain Fitness"),
            'diet2': tk.StringVar(value="Veg")
        }

        left_frame = ttk.Frame(self, padding="5");
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        right_frame = ttk.Frame(self, padding="5");
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.create_user_form(left_frame, "Person 1", 1)
        self.create_user_form(right_frame, "Person 2 (Optional)", 2)

        ttk.Button(self, text="Generate Fitness Report", command=self.submit, style='Accent.TButton').grid(row=1,
                                                                                                           column=0,
                                                                                                           columnspan=2,
                                                                                                           pady=20)

    def create_user_form(self, frame, title, person_num):
        ttk.Label(frame, text=title, font=('Arial', 12, 'bold')).pack(pady=5)

        mapping = {
            "Name": f'name{person_num}', "Gender": f'gender{person_num}', "Age": f'age{person_num}',
            "Height (cm)": f'height{person_num}', "Weight (kg)": f'weight{person_num}',
            "Goal": f'goal{person_num}', "Diet": f'diet{person_num}'
        }

        for label, var_key in mapping.items():
            var = self.vars[var_key]
            ttk.Label(frame, text=label).pack(anchor='w', padx=5)

            if label in ["Gender", "Goal", "Diet"]:
                options = {
                    "Gender": ["Male", "Female"],
                    "Goal": ["Weight Loss", "Weight Gain", "Maintain Fitness"],
                    "Diet": ["Veg", "Non-Veg"]
                }[label]
                ttk.OptionMenu(frame, var, var.get(), *options).pack(fill='x', padx=5, pady=2)
            else:
                ttk.Entry(frame, textvariable=var).pack(fill='x', padx=5, pady=2)

    def submit(self):
        try:
            # Person 1 data
            data1 = calculate_fitness(
                self.vars['name1'].get() or "Person 1", self.vars['gender1'].get(),
                int(self.vars['age1'].get()), float(self.vars['height1'].get()),
                float(self.vars['weight1'].get()), self.vars['goal1'].get(), self.vars['diet1'].get()
            )

            # Person 2 data (optional)
            data2 = None
            if self.vars['name2'].get().strip() or self.vars['age2'].get().strip():
                data2 = calculate_fitness(
                    self.vars['name2'].get() or "Person 2", self.vars['gender2'].get(),
                    int(self.vars['age2'].get()), float(self.vars['height2'].get()),
                    float(self.vars['weight2'].get()), self.vars['goal2'].get(), self.vars['diet2'].get()
                )

            generate_report_window(data1, data2)

        except ValueError:
            messagebox.showerror("Input Error",
                                 "Please ensure all mandatory fields (Name, Age, Height, Weight) are filled and contain valid numbers.")
        except Exception as e:
            messagebox.showerror("Calculation Error", f"An unexpected error occurred: {e}")


# --- 2. CALORIE CALCULATOR FRAME ---

class CalorieFrame(ttk.Frame):
    def __init__(self, parent, data_df):
        super().__init__(parent, padding="10")
        self.data_df = data_df
        self.meal_list = []  # Stores (Food Name, Servings, Calories Per Serving)

        if self.data_df is None:
            ttk.Label(self, text="ERROR: Combined_Food_and_Calories.csv not found.", foreground='red').pack(pady=20)
            return

        # --- Search Controls ---
        ttk.Label(self, text="Search Food:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = ttk.Entry(self, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind('<Return>', lambda event: self.search_food())

        ttk.Button(self, text="Search", command=self.search_food).grid(row=0, column=2, padx=5, pady=5)

        # --- Results Listbox ---
        ttk.Label(self, text="Search Results (Double-click to select):").grid(row=1, column=0, columnspan=3, padx=5,
                                                                              pady=(10, 0), sticky="w")

        self.listbox_frame = ttk.Frame(self);
        self.listbox_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.listbox_frame.grid_columnconfigure(0, weight=1)

        self.results_listbox = tk.Listbox(self.listbox_frame, height=10, width=60)
        self.results_listbox.grid(row=0, column=0, sticky="ew")
        self.results_listbox.bind('<Double-Button-1>', self.on_select_food)

        self.scrollbar = ttk.Scrollbar(self.listbox_frame, orient="vertical", command=self.results_listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_listbox.config(yscrollcommand=self.scrollbar.set)

        # --- Meal List and Controls ---
        ttk.Label(self, text="Current Meal:").grid(row=3, column=0, padx=5, pady=(10, 0), sticky="w")
        self.meal_text = tk.Text(self, height=8, width=60, state='disabled')
        self.meal_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.total_label = ttk.Label(self, text="Total Calories: 0.0", font=('Arial', 12, 'bold'))
        self.total_label.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="w")

        ttk.Button(self, text="Calculate Total", command=self.calculate_total, style='Accent.TButton').grid(row=5,
                                                                                                            column=2,
                                                                                                            padx=5,
                                                                                                            pady=10)
        ttk.Button(self, text="Clear Meal", command=self.clear_meal).grid(row=6, column=2, padx=5, pady=5)

    def search_food(self):
        query = self.search_entry.get().strip().lower()
        self.results_listbox.delete(0, tk.END)

        if not query:
            self.results_listbox.insert(tk.END, "Enter a search term.")
            return

        results = self.data_df[self.data_df['Food_Lower'].str.contains(query, na=False)]

        self.current_results = {}
        if results.empty:
            self.results_listbox.insert(tk.END, f"No results found for '{query}'.")
        else:
            for index, row in results.head(20).iterrows():  # Show only top 20 for performance
                display_text = f"{row['Food']} ({row['Serving']} -> {row['Calories_Clean']:.1f} cal)"
                self.results_listbox.insert(tk.END, display_text)
                self.current_results[display_text] = row

    def on_select_food(self, event):
        selected_index = self.results_listbox.curselection()
        if not selected_index:
            return

        selected_text = self.results_listbox.get(selected_index[0])

        if selected_text in self.current_results:
            food_item = self.current_results[selected_text]
            self.show_quantity_window(food_item)

    def show_quantity_window(self, food_item):
        q_window = Toplevel(self.master)
        q_window.title("Enter Quantity")
        q_window.geometry("350x180")
        q_window.transient(self.master)
        q_window.grab_set()

        food_name = food_item['Food']
        cal_per_serving = food_item['Calories_Clean']

        ttk.Label(q_window, text="Add to Meal:", font=('Arial', 10, 'bold')).pack(pady=5)
        ttk.Label(q_window, text=f"Food: {food_name}", wraplength=300).pack(pady=2)
        ttk.Label(q_window, text=f"Calories per Serving: {cal_per_serving:.1f}").pack(pady=2)

        ttk.Label(q_window, text="Quantity (Servings):").pack(pady=5)
        quantity_entry = ttk.Entry(q_window)
        quantity_entry.pack(pady=5, padx=20, fill='x')

        def add_to_meal():
            try:
                quantity = float(quantity_entry.get().strip())
                if quantity <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than zero.")
                    return

                self.meal_list.append((food_name, quantity, cal_per_serving))
                self.update_meal_display()
                q_window.destroy()

            except ValueError:
                messagebox.showerror("Error", "Invalid quantity. Please enter a number (e.g., 1 or 0.5).")

        ttk.Button(q_window, text="Add to Meal", command=add_to_meal, style='Accent.TButton').pack(pady=10)
        q_window.bind('<Return>', lambda event: add_to_meal())
        quantity_entry.focus_set()

    def update_meal_display(self):
        self.meal_text.config(state='normal')
        self.meal_text.delete(1.0, tk.END)

        output = ""
        for name, qty, cal_per_serv in self.meal_list:
            item_cals = qty * cal_per_serv
            output += f"{name}: {qty} x {cal_per_serv:.1f} cal/serv = {item_cals:.1f} cal\n"

        self.meal_text.insert(tk.INSERT, output)
        self.meal_text.config(state='disabled')

    def calculate_total(self):
        if not self.meal_list:
            self.total_label.config(text="Total Calories: 0.0")
            return

        total_cals = sum(qty * cal_per_serv for name, qty, cal_per_serv in self.meal_list)
        self.total_label.config(text=f"Total Calories: {total_cals:.1f}")

    def clear_meal(self):
        self.meal_list = []
        self.update_meal_display()
        self.total_label.config(text="Total Calories: 0.0")


# --- 3. MAIN APPLICATION (MODE SWITCHER) ---

class MainApp:
    def __init__(self, master, data_df):
        self.master = master
        master.title("Health & Fitness Companion")

        # Apply modern style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Accent.TButton', foreground='white', background='#0078D4')

        # Control variable for mode selection
        self.mode = tk.StringVar(value="calories")  # Default mode is Calorie Calculator

        # --- Mode Selector (The Checkbox/Radio Buttons) ---
        mode_frame = ttk.Frame(master, padding="10 10 10 0")
        mode_frame.pack(fill='x')

        ttk.Label(mode_frame, text="Select Mode: ", font=('Arial', 10, 'bold')).pack(side='left', padx=10)

        ttk.Radiobutton(mode_frame, text="Calculate Calories (Food Search)", variable=self.mode, value="calories",
                        command=self.switch_mode).pack(side='left', padx=10)
        ttk.Radiobutton(mode_frame, text="Calculate BMI & Fitness Plan", variable=self.mode, value="bmi",
                        command=self.switch_mode).pack(side='left', padx=10)

        # --- Content Frame (holds the active mode) ---
        self.content_frame = ttk.Frame(master)
        self.content_frame.pack(fill='both', expand=True)

        self.calorie_frame = CalorieFrame(self.content_frame, data_df)
        self.bmi_frame = BmiFrame(self.content_frame)

        self.switch_mode()  # Initial display setup

    def switch_mode(self):
        # Hide all frames
        for frame in self.content_frame.winfo_children():
            frame.pack_forget()

        # Show the selected frame
        if self.mode.get() == "calories":
            self.calorie_frame.pack(fill='both', expand=True)
            self.master.geometry("550x550")  # Adjust size for calorie frame
        elif self.mode.get() == "bmi":
            self.bmi_frame.pack(fill='both', expand=True)
            self.master.geometry("600x600")  # Adjust size for BMI frame


# --- Main Execution ---

if __name__ == "__main__":
    if FOOD_DATA is None:
        messagebox.showerror("Initialization Error",
                             "Cannot start. 'Combined_Food_and_Calories.csv' not found. Please ensure the data file is in the same directory.")
    else:
        root = tk.Tk()
        MainApp(root, FOOD_DATA)
        root.mainloop()