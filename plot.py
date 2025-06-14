import sys
import json
import inspect
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QSplitter, QTableWidget, QTableWidgetItem,
                             QPushButton, QGroupBox, QMessageBox, QHeaderView,
                             QAbstractItemView, QFileDialog, QToolBar, QAction,
                             QTreeWidget, QTreeWidgetItem, QLineEdit, QSpinBox,
                             QDoubleSpinBox, QComboBox, QTextEdit, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter
import pyqtgraph as pg

# Import shapes - with error handling
try:
    from shapes import *
    SHAPES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import shapes module: {e}")
    SHAPES_AVAILABLE = False

class NoScrollComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class ParameterTreeWidget(QTreeWidget):
    """Custom parameter tree widget for editing shape properties"""

    parameterChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(['Parameter', 'Value'])
        self.setAlternatingRowColors(True)
        self.current_shape_data = None
        # Disable scrolling
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def load_shape_data(self, shape_data):
        """Load shape data into the parameter tree"""
        self.clear()
        self.current_shape_data = shape_data.copy()

        # Add all parameters directly (no grouping except args)
        self.add_parameter(None, 'id', shape_data['id'], 'text')
        self.add_parameter(None, 'name', shape_data['name'], 'text')
        self.add_parameter(None, 'class', shape_data['class'], 'text')

        type_options = ['RF', 'Gradient', 'Signal', 'Trigger', 'Flag', 'General']
        self.add_parameter(None, 'type', shape_data['type'], 'combo', type_options)

        sel_options = ['low', 'medium', 'high', 'tunable', 'not_applicable']
        self.add_parameter(None, 'selectivity', shape_data['selectivity'], 'combo', sel_options)

        dur_options = ['short', 'medium', 'long']
        self.add_parameter(None, 'duration', shape_data['duration'], 'combo', dur_options)

        sar_options = ['low', 'medium', 'high', 'not_applicable']
        self.add_parameter(None, 'sar', shape_data['sar'], 'combo', sar_options)

        self.add_parameter(None, 'description', shape_data['description'], 'text_long')
        self.add_parameter(None, 'usage', shape_data['usage'], 'text_long')

        tags_str = ', '.join(shape_data['tags']) if isinstance(shape_data['tags'], list) else str(shape_data['tags'])
        self.add_parameter(None, 'tags', tags_str, 'text_long')

        # Arguments group - only group we keep
        args_group = QTreeWidgetItem(self, ['Arguments', ''])
        args_group.setExpanded(True)

        for arg_name, arg_value in shape_data['args'].items():
            if isinstance(arg_value, int):
                param_type = 'int'
            elif isinstance(arg_value, float):
                param_type = 'float'
            else:
                param_type = 'text'

            self.add_parameter(args_group, arg_name, arg_value, param_type)

    def add_parameter(self, parent, key, value, param_type, options=None):
        """Add a parameter to the tree"""
        if parent is None:
            item = QTreeWidgetItem(self, [key, ''])
        else:
            item = QTreeWidgetItem(parent, [key, ''])

        if param_type == 'text':
            widget = QLineEdit(str(value))
            widget.textChanged.connect(lambda: self.update_value(key, widget.text()))
        elif param_type == 'text_long':
            widget = QLineEdit(str(value))
            widget.textChanged.connect(lambda: self.update_value(key, widget.text()))
        elif param_type == 'int':
            widget = QSpinBox()
            widget.setRange(-10000, 10000)
            widget.setValue(int(value))
            widget.valueChanged.connect(lambda v: self.update_value(key, v))
        elif param_type == 'float':
            widget = QDoubleSpinBox()
            widget.setRange(-10000.0, 10000.0)
            widget.setDecimals(3)
            widget.setValue(float(value))
            widget.valueChanged.connect(lambda v: self.update_value(key, v))
        elif param_type == 'combo':
            widget = NoScrollComboBox()
            widget.addItems(options)
            widget.setCurrentText(str(value))
            widget.currentTextChanged.connect(lambda v: self.update_value(key, v))

        self.setItemWidget(item, 1, widget)
        return item

    def update_value(self, key, value):
        """Update value in the current shape data"""
        if not self.current_shape_data:
            return

        # Handle nested updates for args
        if key in self.current_shape_data:
            if key == 'tags' and isinstance(value, str):
                # Convert comma-separated string to list
                self.current_shape_data[key] = [tag.strip() for tag in value.split(',') if tag.strip()]
            else:
                self.current_shape_data[key] = value
        elif key in self.current_shape_data.get('args', {}):
            self.current_shape_data['args'][key] = value

        self.parameterChanged.emit()

    def get_current_data(self):
        """Get the current shape data"""
        return self.current_shape_data

class MRShapeGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MR Diagram Shape Manager - JSON Editor")
        self.setGeometry(100, 100, 1600, 1000)

        # Initialize data
        self.shapes_data = []
        self.current_shape_index = -1
        self.shape_classes = {}

        # Setup UI
        self.setup_ui()
        self.setup_toolbar()

        # Load data
        self.load_shapes_data()

        if SHAPES_AVAILABLE:
            self.shape_classes = self.get_shape_classes()

    def get_shape_classes(self):
        """Get all shape classes from the shapes module"""
        classes = {}
        for name, obj in globals().items():
            if (inspect.isclass(obj) and
                issubclass(obj, Shape) and
                obj != Shape):
                classes[name] = obj
        return classes

    def setup_toolbar(self):
        """Setup toolbar with actions"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Load action
        load_action = QAction("Load JSON", self)
        load_action.triggered.connect(self.load_json_file)
        toolbar.addAction(load_action)

        # Save action
        save_action = QAction("Save JSON", self)
        save_action.triggered.connect(self.save_json_file)
        toolbar.addAction(save_action)

    def setup_ui(self):
        """Setup the main user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Right panel (plot)
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (50-50)
        main_splitter.setSizes([800, 800])

    def create_left_panel(self):
        """Create left panel with table and parameter tree"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Create vertical splitter for table and parameter tree
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)

        # Top: Shape table
        table_group = QGroupBox("Shape Database")
        table_layout = QVBoxLayout(table_group)

        self.shape_table = QTableWidget()
        self.setup_table()
        table_layout.addWidget(self.shape_table)

        splitter.addWidget(table_group)

        # Bottom: Parameter tree
        params_group = QGroupBox("Shape Parameters")
        params_layout = QVBoxLayout(params_group)

        self.param_tree = ParameterTreeWidget()
        self.param_tree.parameterChanged.connect(self.on_parameter_changed)
        params_layout.addWidget(self.param_tree)

        # Update button
        update_btn = QPushButton("Update Shape")
        update_btn.clicked.connect(self.update_current_shape)
        params_layout.addWidget(update_btn)

        splitter.addWidget(params_group)

        # Set splitter proportions
        splitter.setSizes([400, 400])

        return widget

    def setup_table(self):
        """Setup the shape table"""
        headers = ['Name', 'Type', 'Class', 'Selectivity', 'Duration', 'SAR', 'Usage']
        self.shape_table.setColumnCount(len(headers))
        self.shape_table.setHorizontalHeaderLabels(headers)

        # Table properties
        self.shape_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shape_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shape_table.setAlternatingRowColors(True)

        # Auto-resize columns
        header = self.shape_table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # Connect selection
        self.shape_table.selectionModel().selectionChanged.connect(self.on_table_selection_changed)

    def create_right_panel(self):
        """Create right panel with plot"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Plot group
        plot_group = QGroupBox("Shape Visualization")
        plot_layout = QVBoxLayout(plot_group)

        # Create plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Normalized Time')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Style the plot
        self.plot_widget.getAxis('left').setPen(pg.mkPen(color='black', width=1))
        self.plot_widget.getAxis('bottom').setPen(pg.mkPen(color='black', width=1))
        self.plot_widget.getAxis('left').setTextPen(pg.mkPen(color='black'))
        self.plot_widget.getAxis('bottom').setTextPen(pg.mkPen(color='black'))

        plot_layout.addWidget(self.plot_widget)

        # Create icon label overlay
        self.icon_label_64 = QLabel(self.plot_widget)
        self.icon_label_64.setFixedSize(64, 64)
        self.icon_label_64.setStyleSheet("""
            QLabel {
                border: 2px solid #d20000;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 255);
            }
        """)
        self.icon_label_64.setAlignment(Qt.AlignCenter)
        self.icon_label_64.hide()  # Hidden initially

        # Create icon label overlay
        self.icon_label_32 = QLabel(self.plot_widget)
        self.icon_label_32.setFixedSize(32, 32)
        self.icon_label_32.setStyleSheet("""
            QLabel {
                border: 2px solid #d20000;
                border-radius: 2px;
                background-color: rgba(255, 255, 255, 255);
            }
        """)
        self.icon_label_32.setAlignment(Qt.AlignCenter)
        self.icon_label_32.hide()  # Hidden initially

        layout.addWidget(plot_group)

        return widget

    def load_shapes_data(self):
        """Load shapes data from JSON file"""
        try:
            with open('shapes.json', 'r') as f:
                data = json.load(f)
                self.shapes_data = data.get('shapes', [])
                self.populate_table()
        except FileNotFoundError:
            QMessageBox.information(self, "Info", "shapes.json not found. Starting with empty database.")
            self.shapes_data = []
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Invalid JSON format: {str(e)}")
            self.shapes_data = []

    def populate_table(self):
        """Populate the table with shape data"""
        self.shape_table.setRowCount(len(self.shapes_data))

        for row, shape in enumerate(self.shapes_data):
            items = [
                shape.get('name', ''),
                shape.get('type', ''),
                shape.get('class', ''),
                shape.get('selectivity', ''),
                shape.get('duration', ''),
                shape.get('sar', ''),
                shape.get('usage', '')[:50] + '...' if len(shape.get('usage', '')) > 50 else shape.get('usage', '')
            ]

            for col, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                self.shape_table.setItem(row, col, item)

    def on_table_selection_changed(self):
        """Handle table selection changes"""
        current_row = self.shape_table.currentRow()
        if 0 <= current_row < len(self.shapes_data):
            self.current_shape_index = current_row
            shape_data = self.shapes_data[current_row]

            # Load into parameter tree
            self.param_tree.load_shape_data(shape_data)

            # Plot the shape
            self.plot_current_shape()

    def on_parameter_changed(self):
        """Handle parameter changes"""
        # Auto-update plot when parameters change
        self.plot_current_shape()

    def plot_current_shape(self):
        """Plot the currently selected shape"""
        if self.current_shape_index < 0 or not SHAPES_AVAILABLE:
            return

        try:
            shape_data = self.param_tree.get_current_data()
            if not shape_data:
                return

            class_name = shape_data.get('class', '')
            if class_name not in self.shape_classes:
                self.plot_widget.clear()
                return

            # Create shape instance
            shape_class = self.shape_classes[class_name]
            shape_instance = shape_class(**shape_data['args'])

            # Get shape data
            if hasattr(shape_instance, 'shape') and shape_instance.shape is not None:
                y_data = shape_instance.shape
            else:
                y_data = shape_instance.generate()

            # Ensure y_data is numpy array
            if not isinstance(y_data, np.ndarray):
                y_data = np.array(y_data)

            # Create x-axis
            x_data = np.linspace(0, 1, len(y_data))

            # Plot
            self.plot_widget.clear()
            pen = pg.mkPen(color='blue', width=2)
            self.plot_widget.plot(x_data, y_data, pen=pen, name=shape_data['name'])

            # Generate and display icon overlay
            self.create_shape_icon(x_data, y_data)

        except Exception as e:
            print(f"Plot error: {e}")
            self.plot_widget.clear()

    def create_shape_icon(self, x_data, y_data):
        """Create a 64x64 QIcon from shape data and display it as overlay"""

        def create_pixmap(size, x_data, y_data):
            icon_size = size

            # Create pixmap
            pixmap = QPixmap(icon_size, icon_size)
            pixmap.fill(Qt.white)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Normalize data
            if len(y_data) > 0 and np.max(y_data) != np.min(y_data):
                y_norm = (y_data - np.min(y_data)) / (np.max(y_data) - np.min(y_data))
                x_norm = (x_data - np.min(x_data)) / (np.max(x_data) - np.min(x_data))

                # Draw shape
                if len(x_norm) > 1:
                    from PyQt5.QtGui import QPen
                    from PyQt5.QtCore import QPointF

                    pen = QPen(QColor(0, 0, 0), size/128)
                    painter.setPen(pen)

                    # Convert to pixel coordinates with margin
                    margin = 8
                    points = []
                    for i in range(len(x_norm)):
                        px = margin + (icon_size - 2*margin) * x_norm[i]
                        py = margin + (icon_size - 2*margin) * (1 - y_norm[i])  # Flip Y
                        points.append(QPointF(px, py))

                    # Draw lines between points
                    for i in range(len(points) - 1):
                        painter.drawLine(points[i], points[i + 1])

            painter.end()

            return pixmap

        try:
            # Create QIcon and set to label
            self.icon_label_64.setPixmap(create_pixmap(64, x_data, y_data))
            self.icon_label_32.setPixmap(create_pixmap(32, x_data, y_data))

            # Position icon overlay in top-right of plot
            self.position_icon_overlay()
            self.icon_label_64.show()
            self.icon_label_32.show()

        except Exception as e:
            print(f"Icon creation error: {e}")
            self.icon_label_64.setText("Error")
            self.icon_label_32.setText("Error")

    def position_icon_overlay(self):
        """Position the icon overlay in the top-right corner of the plot"""
        try:
            # Get plot widget geometry
            plot_geometry = self.plot_widget.geometry()

            # Position icon in top-right corner with margin
            margin = 5
            x = plot_geometry.x() + plot_geometry.width() - 100 - margin
            y = plot_geometry.y() - margin

            # Move the icon label to the correct position
            self.icon_label_64.move(x, y)
            self.icon_label_64.raise_()  # Bring to front

            self.icon_label_32.move(x - 64, y)
            self.icon_label_32.raise_()  # Bring to front

        except Exception as e:
            print(f"Icon positioning error: {e}")

    def resizeEvent(self, event):
        """Handle window resize to reposition icon"""
        super().resizeEvent(event)
        if hasattr(self, 'icon_label') and self.icon_label_64.isVisible():
            self.position_icon_overlay()

        if hasattr(self, 'icon_label') and self.icon_label_32.isVisible():
            self.position_icon_overlay()
    def update_current_shape(self):
        """Update the current shape in the database"""
        if self.current_shape_index < 0:
            QMessageBox.warning(self, "Warning", "No shape selected")
            return

        updated_data = self.param_tree.get_current_data()
        if updated_data:
            self.shapes_data[self.current_shape_index] = updated_data
            self.populate_table()

            # Reselect the current row
            self.shape_table.selectRow(self.current_shape_index)

            QMessageBox.information(self, "Success", "Shape updated successfully")

    def load_json_file(self):
        """Load JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Load JSON File", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.shapes_data = data.get('shapes', [])
                    self.populate_table()
                    QMessageBox.information(self, "Success", f"Loaded {len(self.shapes_data)} shapes")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")

    def save_json_file(self):
        """Save JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "shapes.json", "JSON Files (*.json)")
        if file_path:
            try:
                data = {"shapes": self.shapes_data}
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                QMessageBox.information(self, "Success", f"Saved {len(self.shapes_data)} shapes")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MRShapeGUI()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
