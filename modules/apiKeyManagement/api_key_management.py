import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout,
    QLabel, QMessageBox, QDialog, QFormLayout, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from cryptography.fernet import Fernet

from modules import *

API_KEYS_STORAGE_PATH = "data/api_keys.json"
SECRET_KEY_PATH = "secret.key"

class ApiKeyManagerWidget(AbstractWidget):
    # Signal to notify other widgets that API keys have been updated
    api_keys_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.api_keys = {}  # Initialize API keys dictionary
        self.load_key()
        self.load_api_keys()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label
        label = QLabel("API Keys:")
        layout.addWidget(label)

        # API Key List
        self.api_key_list = QListWidget()
        self.api_key_list.itemClicked.connect(self.display_api_key_details)
        self.populate_api_key_list()
        layout.addWidget(self.api_key_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add API Key")
        self.edit_button = QPushButton("Edit API Key")
        self.delete_button = QPushButton("Delete API Key")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # API Key Details
        self.details_label = QLabel("API Key Details:")
        self.details_display = QLabel("")
        self.details_display.setWordWrap(True)
        layout.addWidget(self.details_label)
        layout.addWidget(self.details_display)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_api_key)
        self.edit_button.clicked.connect(self.edit_api_key)
        self.delete_button.clicked.connect(self.delete_api_key)

        self.setLayout(layout)

    def load_key(self):
        """Load or generate the encryption key."""
        if not os.path.exists(SECRET_KEY_PATH):
            key = Fernet.generate_key()
            with open(SECRET_KEY_PATH, "wb") as key_file:
                key_file.write(key)
            os.chmod(SECRET_KEY_PATH, 0o600)  # Restrict permissions
        else:
            with open(SECRET_KEY_PATH, "rb") as key_file:
                key = key_file.read()
        self.fernet = Fernet(key)

    def save_api_keys(self):
        """Save API keys to the JSON file."""
        try:
            with open(API_KEYS_STORAGE_PATH, 'w') as f:
                json.dump(self.api_keys, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API keys: {e}")

    def populate_api_key_list(self):
        """Populate the QListWidget with API key names."""
        self.api_key_list.clear()
        for api_key_name in self.api_keys:
            self.api_key_list.addItem(api_key_name)

    def display_api_key_details(self, item):
        """Display details of the selected API key."""
        api_key_name = item.text()
        api_key_info = self.api_keys.get(api_key_name, {})
        description = api_key_info.get('description', 'No description provided.')
        details = (
            f"Name: {api_key_name}\n"
            f"Description: {description}\n"
            f"API Key: {'****' if api_key_info.get('api_key') else 'N/A'}"
        )
        self.details_display.setText(details)

    def add_api_key(self):
        """Open a dialog to add a new API key."""
        dialog = ApiKeyDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key_name, api_key, description = dialog.get_api_key_data()
            if api_key_name in self.api_keys:
                QMessageBox.warning(self, "Error", f"API Key Name '{api_key_name}' already exists.")
                return
            encrypted_api_key = self.encrypt_api_key(api_key)
            self.api_keys[api_key_name] = {
                "api_key": encrypted_api_key,
                "description": description
            }
            self.save_api_keys()
            self.populate_api_key_list()
            self.api_keys_updated.emit()  # Notify other widgets
            QMessageBox.information(self, "Success", f"API Key '{api_key_name}' added successfully.")

    def edit_api_key(self):
        """Open a dialog to edit the selected API key."""
        current_item = self.api_key_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select an API key to edit.")
            return
        api_key_name = current_item.text()
        api_key_info = self.api_keys.get(api_key_name, {})
        decrypted_api_key = self.decrypt_api_key(api_key_info.get('api_key', ''))
        description = api_key_info.get('description', '')
        dialog = ApiKeyDialog(self, api_key_name, decrypted_api_key, description, is_edit=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_api_key_name, new_api_key, new_description = dialog.get_api_key_data()
            if new_api_key_name != api_key_name and new_api_key_name in self.api_keys:
                QMessageBox.warning(self, "Error", f"API Key Name '{new_api_key_name}' already exists.")
                return
            encrypted_api_key = self.encrypt_api_key(new_api_key)
            # Remove old entry if name has changed
            if new_api_key_name != api_key_name:
                del self.api_keys[api_key_name]
            self.api_keys[new_api_key_name] = {
                "api_key": encrypted_api_key,
                "description": new_description
            }
            self.save_api_keys()
            self.populate_api_key_list()
            self.api_keys_updated.emit()  # Notify other widgets
            QMessageBox.information(self, "Success", f"API Key '{new_api_key_name}' updated successfully.")

    def delete_api_key(self):
        """Delete the selected API key."""
        current_item = self.api_key_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select an API key to delete.")
            return
        api_key_name = current_item.text()
        confirm = QMessageBox.question(
            self, "Delete API Key",
            f"Are you sure you want to delete the API key '{api_key_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            del self.api_keys[api_key_name]
            self.save_api_keys()
            self.populate_api_key_list()
            self.details_display.setText("")
            self.api_keys_updated.emit()  # Notify other widgets
            QMessageBox.information(self, "Success", f"API Key '{api_key_name}' deleted successfully.")

    def encrypt_api_key(self, api_key):
        """Encrypt the API key."""
        return self.fernet.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, encrypted_api_key):
        """Decrypt the API key."""
        try:
            return self.fernet.decrypt(encrypted_api_key.encode()).decode()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to decrypt API Key: {e}")
            return ""

class ApiKeyDialog(QDialog):
    def __init__(self, parent=None, name="", api_key="", description="", is_edit=False):
        super().__init__(parent)
        self.setWindowTitle("Edit API Key" if is_edit else "Add API Key")
        self.setModal(True)
        self.is_edit = is_edit
        self.init_ui(name, api_key, description)

    def init_ui(self, name, api_key, description):
        layout = QFormLayout()

        # API Key Name
        self.name_input = QLineEdit()
        self.name_input.setText(name)
        layout.addRow("API Key Name:", self.name_input)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(api_key)
        layout.addRow("API Key:", self.api_key_input)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description")
        self.description_input.setText(description)
        layout.addRow("Description:", self.description_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

        self.setLayout(layout)

        # Connect buttons
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    def validate_and_accept(self):
        api_key_name = self.name_input.text().strip()
        api_key = self.api_key_input.text().strip()
        # Description is optional

        # Basic Validation
        if not api_key_name:
            QMessageBox.warning(self, "Input Error", "API Key Name cannot be empty.")
            return
        if not api_key:
            QMessageBox.warning(self, "Input Error", "API Key cannot be empty.")
            return

        self.accept()

    def get_api_key_data(self):
        return (
            self.name_input.text().strip(),
            self.api_key_input.text().strip(),
            self.description_input.toPlainText().strip()
        )
