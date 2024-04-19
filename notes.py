import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate, QDateTime
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
        
        # UI elements
        self.create_widgets()
        
    def create_table(self):
        # A table to store reminders
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reminders (
                            id INTEGER PRIMARY KEY,
                            title TEXT NOT NULL,
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            notes TEXT
                        )''')
        self.conn.commit()
        
    def create_widgets(self):
        # A central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Reminder creation section
        reminder_layout = QVBoxLayout()
        layout.addLayout(reminder_layout)
        
        reminder_layout.addWidget(QLabel("<font color='white'>Title:</font>"))
        self.title_entry = QLineEdit()
        reminder_layout.addWidget(self.title_entry)

        reminder_layout.addWidget(QLabel("<font color='white'>Notes:</font>"))
        self.notes_entry = QTextEdit()
        reminder_layout.addWidget(self.notes_entry)


        add_button = QPushButton("Add Reminder")
        add_button.clicked.connect(self.add_reminder)
        reminder_layout.addWidget(add_button)
        
        # Reminder display section
        self.reminder_tree = QTreeWidget()
        self.reminder_tree.setColumnCount(5)  # Set the number of columns
        self.reminder_tree.setHeaderLabels(["ID", "Title", "Date", "Time", "Notes"])  # Add headers
        layout.addWidget(self.reminder_tree)
        
        # Load existing reminders
        self.load_reminders()

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333;
                color: #fff;
            }
            QTreeWidget {
                background-color: #222;
                color: #fff;
                alternate-background-color: #333;
            }
            QLineEdit, QTextEdit {
                background-color: #222;
                color: #fff;
                selection-background-color: #666;
            }
            QPushButton {
                background-color: #444;
                color: #fff;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)
        
    def add_reminder(self):
        # Get input values
        title = self.title_entry.text()
        # Automatically set the current date
        date = QDate.currentDate().toString(Qt.ISODate)
        # Get the current time in PC's timezone
        current_datetime = QDateTime.currentDateTime()
        time = current_datetime.time().toString("hh:mm AP")  # Format with AM/PM
        notes = self.notes_entry.toPlainText()
        
        # Validate inputs
        if not title:
            QMessageBox.warning(self, "Error", "Please enter title.")
            return
        
        # Insert reminder into database with date and time
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO reminders (title, date, time, notes) VALUES (?, ?, ?, ?)",
                    (title, date, time, notes))
        self.conn.commit()
        
        # Clear input fields
        self.title_entry.clear()
        self.notes_entry.clear()
        
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
            item = QTreeWidgetItem([str(reminder[0]), reminder[1], reminder[2], reminder[3], reminder[4]])
            self.reminder_tree.addTopLevelItem(item)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReminderApp()
    window.show()
    sys.exit(app.exec_())
