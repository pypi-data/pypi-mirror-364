import tkinter as tk
from tk_double_scale import DoubleScale


root = tk.Tk()
root.title('DoubleScale testing')
root.geometry('300x500+1000+200')
root.configure(bg='grey')


# Demonstrating several possible arguments
DoubleScale(root).pack(pady=5)                      # Default parameters
DoubleScale(root, font='Calibri 20').pack(pady=5)   # Custom font
DoubleScale(root, from_=-10, to=10).pack(pady=5)    # Custom range
DoubleScale(root, to=1, decimals=-2).pack(pady=5)   # Custom decimals

# Custom colors
DoubleScale(root, cursor_color='blue', bg_color='#0ff', 
            text_color='blue').pack(pady=5)

# Small size
DoubleScale(root, length=50, thickness=10, cursor_width=5, 
            font='Calibri 8').pack(pady=5)

# Big size
scale = DoubleScale(root, length=200, thickness=30, cursor_width=30, 
                    font='Calibri 20')
scale.pack(pady=5)


# Demonstrating getting and setting values
print(scale.get_values())   # > [0.0, 100.0]

# Values are clamped inside the range defined by from_ and to
scale.set_values(-10, -10)
print(scale.get_values())   # > [0.0, 0.0]

scale.set_values(200, 200)
print(scale.get_values())   # > [100.0, 100.0]

# Values are rounded according to decimals (default is 0 decimals)
scale.set_values(25.123, 75.123)
print(scale.get_values())   # > [25.0, 75.0]

# Change the return type
print(scale.get_values(return_type=int))   # > [25, 75]


root.mainloop()