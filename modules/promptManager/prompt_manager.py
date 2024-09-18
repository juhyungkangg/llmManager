from modules import *
from modules.promptManager.prompt_dialog import PromptDialog
from langchain_core.prompts import ChatPromptTemplate


class PromptManagerWidget(AbstractWidget):
    def __init__(self):
        super().__init__()
        self.load_prompts()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label
        label = QLabel("Configured Prompts:")
        layout.addWidget(label)

        # Prompt List
        self.prompt_list = QListWidget()
        self.prompt_list.itemClicked.connect(self.display_prompt_details)
        self.populate_prompt_list()
        layout.addWidget(self.prompt_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Prompt")
        self.edit_button = QPushButton("Edit Prompt")
        self.delete_button = QPushButton("Delete Prompt")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # Prompt Details
        self.details_label = QLabel("Prompt Details:")
        self.details_display = QLabel("")
        self.details_display.setWordWrap(True)
        layout.addWidget(self.details_label)
        layout.addWidget(self.details_display)

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_prompt)
        self.edit_button.clicked.connect(self.edit_prompt)
        self.delete_button.clicked.connect(self.delete_prompt)

        self.setLayout(layout)

    def save_prompts(self):
        """Save prompts to the JSON file."""
        try:
            with open(PROMPTS_STORAGE_PATH, 'w') as f:
                json.dump(self.prompts, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save prompts: {e}")

    def populate_prompt_list(self):
        """Populate the QListWidget with prompt names."""
        self.prompt_list.clear()
        for prompt_name in self.prompts:
            self.prompt_list.addItem(prompt_name)

    def display_prompt_details(self, item):
        """Display details of the selected prompt."""
        prompt_name = item.text()
        prompt = self.prompts.get(prompt_name, {})
        keys = prompt.get('keys', [])
        keys_formatted = ', '.join(keys)
        details = (
            f"Prompt Name: {prompt_name}\n\n"
            f"System Prompt Template:\n{prompt.get('system_prompt_template', '')}\n\n"
            f"User Prompt Template:\n{prompt.get('user_prompt_template', '')}\n\n"
            f"Keys: {keys_formatted}"
        )
        self.details_display.setText(details)

    def add_prompt(self):
        """Open a dialog to add a new prompt."""
        dialog = PromptDialog(self, title="Add New Prompt")
        if dialog.exec() == QDialog.DialogCode.Accepted:
            prompt_data = dialog.get_prompt_data()
            prompt_name = prompt_data['prompt_name']
            system_prompt = prompt_data['system_prompt_template']
            user_prompt = prompt_data['user_prompt_template']
            keys = prompt_data['keys']

            if prompt_name in self.prompts:
                QMessageBox.warning(self, "Error", f"Prompt '{prompt_name}' already exists.")
                return

            # Encrypt the API Key before storing if necessary
            # Assuming prompts don't have API keys; adjust if they do

            # Store only serializable data
            self.prompts[prompt_name] = {
                "system_prompt_template": system_prompt,
                "user_prompt_template": user_prompt,
                "keys": keys
                # "prompt": ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])
                # Removed 'prompt' as it's not JSON-serializable
            }

            self.save_prompts()
            self.populate_prompt_list()
            QMessageBox.information(self, "Success", f"Prompt '{prompt_name}' added successfully.")

    def edit_prompt(self):
        """Open a dialog to edit the selected prompt."""
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a prompt to edit.")
            return
        prompt_name = current_item.text()
        prompt = self.prompts.get(prompt_name, {})

        dialog = PromptDialog(
            self,
            title="Edit Prompt",
            prompt_data={
                "prompt_name": prompt_name,
                "system_prompt_template": prompt.get("system_prompt_template", ""),
                "user_prompt_template": prompt.get("user_prompt_template", ""),
                "keys": prompt.get("keys", [])
            }
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_prompt_data()
            new_prompt_name = updated_data['prompt_name']
            system_prompt = updated_data['system_prompt_template']
            user_prompt = updated_data['user_prompt_template']
            keys = updated_data['keys']

            if new_prompt_name != prompt_name and new_prompt_name in self.prompts:
                QMessageBox.warning(self, "Error", f"Prompt name '{new_prompt_name}' already exists.")
                return

            # If name changed, remove old entry
            if new_prompt_name != prompt_name:
                del self.prompts[prompt_name]

            # Update prompt configuration
            self.prompts[new_prompt_name] = {
                "system_prompt_template": system_prompt,
                "user_prompt_template": user_prompt,
                "keys": keys
                # "prompt": ChatPromptTemplate.from_messages([("system", system_prompt), ("user", user_prompt)])
                # Removed 'prompt' as it's not JSON-serializable
            }

            self.save_prompts()
            self.populate_prompt_list()
            QMessageBox.information(self, "Success", f"Prompt '{new_prompt_name}' updated successfully.")

    def delete_prompt(self):
        """Delete the selected prompt."""
        current_item = self.prompt_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a prompt to delete.")
            return
        prompt_name = current_item.text()
        confirm = QMessageBox.question(
            self, "Delete Prompt",
            f"Are you sure you want to delete the prompt '{prompt_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            del self.prompts[prompt_name]
            self.save_prompts()
            self.populate_prompt_list()
            self.details_display.setText("")
            QMessageBox.information(self, "Success", f"Prompt '{prompt_name}' deleted successfully.")

    def get_prompt_instance(self, prompt_name):
        """Reconstruct the ChatPromptTemplate instance from stored data."""
        prompt_data = self.prompts.get(prompt_name)
        if not prompt_data:
            QMessageBox.warning(self, "Error", f"Prompt '{prompt_name}' not found.")
            return None

        system_prompt = prompt_data.get('system_prompt_template')
        user_prompt = prompt_data.get('user_prompt_template')

        if not system_prompt or not user_prompt:
            QMessageBox.warning(self, "Error", f"Prompt '{prompt_name}' is incomplete.")
            return None

        return ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
