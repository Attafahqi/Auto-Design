import os
import sys
import shutil
import json
import subprocess
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import Asset.rsc

script_directory = os.path.dirname(os.path.abspath(__file__))
png_file_path = os.path.join(script_directory, "Template.png")
json_file_path = os.path.join(script_directory, 'config.json')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    raise ValueError("Invalid HEX color format.")


def saved_to_json(folder_path, start_color_rgb, end_color_rgb, border_thickness):
    config_data = {
        "location": folder_path,
        "start_color": start_color_rgb,
        "end_color": end_color_rgb,
        "border": f"{border_thickness}px"
    }

    with open(json_file_path, mode='w') as json_file:
        json.dump(config_data, json_file, indent=4)


class Setup(QMainWindow):
    def __init__(self):
        super(Setup, self).__init__()
        uic.loadUi("UI/Home.ui", self)
        self.setWindowTitle("ATD AutoDesign")
        self.setWindowIcon(QIcon("Asset/ATD Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.show()

        self.Exit.clicked.connect(self.quit)
        self.BrowseTemplate.clicked.connect(self.browseTemplate)
        self.BrowseSaving.clicked.connect(self.browseSaving)
        self.Submit.clicked.connect(self.done)

    def quit(self):
        self.close()
        QApplication.quit()

    def browseTemplate(self):
        fTemplate, _ = QFileDialog.getOpenFileName(self, 'Search Template File', 'C:/', 'Images (*.png *.xmp *.jpg)')
        if fTemplate:
            self.Template.setText(fTemplate)

    def browseSaving(self):
        fSaving = QFileDialog.getExistingDirectory(self, 'Choose Saving Folder', 'C:/')
        if fSaving:
            self.Saving.setText(fSaving)

    def done(self):
        file_path = self.Template.text()
        folder_path = self.Saving.text()

        if not os.path.isfile(file_path) and not os.path.isdir(folder_path):
            self.Template.clear()
            self.show_warning("Your template file and saving folder does not exist. Please try again.")
            return

        if not os.path.isfile(file_path):
            self.Template.clear()
            self.show_warning("Your template file does not exist. Please try again.")
            return

        if not os.path.isdir(folder_path):
            self.Saving.clear()
            self.show_warning("Your saving folder does not exist. Please try again.")
            return

        start_color = self.StartColor.text()
        end_color = self.EndColor.text()
        border_thickness = self.BorderSize.text()

        if not border_thickness.isdigit():
            self.show_warning("Border thickness must be a numeric value.")
            return

        try:
            start_color_rgb = hex_to_rgb(start_color)
            end_color_rgb = hex_to_rgb(end_color)
        except ValueError as e:
            self.show_warning(str(e))
            return

        saved_to_json(folder_path, start_color_rgb, end_color_rgb, border_thickness)

        shutil.copy(file_path, png_file_path)

        self.close()
        subprocess.run([sys.executable, 'story.py'])
        QApplication.quit()

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()


def main():
    app = QApplication(sys.argv)

    if os.path.isfile(png_file_path) and os.path.isfile(json_file_path):
        subprocess.run([sys.executable, 'story.py'])
        QApplication.quit()
    else:
        window = Setup()
        window.show()
        app.exec_()

if __name__ == "__main__":
    main()
