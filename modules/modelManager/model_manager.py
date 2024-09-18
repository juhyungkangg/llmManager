from modules import *
from modules.modelManager.model_dialog import *
from modules.apiKeyManagement.api_key_management import *

class ModelManagerWidget(AbstractWidget):
    def __init__(self):
        super().__init__()
        self.models = {}  # Initialize models dictionary
        self.load_key()
        self.load_models()
        self.load_api_keys()
        self.api_key_names = self.api_keys.keys()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label
        label = QLabel("Configured Models:")
        layout.addWidget(label)

        # Model List
        self.model_list = QListWidget()
        self.model_list.itemClicked.connect(self.display_model_details)
        self.populate_model_list()
        layout.addWidget(self.model_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Model")
        self.edit_button = QPushButton("Edit Model")
        self.delete_button = QPushButton("Delete Model")
        self.refresh_button = QPushButton("Refresh API Keys")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)
        layout.addLayout(button_layout)

        # Model Details (Optional)
        self.details_label = QLabel("Model Details:")
        self.details_display = QLabel("")
        self.details_display.setWordWrap(True)
        layout.addWidget(self.details_label)
        layout.addWidget(self.details_display)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_model)
        self.edit_button.clicked.connect(self.edit_model)
        self.delete_button.clicked.connect(self.delete_model)
        self.refresh_button.clicked.connect(self.refresh_api_keys)

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

    def load_api_keys(self):
        """Load API keys from the JSON file."""
        if not os.path.exists(API_KEYS_STORAGE_PATH):
            os.makedirs(os.path.dirname(API_KEYS_STORAGE_PATH), exist_ok=True)
            with open(API_KEYS_STORAGE_PATH, 'w') as f:
                json.dump({}, f)  # Initialize with empty dict

        try:
            with open(API_KEYS_STORAGE_PATH, 'r') as f:
                self.api_keys = json.load(f)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load API keys: {e}")
            self.api_keys = {}

    def save_models(self):
        """Save models to the JSON file."""
        try:
            with open(MODELS_STORAGE_PATH, 'w') as f:
                json.dump(self.models, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save models: {e}")

    def populate_model_list(self):
        """Populate the QListWidget with model names."""
        self.model_list.clear()
        for model_name in self.models:
            self.model_list.addItem(model_name)


    def display_model_details(self, item):
        """Display details of the selected model."""
        model_name = item.text()
        model = self.models.get(model_name, {})
        details = (
            f"Name: {model_name}\n"
            f"Type: {model.get('type', 'N/A')}\n"
            f"LLM Model: {model.get('llm_model', 'N/A')}\n"
            f"API Key Name: {model.get('api_key_name', 'N/A')}\n"
        )
        self.details_display.setText(details)

    def add_model(self):
        """Open a dialog to add a new model."""
        dialog = ModelDialog(self, existing_api_key_names=self.api_key_names)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            model_data = dialog.get_model_data()
            model_name = model_data['name']
            api_key_name = model_data['api_key_name']

            if model_name in self.models:
                QMessageBox.warning(self, "Error", f"Model '{model_name}' already exists.")
                return

            # Store only serializable data
            self.models[model_name] = {
                "type": model_data['type'],
                "llm_model": model_data['llm_model'],
                "api_key_name": api_key_name,
            }
            self.save_models()
            self.populate_model_list()
            QMessageBox.information(self, "Success", f"Model '{model_name}' added successfully.")

    def edit_model(self):
        """Open a dialog to edit the selected model."""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a model to edit.")
            return
        model_name = current_item.text()
        model = self.models.get(model_name, {})
        dialog = ModelDialog(
            self, model_name, model, existing_api_key_names=self.api_key_names
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_model_data()
            new_name = updated_data['name']
            new_api_key_name = updated_data['api_key_name']

            if new_name != model_name and new_name in self.models:
                QMessageBox.warning(self, "Error", f"Model name '{new_name}' already exists.")
                return

            # If name changed, remove old entry
            if new_name != model_name:
                del self.models[model_name]

            # Update model configuration
            self.models[new_name] = {
                "type": updated_data['type'],
                "llm_model": updated_data['llm_model'],
                "api_key_name": new_api_key_name,
            }
            self.save_models()
            self.populate_model_list()
            QMessageBox.information(self, "Success", f"Model '{new_name}' updated successfully.")

    def delete_model(self):
        """Delete the selected model."""
        current_item = self.model_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a model to delete.")
            return
        model_name = current_item.text()
        confirm = QMessageBox.question(
            self, "Delete Model",
            f"Are you sure you want to delete the model '{model_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            del self.models[model_name]
            self.save_models()
            self.populate_model_list()
            self.details_display.setText("")
            QMessageBox.information(self, "Success", f"Model '{model_name}' deleted successfully.")

    def refresh_api_keys(self):
        """Refresh the list of API Key Names from ApiKeyManagerWidget."""
        self.load_api_keys()
        self.api_key_names = self.api_keys.keys()
        # No immediate UI update needed since ModelDialog fetches API Key Names when opened
