import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class ReminderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("মনে নাই")
        
        # Entry for user to input reminder
        self.reminder_entry = tk.Entry(master, width=30)
        self.reminder_entry.grid(row=0, column=0, padx=10, pady=10)
        
        # Button to set reminder
        self.set_button = tk.Button(master, text="মনে করাই দিয়েন", command=self.set_reminder)
        self.set_button.grid(row=0, column=1, padx=10, pady=10)

    def set_reminder(self):
        reminder_text = self.reminder_entry.get()
        if reminder_text:
            # Set a reminder for 5 seconds from now (for demonstration)
            current_time = datetime.now()
            reminder_time = current_time + timedelta(seconds=5)
            
            # Display a message box with the reminder text after 5 seconds
            self.master.after(5000, lambda: self.show_reminder(reminder_text))
        else:
            messagebox.showwarning("সতর্কতা", "কিছু একটা তো লেখেন")

    def show_reminder(self, reminder_text):
        messagebox.showinfo("মনে নাই", f"আপনে বলসিলেন : {reminder_text}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReminderApp(root)
    root.mainloop()
