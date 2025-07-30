from PySide6.QtWidgets import (QVBoxLayout, QLabel, QLineEdit, QGroupBox, QDialog, QHBoxLayout, QDialogButtonBox,
                               QMessageBox, QComboBox, QFormLayout, QDoubleSpinBox, QWidget, QPushButton, QCheckBox,
                               QSpinBox)
from PySide6.QtCore import Qt


class GBTCPortCreateDialog(QDialog):
    def __init__(self, managers, parent=None, data=None):
        super().__init__(parent)

        if data is None:
            self.setWindowTitle("Create GBTC Port")
        else:
            self.setWindowTitle("Edit GBTC Port")
        self.setModal(True)
        self.resize(350, 300)
        self.setMaximumHeight(300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create main form
        self.form = setup_gbtc_port_parameters(layout)
        prepare_gbtc_port_parameters(self.form, managers)

        # OK/Cancel buttons (create before connecting signals)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.ok_button = button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        layout.addWidget(button_box)

        # Connect port type change signal
        self.form['port_type'].currentTextChanged.connect(self.on_port_type_changed)

        # Connect positioning mode change signal
        self.form['positioning_mode'].currentTextChanged.connect(lambda: on_positioning_mode_changed(self.form))

        # Connect validation signals
        self.connect_validation_signals()

        if data:
            self.fill_form(data, managers)

        # Initialize visibility and validation
        self.on_port_type_changed(self.form['port_type'].currentText())

    def on_port_type_changed(self, port_type):
        """Handle port type change to show/hide appropriate controls"""
        is_tx_port = (port_type == "TX Port")
        self.form['also_rx_port'].setVisible(is_tx_port)

        # Show/hide frequency sweep group for TX ports only
        self.form['freq_sweep_group'].setVisible(is_tx_port)

        # Get the form layout for beam parameters
        beam_layout = self.form['beam_group'].layout()

        # Find and show/hide beam parameter widgets based on port type
        for i in range(beam_layout.rowCount()):
            label_item = beam_layout.itemAt(i, QFormLayout.LabelRole)
            field_item = beam_layout.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if label_widget and field_widget:
                    label_text = label_widget.text()

                    if label_text == "Source:":
                        # Show for TX Port
                        label_widget.setVisible(is_tx_port)
                        field_widget.setVisible(is_tx_port)
                    elif label_text in ["Port name:", "Waist radius w0:", "Waist position offset z0:"]:
                        # Show for RX Port
                        label_widget.setVisible(not is_tx_port)
                        field_widget.setVisible(not is_tx_port)

        # Show/hide positioning mode for RX ports only
        if hasattr(self, 'form') and 'port_group' in self.form:
            # Find the positioning mode row in the port group layout
            port_layout = self.form['port_group'].layout()
            for i in range(port_layout.rowCount()):
                label_item = port_layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label_widget = label_item.widget()
                    if label_widget.text() == "Positioning mode:":
                        field_item = port_layout.itemAt(i, QFormLayout.FieldRole)
                        label_widget.setVisible(not is_tx_port)
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(not is_tx_port)
                        break

        # Hide/show position and rotation groups for TX ports
        if hasattr(self, 'form') and 'port_group' in self.form:
            self.form['port_group'].setVisible(not is_tx_port)

        # Set default values for TX ports
        if is_tx_port:
            # Reset position to (0, 0, 0)
            self.form['position_x'].setValue(0.0)
            self.form['position_y'].setValue(0.0)
            self.form['position_z'].setValue(0.0)

            # Reset rotation to (0, 0, 0)
            self.form['rotation_x'].setValue(0.0)
            self.form['rotation_y'].setValue(0.0)
            self.form['rotation_z'].setValue(0.0)
        else:
            # For RX ports, trigger positioning mode update
            on_positioning_mode_changed(self.form)

        self.validate_form()

    def fill_form(self, data, managers):
        """Fill the form with existing data"""
        prepare_gbtc_port_parameters(self.form, managers)

        # Handle port type
        if 'port_type' in data:
            self.form['port_type'].setCurrentText(data['port_type'])

        # Handle positioning mode for RX ports - detect from presence of distance_lens_sample
        if data['port_type'] == 'RX Port':
            if 'port' in data and 'distance_lens_sample' in data['port']:
                self.form['positioning_mode'].setCurrentText("Relatif au sample")
            else:
                self.form['positioning_mode'].setCurrentText("Positionnement absolu")

        # Handle frequency sweep parameters for TX ports
        if data['port_type'] == 'TX Port' and 'frequency_sweep' in data:
            freq_sweep = data['frequency_sweep']
            if 'start' in freq_sweep:
                self.form['freq_start'].setValue(freq_sweep['start'])
            if 'stop' in freq_sweep:
                self.form['freq_stop'].setValue(freq_sweep['stop'])
            if 'num_points' in freq_sweep:
                self.form['freq_num_points'].setValue(freq_sweep['num_points'])

        # Handle lens parameters
        if 'lens' in data:
            lens_data = data['lens']
            if 'focal' in lens_data:
                self.form['focal_length'].setValue(lens_data['focal'] * 1000)  # Convert m to mm
            if 'R1' in lens_data:
                self.form['R1'].setValue(lens_data['R1'] * 1000)  # Convert m to mm
            if 'R2' in lens_data:
                self.form['R2'].setValue(lens_data['R2'] * 1000)  # Convert m to mm
            if 'radius' in lens_data:
                self.form['radius'].setValue(lens_data['radius'] * 1000)  # Convert m to mm
            if 'thickness' in lens_data:
                self.form['thickness'].setValue(lens_data['thickness'] * 1000)  # Convert m to mm
            if 'ior' in lens_data:
                self.form['ior'].setValue(lens_data['ior'])

        # Handle port parameters
        if 'port' in data:
            port = data['port']
            if 'w0' in port:
                self.form['w0'].setValue(port['w0'] * 1000)  # Convert m to mm
            if 'z0' in port:
                self.form['z0'].setValue(port['z0'] * 1000)  # Convert m to mm
            if 'distance_port_lens' in port:
                self.form['relative_distance'].setValue(port['distance_port_lens'] * 1000)  # Convert m to mm
            if 'distance_lens_sample' in port:
                self.form['distance_lens_sample'].setValue(port['distance_lens_sample'] * 1000)  # Convert m to mm

        # Handle source selection
        if 'source' in data:
            # TX Port - find and select the source by UUID
            index = self.form['source_list'].findData(data['source'])
            if index >= 0:
                self.form['source_list'].setCurrentIndex(index)
        elif 'source_name' in data:
            # RX Port - set the source name
            self.form['source_name'].setText(data['source_name'])

        # Handle position
        if 'position' in data:
            pos = data['position']
            if 'x' in pos:
                self.form['position_x'].setValue(pos['x'] * 1000)  # Convert m to mm
            if 'y' in pos:
                self.form['position_y'].setValue(pos['y'] * 1000)  # Convert m to mm
            if 'z' in pos:
                self.form['position_z'].setValue(pos['z'] * 1000)  # Convert m to mm

        # Handle rotation (assuming degrees)
        if 'rotation' in data:
            rot = data['rotation']
            if 'x' in rot:
                self.form['rotation_x'].setValue(rot['x'])
            if 'y' in rot:
                self.form['rotation_y'].setValue(rot['y'])
            if 'z' in rot:
                self.form['rotation_z'].setValue(rot['z'])

    def connect_validation_signals(self):
        """Connect signals for form validation"""
        self.form['port_type'].currentTextChanged.connect(self.validate_form)
        self.form['positioning_mode'].currentTextChanged.connect(self.validate_form)
        self.form['source_list'].currentTextChanged.connect(self.validate_form)
        self.form['freq_start'].valueChanged.connect(self.validate_form)
        self.form['freq_stop'].valueChanged.connect(self.validate_form)
        self.form['freq_num_points'].valueChanged.connect(self.validate_form)
        self.form['focal_length'].valueChanged.connect(self.validate_form)
        self.form['R1'].valueChanged.connect(self.validate_form)
        self.form['R2'].valueChanged.connect(self.validate_form)
        self.form['radius'].valueChanged.connect(self.validate_form)
        self.form['thickness'].valueChanged.connect(self.validate_form)
        self.form['ior'].valueChanged.connect(self.validate_form)
        self.form['relative_distance'].valueChanged.connect(self.validate_form)
        self.form['distance_lens_sample'].valueChanged.connect(self.validate_form)
        self.form['source_name'].textChanged.connect(self.validate_form)
        self.form['w0'].valueChanged.connect(self.validate_form)

    def validate_form(self):
        """Validate form inputs and enable/disable OK button"""
        # Check required fields
        port_type = self.form['port_type'].currentText()

        # Source validation depends on port type
        if port_type == "TX Port":
            source_valid = self.form['source_list'].currentData() is not None
            source_error = "Please select a source."

            # Frequency sweep validation for TX ports
            freq_start = self.form['freq_start'].value()
            freq_stop = self.form['freq_stop'].value()
            freq_num_points = self.form['freq_num_points'].value()

            freq_valid = (freq_start > 0 and freq_stop > freq_start and freq_num_points >= 2)
            if not freq_valid:
                if freq_start <= 0:
                    freq_error = "Start frequency must be greater than 0."
                elif freq_stop <= freq_start:
                    freq_error = "Stop frequency must be greater than start frequency."
                else:
                    freq_error = "Number of points must be at least 2."
        else:  # RX Port
            source_valid = bool(self.form['source_name'].text().strip())
            source_error = "Port name is required."
            # Also validate w0 for RX Port
            w0_valid = self.form['w0'].value() > 0
            freq_valid = True  # No frequency validation for RX ports

        # Common validations
        focal_length_valid = self.form['focal_length'].value() != 0.0  # Can be negative
        radius_valid = self.form['radius'].value() > 0
        thickness_valid = self.form['thickness'].value() > 0
        ior_valid = self.form['ior'].value() >= 1.0

        # For RX ports with relative positioning, validate distance_lens_sample
        distance_lens_sample_valid = True
        if (port_type == "RX Port" and
                self.form['positioning_mode'].currentText() == "Relatif au sample"):
            distance_lens_sample_valid = self.form['distance_lens_sample'].value() > 0

        # Enable OK button if all validations pass
        if port_type == "TX Port":
            is_valid = (source_valid and freq_valid and focal_length_valid and radius_valid and
                        thickness_valid and ior_valid)
        else:  # RX Port
            is_valid = (source_valid and w0_valid and focal_length_valid and radius_valid and
                        thickness_valid and ior_valid and distance_lens_sample_valid)

        self.ok_button.setEnabled(is_valid)

        # Set tooltip based on validation state
        if not source_valid:
            self.ok_button.setToolTip(source_error)
        elif port_type == "TX Port" and not freq_valid:
            self.ok_button.setToolTip(freq_error)
        elif port_type == "RX Port" and not w0_valid:
            self.ok_button.setToolTip("Waist radius must be greater than 0.")
        elif not focal_length_valid:
            self.ok_button.setToolTip("Focal length cannot be zero.")
        elif not radius_valid:
            self.ok_button.setToolTip("Lens radius must be greater than 0.")
        elif not thickness_valid:
            self.ok_button.setToolTip("Thickness must be greater than 0.")
        elif not ior_valid:
            self.ok_button.setToolTip("Index of refraction must be ≥ 1.0.")
        elif not distance_lens_sample_valid:
            self.ok_button.setToolTip("Distance lens-sample must be greater than 0.")
        else:
            self.ok_button.setToolTip("Ready to create GBTC port.")

    def get_data(self):
        """Return form data"""
        return get_gbtc_port_parameters(self.form)

    def accept(self):
        """Override accept to collect form data"""
        try:
            data = self.get_data()
            if data:
                super().accept()
        except Exception as e:
            QMessageBox.warning(self, "Invalid Input",
                                f"Please check your input values:\n{str(e)}")


class GBTCPortEdit(QGroupBox):
    def __init__(self, callback_fn, parent=None):
        super().__init__(parent)

        self.setTitle("GBTC Port")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.form = setup_gbtc_port_parameters(layout)

        # Connect port type change signal
        self.form['port_type'].currentTextChanged.connect(self.on_port_type_changed)

        # Connect positioning mode change signal
        self.form['positioning_mode'].currentTextChanged.connect(lambda: on_positioning_mode_changed(self.form))

        # Button
        apply_btn = QPushButton("Apply modifications")
        apply_btn.clicked.connect(callback_fn)
        layout.addWidget(apply_btn)

    def on_port_type_changed(self, port_type):
        """Handle port type change to show/hide appropriate controls"""
        is_tx_port = (port_type == "TX Port")
        self.form['also_rx_port'].setVisible(is_tx_port)

        # Show/hide frequency sweep group for TX ports only
        self.form['freq_sweep_group'].setVisible(is_tx_port)

        # Get the form layout for beam parameters
        beam_layout = self.form['beam_group'].layout()

        # Find and show/hide beam parameter widgets based on port type
        for i in range(beam_layout.rowCount()):
            label_item = beam_layout.itemAt(i, QFormLayout.LabelRole)
            field_item = beam_layout.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if label_widget and field_widget:
                    label_text = label_widget.text()

                    if label_text == "Source:":
                        # Show for TX Port
                        label_widget.setVisible(is_tx_port)
                        field_widget.setVisible(is_tx_port)
                    elif label_text in ["Port name:", "Waist radius w0:", "Waist position offset z0:"]:
                        # Show for RX Port
                        label_widget.setVisible(not is_tx_port)
                        field_widget.setVisible(not is_tx_port)

        # Show/hide positioning mode for RX ports only
        if hasattr(self, 'form') and 'port_group' in self.form:
            # Find the positioning mode row in the port group layout
            port_layout = self.form['port_group'].layout()
            for i in range(port_layout.rowCount()):
                label_item = port_layout.itemAt(i, QFormLayout.LabelRole)
                if label_item and label_item.widget():
                    label_widget = label_item.widget()
                    if label_widget.text() == "Positioning mode:":
                        field_item = port_layout.itemAt(i, QFormLayout.FieldRole)
                        label_widget.setVisible(not is_tx_port)
                        if field_item and field_item.widget():
                            field_item.widget().setVisible(not is_tx_port)
                        break

        # Hide/show position and rotation groups for TX ports
        if hasattr(self, 'form') and 'port_group' in self.form:
            self.form['port_group'].setVisible(not is_tx_port)

        # Set default values for TX ports
        if is_tx_port:
            # Reset position to (0, 0, 0)
            self.form['position_x'].setValue(0.0)
            self.form['position_y'].setValue(0.0)
            self.form['position_z'].setValue(0.0)

            # Reset rotation to (0, 0, 0)
            self.form['rotation_x'].setValue(0.0)
            self.form['rotation_y'].setValue(0.0)
            self.form['rotation_z'].setValue(0.0)
        else:
            # For RX ports, trigger positioning mode update
            on_positioning_mode_changed(self.form)

    def fill(self, data, managers):
        """Fill the form with existing data"""
        prepare_gbtc_port_parameters(self.form, managers)

        # Handle port type
        if 'port_type' in data:
            self.form['port_type'].setCurrentText(data['port_type'])

        # Handle positioning mode for RX ports - detect from presence of distance_lens_sample
        if data['port_type'] == 'RX Port':
            if 'port' in data and 'distance_lens_sample' in data['port']:
                self.form['positioning_mode'].setCurrentText("Relatif au sample")
            else:
                self.form['positioning_mode'].setCurrentText("Positionnement absolu")
        elif data.get('is_rx', False):
            self.form['also_rx_port'].setChecked(True)

        # Handle frequency sweep parameters for TX ports
        if data['port_type'] == 'TX Port' and 'frequency_sweep' in data:
            freq_sweep = data['frequency_sweep']
            if 'start' in freq_sweep:
                self.form['freq_start'].setValue(freq_sweep['start'])
            if 'stop' in freq_sweep:
                self.form['freq_stop'].setValue(freq_sweep['stop'])
            if 'num_points' in freq_sweep:
                self.form['freq_num_points'].setValue(freq_sweep['num_points'])

        # Handle lens parameters
        if 'lens' in data:
            lens_data = data['lens']
            if 'focal' in lens_data:
                self.form['focal_length'].setValue(lens_data['focal'] * 1000)  # Convert m to mm
            if 'R1' in lens_data:
                self.form['R1'].setValue(lens_data['R1'] * 1000)  # Convert m to mm
            if 'R2' in lens_data:
                self.form['R2'].setValue(lens_data['R2'] * 1000)  # Convert m to mm
            if 'radius' in lens_data:
                self.form['radius'].setValue(lens_data['radius'] * 1000)  # Convert m to mm
            if 'thickness' in lens_data:
                self.form['thickness'].setValue(lens_data['thickness'] * 1000)  # Convert m to mm
            if 'ior' in lens_data:
                self.form['ior'].setValue(lens_data['ior'])

        # Handle port parameters
        if 'port' in data:
            port = data['port']
            if 'w0' in port:
                self.form['w0'].setValue(port['w0'] * 1000)  # Convert m to mm
            if 'z0' in port:
                self.form['z0'].setValue(port['z0'] * 1000)  # Convert m to mm
            if 'distance_port_lens' in port:
                self.form['relative_distance'].setValue(port['distance_port_lens'] * 1000)  # Convert m to mm
            if 'distance_lens_sample' in port:
                self.form['distance_lens_sample'].setValue(port['distance_lens_sample'] * 1000)  # Convert m to mm

        # Handle source selection
        if 'source' in data:
            # TX Port - find and select the source by UUID
            index = self.form['source_list'].findData(data['source'])
            if index >= 0:
                self.form['source_list'].setCurrentIndex(index)
        elif 'source_name' in data:
            # RX Port - set the source name
            self.form['source_name'].setText(data['source_name'])

        # Handle position
        if 'position' in data:
            pos = data['position']
            self.form['position_x'].setValue(pos[0] * 1000)  # Convert m to mm
            self.form['position_y'].setValue(pos[1] * 1000)  # Convert m to mm
            self.form['position_z'].setValue(pos[2] * 1000)  # Convert m to mm

        # Handle rotation (assuming degrees)
        if 'rotation' in data:
            rot = data['rotation']
            self.form['rotation_x'].setValue(rot[0])
            self.form['rotation_y'].setValue(rot[1])
            self.form['rotation_z'].setValue(rot[2])

        # Initialize visibility after filling
        self.on_port_type_changed(self.form['port_type'].currentText())

    def get_parameters(self):
        """Return form parameters"""
        return get_gbtc_port_parameters(self.form)

    def update_parameters(self, obj):
        obj['parameters'] = get_gbtc_port_parameters(self.form)


def on_positioning_mode_changed(form):
    """Handle positioning mode change to show/hide appropriate controls"""
    # Only apply if this is an RX port
    if form['port_type'].currentText() == "RX Port":
        positioning_mode = form['positioning_mode'].currentText()
        is_absolute = (positioning_mode == "Positionnement absolu")

        port_layout = form['port_group'].layout()
        # Show/hide controls based on positioning mode
        for i in range(port_layout.rowCount()):
            label_item = port_layout.itemAt(i, QFormLayout.LabelRole)
            field_item = port_layout.itemAt(i, QFormLayout.FieldRole)

            if label_item and field_item:
                label_widget = label_item.widget()
                field_widget = field_item.widget()

                if label_widget and field_widget:
                    label_text = label_widget.text()

                    if label_text in ["Pos:", "Rot:"]:
                        # Show for absolute positioning
                        label_widget.setVisible(is_absolute)
                        field_widget.setVisible(is_absolute)
                    elif label_text == "Dist lens-sample:":
                        # Show for relative positioning
                        label_widget.setVisible(not is_absolute)
                        field_widget.setVisible(not is_absolute)


def get_gbtc_port_parameters(form):
    """Get parameters from form"""
    port_type = form['port_type'].currentText()

    # Base data structure
    data = {
        'port_type': port_type,
        'lens': {
            'focal': form['focal_length'].value() * 1e-3,  # Convert mm to m
            'R1': form['R1'].value() * 1e-3,  # Convert mm to m
            'R2': form['R2'].value() * 1e-3,  # Convert mm to m
            'radius': form['radius'].value() * 1e-3,  # Convert mm to m
            'thickness': form['thickness'].value() * 1e-3,  # Convert mm to m
            'ior': form['ior'].value()
        },
        'port': {
            'distance_port_lens': form['relative_distance'].value() * 1e-3,  # Convert mm to m
        }
    }

    # Add port-specific data
    if port_type == "TX Port":
        # For TX Port: store the selected source UUID
        selected_uuid = form['source_list'].currentData()
        if selected_uuid:
            data['source'] = selected_uuid

        data['is_rx'] = form['also_rx_port'].isChecked()

        # Add frequency sweep parameters for TX ports
        data['frequency_sweep'] = {
            'start': form['freq_start'].value(),  # GHz
            'stop': form['freq_stop'].value(),  # GHz
            'num_points': form['freq_num_points'].value()
        }

        # Always include position and rotation for TX ports
        data['position'] = (
            form['position_x'].value() * 1e-3,  # Convert mm to m
            form['position_y'].value() * 1e-3,  # Convert mm to m
            form['position_z'].value() * 1e-3  # Convert mm to m
        )
        data['rotation'] = (
            form['rotation_x'].value(),  # Degrees
            form['rotation_y'].value(),  # Degrees
            form['rotation_z'].value()  # Degrees
        )
    else:  # RX Port
        # For RX Port: store manual parameters
        data['source_name'] = form['source_name'].text().strip()
        data['port']['w0'] = form['w0'].value() * 1e-3  # Convert mm to m
        data['port']['z0'] = form['z0'].value() * 1e-3  # Convert mm to m

        # Determine positioning mode from UI
        positioning_mode = form['positioning_mode'].currentText()

        if positioning_mode == "Positionnement absolu":
            # Include absolute position and rotation
            data['position'] = (
                form['position_x'].value() * 1e-3,  # Convert mm to m
                form['position_y'].value() * 1e-3,  # Convert mm to m
                form['position_z'].value() * 1e-3  # Convert mm to m
            )
            data['rotation'] = (
                form['rotation_x'].value(),  # Degrees
                form['rotation_y'].value(),  # Degrees
                form['rotation_z'].value()  # Degrees
            )
        else:  # "Relatif au sample"
            # Include distance_lens_sample instead
            data['port']['distance_lens_sample'] = form['distance_lens_sample'].value() * 1e-3  # Convert mm to m

    return data


def setup_gbtc_port_parameters(layout) -> dict:
    """Create the parameter input form"""
    form = {
        'port_type': QComboBox(),
        'also_rx_port': QCheckBox(),
        'positioning_mode': QComboBox(),
        'source_list': QComboBox(),
        'freq_start': QDoubleSpinBox(prefix='start: ', suffix=' GHz', decimals=2, minimum=10, maximum=1000.0, value=220.0),
        'freq_stop': QDoubleSpinBox(prefix='stop: ', suffix=' GHz', decimals=2, minimum=10, maximum=1000.0, value=330.0),
        'freq_num_points': QSpinBox(prefix='pts: ', minimum=1, maximum=10000, value=1001),
        'focal_length': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=-10000.0, maximum=10000.0, value=100.0),
        'R1': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=-10000.0, maximum=10000.0, value=0.0),
        'R2': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=-10000.0, maximum=10000.0, value=-40.0),
        'radius': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=0.001, maximum=1000.0, value=50.0),
        'thickness': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=0.001, maximum=1000.0, value=13.0),
        'ior': QDoubleSpinBox(decimals=6, minimum=1.0, maximum=10.0, value=1.4),
        'relative_distance': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=-10000.0, maximum=10000.0, value=95.0),
        'distance_lens_sample': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=0.001, maximum=10000.0, value=100.0),
        'source_name': QLineEdit(),
        'w0': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=0.001, maximum=1000.0, value=10.0),
        'z0': QDoubleSpinBox(suffix=' mm', decimals=4, minimum=-1000.0, maximum=1000.0, value=0.0),
        'position_x': QDoubleSpinBox(suffix=' mm', decimals=2, minimum=-10000.0, maximum=10000.0, value=0.0),
        'position_y': QDoubleSpinBox(suffix=' mm', decimals=2, minimum=-10000.0, maximum=10000.0, value=0.0),
        'position_z': QDoubleSpinBox(suffix=' mm', decimals=3, minimum=-10000.0, maximum=10000.0, value=0.0),
        'rotation_x': QDoubleSpinBox(suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
        'rotation_y': QDoubleSpinBox(suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
        'rotation_z': QDoubleSpinBox(suffix=' °', decimals=2, minimum=-360.0, maximum=360.0, value=0.0),
    }

    # Configure port type
    form['port_type'].addItems(["TX Port", "RX Port"])
    form['port_type'].setCurrentText("TX Port")  # Default to TX Port

    form['also_rx_port'].setText("Act as RX port too (S11)")
    form['also_rx_port'].setChecked(False)  # Default to unchecked

    # Configure positioning mode
    form['positioning_mode'].addItems(["Positionnement absolu", "Relatif au sample"])
    form['positioning_mode'].setCurrentText("Positionnement absolu")  # Default to absolute

    # Configure source name
    form['source_name'].setPlaceholderText("e.g., RX1")

    # GroupBox for port type
    port_type_group = QGroupBox("Port Type")
    port_type_layout = QFormLayout()
    port_type_layout.addRow("Port type:", form['port_type'])
    port_type_layout.addRow("", form['also_rx_port'])
    port_type_group.setLayout(port_type_layout)
    layout.addWidget(port_type_group)

    # GroupBox for Gaussian beam parameters
    form['beam_group'] = QGroupBox("Gaussian Beam Parameters")
    beam_layout = QFormLayout()

    # For TX Port: show source list
    beam_layout.addRow("Source:", form['source_list'])

    # For RX Port: show manual parameters
    beam_layout.addRow("Port name:", form['source_name'])
    beam_layout.addRow("Waist radius w0:", form['w0'])
    beam_layout.addRow("Waist position offset z0:", form['z0'])

    form['beam_group'].setLayout(beam_layout)
    layout.addWidget(form['beam_group'])

    # GroupBox for frequency sweep (TX ports only)
    form['freq_sweep_group'] = QGroupBox("Frequency Sweep")
    freq_layout = QHBoxLayout()
    freq_layout.addWidget(form['freq_start'])
    freq_layout.addWidget(form['freq_stop'])
    freq_layout.addWidget(form['freq_num_points'])
    form['freq_sweep_group'].setLayout(freq_layout)
    layout.addWidget(form['freq_sweep_group'])

    # GroupBox for lens parameters and positioning
    lens_group = QGroupBox("Lens Parameters and Positioning")
    lens_layout = QFormLayout()

    lens_layout.addRow("Focal length:", form['focal_length'])
    lens_layout.addRow("Radius of curvature R1:", form['R1'])
    lens_layout.addRow("Radius of curvature R2:", form['R2'])
    lens_layout.addRow("Lens radius:", form['radius'])
    lens_layout.addRow("Thickness:", form['thickness'])
    lens_layout.addRow("Index of refraction:", form['ior'])
    lens_layout.addRow("Relative distance:", form['relative_distance'])

    lens_group.setLayout(lens_layout)
    layout.addWidget(lens_group)

    # GroupBox for port positioning
    form['port_group'] = QGroupBox("Port Positioning")
    port_layout = QFormLayout()

    # Positioning mode (only for RX ports)
    port_layout.addRow("Mode:", form['positioning_mode'])

    # Position layout
    position_widget = QWidget()
    position_layout = QHBoxLayout(position_widget)
    position_layout.setContentsMargins(0, 0, 0, 0)
    position_layout.addWidget(form['position_x'])
    position_layout.addWidget(form['position_y'])
    position_layout.addWidget(form['position_z'])
    port_layout.addRow("Pos:", position_widget)

    # Rotation layout
    rotation_widget = QWidget()
    rotation_layout = QHBoxLayout(rotation_widget)
    rotation_layout.setContentsMargins(0, 0, 0, 0)
    rotation_layout.addWidget(form['rotation_x'])
    rotation_layout.addWidget(form['rotation_y'])
    rotation_layout.addWidget(form['rotation_z'])
    port_layout.addRow("Rot:", rotation_widget)

    port_layout.addRow("Dist lens-sample:", form['distance_lens_sample'])

    form['port_group'].setLayout(port_layout)
    layout.addWidget(form['port_group'])

    return form


def prepare_gbtc_port_parameters(form, managers):
    """Prepare the form with available sources"""
    # Get available sources - only GaussianBeam for TX ports
    sources = get_gbtc_compatible_sources(managers)

    form['source_list'].clear()
    form['source_list'].addItem('None', None)

    for item_id, item in sources:
        name = item.get('name', f'Source {item_id[:8]}')  # Use name or fallback
        form['source_list'].addItem(name, item_id)  # Display name, store UUID


def get_gbtc_compatible_sources(managers):
    """Get sources compatible with GBTC - only GaussianBeam sources"""
    sources = []

    # Only get GaussianBeam sources for TX ports from source manager
    if len(managers) > 1:
        try:
            gb_sources = managers[1].get_sources(only_type='GaussianBeam')
            sources.extend(gb_sources)
        except:
            pass

    return sources


# Test application
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit


    class MockObjectManager:
        def get_objects_by_type(self):
            return {
                'GBE': [
                    ("12345678-1234-1234-1234-123456789abc", {"name": "GBE 1"}),
                    ("87654321-4321-4321-4321-cba987654321", {"name": "GBE 2"})
                ],
                'Domain': [
                    ("domain-1234", {"name": "Domain 1"})
                ],
                'GBTCPort': [
                    ("port-1234", {"name": "Port 1"})
                ]
            }


    class MockSourceManager:
        def get_sources(self, only_type=None):
            if only_type == 'GaussianBeam':
                return [
                    ("gb-5678", {"name": "Gaussian Beam 1"}),
                    ("gb-9012", {"name": "Gaussian Beam 2"}),
                    ("gb-abcd", {"name": "Main TX Source"})
                ]
            return []


    class TestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("GBTC Port Dialog Test")
            self.setGeometry(100, 100, 600, 400)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Button to open create dialog
            create_btn = QPushButton("Create New GBTC Port")
            create_btn.clicked.connect(self.create_port)
            layout.addWidget(create_btn)

            # Button to open edit dialog
            edit_btn = QPushButton("Edit Existing GBTC Port")
            edit_btn.clicked.connect(self.edit_port)
            layout.addWidget(edit_btn)

            # Text area to display results
            self.result_text = QTextEdit()
            self.result_text.setReadOnly(True)
            layout.addWidget(self.result_text)

        def create_port(self):
            managers = [MockObjectManager(), MockSourceManager()]
            dialog = GBTCPortCreateDialog(managers, self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                self.display_result("Created GBTC Port", data)

        def edit_port(self):
            managers = [MockObjectManager(), MockSourceManager()]

            # Sample existing data for TX Port with frequency sweep
            existing_data_tx = {
                'port_type': 'TX Port',
                'frequency_sweep': {
                    'start': 2.0,  # GHz
                    'stop': 8.0,  # GHz
                    'num_points': 201
                },
                'lens': {
                    'ior': 1.4,
                    'focal': 0.1,  # 100mm in meters
                    'R1': 0.,  # Inf -> 0
                    'R2': -0.04,  # -40mm in meters
                    'radius': 0.05,  # 50mm in meters
                    'thickness': 0.013  # 13mm in meters
                },
                'port': {
                    'distance_port_lens': 0.095,  # 95mm in meters
                },
                'source': '12345678-1234-1234-1234-123456789abc',
                'position': (0.001, 0.002, 0.003),
                'rotation': (10.0, 20.0, 30.0)
            }

            dialog = GBTCPortCreateDialog(managers, self, existing_data_tx)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_data()
                self.display_result("Edited GBTC Port", data)

        def display_result(self, title, data):
            result_text = f"\n{title}:\n"
            result_text += f"Port Type: {data['port_type']}\n"

            # Display frequency sweep for TX ports
            if data['port_type'] == 'TX Port' and 'frequency_sweep' in data:
                freq = data['frequency_sweep']
                result_text += f"\nFrequency Sweep:\n"
                result_text += f"  Start: {freq['start']:.3f} GHz\n"
                result_text += f"  Stop: {freq['stop']:.3f} GHz\n"
                result_text += f"  Points: {freq['num_points']}\n"

            result_text += "\nLens Parameters:\n"
            lens = data['lens']
            result_text += f"  Focal Length: {lens['focal'] * 1000:.4f} mm\n"
            result_text += f"  R1: {lens['R1'] * 1000:.4f} mm\n"
            result_text += f"  R2: {lens['R2'] * 1000:.4f} mm\n"
            result_text += f"  Radius: {lens['radius'] * 1000:.4f} mm\n"
            result_text += f"  Thickness: {lens['thickness'] * 1000:.4f} mm\n"
            result_text += f"  Index of Refraction: {lens['ior']:.6f}\n"

            if 'port' in data:
                port = data['port']
                result_text += f"\nPort Parameters:\n"
                result_text += f"  Distance Port-Lens: {port['distance_port_lens'] * 1000:.4f} mm\n"
                if 'w0' in port:
                    result_text += f"  Waist Radius: {port['w0'] * 1000:.4f} mm\n"
                if 'z0' in port:
                    result_text += f"  Waist Position: {port['z0'] * 1000:.4f} mm\n"
                if 'distance_lens_sample' in port:
                    result_text += f"  Distance Lens-Sample: {port['distance_lens_sample'] * 1000:.4f} mm\n"

            if data['port_type'] == 'TX Port':
                result_text += f"\nSource Reference:\n"
                result_text += f"  Source UUID: {data.get('source', 'None')}\n"
            else:
                result_text += f"\nGaussian Beam:\n"
                result_text += f"  Port Name: {data.get('source_name', 'None')}\n"

            if 'position' in data:
                pos = data['position']
                result_text += f"\nPosition:\n"
                result_text += f"  X: {pos[0] * 1000:.4f} mm\n"
                result_text += f"  Y: {pos[1] * 1000:.4f} mm\n"
                result_text += f"  Z: {pos[2] * 1000:.4f} mm\n"

            if 'rotation' in data:
                rot = data['rotation']
                result_text += f"\nRotation:\n"
                result_text += f"  X: {rot[0]:.2f}°\n"
                result_text += f"  Y: {rot[1]:.2f}°\n"
                result_text += f"  Z: {rot[2]:.2f}°\n"

            # Display the raw data structure
            result_text += f"\nRaw Data Structure:\n{data}\n"

            self.result_text.append(result_text)


    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())