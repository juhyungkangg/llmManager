from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar, QHBoxLayout, QSpinBox, \
    QLineEdit
from PyQt6.QtWidgets import QApplication

class DecompressorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # File Selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Select ZST File:")
        self.file_path = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_button)

        # Chunk Size
        chunk_layout = QHBoxLayout()
        self.chunk_label = QLabel("Chunk Size (MB):")
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(1, 1000)
        self.chunk_size.setValue(100)
        chunk_layout.addWidget(self.chunk_label)
        chunk_layout.addWidget(self.chunk_size)

        # Start Button and Progress Bar
        action_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Decompression")
        self.start_button.clicked.connect(self.start_decompression)
        self.progress_bar = QProgressBar()
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.progress_bar)

        # Log/Output
        self.log_label = QLabel("Status: Waiting to start.")

        # Add all layouts to main layout
        layout.addLayout(file_layout)
        layout.addLayout(chunk_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.log_label)

        self.setLayout(layout)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select ZST File", "", "ZST Files (*.zst)")
        if file_path:
            self.file_path.setText(file_path)

    def start_decompression(self):
        # Placeholder for decompression logic
        zst_file = self.file_path.text()
        chunk = self.chunk_size.value()

        if not zst_file:
            self.log_label.setText("Status: Please select a ZST file.")
            return

        # Update status
        self.log_label.setText(f"Status: Decompressing {zst_file} in chunks of {chunk}MB...")

        # Simulate progress
        for i in range(1, 101):
            self.progress_bar.setValue(i)
            QApplication.processEvents()  # Keeps the UI responsive
            # Here, integrate actual decompression logic and update progress accordingly

        self.log_label.setText("Status: Decompression completed successfully.")
