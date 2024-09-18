# modules/llm_runner.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout,
    QLabel, QLineEdit, QProgressBar, QTextEdit, QMessageBox, QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import json

from modules.llmRunner.llm_runner_thread import *


class LLMRunnerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Chain Selection
        chain_layout = QHBoxLayout()
        self.chain_label = QLabel("Select LangChain:")
        self.chain_combo = QComboBox()
        # Load chains from the chains.json file
        self.load_chains()
        chain_layout.addWidget(self.chain_label)
        chain_layout.addWidget(self.chain_combo)

        # Input Directory
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Input Data Directory:")
        self.input_path = QLineEdit()
        self.input_path.setText("/Users/juhyung/Desktop/data/processed/news")
        self.input_browse = QPushButton("Browse")
        self.input_browse.clicked.connect(self.browse_input_dir)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_browse)

        # Output Directory
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Data Directory:")
        self.output_path = QLineEdit()
        self.output_path.setText("/Users/juhyung/Desktop/data/llm_processed/news")
        self.output_browse = QPushButton("Browse")
        self.output_browse.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse)

        # Batch Size
        batch_layout = QHBoxLayout()
        self.batch_label = QLabel("Batch Size:")
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 100000)
        self.batch_size.setValue(100)
        batch_layout.addWidget(self.batch_label)
        batch_layout.addWidget(self.batch_size)

        # Execute Button and Progress Bar
        execute_layout = QHBoxLayout()
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_llm)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_llm)
        self.stop_button.setEnabled(False)
        self.progress_bar = QProgressBar()
        execute_layout.addWidget(self.execute_button)
        execute_layout.addWidget(self.stop_button)
        execute_layout.addWidget(self.progress_bar)

        # Log/Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # Add all layouts to main layout
        layout.addLayout(chain_layout)
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(batch_layout)
        layout.addLayout(execute_layout)
        layout.addWidget(QLabel("Logs:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def load_chains(self):
        chains_path = "data/chains.json"
        if os.path.exists(chains_path):
            with open(chains_path, 'r') as f:
                chains = json.load(f)
                self.chain_combo.addItems(chains.keys())
        else:
            QMessageBox.warning(self, "Error", "No LangChains found. Please create a chain in Langchain Manager.")

    def browse_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Data Directory")
        if dir_path:
            self.input_path.setText(dir_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Data Directory")
        if dir_path:
            self.output_path.setText(dir_path)

    def execute_llm(self):
        chain_name = self.chain_combo.currentText()
        if not chain_name:
            QMessageBox.warning(self, "Error", "Please select a LangChain.")
            return
        input_dir = self.input_path.text()
        output_dir = self.output_path.text()
        batch_size = self.batch_size.value()

        if not os.path.isdir(input_dir):
            QMessageBox.warning(self, "Error", "Please select a valid input data directory.")
            return
        if not os.path.isdir(output_dir):
            QMessageBox.warning(self, "Error", "Please select a valid output data directory.")
            return

        # Load the selected chain configuration
        chains_path = "data/chains.json"
        with open(chains_path, 'r') as f:
            chains = json.load(f)
            chain_config = chains.get(chain_name, {})
            if not chain_config:
                QMessageBox.warning(self, "Error", "Selected LangChain configuration not found.")
                return

        # Disable execute button and enable stop button
        self.execute_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Initialize and start the thread
        self.thread = LLMRunnerThread(chain_config, input_dir, output_dir, batch_size)
        self.thread.progress.connect(self.update_progress)
        self.thread.log.connect(self.append_log)
        self.thread.finished_signal.connect(self.execution_finished)
        self.thread.start()

    def stop_llm(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.append_log("LLM Runner stopped by user.")
            self.execute_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def append_log(self, message):
        self.log_output.append(message)

    def execution_finished(self):
        self.execute_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        QMessageBox.information(self, "Execution Finished", "LLM Runner has completed the process.")
