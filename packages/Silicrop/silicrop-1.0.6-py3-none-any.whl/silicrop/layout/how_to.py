from PyQt5.QtWidgets import QMessageBox

def show_howto_popup(parent):
    """Display a pop-up with tutorial information."""
    # Create the pop-up
    popup = QMessageBox(parent)
    popup.setWindowTitle("How to Use")
    popup.setText(
        "Welcome to Silicrop!\n\n"
        "1. Drag and drop images into the left panel.\n"
        "2. Select an image and choose the dimension (<= 150 mm or >= 200 mm).\n"
        "3. In manual mode, you need to select 5 points.\n"
        "4. For dimensions <= 150 mm, the first and last points are used to identify the flat part.\n"
        "5. For dimensions >= 200 mm, the first point is used to identify the notch.\n\n"
    )
    popup.setIcon(QMessageBox.Information)
    popup.setStandardButtons(QMessageBox.Ok)
    popup.exec_()