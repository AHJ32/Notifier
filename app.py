import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel,
    QPushButton, QLineEdit, QTextEdit, QTreeWidget, QTreeWidgetItem, QMessageBox, QMenu, QAction, QDialog, QInputDialog
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate, QDateTime
import sqlite3

class AddNoteWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add note")
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
        add_button.clicked.connect(self.add_note)
        layout.addWidget(add_button)

        # to remove the question mark button from the title bar
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

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

        
    def add_note(self):
        # Get input values
        title = self.title_entry.text()
        notes = self.notes_entry.toPlainText()

        # Emit a signal to send the input values back to the main window
        self.accept()

class ViewNoteDialog(QDialog):
    def __init__(self, title, note):
        super().__init__()
        self.setWindowTitle(title)  # Set the window title to the note title
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
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

class NoteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note App")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon(r"pngs\logo.png"))
        
        # Connect to the database
        self.conn = sqlite3.connect('notes.db')
        self.create_table()

        # UI elements
        self.create_widgets()

    def create_table(self):
        # A table to store notes
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS notes (
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

        
        # Note creation section
        note_layout = QVBoxLayout()
        layout.addLayout(note_layout)

        # Define the "Add note" button to open the new window
        add_button = QPushButton("Add note")
        add_button.clicked.connect(self.open_add_note_window)
        note_layout.addWidget(add_button)

        # Note display section
        self.note_tree = QTreeWidget()
        self.note_tree.setColumnCount(4)  # Set the number of columns
        self.note_tree.setHeaderLabels(["ID", "Title", "Date", "Time"])  # Add headers
        self.note_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.note_tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.note_tree)

        # Connect double click event to view note
        self.note_tree.itemDoubleClicked.connect(self.view_selected_note)
        
        # Load existing notes
        self.load_notes()
        
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

    def open_add_note_window(self):
        # Create and open the new window for adding notes
        add_window = AddNoteWindow()
        if add_window.exec_() == QDialog.Accepted:
            # If the user clicks "Add" in the new window, add the note
            self.add_note(add_window.title_entry.text(), add_window.notes_entry.toPlainText())

    def add_note(self, title, notes):
        # Automatically set the current date
        date = QDate.currentDate().toString(Qt.ISODate)
        # Get the current time in PC's timezone
        current_datetime = QDateTime.currentDateTime()
        time = current_datetime.time().toString("hh:mm AP")  # Format with AM/PM

        # Validate inputs
        if not title:
            QMessageBox.warning(self, "Error", "Please enter title.")
            return

        # Insert note into database with date and time
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO notes (title, date, time, notes) VALUES (?, ?, ?, ?)",
                       (title, date, time, notes))
        self.conn.commit()

        # Reload notes
        self.load_notes()

    def load_notes(self):
        # Clear existing data
        self.note_tree.clear()

        # Fetch notes from database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notes")
        notes = cursor.fetchall()

        # Display notes in TreeWidget
        for note in notes:
            item = QTreeWidgetItem([str(note[0]), note[1], note[2], note[3], ""])
            item.setData(4, Qt.UserRole, note[4])  # Store notes in UserRole for future use
            self.note_tree.addTopLevelItem(item)
            
    def view_selected_note(self, item, column):
        # Get the note title and text from the selected item
        title = item.text(1)  # Assuming the title is in the second column
        note = item.data(4, Qt.UserRole)
        # Open the view dialog with the selected note and title
        view_dialog = ViewNoteDialog(title, note)
        view_dialog.exec_()

    def show_context_menu(self, position):
        menu = QMenu(self)
        edit_action = QAction("Edit", self)
        delete_action = QAction("Delete", self)
        menu.addAction(edit_action)
        menu.addAction(delete_action)
        action = menu.exec_(self.note_tree.mapToGlobal(position))
        if action == edit_action:
            self.edit_selected_note()
        elif action == delete_action:
            self.delete_selected_note()

    def edit_selected_note(self):
        
        selected_item = self.note_tree.currentItem()
        if selected_item:
            note = selected_item.data(4, Qt.UserRole)
            new_note, ok = QInputDialog.getText(self, "Edit Note", "Edit your note:", QLineEdit.Normal, note)
            if ok:
                selected_item.setData(4, Qt.UserRole, new_note)
                selected_item.setText(4, new_note)
                
    def delete_selected_note(self):
        selected_item = self.note_tree.currentItem()
        if selected_item:
            confirmation = QMessageBox.question(self, "Delete Note", "Are you sure you want to delete this note?",
                                                QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                note_id = selected_item.text(0)
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                self.conn.commit()
                self.note_tree.takeTopLevelItem(self.note_tree.indexOfTopLevelItem(selected_item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteApp()
    window.show()
    sys.exit(app.exec_())
