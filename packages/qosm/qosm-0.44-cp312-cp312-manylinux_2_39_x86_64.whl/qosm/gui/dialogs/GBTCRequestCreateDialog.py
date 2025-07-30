from PySide6.QtWidgets import (QVBoxLayout, QLabel, QGroupBox, QGridLayout, QDialog, QDialogButtonBox,
                               QComboBox, QPushButton, QFormLayout, QCheckBox)


class GBTCRequestCreateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create GBTC Request")
        self.setModal(True)
        self.resize(350, 150)

        # link objects
        object_manager = parent.object_manager if hasattr(parent, "object_manager") else None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Set fields and combobox
        self.form = setup_gbtc_request_parameters(layout)
        prepare_gbtc_request_parameters(self.form, object_manager)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_parameters(self):
        try:
            return get_gbtc_request_parameters(self.form)

        except ValueError as e:
            print(e)
            return None


class GBTCRequestEdit(QDialog):
    def __init__(self, callback_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GBTC Request")
        self.setModal(True)
        self.resize(350, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Set fields and combobox
        self.form = setup_gbtc_request_parameters(layout)

        # Button
        request_update = QPushButton("Update")
        request_update.clicked.connect(callback_fn)
        layout.addWidget(request_update)

    def fill(self, data, managers):
        prepare_gbtc_request_parameters(self.form, managers[0], linked_port_uuid=data.get('port', None))

        # Set S parameter
        s_param_map = {'S11': 0, 'S21': 1}
        self.form['s_parameter'].setCurrentIndex(s_param_map[data['s_parameter']])

    def get_parameters(self):
        try:
            return get_gbtc_request_parameters(self.form)

        except ValueError as e:
            print(e)
            return None

    def update_parameters(self, obj):
        obj['parameters'] = get_gbtc_request_parameters(self.form)


def get_gbtc_request_parameters(form):
    return {
        's_parameter': form['s_parameter'].currentData(),
        'port': form['port'].currentData(),
    }


def setup_gbtc_request_parameters(layout) -> dict:
    # Initialization
    form = {
        's_parameter': QComboBox(),
        'port': QComboBox(),
    }

    # Parameters group
    group1 = QGroupBox("Request Parameters")
    group_layout1 = QFormLayout()
    group1.setLayout(group_layout1)

    # S Parameter selection
    form['s_parameter'].addItem("S11", 'S11')
    form['s_parameter'].addItem("S21", 'S21')

    group_layout1.addRow(QLabel("S Parameter:"), form['s_parameter'])
    group_layout1.addRow(QLabel("Connected Port:"), form['port'])

    layout.addWidget(group1)

    return form


def prepare_gbtc_request_parameters(form, object_manager, linked_port_uuid=None):
    """Prepare the form with available RX ports from GBTC objects"""
    if object_manager is None:
        return

    # Get all GBTC objects
    list_gbtc_objects = object_manager.get_objects_by_type().get('GBTCPort', [])

    form['port'].clear()
    form['port'].addItem('None', None)

    selected_id = 0
    i = 1

    for item_id, item in list_gbtc_objects:
        # Check if this GBTC object has RX ports
        params = item['parameters']
        if 'port_type' in params and (params['port_type'] == 'RX Port'
            or (params['port_type'] == 'TX Port' and params.get('is_rx', False))):
            # Create display name from port info
            if params['port_type'] == 'RX Port':
                port_name = params.get('source_name', f'RX Port {item_id[:8]}')
            else:
                port_name = item.get('name', f'TX Port {item_id[:8]}')
                port_name = f'TX/RX: {port_name}'
            form['port'].addItem(port_name, item_id)  # Display name, store UUID

            if item_id == linked_port_uuid:
                selected_id = i
            i += 1

            if params['port_type'] == 'TX Port':
                form['s_parameter'].setCurrentText('S11')

    if selected_id is not None:
        form['port'].setCurrentIndex(selected_id)


# Test application
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit


    class MockObjectManager:
        def get_objects_by_type(self):
            return {
                'GBTCPort': [
                    ("12345678-1234-1234-1234-123456789abc", {
                        "port_type": "RX Port",
                        "source_name": "RX Port 1",
                        "lens": {"focal": 0.1},
                        "port": {"w0": 0.01, "z0": 0.0}
                    }),
                    ("87654321-4321-4321-4321-cba987654321", {
                        "port_type": "TX Port",
                        "source": "some-source-uuid",
                        "lens": {"focal": 0.1}
                    }),
                    ("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", {
                        "port_type": "RX Port",
                        "source_name": "RX Port 2",
                        "lens": {"focal": 0.15},
                        "port": {"w0": 0.008, "z0": 0.0}
                    })
                ]
            }


    class TestMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("GBTC Request Dialog Test")
            self.setGeometry(100, 100, 600, 400)

            # Mock object manager
            self.object_manager = MockObjectManager()

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            # Button to open create dialog
            create_btn = QPushButton("Create New GBTC Request")
            create_btn.clicked.connect(self.create_request)
            layout.addWidget(create_btn)

            # Button to open edit dialog
            edit_btn = QPushButton("Edit Existing GBTC Request")
            edit_btn.clicked.connect(self.edit_request)
            layout.addWidget(edit_btn)

            # Text area to display results
            self.result_text = QTextEdit()
            self.result_text.setReadOnly(True)
            layout.addWidget(self.result_text)

        def create_request(self):
            dialog = GBTCRequestCreateDialog(self)
            if dialog.exec() == QDialog.Accepted:
                data = dialog.get_parameters()
                self.display_result("Created GBTC Request", data)

        def edit_request(self):
            # Sample existing data
            existing_data = {
                's_parameter': 'S21',
                'port': '12345678-1234-1234-1234-123456789abc',
            }

            dialog = GBTCRequestEdit(lambda: self.display_result("Updated GBTC Request", dialog.get_parameters()), self)
            dialog.fill(existing_data, [self.object_manager])
            dialog.exec()

        def display_result(self, title, data):
            if data is None:
                self.result_text.append(f"\n{title}: Invalid parameters\n")
                return

            result_text = f"\n{title}:\n"
            result_text += f"S Parameter: {data['s_parameter']}\n"
            result_text += f"Connected Port UUID: {data['port']}\n"
            result_text += f"Raw Data Structure: {data}\n"

            self.result_text.append(result_text)


    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec())