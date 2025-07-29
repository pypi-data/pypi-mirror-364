import pandas as pd
import pyqtgraph as pg
from PySide6 import QtWidgets
from PySide6.QtCore import QThread, QObject, Signal, Slot, Qt, QPointF, QSettings
from PySide6.QtGui import QStandardItemModel, QStandardItem, QAction

from .about_dialog import AboutDialog
from ..core import data_processing
from ..utils import load_image


class Worker(QObject):
    finished = Signal(object, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    @Slot()
    def run(self):
        processed_data = data_processing.load_and_process_savegame(self.file_path)
        self.finished.emit(processed_data, self.file_path)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.MAX_RECENT_FILES = 5
        self.settings = QSettings("nullfinder", "nullfinder")

        self.worker = None
        self.thread = None
        self.about_action = None
        self.exit_action = None
        self.open_action = None
        self.reload_action = None
        self.recent_files_menu = None
        self.plot_widget = None
        self.tree_widget = None
        self.table_view = None
        self.progress_bar = None
        self.current_file_path = None
        self.dataframe = None
        self.plotted_data = None
        self.roi = None
        self.scatter_plot_item = None

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self.setWindowTitle("nullfinder")
        self.setWindowIcon(load_image("assets/icon.png", "nullfinder"))

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        self.open_action = file_menu.addAction("&Open...")
        self.open_action.setShortcut("Ctrl+O")
        self.reload_action = file_menu.addAction("&Reload")
        self.reload_action.setShortcut("F5")
        file_menu.addSeparator()
        self.recent_files_menu = file_menu.addMenu("&Recent Files")
        file_menu.addSeparator()
        self.exit_action = file_menu.addAction("&Exit")
        self.exit_action.setShortcut("Ctrl+Q")

        help_menu = menu_bar.addMenu("&Help")
        self.about_action = help_menu.addAction("&About")

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        main_splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
        top_splitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabel("XML Structure")
        top_splitter.addWidget(self.tree_widget)

        self.plot_widget = pg.PlotWidget()
        self.scatter_plot_item = pg.ScatterPlotItem(pen=None, symbol="o", symbolSize=5)
        self.plot_widget.addItem(self.scatter_plot_item)

        self.roi = pg.RectROI(
            [0, 0], [1, 1], rotatable=True, resizable=True, pen=pg.mkPen("y", width=2)
        )
        self.roi.setZValue(10)
        self.roi.hide()
        self.plot_widget.addItem(self.roi)

        top_splitter.addWidget(self.plot_widget)
        top_splitter.setSizes([300, 700])
        main_splitter.addWidget(top_splitter)

        self.table_view = QtWidgets.QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setModel(QStandardItemModel())
        main_splitter.addWidget(self.table_view)
        main_splitter.setSizes([700, 300])

        layout.addWidget(main_splitter)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.statusBar().showMessage("No file selected.")

    def _connect_signals(self):
        self.open_action.triggered.connect(self.open_file_dialog)
        self.reload_action.triggered.connect(self.reload_file)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.roi.sigRegionChangeFinished.connect(self.on_roi_changed)
        self.recent_files_menu.aboutToShow.connect(self._update_recent_files_menu)

    def _add_to_recent_files(self, file_path):
        if not file_path:
            return

        files = self.settings.value("recentFiles", [], type=list)
        try:
            files.remove(file_path)
        except ValueError:
            pass
        files.insert(0, file_path)

        max_files = getattr(self, "MAX_RECENT_FILES", 10)
        del files[max_files:]

        self.settings.setValue("recentFiles", files)
        self._update_recent_files_menu()

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()
        files = self.settings.value("recentFiles", [], type=list)
        actions = []
        for file_path in files:
            action = QAction(file_path, self)
            action.setData(file_path)
            action.triggered.connect(self._open_recent_file)
            actions.append(action)
        self.recent_files_menu.addActions(actions)
        self.recent_files_menu.setEnabled(len(files) > 0)

    @Slot()
    def _open_recent_file(self):
        action = self.sender()
        if isinstance(action, QAction):
            file_path = action.data()
            if file_path:
                self.process_file_in_thread(file_path)

    @Slot()
    def reload_file(self):
        if self.current_file_path:
            self.process_file_in_thread(self.current_file_path)
        else:
            self.open_file_dialog()

    @Slot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    @Slot()
    def open_file_dialog(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Save Game Files (*.xml.gz)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.process_file_in_thread(selected_files[0])
            else:
                self.statusBar().showMessage("No file selected.")

    def process_file_in_thread(self, file_path):
        self.open_action.setEnabled(False)
        self.reload_action.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage(f"Processing: {file_path}")

        self.thread = QThread()
        self.worker = Worker(file_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_processing_complete)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    @Slot(object, str)
    def on_processing_complete(self, processed_data, file_path):
        self.progress_bar.setVisible(False)
        self.open_action.setEnabled(True)

        if processed_data is None:
            QtWidgets.QMessageBox.critical(self, "Error", "Failed to process file.")
            self.statusBar().showMessage("Error processing file.", 5000)
            self.current_file_path = None
            self.reload_action.setEnabled(False)
            self.dataframe = None
            self.update_tree_widget(None)
            self.update_plot_widget(pd.DataFrame())
            self.update_table_widget(pd.DataFrame())
            return

        self.current_file_path = file_path
        self._add_to_recent_files(file_path)
        self.reload_action.setEnabled(True)
        self.dataframe = processed_data.dataframe
        self.update_tree_widget(processed_data.xml_tree_snippet)
        self.update_plot_widget(self.dataframe)
        self.update_table_widget(self.dataframe)
        self.statusBar().showMessage(f"Successfully processed: {file_path}", 5000)

    def update_tree_widget(self, root_element):
        self.tree_widget.clear()
        if root_element:
            self.populate_tree(root_element, self.tree_widget)

    def update_plot_widget(self, df):
        if not df.empty and "time" in df.columns and "price" in df.columns:
            try:
                df_copy = df.copy()
                df_copy["time"] = pd.to_numeric(df_copy["time"], errors="coerce")
                df_copy["price"] = pd.to_numeric(df_copy["price"], errors="coerce")

                self.plotted_data = df_copy.dropna(subset=["time", "price"])

                if self.plotted_data.empty:
                    self.scatter_plot_item.clear()
                    self.roi.hide()
                    return

                self.scatter_plot_item.setData(
                    pos=self.plotted_data[["time", "price"]].values
                )

                min_time, max_time = (
                    self.plotted_data["time"].min(),
                    self.plotted_data["time"].max(),
                )
                min_price, max_price = (
                    self.plotted_data["price"].min(),
                    self.plotted_data["price"].max(),
                )

                self.roi.setPos([min_time, min_price])
                self.roi.setSize(
                    [(max_time - min_time) * 0.25, (max_price - min_price) * 0.25]
                )
                self.roi.show()
                self.on_roi_changed()

            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, "Plotting Error", f"Could not plot data: {e}"
                )
        else:
            self.scatter_plot_item.clear()
            self.roi.hide()

    @Slot()
    def on_roi_changed(self):
        if self.plotted_data is None or self.plotted_data.empty:
            self.update_table_widget(pd.DataFrame())
            return

        roi_shape = self.roi.mapToParent(self.roi.shape())
        points = self.plotted_data[["time", "price"]].values

        selected_mask = [roi_shape.contains(QPointF(p[0], p[1])) for p in points]

        selected_df = self.plotted_data[selected_mask]
        self.update_table_widget(selected_df)

    def update_table_widget(self, df):
        model = self.table_view.model()
        model.clear()
        if not df.empty:
            model.setHorizontalHeaderLabels(df.columns)
            for i, row in df.iterrows():
                items = [QStandardItem(str(cell)) for cell in row]
                model.appendRow(items)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()

    def populate_tree(self, element, parent):
        item = QtWidgets.QTreeWidgetItem(parent)
        item.setText(0, element.tag)
        if element.text and element.text.strip():
            text_item = QtWidgets.QTreeWidgetItem(item)
            text_item.setText(0, element.text.strip())
        for attr_name, attr_value in element.attrib.items():
            attr_item = QtWidgets.QTreeWidgetItem(item)
            attr_item.setText(0, f"{attr_name}: {attr_value}")
        for child in element:
            self.populate_tree(child, item)
