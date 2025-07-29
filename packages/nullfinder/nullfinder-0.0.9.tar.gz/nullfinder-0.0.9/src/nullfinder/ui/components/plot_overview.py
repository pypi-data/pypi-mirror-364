import pandas as pd
import pyqtgraph as pg
from PySide6.QtCore import Signal, Slot, QPointF
from PySide6.QtWidgets import QMessageBox


class PlotOverview(pg.PlotWidget):
    roi_selection_changed = Signal(pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.plotted_data = None

        self._init_plot_elements()
        self.connect_signals()

    def _init_plot_elements(self):
        self.scatter_plot_item = pg.ScatterPlotItem(
            pen=None,
            symbol="o",
            symbolSize=5,
        )
        self.addItem(self.scatter_plot_item)

        self.roi = pg.RectROI(
            [0, 0], [1, 1], rotatable=True, resizable=True, pen=pg.mkPen("y", width=2)
        )
        self.roi.setZValue(10)
        self.roi.hide()
        self.addItem(self.roi)

    def connect_signals(self):
        self.roi.sigRegionChangeFinished.connect(self._on_roi_changed)

    def data_update(self, df: pd.DataFrame):
        if not df.empty and "time" in df.columns and "price" in df.columns:
            try:
                df_copy = df.copy()
                df_copy["time"] = pd.to_numeric(df_copy["time"], errors="coerce")
                df_copy["price"] = pd.to_numeric(df_copy["price"], errors="coerce")

                self.plotted_data = df_copy.dropna(subset=["time", "price"])

                if self.plotted_data.empty:
                    self._clear_plot()
                    return

                self.scatter_plot_item.setData(
                    pos=self.plotted_data[["time", "price"]].values
                )

                self._setup_roi()

            except Exception as e:
                self._show_error(f"Could not plot data: {e}")
        else:
            self._clear_plot()

    def _setup_roi(self):
        if self.plotted_data is None or self.plotted_data.empty:
            return

        min_time, max_time = (
            self.plotted_data["time"].min(),
            self.plotted_data["time"].max(),
        )
        min_price, max_price = (
            self.plotted_data["price"].min(),
            self.plotted_data["price"].max(),
        )

        self.roi.setPos([min_time, min_price])
        self.roi.setSize([(max_time - min_time) * 0.25, (max_price - min_price) * 0.25])
        self.roi.show()
        self._on_roi_changed()

    def _clear_plot(self):
        self.scatter_plot_item.clear()
        self.roi.hide()
        self.plotted_data = None

    @Slot()
    def _on_roi_changed(self):
        if self.plotted_data is None or self.plotted_data.empty:
            self.update_table_widget(pd.DataFrame())
            return

        roi_shape = self.roi.mapToParent(self.roi.shape())
        points = self.plotted_data[["time", "price"]].values

        selected_mask = [roi_shape.contains(QPointF(p[0], p[1])) for p in points]

        selected_df = self.plotted_data[selected_mask]
        self.roi_selection_changed.emit(selected_df)

    def _show_error(self, message):
        if self.parent():
            QMessageBox.warning(self.parent(), "Plotting Error", message)
