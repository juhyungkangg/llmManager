from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLineEdit, QLabel, QTableView
from PyQt6.QtCore import QAbstractTableModel, Qt, QModelIndex
import pandas as pd


class PandasModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])
        return None


class TextViewerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.df = pd.DataFrame()

    def init_ui(self):
        layout = QVBoxLayout()

        # File Selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("Select CSV File:")
        self.file_path = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(self.browse_button)

        # Filter Options
        filter_layout = QHBoxLayout()
        self.start_label = QLabel("Start Line:")
        self.start_input = QLineEdit()
        self.end_label = QLabel("End Line:")
        self.end_input = QLineEdit()
        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.apply_filter)
        filter_layout.addWidget(self.start_label)
        filter_layout.addWidget(self.start_input)
        filter_layout.addWidget(self.end_label)
        filter_layout.addWidget(self.end_input)
        filter_layout.addWidget(self.filter_button)

        # Table View
        self.table_view = QTableView()

        # Add to main layout
        layout.addLayout(file_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.table_view)

        self.setLayout(layout)

    def browse_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            self.file_path.setText(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            # For large files, read only the first 1000 rows initially
            self.df = pd.read_csv(file_path, chunksize=100000)
            self.current_chunk = next(self.df)
            self.display_data(self.current_chunk)
        except Exception as e:
            self.file_path.setText(f"Error loading file: {str(e)}")

    def apply_filter(self):
        try:
            start = int(self.start_input.text())
            end = int(self.end_input.text())
            # For simplicity, assume line numbers correspond to DataFrame indices
            filtered_data = self.current_chunk.iloc[start:end]
            self.display_data(filtered_data)
        except Exception as e:
            self.start_input.setText(f"Error: {str(e)}")

    def display_data(self, data):
        model = PandasModel(data)
        self.table_view.setModel(model)
