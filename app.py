import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QAction, QDialog, QInputDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate, QDateTime
import sqlite3

# A new window class for adding reminders
class AddReminderWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Reminder")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Title")
        layout.addWidget(self.title_entry)

        self.notes_entry = QTextEdit()
        self.notes_entry.setPlaceholderText("Note")
        layout.addWidget(self.notes_entry)

        add_button = QPushButton("Save")
        add_button.clicked.connect(self.add_reminder)
        layout.addWidget(add_button)

        
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)# wrotea his to remove the question mark button from the title bar

        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #fff;
            }
            QHeaderView {
                background-color: #222;
                color: #fff;
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
        notes = self.notes_entry.toPlainText()

        # Emit a signal to send the input values back to the main window
        self.accept()

class ViewNoteDialog(QDialog):
    def __init__(self, note):
        super().__init__()
        self.setWindowTitle("View Note")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.notes_display = QTextEdit()
        self.notes_display.setPlainText(note)
        self.notes_display.setReadOnly(True)
        layout.addWidget(self.notes_display)

        # Apply dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #333;
                color: #fff;
            }
            QHeaderView {
                background-color: #222;
                color: #fff;
            }
            QTextEdit {
                background-color: #222;
                color: #fff;
                selection-background-color: #666;
            }
        """)

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

        # "Add Reminder" button to open the new window
        add_button = QPushButton("Add Reminder")
        add_button.clicked.connect(self.open_add_reminder_window)
        reminder_layout.addWidget(add_button)

        # Reminder display section
        self.reminder_tree = QTreeWidget()
        self.reminder_tree.setColumnCount(4)  # Set the number of columns
        self.reminder_tree.setHeaderLabels(["ID", "Title", "Date", "Time"])  # Add headers
        self.reminder_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reminder_tree.customContextMenuRequested.connect(self.show_context_menu)
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

    def open_add_reminder_window(self):
        # Create and open the new window for adding reminders
        add_window = AddReminderWindow()
        if add_window.exec_() == QDialog.Accepted:
            # If the user clicks "Add" in the new window, add the reminder
            self.add_reminder(add_window.title_entry.text(), add_window.notes_entry.toPlainText())

    def add_reminder(self, title, notes):
        # Automatically set the current date
        date = QDate.currentDate().toString(Qt.ISODate)
        # Get the current time in PC's timezone
        current_datetime = QDateTime.currentDateTime()
        time = current_datetime.time().toString("hh:mm AP")  # Format with AM/PM

        # Validate inputs
        if not title:
            QMessageBox.warning(self, "Error", "Please enter title.")
            return

        # Insert reminder into database with date and time
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO reminders (title, date, time, notes) VALUES (?, ?, ?, ?)",
                       (title, date, time, notes))
        self.conn.commit()

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
            item = QTreeWidgetItem([str(reminder[0]), reminder[1], reminder[2], reminder[3], ""])
            item.setData(4, Qt.UserRole, reminder[4])  # Store notes in UserRole for future use
            self.reminder_tree.addTopLevelItem(item)

    def show_context_menu(self, position):
        menu = QMenu(self)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        action = menu.exec_(self.reminder_tree.mapToGlobal(position))
        if action == edit_action:
            self.edit_selected_note()
        elif action == delete_action:
            self.delete_selected_note()

    def edit_selected_note(self):
        selected_item = self.reminder_tree.currentItem()
        if selected_item:
            note = selected_item.data(4, Qt.UserRole)
            new_note, ok = QInputDialog.getText(self, "Edit Note", "Edit your note:", QLineEdit.Normal, note)
            if ok:
                selected_item.setData(4, Qt.UserRole, new_note)
                selected_item.setText(4, new_note)

    def delete_selected_note(self):
        selected_item = self.reminder_tree.currentItem()
        if selected_item:
            confirmation = QMessageBox.question(self, "Delete Note", "Are you sure you want to delete this note?",
                                                QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                note_id = selected_item.text(0)
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM reminders WHERE id = ?", (note_id,))
                self.conn.commit()
                self.reminder_tree.takeTopLevelItem(self.reminder_tree.indexOfTopLevelItem(selected_item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReminderApp()
    window.show()
    sys.exit(app.exec_())
