# Launcher for the Silicrop application

from PyQt5.QtWidgets import QApplication
import sys
from silicrop.layout.components import ImageProcessorApp
from silicrop.layout.theme import apply_light_theme
from silicrop import assets
from importlib.resources import files, as_file
from PyQt5.QtGui import QIcon

def main():
    # Create the application instance
    app = QApplication(sys.argv)
    
        # ✅ C’est ici qu’on peut charger l’icône
    with as_file(files(assets).joinpath("icon.png")) as icon_path:
        app.setWindowIcon(QIcon(str(icon_path)))
    # Apply the light theme to the application
    apply_light_theme(app)
    
    # Create and display the main window
    window = ImageProcessorApp()
    window.show()

    # Execute the application event loop
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()