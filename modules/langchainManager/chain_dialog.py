from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt


class ChainDialog(QDialog):
    def __init__(self, parent=None, title="Create/Edit Chain", chain_data=None, prompts=None, models=None,
                 output_parsers=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.chain_data = chain_data if chain_data else {}
        self.prompts = prompts if prompts else []
        self.models = models if models else []
        self.output_parsers = output_parsers if output_parsers else []
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Chain Name
        self.chain_name_input = QLineEdit()
        self.chain_name_input.setText(self.chain_data.get("chain_name", ""))
        layout.addRow("Chain Name:", self.chain_name_input)

        # Prompt Selection
        self.prompt_combo = QComboBox()
        self.prompt_combo.addItems(self.prompts)
        self.prompt_combo.setCurrentText(self.chain_data.get("prompt_name", ""))
        layout.addRow("Select Prompt:", self.prompt_combo)

        # Model Selection
        self.model_combo = QComboBox()
        self.model_combo.addItems(self.models)
        self.model_combo.setCurrentText(self.chain_data.get("model_name", ""))
        layout.addRow("Select Model:", self.model_combo)

        # Output Parser Selection
        self.output_parser_combo = QComboBox()
        self.output_parser_combo.addItems(self.output_parsers)
        self.output_parser_combo.setCurrentText(self.chain_data.get("output_parser", ""))
        layout.addRow("Select Output Parser:", self.output_parser_combo)

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
        chain_name = self.chain_name_input.text().strip()
        prompt_name = self.prompt_combo.currentText().strip()
        model_name = self.model_combo.currentText().strip()
        output_parser = self.output_parser_combo.currentText().strip()

        # Basic Validation
        if not chain_name:
            QMessageBox.warning(self, "Input Error", "Chain Name cannot be empty.")
            return
        if not prompt_name:
            QMessageBox.warning(self, "Input Error", "Please select a Prompt.")
            return
        if not model_name:
            QMessageBox.warning(self, "Input Error", "Please select a Model.")
            return
        if not output_parser:
            QMessageBox.warning(self, "Input Error", "Please select an Output Parser.")
            return

        self.accept()

    def get_chain_data(self):
        return {
            "chain_name": self.chain_name_input.text().strip(),
            "prompt_name": self.prompt_combo.currentText().strip(),
            "model_name": self.model_combo.currentText().strip(),
            "output_parser": self.output_parser_combo.currentText().strip()
        }
