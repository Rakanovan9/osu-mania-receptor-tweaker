"""Desktop wrapper: opens index.html in a native window (Edge WebView2) and
gives the page a native "Save as" dialog and skin folder access through window.pywebview.api."""

import base64
import os
import sys

import webview

APP_TITLE = "osu!mania Receptor Fixer"
SKINS_DIR = os.path.expandvars(r"%LOCALAPPDATA%\osu!\Skins")


def web_root():
    # PyInstaller unpacks bundled files to sys._MEIPASS/web; in development the
    # page lives in the project folder one level above this script.
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "web")
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Api:
    def __init__(self):
        self._skin = None  # the skin folder the page opened; every path below is relative to it

    def pick_skin(self):
        """Shows a folder dialog (starting in osu!'s Skins folder). Returns the folder name, or None."""
        start = SKINS_DIR if os.path.isdir(SKINS_DIR) else ""
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG, directory=start)
        if not result:
            return None
        self._skin = os.path.realpath(result if isinstance(result, str) else result[0])
        return os.path.basename(self._skin)

    def _path(self, rel):
        if not self._skin:
            raise ValueError("no skin folder open")
        path = os.path.realpath(os.path.join(self._skin, rel))
        if os.path.commonpath([path, self._skin]) != self._skin:
            raise ValueError("path outside the skin folder")
        return path

    def read_file(self, rel):
        """The file's bytes as base64, or None if it does not exist."""
        path = self._path(rel)
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def write_file(self, rel, data_b64):
        path = self._path(rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(base64.b64decode(data_b64))
        return True

    def save_file(self, name, data_b64):
        """Shows a Save dialog and writes the file. Returns the path, or None if cancelled."""
        ext = os.path.splitext(name)[1].lower()
        file_types = ("ZIP archive (*.zip)",) if ext == ".zip" else ("PNG image (*.png)",)
        result = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG, save_filename=name, file_types=file_types
        )
        if not result:
            return None
        path = result if isinstance(result, str) else result[0]
        with open(path, "wb") as f:
            f.write(base64.b64decode(data_b64))
        return path


def main():
    webview.create_window(
        APP_TITLE,
        url=os.path.join(web_root(), "index.html"),
        js_api=Api(),
        width=1200,
        height=900,
        min_size=(760, 600),
        background_color="#E4E4E4",
    )
    # Serve the page over a local http server so canvas pixel reads and fetch behave
    # exactly as in a browser; private_mode=False keeps settings between launches.
    webview.start(http_server=True, private_mode=False)


if __name__ == "__main__":
    main()
