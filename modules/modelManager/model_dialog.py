# model_dialog.py

from PyQt6.QtWidgets import (
    QPushButton, QHBoxLayout,
    QMessageBox, QDialog, QFormLayout, QLineEdit, QComboBox,
    QInputDialog, QLabel
)
from PyQt6.QtCore import Qt

class ModelDialog(QDialog):
    def __init__(self, parent=None, name="", model=None, existing_api_key_names=None):
        super().__init__(parent)
        self.setWindowTitle("Model Configuration")
        self.setModal(True)
        self.model = model if model else {}
        self.existing_api_key_names = existing_api_key_names or []
        self.init_ui(name)

    def init_ui(self, name):
        layout = QFormLayout()

        # Model Name
        self.name_input = QLineEdit()
        self.name_input.setText(name)
        layout.addRow("Model Name:", self.name_input)

        # LLM Model Combo Box
        self.llm_model_input = QComboBox()
        self.llm_model_input.addItems(["ChatGPT", "LLaMA", "Claude.ai", "Other"])
        # Set the current selection if editing
        current_llm = self.model.get('llm_model', "ChatGPT")
        index = self.llm_model_input.findText(current_llm)
        if index != -1:
            self.llm_model_input.setCurrentIndex(index)
        else:
            # If the current_llm is not in the list, add it
            self.llm_model_input.addItem(current_llm)
            self.llm_model_input.setCurrentText(current_llm)
        layout.addRow("LLM Model:", self.llm_model_input)

        # Connect "Other" selection to allow custom input
        self.llm_model_input.currentTextChanged.connect(self.handle_llm_selection)

        # API Key Name as ComboBox
        self.api_key_name_input = QComboBox()
        self.api_key_name_input.setEditable(True)
        self.api_key_name_input.addItems(self.existing_api_key_names)
        self.api_key_name_input.setCurrentText(self.model.get('api_key_name', ''))
        layout.addRow("API Key Name:", self.api_key_name_input)

        # # API Key
        # self.api_key_input = QLineEdit()
        # self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        # self.api_key_input.setText(self.model.get('api_key', ''))
        # layout.addRow("API Key:", self.api_key_input)

        # Model Type
        self.type_input = QLineEdit()
        self.type_input.setText(self.model.get('type', ''))
        layout.addRow("Model Type:", self.type_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)

        self.setLayout(layout)

        # Connect buttons to functions
        self.save_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    def handle_llm_selection(self, text):
        if text == "Other":
            custom_llm, ok = QInputDialog.getText(self, "Custom LLM Model", "Enter custom LLM model name:")
            if ok and custom_llm.strip():
                # Replace "Other" with the custom input
                index = self.llm_model_input.findText("Other")
                if index != -1:
                    self.llm_model_input.setItemText(index, custom_llm.strip())
            else:
                # Revert to a default if no input is provided
                self.llm_model_input.setCurrentText("ChatGPT")

    def validate_and_accept(self):
        model_name = self.name_input.text().strip()
        model_type = self.type_input.text().strip()
        llm_model = self.llm_model_input.currentText().strip()
        api_key_name = self.api_key_name_input.currentText().strip()

        # Basic Validation
        if not model_name:
            QMessageBox.warning(self, "Input Error", "Model Name cannot be empty.")
            return
        if not model_type:
            QMessageBox.warning(self, "Input Error", "Model Type cannot be empty.")
            return
        if not api_key_name:
            QMessageBox.warning(self, "Input Error", "API Key Name cannot be empty.")
            return
        if not llm_model:
            QMessageBox.warning(self, "Input Error", "LLM Model must be selected.")
            return

        # Additional validations can be added here

        self.accept()

    def get_model_data(self):
        return {
            "name": self.name_input.text().strip(),
            "type": self.type_input.text().strip(),
            "llm_model": self.llm_model_input.currentText().strip(),
            "api_key_name": self.api_key_name_input.currentText().strip(),
        }
