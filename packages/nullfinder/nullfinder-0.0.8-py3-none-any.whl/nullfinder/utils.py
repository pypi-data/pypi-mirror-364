from importlib import resources

from PySide6.QtGui import QPixmap


def load_image(image_path: str, package: str) -> QPixmap:
    try:
        resource_path = resources.files(package).joinpath(image_path)
        with resources.as_file(resource_path) as image_file:
            return QPixmap(image_file)
    except Exception as e:
        print(f"Error loading image '{image_path}': {e}")
        return QPixmap()
