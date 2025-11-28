import sys, os

# Añadir el directorio raíz al sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from gui.gui import YTGuiApp


if __name__ == "__main__":
    app = YTGuiApp()
    app.mainloop()
