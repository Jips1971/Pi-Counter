import tkinter as tk
from tkinter import ttk
import threading
import time

# Cancel flag
cancel_flag = False

# Spigot algorithm for generating digits of π
def generate_pi_digits(n, digit_callback, is_cancelled):
    q, r, t, k, n_, l = 1, 0, 1, 1, 3, 3
    decimal = 0
    counter = 0
    result = ""

    while counter < n:
        if is_cancelled():
            break

        if 4 * q + r - t < n_ * t:
            digit_callback(str(n_))
            result += str(n_)
            if counter == 0:
                digit_callback(".")
                result += "."
            counter += 1
            nr = 10 * (r - n_ * t)
            n_ = ((10 * (3 * q + r)) // t) - 10 * n_
            q *= 10
            r = nr
        else:
            nr = (2 * q + r) * l
            nn = (q * (7 * k + 2) + r * l) // (t * l)
            q *= k
            t *= l
            l += 2
            k += 1
            n_ = nn
            r = nr
        if n <= 500:
            time.sleep(0.01)  # For small values, keep visible updates
        elif counter % 100 == 0:
            time.sleep(0.001)  # Light delay every 100 digits
    return result

# Background thread logic
def calculate_pi_digits_thread(digits):
    global cancel_flag
    cancel_flag = False
    start_time = time.time()

    def is_cancelled():
        return cancel_flag

    def digit_callback(digit):
        root.after(0, lambda: display_text.insert(tk.END, digit))
        root.after(0, lambda: progress_bar.step(1))

    root.after(0, lambda: display_text.delete("1.0", tk.END))
    root.after(0, lambda: progress_bar.config(value=0, maximum=digits))

    generate_pi_digits(digits, digit_callback, is_cancelled)
    duration = time.time() - start_time

    def finish():
        go_button.config(state="normal")
        cancel_button.config(state="disabled")
        if cancel_flag:
            display_text.insert(tk.END, f"\n\nCancelled after {duration:.2f} seconds.")
        else:
            display_text.insert(tk.END, f"\n\nDone in {duration:.2f} seconds.")

    root.after(0, finish)

# Start from GUI
def start_calculation():
    try:
        digits = int(entry.get())
        if digits < 1 or digits > 10000:
            display_text.delete("1.0", tk.END)
            display_text.insert(tk.END, "Enter a number between 1 and 10,000.")
            return

        go_button.config(state="disabled")
        cancel_button.config(state="normal")
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, "π = ")
        thread = threading.Thread(target=calculate_pi_digits_thread, args=(digits,))
        thread.start()

    except ValueError:
        display_text.delete("1.0", tk.END)
        display_text.insert(tk.END, "Please enter a valid integer.")

# Cancel handler
def cancel_calculation():
    global cancel_flag
    cancel_flag = True

# GUI setup
root = tk.Tk()
root.title("Live π Digit Generator (up to 10,000 digits)")

tk.Label(root, text="Number of digits (1–10,000):").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)

go_button = tk.Button(root, text="Go", command=start_calculation)
go_button.pack(pady=5)

cancel_button = tk.Button(root, text="Cancel", command=cancel_calculation, state="disabled")
cancel_button.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=5)

# Use a scrollable Text widget for large output
text_frame = tk.Frame(root)
text_frame.pack(padx=10, pady=5, fill="both", expand=True)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

display_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=20)
display_text.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar.config(command=display_text.yview)

root.mainloop()
