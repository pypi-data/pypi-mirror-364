import importlib.metadata

from PySide6 import QtWidgets


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About nullfinder")
        self.setMinimumSize(400, 300)

        layout = QtWidgets.QVBoxLayout(self)

        try:
            app_version = importlib.metadata.version("nullfinder")
        except importlib.metadata.PackageNotFoundError:
            app_version = "?.?.? (development)"

        app_info_text = f"""
        <h3>nullfinder {app_version}</h3>
        <p>A tool to find and visualize nulls in DataFrames.</p>
        <b>Used libraries:</b>
        """
        app_info_label = QtWidgets.QLabel(app_info_text)
        app_info_label.setWordWrap(True)
        layout.addWidget(app_info_label)

        dep_text_edit = QtWidgets.QTextEdit()
        dep_text_edit.setReadOnly(True)
        dep_text_edit.setHtml(self._get_dependency_info_html())
        layout.addWidget(dep_text_edit)

        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

        self.setLayout(layout)

    @staticmethod
    def _get_dependency_info_html():
        dependencies = ["PySide6", "pandas", "pyqtgraph"]
        dep_info = []
        for dep in dependencies:
            try:
                version = importlib.metadata.version(dep)
                metadata = importlib.metadata.metadata(dep)
                license_str = metadata.get("License", "Unknown")
                if license_str == "Unknown":
                    for classifier in metadata.get_all("Classifier", []):
                        if classifier.startswith("License ::"):
                            license_str = classifier.split("::")[-1].strip()
                            break
                dep_info.append(f"{dep} {version} (License: {license_str})")
            except importlib.metadata.PackageNotFoundError:
                dep_info.append(f"{dep}: Not found")

        dep_html = "<br><br>".join(dep_info)
        return dep_html
