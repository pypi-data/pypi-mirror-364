from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QGroupBox, QDialog, QDialogButtonBox,
                               QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox, QWidget, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QFileDialog, QCompleter)
from PySide6.QtCore import Qt, QLocale
import csv
import numpy as np


class MultiLayerSampleCreateDialog(QDialog):
    def __init__(self, managers, parent=None, data=None):
        super().__init__(parent)

        if data is None:
            self.setWindowTitle("Create MultiLayer Sample")
        else:
            self.setWindowTitle("Edit MultiLayer Sample")
        self.setModal(True)
        self.resize(700, 700)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create main form
        self.form = setup_multilayer_sample_parameters(layout)
        prepare_multilayer_sample_parameters(self.form, managers)

        # OK/Cancel buttons (create before connecting signals)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(button_box)

        # Connect validation signals
        self.connect_validation_signals()

        if data:
            self.fill_form(data, managers)

        # Initial validation
        self.validate_form()

    def fill_form(self, data, managers):
        """Fill the form with existing data"""
        prepare_multilayer_sample_parameters(self.form, managers)

        # Handle distance
        if 'distance_port_sample' in data:
            self.form['distance_port_sample'].setValue(data['distance_port_sample'] * 1000)  # Convert m to mm

        # Handle calibration
        if 'calibration' in data:
            calib_map = {'trl': 1, 'norm': 0}
            self.form['calibration'].setCurrentIndex(calib_map.get(data['calibration'], 0))

        # Handle number of reflections
        if 'num_reflections' in data:
            self.form['num_reflections'].setValue(data['num_reflections'])

        # Handle rotation
        if 'rotation' in data:
            rot = data['rotation']
            if isinstance(rot, (list, tuple)) and len(rot) >= 3:
                self.form['rotation_x'].setValue(rot[0])
                self.form['rotation_y'].setValue(rot[1])
                self.form['rotation_z'].setValue(rot[2])

        # Handle GBTC Port source
        if 'source' in data:
            source_uuid = data['source']
            index = self.form['source_port'].findData(source_uuid)
            if index >= 0:
                self.form['source_port'].setCurrentIndex(index)

        # Handle layers (MUT)
        if 'mut' in data:
            layers = data['mut']
            self.form['layers_table'].setRowCount(len(layers))

            for i, layer in enumerate(layers):
                # CSV Browse button
                browse_btn = QPushButton("📁")
                browse_btn.setFixedWidth(40)
                browse_btn.clicked.connect(lambda checked, row=i: self.browse_csv_for_row(row))
                self.form['layers_table'].setCellWidget(i, 0, browse_btn)

                # Epsilon_r
                epsilon_r = layer.get('epsilon_r', 1.0)
                if isinstance(epsilon_r, str) and epsilon_r.endswith('.csv'):
                    # It's a CSV file path
                    epsilon_str = epsilon_r
                elif isinstance(epsilon_r, complex):
                    epsilon_str = f"{epsilon_r.real:.6g}{epsilon_r.imag:+.6g}j"
                else:
                    epsilon_str = f"{epsilon_r:.6g}"
                self.form['layers_table'].setItem(i, 1, QTableWidgetItem(epsilon_str))

                # Thickness
                thickness = layer.get('thickness', 0.0)
                thickness_str = f"{thickness * 1000:.6g}"  # Convert m to mm
                self.form['layers_table'].setItem(i, 2, QTableWidgetItem(thickness_str))

    def browse_csv_for_row(self, row):
        """Browse CSV file for specific row"""
        # Get current file path if it exists
        current_item = self.form['layers_table'].item(row, 1)
        start_directory = ""

        if current_item and current_item.text().strip():
            current_path = current_item.text().strip()
            # Check if current text is a file path
            if current_path.endswith('.csv'):
                import os
                if os.path.exists(current_path):
                    start_directory = os.path.dirname(current_path)
                elif os.path.exists(os.path.dirname(current_path)):
                    start_directory = os.path.dirname(current_path)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file for epsilon_r",
            start_directory,
            "CSV files (*.csv);;All files (*)"
        )

        if file_path:
            # Set the CSV file path in the epsilon_r column
            self.form['layers_table'].setItem(row, 1, QTableWidgetItem(file_path))
            self.validate_form()

    def connect_validation_signals(self):
        """Connect signals for form validation"""
        self.form['distance_port_sample'].valueChanged.connect(self.validate_form)
        self.form['calibration'].currentTextChanged.connect(self.validate_form)
        self.form['num_reflections'].valueChanged.connect(self.validate_form)
        self.form['source_port'].currentTextChanged.connect(self.validate_form)
        self.form['layers_table'].cellChanged.connect(self.validate_form)

    def validate_form(self):
        """Validate form inputs and enable/disable OK button"""
        # Check if we have at least one layer
        layers_valid = self.form['layers_table'].rowCount() > 0

        # Check if all layers have valid data
        all_layers_valid = True
        for row in range(self.form['layers_table'].rowCount()):
            epsilon_item = self.form['layers_table'].item(row, 1)
            thickness_item = self.form['layers_table'].item(row, 2)

            if not epsilon_item or not thickness_item:
                all_layers_valid = False
                break

            epsilon_text = epsilon_item.text().strip()
            thickness_text = thickness_item.text().strip()

            if not epsilon_text or not thickness_text:
                all_layers_valid = False
                break

            # Try to parse epsilon_r
            try:
                self.parse_epsilon_r(epsilon_text)
            except:
                all_layers_valid = False
                break

            # Try to parse thickness
            try:
                float(thickness_text)
            except:
                all_layers_valid = False
                break

        # Distance validation
        distance_valid = self.form['distance_port_sample'].value() >= 0

        # Number of reflections validation
        reflections_valid = self.form['num_reflections'].value() >= 0

        # Source port validation
        source_valid = self.form['source_port'].currentData() is not None

        # Enable OK button if all validations pass
        is_valid = (layers_valid and all_layers_valid and distance_valid and
                    reflections_valid and source_valid)

        self.ok_button.setEnabled(is_valid)

        # Update remove button state
        self.update_remove_button_state()

        # Set tooltip based on validation state
        if not source_valid:
            self.ok_button.setToolTip("Please select a GBTC Port source.")
        elif not layers_valid:
            self.ok_button.setToolTip("At least one layer is required.")
        elif not all_layers_valid:
            self.ok_button.setToolTip("All layers must have valid epsilon_r and thickness values.")
        elif not distance_valid:
            self.ok_button.setToolTip("Distance must be >= 0.")
        elif not reflections_valid:
            self.ok_button.setToolTip("Number of reflections must be >= 0.")
        else:
            self.ok_button.setToolTip("Ready to create MultiLayer Sample.")

    def update_remove_button_state(self):
        """Update the remove button state based on number of layers"""
        if hasattr(self.form, 'remove_layer_btn'):
            # Disable remove button if only 1 layer remains
            layer_count = self.form['layers_table'].rowCount()
            self.form['remove_layer_btn'].setEnabled(layer_count > 1)

    def parse_epsilon_r(self, text):
        """Parse epsilon_r from text - can be real number, complex, or CSV file path"""
        text = text.strip().replace(' ', '')

        # Check if it's a file path
        if text.endswith('.csv'):
            return text  # Return file path as-is

        # Try to parse as complex number
        try:
            # Handle different complex number formats
            if 'j' in text or 'i' in text:
                # Replace 'i' with 'j' for Python complex parsing
                text = text.replace('i', 'j')
                return complex(text)
            else:
                # Real number
                return float(text)
        except:
            raise ValueError(f"Invalid epsilon_r format: {text}")

    def get_data(self):
        """Return form data"""
        return get_multilayer_sample_parameters(self.form)

    def accept(self):
        """Override accept to collect form data"""
        try:
            data = self.get_data()
            if data:
                super().accept()
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input",
                                f"Please check your input values:\n{str(e)}")


class MultiLayerSampleEdit(QGroupBox):
    def __init__(self, callback_fn, parent=None):
        super().__init__(parent)

        self.setTitle("MultiLayer Sample")
        self.setWindowTitle('GBTC Multilayer Sample')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.form = setup_multilayer_sample_parameters(layout)

        # Button
        apply_btn = QPushButton("Apply modifications")
        apply_btn.clicked.connect(callback_fn)
        layout.addWidget(apply_btn)

    def browse_csv_for_row(self, row):
        """Browse CSV file for specific row"""
        # Get current file path if it exists
        current_item = self.form['layers_table'].item(row, 1)
        start_directory = ""

        if current_item and current_item.text().strip():
            current_path = current_item.text().strip()
            # Check if current text is a file path
            if current_path.endswith('.csv'):
                import os
                if os.path.exists(current_path):
                    start_directory = os.path.dirname(current_path)
                elif os.path.exists(os.path.dirname(current_path)):
                    start_directory = os.path.dirname(current_path)

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file for epsilon_r",
            start_directory,
            "CSV files (*.csv);;All files (*)"
        )

        if file_path:
            # Set the CSV file path in the epsilon_r column
            self.form['layers_table'].setItem(row, 1, QTableWidgetItem(file_path))

    def fill(self, data, managers):
        """Fill the form with existing data"""
        prepare_multilayer_sample_parameters(self.form, managers)

        # Handle distance
        if 'distance_port_sample' in data:
            self.form['distance_port_sample'].setValue(data['distance_port_sample'] * 1000)  # Convert m to mm

        # Handle calibration
        if 'calibration' in data:
            calib_map = {'trl': 1, 'norm': 0}
            self.form['calibration'].setCurrentIndex(calib_map.get(data['calibration'], 0))

        # Handle number of reflections
        if 'num_reflections' in data:
            self.form['num_reflections'].setValue(data['num_reflections'])

        # Handle rotation
        if 'rotation' in data:
            rot = data['rotation']
            if isinstance(rot, (list, tuple)) and len(rot) >= 3:
                self.form['rotation_x'].setValue(rot[0])
                self.form['rotation_y'].setValue(rot[1])
                self.form['rotation_z'].setValue(rot[2])

        # Handle GBTC Port source
        if 'source' in data:
            source_uuid = data['source']
            index = self.form['source_port'].findData(source_uuid)
            if index >= 0:
                self.form['source_port'].setCurrentIndex(index)

        # Handle layers (MUT)
        if 'mut' in data:
            layers = data['mut']
            self.form['layers_table'].setRowCount(len(layers))

            for i, layer in enumerate(layers):
                # CSV Browse button
                browse_btn = QPushButton("📁")
                browse_btn.setFixedWidth(40)
                browse_btn.clicked.connect(lambda checked, row=i: self.browse_csv_for_row(row))
                self.form['layers_table'].setCellWidget(i, 0, browse_btn)

                # Epsilon_r
                epsilon_r = layer.get('epsilon_r', 1.0)
                if isinstance(epsilon_r, str) and epsilon_r.endswith('.csv'):
                    # It's a CSV file path
                    epsilon_str = epsilon_r
                elif isinstance(epsilon_r, complex):
                    epsilon_str = f"{epsilon_r.real:.6g}{epsilon_r.imag:+.6g}j"
                else:
                    epsilon_str = f"{epsilon_r:.6g}"
                self.form['layers_table'].setItem(i, 1, QTableWidgetItem(epsilon_str))

                # Thickness
                thickness = layer.get('thickness', 0.0)
                thickness_str = f"{thickness * 1000:.6g}"  # Convert m to mm
                self.form['layers_table'].setItem(i, 2, QTableWidgetItem(thickness_str))

    def get_parameters(self):
        """Return form parameters"""
        return get_multilayer_sample_parameters(self.form)

    def update_parameters(self, obj):
        """Return form parameters"""
        obj['parameters'] = get_multilayer_sample_parameters(self.form)


def get_multilayer_sample_parameters(form):
    """Get parameters from form"""

    # Parse layers from table
    layers = []
    for row in range(form['layers_table'].rowCount()):
        epsilon_item = form['layers_table'].item(row, 1)
        thickness_item = form['layers_table'].item(row, 2)

        if epsilon_item and thickness_item:
            epsilon_text = epsilon_item.text().strip()
            thickness_text = thickness_item.text().strip()

            if epsilon_text and thickness_text:
                # Parse epsilon_r
                if epsilon_text.endswith('.csv'):
                    epsilon_r = epsilon_text  # Keep as file path
                else:
                    epsilon_text = epsilon_text.replace(' ', '')
                    try:
                        if 'j' in epsilon_text or 'i' in epsilon_text:
                            epsilon_text = epsilon_text.replace('i', 'j')
                            epsilon_r = complex(epsilon_text)
                        else:
                            epsilon_r = float(epsilon_text)
                    except:
                        epsilon_r = 1.0

                # Parse thickness
                try:
                    thickness = float(thickness_text) * 1e-3  # Convert mm to m
                except:
                    thickness = 0.0

                layers.append({
                    'epsilon_r': epsilon_r,
                    'thickness': thickness
                })

    # Get calibration
    calibration = form['calibration'].currentData()

    # Get source port UUID
    source_uuid = form['source_port'].currentData()

    # Get rotation vector
    rotation_vector = [
        form['rotation_x'].value(),
        form['rotation_y'].value(),
        form['rotation_z'].value()
    ]

    return {
        'distance_port_sample': form['distance_port_sample'].value() * 1e-3,  # Convert mm to m
        'mut': layers,
        'calibration': calibration,
        'source': source_uuid,
        'num_reflections': form['num_reflections'].value(),
        'rotation': rotation_vector
    }


def setup_multilayer_sample_parameters(layout) -> dict:
    """Create the parameter input form"""

    # Force locale to use dots for decimal separator
    QLocale.setDefault(QLocale.c())

    form = {
        'distance_port_sample': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=0.0, maximum=10000.0, value=10.0),
        'calibration': QComboBox(),
        'source_port': QComboBox(),
        'num_reflections': QSpinBox(minimum=0, maximum=100, value=2),
        'rotation_x': QDoubleSpinBox(prefix='rx: ', suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
        'rotation_y': QDoubleSpinBox(prefix='ry: ', suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
        'rotation_z': QDoubleSpinBox(prefix='rz: ', suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
        'layers_table': QTableWidget(),
        'add_layer_btn': QPushButton("Add Layer"),
        'remove_layer_btn': QPushButton("Remove Layer")
    }

    # Set locale for all QDoubleSpinBox widgets
    for key, widget in form.items():
        if isinstance(widget, QDoubleSpinBox):
            widget.setLocale(QLocale.c())

    # Configure calibration
    form['calibration'].addItem("Norm", 'norm')
    form['calibration'].addItem("TRL", 'trl')

    # Configure source port (will be populated by prepare_multilayer_sample_parameters)
    form['source_port'].setEnabled(True)

    # GroupBox for sample parameters
    sample_group = QGroupBox("Sample Parameters")
    sample_layout = QFormLayout()

    sample_layout.addRow("GBTC TX Port Source:", form['source_port'])
    sample_layout.addRow("Distance Lens-Sample:", form['distance_port_sample'])
    sample_layout.addRow("Calibration Type:", form['calibration'])
    sample_layout.addRow("Number of Reflections:", form['num_reflections'])

    sample_group.setLayout(sample_layout)
    layout.addWidget(sample_group)

    # GroupBox for rotation
    rotation_group = QGroupBox("Rotation")
    rotation_layout = QHBoxLayout()

    rotation_layout.addWidget(form['rotation_x'])
    rotation_layout.addWidget(form['rotation_y'])
    rotation_layout.addWidget(form['rotation_z'])

    rotation_group.setLayout(rotation_layout)
    layout.addWidget(rotation_group)

    # GroupBox for layers
    layers_group = QGroupBox("Layers (Material Under Test)")
    layers_layout = QVBoxLayout()

    # Table for layers - 3 columns now
    form['layers_table'].setColumnCount(3)
    form['layers_table'].setHorizontalHeaderLabels(["Load", "Epsilon_r (complex)", "Thickness (mm)"])

    # Configure table to use full width
    header = form['layers_table'].horizontalHeader()

    # Column widths: Browse button (100px), Epsilon_r (stretch), Thickness (120px)
    header.setSectionResizeMode(0, QHeaderView.Fixed)
    header.resizeSection(0, 40)  # Fixed width for browse button

    header.setSectionResizeMode(1, QHeaderView.Stretch)  # Epsilon_r takes remaining space

    header.setSectionResizeMode(2, QHeaderView.Fixed)
    header.resizeSection(2, 120)  # Fixed width for thickness

    # Set minimum height and ensure table stretches
    form['layers_table'].setMinimumHeight(200)
    form['layers_table'].setSizePolicy(form['layers_table'].sizePolicy().horizontalPolicy(),
                                       form['layers_table'].sizePolicy().verticalPolicy())

    layers_layout.addWidget(form['layers_table'])

    # Buttons for layer management
    button_layout = QHBoxLayout()
    button_layout.addWidget(form['add_layer_btn'])
    button_layout.addWidget(form['remove_layer_btn'])
    button_layout.addStretch()

    layers_layout.addLayout(button_layout)
    layers_group.setLayout(layers_layout)
    layout.addWidget(layers_group)

    # Connect button signals
    form['add_layer_btn'].clicked.connect(lambda: add_layer(form))
    form['remove_layer_btn'].clicked.connect(lambda: remove_layer(form))

    # Add initial layer
    add_layer(form)

    return form


def add_layer(form):
    """Add a new layer to the table"""
    current_rows = form['layers_table'].rowCount()
    form['layers_table'].insertRow(current_rows)

    # Add browse button in first column
    browse_btn = QPushButton("📁")
    browse_btn.setFixedWidth(40)
    # We need to get the parent dialog/widget to connect the signal properly
    parent_widget = form['layers_table'].parent()
    while parent_widget and not hasattr(parent_widget, 'browse_csv_for_row'):
        parent_widget = parent_widget.parent()

    if parent_widget and hasattr(parent_widget, 'browse_csv_for_row'):
        browse_btn.clicked.connect(lambda checked, row=current_rows: parent_widget.browse_csv_for_row(row))

    form['layers_table'].setCellWidget(current_rows, 0, browse_btn)

    # Set default values for epsilon_r and thickness
    form['layers_table'].setItem(current_rows, 1, QTableWidgetItem("1.0"))
    form['layers_table'].setItem(current_rows, 2, QTableWidgetItem("1.0"))

    # Update remove button state
    update_remove_button_state(form)


def remove_layer(form):
    """Remove the selected layer from the table"""
    current_row = form['layers_table'].currentRow()

    # Don't allow removal if only 1 layer remains
    if form['layers_table'].rowCount() <= 1:
        QMessageBox.information(None, "Cannot Remove Layer",
                                "At least one layer must be present.")
        return

    if current_row >= 0:
        form['layers_table'].removeRow(current_row)
    else:
        # If no row is selected, remove the last row
        if form['layers_table'].rowCount() > 1:
            form['layers_table'].removeRow(form['layers_table'].rowCount() - 1)

    # Update remove button state
    update_remove_button_state(form)


def update_remove_button_state(form):
    """Update the remove button state based on number of layers"""
    if 'remove_layer_btn' in form:
        # Disable remove button if only 1 layer remains
        layer_count = form['layers_table'].rowCount()
        form['remove_layer_btn'].setEnabled(layer_count > 1)


def prepare_multilayer_sample_parameters(form, managers):
    """Prepare the form with available parameters"""
    # Clear existing items
    form['source_port'].clear()

    # Populate GBTC Port sources (TX type only)
    if managers and len(managers) > 0:
        # Assuming first manager is object_manager
        object_manager = managers[0]

        # Get GBTC Ports of type TX
        if hasattr(object_manager, 'get_objects_by_type'):
            gbtc_ports = object_manager.get_objects_by_type().get('GBTCPort', [])

            # Filter for TX ports only
            tx_ports = []
            for port_uuid, port in gbtc_ports:
                port_data = port['parameters']
                if port_data.get('port_type') == 'TX Port':
                    # Create display name
                    source_name = port.get('name', 'Unknown')
                    display_name = source_name
                    tx_ports.append((port_uuid, display_name))

            # Sort by display name
            tx_ports.sort(key=lambda x: x[1])

            # Add to combo box
            for port_uuid, display_name in tx_ports:
                form['source_port'].addItem(display_name, port_uuid)

    # If no ports available, add placeholder
    if form['source_port'].count() == 0:
        form['source_port'].addItem("No TX Ports available", None)
        form['source_port'].setEnabled(False)
    else:
        form['source_port'].setEnabled(True)


# Test application
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit


    class MockObjectManager:
        def get_objects_by_type(self):
            # Mock GBTC Ports for testing
            return {
                'GBTCPort': (
                    ('port-uuid-1', {
                        'name': 'Main TX',
                        'parameters': {
                            'port_type': 'TX Port',
                            'lens': {'focal': 0.1}
                        }}),
                    ('port-uuid-2', {
                        'name': 'RX1',
                        'parameters': {
                            'port_type': 'RX Port',
                            'lens': {'focal': 0.1}
                        }}),
                    ('port-uuid-3', {
                        'name': 'RX1',
                        'parameters': {
                            'port_type': 'TX Port',
                            'source_name': 'Secondary TX',
                            'lens': {'focal': 0.15}
                        }})
                )
            }


    class MockSourceManager:
        def get_sources(self, only_type=None):
            return []


    class TestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MultiLayer Sample Dialog Test")
            self.setGeometry(100, 100, 900, 600)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Button to open create dialog
            create_btn = QPushButton("Create New MultiLayer Sample")
            create_btn.clicked.connect(self.create_sample)
            layout.addWidget(create_btn)

            # Button to open edit dialog
            edit_btn = QPushButton("Edit Existing MultiLayer Sample")
            edit_btn.clicked.connect(self.edit_sample)
            layout.addWidget(edit_btn)

            # Text area to display results
            self.result_text = QTextEdit()
            self.result_text.setReadOnly(True)
            layout.addWidget(self.result_text)

        def create_sample(self):
            managers = [MockObjectManager(), MockSourceManager()]
            dialog = MultiLayerSampleCreateDialog(managers, self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                self.display_result("Created MultiLayer Sample", data)

        def edit_sample(self):
            managers = [MockObjectManager(), MockSourceManager()]

            # Sample existing data
            existing_data = {
                'distance_port_sample': 0.01,  # 10mm in meters
                'mut': [
                    {
                        'epsilon_r': 2.1,
                        'thickness': 0.001  # 1mm in meters
                    },
                    {
                        'epsilon_r': 30.5 - 16j,
                        'thickness': 0.0006  # 0.6mm in meters
                    }
                ],
                'calibration': 'trl',
                'source': 'port-uuid-1',  # Reference to TX Port
                'num_reflections': 3,
                'rotation': [10.0, 20.0, 30.0]
            }

            dialog = MultiLayerSampleCreateDialog(managers, self, existing_data)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                self.display_result("Edited MultiLayer Sample", data)

        def display_result(self, title, data):
            result_text = f"\n{title}:\n"
            result_text += f"Distance Port-Sample: {data['distance_port_sample'] * 1000:.4f} mm\n"
            result_text += f"Calibration: {data['calibration'].upper()}\n"
            result_text += f"Source GBTC Port: {data['source']}\n"
            result_text += f"Number of Reflections: {data['num_reflections']}\n"

            result_text += f"Rotation: [{data['rotation'][0]:.2f}°, {data['rotation'][1]:.2f}°, {data['rotation'][2]:.2f}°]\n"

            result_text += f"\nLayers ({len(data['mut'])}):\n"
            for i, layer in enumerate(data['mut']):
                result_text += f"  Layer {i + 1}:\n"
                result_text += f"    Epsilon_r: {layer['epsilon_r']}\n"
                result_text += f"    Thickness: {layer['thickness'] * 1000:.4f} mm\n"

            # Display the raw data structure
            result_text += f"\nRaw Data Structure:\n{data}\n"

            self.result_text.append(result_text)


    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())