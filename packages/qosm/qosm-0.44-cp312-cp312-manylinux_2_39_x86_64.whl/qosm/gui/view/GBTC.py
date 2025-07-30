import numpy as np
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
                               QPushButton, QGridLayout, QGroupBox, QSizePolicy, QFileDialog, QMessageBox, QDialog,
                               QDoubleSpinBox, QProgressDialog, QCheckBox)
from PySide6.QtCore import Qt, Signal
import matplotlib
from qosm.gui.objects import HDF5Exporter

matplotlib.use('Agg')  # Force Agg backend before any other matplotlib imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os


class GBTCCanvas(FigureCanvas):
    """Integrated matplotlib canvas for displaying GBTC S-parameters"""

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(12, 8))
        super().__init__(self.figure)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # Store current plot data for export
        self.current_plot_data = None
        self.current_plot_info = None

    def plot_s_parameters(self, data_dict, show_gbtc=True, show_pw=True, show_s11=True, show_s21=True, iteration=0,
                          iteration_info=None):
        """
        Display S-parameters (S11 and S21) for GBTC and/or PW methods

        Args:
            data_dict: Dictionary containing GBTC simulation results
            show_gbtc: bool, whether to show GBTC results
            show_pw: bool, whether to show PW results
            show_s11: bool, whether to show S11 parameters
            show_s21: bool, whether to show S21 parameters
            iteration: int, which iteration to display (0-based index)
            iteration_info: str, formatted iteration information for title
        """
        # Clear figure
        self.figure.clear()

        # Get data
        gbtc_data = data_dict['data']
        sweep_frequency_values = data_dict.get('sweep_frequency_values', [])

        if not gbtc_data or len(sweep_frequency_values) == 0:
            # No data to plot
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No GBTC data available',
                    ha='center', va='center', transform=ax.transAxes, fontsize=16)
            self.draw()
            return

        # Determine what to plot
        plot_params = []
        if show_s11:
            plot_params.append('S11')
        if show_s21:
            plot_params.append('S21')

        if not plot_params:
            # No parameters selected
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No S-parameters selected for display',
                    ha='center', va='center', transform=ax.transAxes, fontsize=16)
            self.draw()
            return

        # Create subplots: magnitude and phase
        ax_mag = self.figure.add_subplot(2, 1, 1)
        ax_phase = self.figure.add_subplot(2, 1, 2)

        # Plot colors and line styles
        colors = {'gbtc': {'S11': 'blue', 'S21': 'red'},
                  'pw': {'S11': 'cyan', 'S21': 'orange'}}
        line_styles = {'gbtc': '-', 'pw': '--'}

        # X-axis is always frequency
        x_values = np.array(sweep_frequency_values)
        x_label = 'Frequency (GHz)'

        # Plot data for each method and parameter
        legend_entries_mag = []
        legend_entries_phase = []

        for method in ['gbtc', 'pw']:
            if (method == 'gbtc' and not show_gbtc) or (method == 'pw' and not show_pw):
                continue

            method_data = gbtc_data.get(method, {})
            if not method_data:
                continue

            for param in plot_params:
                param_data = method_data.get(param, [])
                if len(param_data) == 0:
                    continue

                # Convert to numpy array
                param_array = np.array(param_data)

                # Handle different data formats: KxN (iterations) or Nx1 (legacy)
                if param_array.ndim == 2:
                    # New format: KxN where K is number of iterations
                    num_iterations, num_points = param_array.shape

                    # Check if requested iteration exists
                    if iteration >= num_iterations:
                        print(f"Warning: Iteration {iteration} not available for {method} {param}. "
                              f"Available iterations: 0-{num_iterations - 1}. Using iteration 0.")
                        iteration_to_use = 0
                    else:
                        iteration_to_use = iteration

                    # Extract data for the specific iteration
                    param_iteration_data = param_array[iteration_to_use, :]

                elif param_array.ndim == 1:
                    # Legacy format: Nx1 - treat as single iteration
                    param_iteration_data = param_array
                    if iteration > 0:
                        print(f"Warning: Only one iteration available for {method} {param}, "
                              f"but iteration {iteration} was requested.")
                else:
                    print(f"Error: Unexpected data format for {method} {param}")
                    continue

                # Find valid (non-NaN) indices
                valid_mask = ~(np.isnan(param_iteration_data.real) | np.isnan(param_iteration_data.imag))

                if not np.any(valid_mask):
                    continue  # All values are NaN

                x_valid = x_values[valid_mask]
                param_valid = param_iteration_data[valid_mask]

                # Calculate magnitude and phase
                magnitude_db = 20 * np.log10(np.abs(param_valid))
                phase_deg = np.angle(param_valid, deg=True)

                # Plot magnitude
                color = colors[method][param]
                linestyle = line_styles[method]
                label = f'{param} ({method.upper()})'

                ax_mag.plot(x_valid, magnitude_db, color=color, linestyle=linestyle,
                            linewidth=2, label=label)
                legend_entries_mag.append(label)

                # Plot phase
                ax_phase.plot(x_valid, phase_deg, color=color, linestyle=linestyle,
                              linewidth=2, label=label)
                legend_entries_phase.append(label)

        # Format magnitude plot
        ax_mag.set_ylabel('Magnitude (dB)')
        ax_mag.grid(True, alpha=0.3)
        ax_mag.legend(loc='upper right')

        # Create title with iteration information
        if iteration_info:
            title = f'S-Parameters - {iteration_info}'
        else:
            title = f'S-Parameters'
        ax_mag.set_title(title)

        # Format phase plot
        ax_phase.set_xlabel(x_label)
        ax_phase.set_ylabel('Phase (degrees)')
        ax_phase.grid(True, alpha=0.3)
        ax_phase.legend(loc='upper right')

        # Adjust layout
        self.figure.tight_layout()

        # Store current plot data for export
        export_title = f'GBTC S-Parameters - {data_dict.get("req_name", "Simulation")}'
        if iteration_info:
            export_title += f' - {iteration_info}'

        self.current_plot_data = {
            'x_values': x_values,
            'x_label': x_label,
            'gbtc_data': gbtc_data.get('gbtc', {}),
            'pw_data': gbtc_data.get('pw', {}),
            'show_gbtc': show_gbtc,
            'show_pw': show_pw,
            'show_s11': show_s11,
            'show_s21': show_s21,
            'iteration': iteration,
            'iteration_info': iteration_info,
            'title': export_title
        }

        # Update canvas
        self.draw()

    def export_image(self, filename, dpi=300, bbox_inches='tight'):
        """Export current plot to image file"""
        if self.current_plot_data is None:
            raise ValueError("No plot data available for export")

        try:
            self.figure.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False

    def export_high_quality_image(self, filename, figsize=(12, 8), dpi=300):
        """Export high-quality standalone image"""
        if self.current_plot_data is None:
            raise ValueError("No plot data available for export")

        try:
            # Create new figure for export
            export_fig = Figure(figsize=figsize)
            data = self.current_plot_data

            # Create subplots
            ax_mag = export_fig.add_subplot(2, 1, 1)
            ax_phase = export_fig.add_subplot(2, 1, 2)

            # Plot colors and line styles
            colors = {'gbtc': {'S11': 'blue', 'S21': 'red'},
                      'pw': {'S11': 'cyan', 'S21': 'orange'}}
            line_styles = {'gbtc': '-', 'pw': '--'}

            x_values = data['x_values']
            x_label = data['x_label']
            iteration = data['iteration']
            iteration_info = data.get('iteration_info', None)

            # Plot data for each method and parameter
            for method in ['gbtc', 'pw']:
                if (method == 'gbtc' and not data['show_gbtc']) or (method == 'pw' and not data['show_pw']):
                    continue

                method_data = data.get(f'{method}_data', {})
                if not method_data:
                    continue

                for param in ['S11', 'S21']:
                    if (param == 'S11' and not data['show_s11']) or (param == 'S21' and not data['show_s21']):
                        continue

                    param_data = method_data.get(param, [])
                    if len(param_data) == 0:
                        continue

                    # Convert to numpy array and handle iterations
                    param_array = np.array(param_data)

                    # Handle different data formats
                    if param_array.ndim == 2:
                        num_iterations = param_array.shape[0]
                        iteration_to_use = min(iteration, num_iterations - 1)
                        param_iteration_data = param_array[iteration_to_use, :]
                    else:
                        param_iteration_data = param_array

                    valid_mask = ~(np.isnan(param_iteration_data.real) | np.isnan(param_iteration_data.imag))

                    if not np.any(valid_mask):
                        continue

                    x_valid = x_values[valid_mask]
                    param_valid = param_iteration_data[valid_mask]

                    # Calculate magnitude and phase
                    magnitude_db = 20 * np.log10(np.abs(param_valid))
                    phase_deg = np.angle(param_valid, deg=True)
                    phase_deg = np.unwrap(np.deg2rad(phase_deg), period=2 * np.pi) * 180 / np.pi

                    # Plot
                    color = colors[method][param]
                    linestyle = line_styles[method]
                    label = f'{param} ({method.upper()})'

                    ax_mag.plot(x_valid, magnitude_db, color=color, linestyle=linestyle,
                                linewidth=2, label=label)
                    ax_phase.plot(x_valid, phase_deg, color=color, linestyle=linestyle,
                                  linewidth=2, label=label)

            # Format plots
            ax_mag.set_ylabel('Magnitude (dB)')
            ax_mag.grid(True, alpha=0.3)
            ax_mag.legend(loc='upper right')

            # Use the stored title or create one with iteration info
            if 'title' in data:
                ax_mag.set_title(data['title'])
            elif iteration_info:
                ax_mag.set_title(f'GBTC S-Parameters - {iteration_info}')
            else:
                ax_mag.set_title('GBTC S-Parameters')

            ax_phase.set_xlabel(x_label)
            ax_phase.set_ylabel('Phase (degrees)')
            ax_phase.grid(True, alpha=0.3)
            ax_phase.legend(loc='upper right')

            export_fig.tight_layout()

            # Save
            export_fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            return True

        except Exception as e:
            print(f"Error saving high-quality image: {e}")
            return False


class GBTCViewer(QWidget):
    """Main widget for visualizing GBTC S-parameter results"""

    # Signal emitted when a new view is requested
    new_view_requested = Signal(dict)

    def __init__(self, available_requests, selected_request=None, view_id=1, parent=None):
        super().__init__(parent)
        self.request = available_requests.get('GBTCSim', {})
        self.view_id = view_id

        # Display options
        self.show_gbtc = True
        self.show_pw = True
        self.show_s11 = self.request['s_parameters'].get('S11', False)
        self.show_s21 = self.request['s_parameters'].get('S21', False)

        # Iteration control
        self.current_iteration = 0
        self.max_iterations = self._get_max_iterations()

        self.setup_ui()
        self.update_display()

    def _get_max_iterations(self):
        """Determine the maximum number of iterations available in the data"""
        max_iter = 1  # Default to 1 iteration (legacy format)

        try:
            gbtc_data = self.request.get('data', {})

            for method in ['gbtc', 'pw']:
                method_data = gbtc_data.get(method, {})
                if not method_data:
                    continue

                for param in ['S11', 'S21']:
                    param_data = method_data.get(param, [])
                    if len(param_data) == 0:
                        continue

                    param_array = np.array(param_data)
                    if param_array.ndim == 2:
                        # KxN format: K iterations, N frequency points
                        num_iterations = param_array.shape[0]
                        max_iter = max(max_iter, num_iterations)

        except Exception as e:
            print(f"Error determining max iterations: {e}")

        return max_iter

    def _get_iteration_info(self, iteration):
        """Get iteration parameter information for display in title

        Args:
            iteration: Current iteration index

        Returns:
            str: Formatted string with parameter name and value, or None if not available
        """
        try:
            # Get sweep information from self.request
            sweep_values = self.request.get('sweep_values', [])
            sweep_parameter = self.request.get('sweep_attribute', '')
            sweep_target_name = self.request.get('sweep_target_name', '')

            # Convert to numpy array if it isn't already, and handle empty cases
            if sweep_values is not None:
                sweep_values = np.array(sweep_values)

            # Check if we have valid data
            if (sweep_values is not None and
                    len(sweep_values) > 0 and
                    sweep_parameter and
                    len(sweep_values) > iteration):

                param_value = sweep_values[iteration]

                # Format the value appropriately
                if isinstance(param_value, (int, float, np.integer, np.floating)):
                    if param_value == int(param_value):
                        value_str = f"{int(param_value)}"
                    else:
                        # Use appropriate precision based on magnitude
                        if abs(param_value) >= 1000:
                            value_str = f"{param_value:.0f}"
                        elif abs(param_value) >= 100:
                            value_str = f"{param_value:.1f}"
                        elif abs(param_value) >= 10:
                            value_str = f"{param_value:.2f}"
                        else:
                            value_str = f"{param_value:.3f}"
                else:
                    value_str = str(param_value)

                # Determine unit based on parameter name
                unit = ""
                if sweep_parameter in ['pose.x', 'pose.y', 'pose.z']:
                    unit = "mm"
                elif sweep_parameter in ['pose.rx', 'pose.ry', 'pose.rz']:
                    unit = "deg"

                # Format as "{parameter}: {value} {unit}"
                if unit:
                    return f"{sweep_target_name} → {sweep_parameter}: {value_str} {unit}"
                else:
                    return f"{sweep_target_name} → {sweep_parameter}: {value_str}"

            # Check if there are multiple iterations
            if self.max_iterations > 1:
                return f"Iteration {iteration}"
            else:
                # Single iteration case - don't show iteration info
                return None

        except Exception as e:
            print(f"Error getting iteration info: {e}")
            print(f"sweep_values type: {type(self.request.get('sweep_values', []))}")
            print(f"sweep_values content: {self.request.get('sweep_values', [])}")
            print(f"sweep_parameter: {self.request.get('sweep_parameter', '')}")
            return f"Iteration {iteration}"

    def setup_ui(self):
        """User interface setup"""
        layout = QVBoxLayout(self)

        # Request selection
        request_group = QGroupBox("Request Selection")
        request_layout = QGridLayout(request_group)

        request_layout.addWidget(QLabel("Request:"), 0, 0)
        request_label = QLabel('GBTC Simulation')
        request_layout.addWidget(request_label, 0, 1)

        layout.addWidget(request_group)

        # Display controls
        controls_group = QGroupBox("Display Controls")
        controls_layout = QHBoxLayout(controls_group)

        # Iteration control
        controls_layout.addWidget(QLabel("Iteration:"))

        self.iteration_spinbox = QSpinBox()
        self.iteration_spinbox.setMinimum(0)
        self.iteration_spinbox.setMaximum(max(0, self.max_iterations - 1))
        self.iteration_spinbox.setValue(self.current_iteration)

        # Update tooltip with parameter info if available
        tooltip_text = f"Select iteration (0 to {self.max_iterations - 1})"
        sweep_attribute = self.request.get('sweep_attribute', '')
        if sweep_attribute:
            tooltip_text += f"\nParameter: {sweep_attribute}"
        self.iteration_spinbox.setToolTip(tooltip_text)

        self.iteration_spinbox.valueChanged.connect(self.on_iteration_changed)
        controls_layout.addWidget(self.iteration_spinbox)

        # Iteration info label
        self.iteration_info_label = QLabel(f"/ {self.max_iterations - 1}")
        controls_layout.addWidget(self.iteration_info_label)

        # Add some spacing
        controls_layout.addStretch()

        # Method selection checkboxes
        controls_layout.addWidget(QLabel("Methods:"))

        self.gbtc_checkbox = QCheckBox("GBTC")
        self.gbtc_checkbox.setChecked(self.show_gbtc)
        self.gbtc_checkbox.toggled.connect(self.on_gbtc_toggled)
        controls_layout.addWidget(self.gbtc_checkbox)

        self.pw_checkbox = QCheckBox("PW")
        self.pw_checkbox.setChecked(self.show_pw)
        self.pw_checkbox.toggled.connect(self.on_pw_toggled)
        controls_layout.addWidget(self.pw_checkbox)

        # Spacing
        controls_layout.addStretch()

        # Parameter selection checkboxes
        controls_layout.addWidget(QLabel("Parameters:"))

        self.s11_checkbox = QCheckBox("S11")
        self.s11_checkbox.setVisible(self.request['s_parameters'].get('S11', False))
        self.s11_checkbox.setChecked(self.show_s11)
        self.s11_checkbox.toggled.connect(self.on_s11_toggled)
        controls_layout.addWidget(self.s11_checkbox)

        self.s21_checkbox = QCheckBox("S21")
        self.s21_checkbox.setVisible(self.request['s_parameters'].get('S21', False))
        self.s21_checkbox.setChecked(self.show_s21)
        self.s21_checkbox.toggled.connect(self.on_s21_toggled)
        controls_layout.addWidget(self.s21_checkbox)

        # Spacing
        controls_layout.addStretch()

        # Export button
        self.export_button = QPushButton("Export Image")
        self.export_button.setToolTip("Export current plot as image")
        self.export_button.clicked.connect(self.export_current_plot)
        controls_layout.addWidget(self.export_button)

        # Export HDF5 button
        self.export_hdf5_button = QPushButton("Export HDF5")
        self.export_hdf5_button.setToolTip("Export current request data to HDF5 format")
        self.export_hdf5_button.clicked.connect(self.export_hdf5_data)
        controls_layout.addWidget(self.export_hdf5_button)

        layout.addWidget(controls_group)

        # Canvas for display
        self.canvas = GBTCCanvas(self)
        layout.addWidget(self.canvas)

        # Initialize HDF5 exporter
        self.hdf5_exporter = HDF5Exporter(self)

    def on_iteration_changed(self, value):
        """Callback for iteration spinbox change"""
        self.current_iteration = value
        self.update_display()

    def on_gbtc_toggled(self, checked):
        """Callback for GBTC checkbox toggle"""
        self.show_gbtc = checked
        self.update_display()

    def on_pw_toggled(self, checked):
        """Callback for PW checkbox toggle"""
        self.show_pw = checked
        self.update_display()

    def on_s11_toggled(self, checked):
        """Callback for S11 checkbox toggle"""
        self.show_s11 = checked
        self.update_display()

    def on_s21_toggled(self, checked):
        """Callback for S21 checkbox toggle"""
        self.show_s21 = checked
        self.update_display()

    def export_current_plot(self):
        """Export current plot to image file"""
        if self.canvas.current_plot_data is None:
            QMessageBox.warning(self, "Export Error", "No plot available to export.")
            return

        # Get current request info for filename suggestion
        data_dict = self.request
        req_name = str(data_dict.get('req_name', 'unknown'))

        # Create suggested filename
        methods = []
        if self.show_gbtc:
            methods.append('gbtc')
        if self.show_pw:
            methods.append('pw')
        method_suffix = '_' + '_'.join(methods) if methods else ''

        params = []
        if self.show_s11:
            params.append('s11')
        if self.show_s21:
            params.append('s21')
        param_suffix = '_' + '_'.join(params) if params else ''

        suggested_name = f"{req_name}_sparams{method_suffix}{param_suffix}_iter{self.current_iteration}.png"

        # Open file dialog
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export GBTC S-Parameters Plot",
            suggested_name,
            "PNG Images (*.png);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)"
        )

        if filename:
            try:
                # Determine export method based on file extension
                ext = os.path.splitext(filename)[1].lower()

                if ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                    # Use high-quality export for raster formats
                    success = self.canvas.export_high_quality_image(filename, dpi=300)
                else:
                    # Use standard export for vector formats
                    success = self.canvas.export_image(filename)

                if success:
                    QMessageBox.information(self, "Export Successful",
                                            f"Plot exported successfully to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Error",
                                         "Failed to export plot. Please check the filename and try again.")

            except Exception as e:
                QMessageBox.critical(self, "Export Error",
                                     f"An error occurred during export:\n{str(e)}")

    def export_hdf5_data(self):
        """Export current request data to HDF5 format"""
        data_dict = self.request

        if not data_dict:
            QMessageBox.warning(self, "Export Error", "No data available to export.")
            return

        # Generate suggested filename
        req_name = str(data_dict.get('req_name', 'unknown_request'))
        clean_name = "".join(c for c in req_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        suggested_filename = f"{clean_name}_gbtc_data.h5"

        # Export the data
        self.hdf5_exporter.export_single_request(data_dict, suggested_filename)

    def update_display(self):
        """Update the S-parameter display"""
        data_dict = self.request
        if data_dict.get('request_type', None) == 'GBTCSim':
            # Get iteration info for the title
            iteration_info = self._get_iteration_info(self.current_iteration)

            self.canvas.plot_s_parameters(
                data_dict,
                show_gbtc=self.show_gbtc,
                show_pw=self.show_pw,
                show_s11=self.show_s11,
                show_s21=self.show_s21,
                iteration=self.current_iteration,
                iteration_info=iteration_info
            )
        else:
            # Clear canvas if no valid data
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            ax.text(0.5, 0.5, 'No GBTC simulation data available',
                    ha='center', va='center', transform=ax.transAxes, fontsize=16)
            self.canvas.draw()

    def refresh_iteration_controls(self):
        """Refresh iteration controls when data changes"""
        self.max_iterations = self._get_max_iterations()
        self.iteration_spinbox.setMaximum(max(0, self.max_iterations - 1))
        self.iteration_info_label.setText(f"/ {self.max_iterations - 1}")

        # Reset to first iteration if current iteration is out of bounds
        if self.current_iteration >= self.max_iterations:
            self.current_iteration = 0
            self.iteration_spinbox.setValue(self.current_iteration)