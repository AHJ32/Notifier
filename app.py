import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem, QCheckBox, QMessageBox, QCalendarWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate  
import sqlite3

class ReminderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reminder App")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(r"pngs\logo.png"))

        
        # Connect to the database
        self.conn = sqlite3.connect('reminders.db')
        self.create_table()
        
        # Create UI elements
        self.create_widgets()
        
    def create_table(self):
        # Create a table to store reminders
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                            id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            notes TEXT,
                            recurring TEXT
                        )''')
        self.conn.commit()
        
    def create_widgets(self):
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Reminder creation section
        reminder_layout = QVBoxLayout()
        layout.addLayout(reminder_layout)
        
        reminder_layout.addWidget(QLabel("Title:"))
        self.title_entry = QLineEdit()
        reminder_layout.addWidget(self.title_entry)
        
        reminder_layout.addWidget(QLabel("Date:"))
        self.date_button = QPushButton("Choose Date")
        self.date_button.clicked.connect(self.show_calendar)
        reminder_layout.addWidget(self.date_button)
        
        reminder_layout.addWidget(QLabel("Time (HH:MM):"))
        self.time_entry = QLineEdit()
        reminder_layout.addWidget(self.time_entry)
        
        reminder_layout.addWidget(QLabel("Notes:"))
        self.notes_entry = QTextEdit()
        reminder_layout.addWidget(self.notes_entry)
        
        self.recurring_checkbox = QCheckBox("Recurring")
        reminder_layout.addWidget(self.recurring_checkbox)
        
        add_button = QPushButton("Add Reminder")
        add_button.clicked.connect(self.add_reminder)
        reminder_layout.addWidget(add_button)
        
        # Reminder display section
        self.reminder_tree = QTreeWidget()
        self.reminder_tree.setColumnCount(5)
        self.reminder_tree.setHeaderLabels(["Title", "Date", "Time", "Notes", "Recurring"])
        layout.addWidget(self.reminder_tree)
        
        # Load existing reminders
        self.load_reminders()
        
    def show_calendar(self):
        # Create a calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setWindowModality(Qt.ApplicationModal)
        self.calendar.clicked.connect(self.set_date)
        self.calendar.show()
        
    def set_date(self, date):
        # Set the selected date to the date entry
        self.date_button.setText(date.toString(Qt.ISODate))
        self.calendar.deleteLater()
        
    def add_reminder(self):
        # Get input values
        title = self.title_entry.text()
        date = self.date_button.text()  # Retrieve selected date from the button text
        time = self.time_entry.text()
        notes = self.notes_entry.toPlainText()
        recurring = "Yes" if self.recurring_checkbox.isChecked() else "No"
        
        # Validate inputs
        if not title or not date or not time:
            QMessageBox.warning(self, "Error", "Please enter title, date, and time.")
            return
        
        # Insert reminder into database
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO reminders (title, date, time, notes, recurring) VALUES (?, ?, ?, ?, ?)",
                       (title, date, time, notes, recurring))
        self.conn.commit()
        
        # Clear input fields
        self.title_entry.clear()
        self.time_entry.clear()
        self.notes_entry.clear()
        self.recurring_checkbox.setChecked(False)
        
        # Reload reminders
        self.load_reminders()
        
    def load_reminders(self):
        # Clear existing data
        self.reminder_tree.clear()
        
        # Fetch reminders from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM reminders")
        reminders = cursor.fetchall()
        
        # Display reminders in TreeWidget
        for reminder in reminders:
            item = QTreeWidgetItem([str(val) for val in reminder])
            self.reminder_tree.addTopLevelItem(item)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReminderApp()
    window.show()
    sys.exit(app.exec_())
