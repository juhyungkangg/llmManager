from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QTextEdit, QMessageBox, QListWidget, QListWidgetItem,
    QInputDialog
)

class PromptDialog(QDialog):
    def __init__(self, parent=None, title="Create Prompt", prompt_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.prompt_data = prompt_data if prompt_data else {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form Layout for input fields
        form_layout = QFormLayout()

        # Prompt Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter prompt name")
        if 'prompt_name' in self.prompt_data:
            self.name_input.setText(self.prompt_data['prompt_name'])
        form_layout.addRow(QLabel("Prompt Name:"), self.name_input)

        # System Prompt Template
        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setFixedSize(600,300)
        self.system_prompt_input.setLineWrapColumnOrWidth(600)
        self.system_prompt_input.setPlaceholderText("Enter system prompt template")
        if 'system_prompt_template' in self.prompt_data:
            self.system_prompt_input.setText(self.prompt_data['system_prompt_template'])
        form_layout.addRow(QLabel("System Prompt Template:"), self.system_prompt_input)

        # User Prompt Template
        self.user_prompt_input = QTextEdit()
        self.user_prompt_input.setFixedSize(600,300)
        self.user_prompt_input.setLineWrapColumnOrWidth(600)
        self.user_prompt_input.setPlaceholderText("Enter user prompt template")
        if 'user_prompt_template' in self.prompt_data:
            self.user_prompt_input.setText(self.prompt_data['user_prompt_template'])
        form_layout.addRow(QLabel("User Prompt Template:"), self.user_prompt_input)

        # Keys Section
        self.keys_label = QLabel("Keys:")
        self.keys_list = QListWidget()
        self.keys_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        # Populate keys if editing an existing prompt
        if 'keys' in self.prompt_data:
            for key in self.prompt_data['keys']:
                self.keys_list.addItem(QListWidgetItem(key))

        # Add and Remove Buttons for Keys
        keys_buttons_layout = QHBoxLayout()
        self.add_key_button = QPushButton("Add Key")
        self.remove_key_button = QPushButton("Remove Key")
        keys_buttons_layout.addWidget(self.add_key_button)
        keys_buttons_layout.addWidget(self.remove_key_button)

        # Connect buttons
        self.add_key_button.clicked.connect(self.add_key)
        self.remove_key_button.clicked.connect(self.remove_key)

        # Assemble Keys Section
        layout.addLayout(form_layout)
        layout.addWidget(self.keys_label)
        layout.addWidget(self.keys_list)
        layout.addLayout(keys_buttons_layout)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect Save and Cancel buttons
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    def add_key(self):
        key, ok = QInputDialog.getText(self, "Add Key", "Enter key:")
        if ok and key.strip():
            key = key.strip()
            # Check for duplicates
            existing_keys = [self.keys_list.item(i).text() for i in range(self.keys_list.count())]
            if key in existing_keys:
                QMessageBox.warning(self, "Duplicate Key", f"The key '{key}' already exists.")
                return
            self.keys_list.addItem(QListWidgetItem(key))
        elif ok:
            QMessageBox.warning(self, "Invalid Input", "Key cannot be empty.")

    def remove_key(self):
        selected_items = self.keys_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a key to remove.")
            return
        for item in selected_items:
            self.keys_list.takeItem(self.keys_list.row(item))

    def validate_and_accept(self):
        prompt_name = self.name_input.text().strip()
        system_prompt = self.system_prompt_input.toPlainText().strip()
        user_prompt = self.user_prompt_input.toPlainText().strip()
        keys = [self.keys_list.item(i).text() for i in range(self.keys_list.count())]

        # Basic Validation
        if not prompt_name:
            QMessageBox.warning(self, "Input Error", "Prompt Name cannot be empty.")
            return
        if not system_prompt:
            QMessageBox.warning(self, "Input Error", "System Prompt Template cannot be empty.")
            return
        if not user_prompt:
            QMessageBox.warning(self, "Input Error", "User Prompt Template cannot be empty.")
            return
        # Removed the check for keys being non-empty

        # Additional validations can be added here

        self.accept()

    def get_prompt_data(self):
        return {
            "prompt_name": self.name_input.text().strip(),
            "system_prompt_template": self.system_prompt_input.toPlainText().strip(),
            "user_prompt_template": self.user_prompt_input.toPlainText().strip(),
            "keys": [self.keys_list.item(i).text() for i in range(self.keys_list.count())]
        }
