import os
import sys
import json
import subprocess
from PIL import Image, ImageDraw, ImageFilter
from datetime import datetime
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QDialog, QFileDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
import Asset.rsc

script_directory = os.path.dirname(os.path.abspath(__file__))
png_file_path = os.path.join(script_directory, "Template.png")
json_file_path = os.path.join(script_directory, 'config.json')


def read_config_from_json(json_path):
    try:
        with open(json_path, mode='r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
    return None


def create_gradient_border(poster_size, border_width, start_color, end_color):
    width, height = poster_size

    bordered_width = width + border_width * 2
    bordered_height = height + border_width * 2

    gradient = Image.new("RGBA", (bordered_width, bordered_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)

    for i in range(border_width):
        ratio = i / border_width
        r = int(start_color[0] + ratio * (end_color[0] - start_color[0]))
        g = int(start_color[1] + ratio * (end_color[1] - start_color[1]))
        b = int(start_color[2] + ratio * (end_color[2] - start_color[2]))
        color = (r, g, b, 255)

        draw.rectangle(
            [i, i, bordered_width - i - 1, bordered_height - i - 1],
            outline=color,
        )

    final_color = (end_color[0], end_color[1], end_color[2], 255)
    draw.rectangle(
        [border_width, border_width, bordered_width - border_width - 1, bordered_height - border_width - 1],
        fill=final_color,
    )

    return gradient


def create_poster_in_template(template_path, posters_folder, output_base_folder, start_color, end_color, border_width, folder_date):
    template = Image.open(template_path).convert("RGBA")
    
    output_folder = os.path.join(output_base_folder, folder_date)
    os.makedirs(output_folder, exist_ok=True)
    
    for poster_filename in os.listdir(posters_folder):
        poster_path = os.path.join(posters_folder, poster_filename)
        
        if not poster_filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        
        try:
            poster = Image.open(poster_path).convert("RGBA")
            
            target_width = 800
            width_percent = target_width / poster.width
            target_height = int(poster.height * width_percent)
            poster_resized = poster.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            gradient_border = create_gradient_border(poster_resized.size, border_width, start_color, end_color)
            
            gradient_border.paste(poster_resized, (border_width, border_width), poster_resized)
            
            canvas = template.copy()
            
            x_offset = (canvas.width - gradient_border.width) // 2
            y_offset = (canvas.height - gradient_border.height) // 2
            
            if gradient_border.height - border_width * 2 > 1340:
                y_offset += 50 
            
            canvas.paste(gradient_border, (x_offset, y_offset), gradient_border)
            
            output_path = os.path.join(output_folder, poster_filename)
            canvas.save(output_path, format="PNG")
            print(f"Saved: {output_path}")
        
        except Exception as e:
            print(f"Error processing {poster_filename}: {e}")

class Story(QMainWindow):
    def __init__(self):
        super(Story, self).__init__()
        uic.loadUi("UI/Story.ui", self)
        self.setWindowTitle("ATD AutoDesign")
        self.setWindowIcon(QIcon("Asset/ATD Logo.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        today = QDate.currentDate()
        self.UploadDate.setDate(today)
        self.show()

        self.Exit.clicked.connect(self.quit)
        self.BrowsePosters.clicked.connect(self.browsePosters)
        self.Generate.clicked.connect(self.generate)
        self.Reset.clicked.connect(self.reset)

    def show_warning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def quit(self):
        self.close()
        QApplication.quit()
    
    def browsePosters(self):
        fPosters = QFileDialog.getExistingDirectory(self, 'Search Posters Folder', 'C:/')
        if fPosters:
            self.Posters.setText(fPosters)
    
    def generate(self):
        template_path = "Template.png"
        json_path = "config.json"
        config = read_config_from_json(json_path)

        posters_folder = self.Posters.text()
        if not os.path.isdir(posters_folder):
            self.Posters.clear()
            self.show_warning("Your posters folder does not exist. Please try again.")
            return

        folder_date_qt = self.UploadDate.date()
        folder_date = folder_date_qt.toPyDate()
        folder_date_str = folder_date.strftime("%Y-%m-%d")  

        try:
            datetime.strptime(folder_date_str, "%Y-%m-%d") 
        except ValueError:
            self.show_warning("Invalid date")
            return

        start_color = tuple(config.get("start_color", [0, 0, 0]))
        end_color = tuple(config.get("end_color", [255, 255, 255]))
        try:
            border_width = int(config.get("border", "5px").replace("px", ""))
        except ValueError:
            self.show_warning("Invalid border")
            return

        output_base_folder = config["location"]

        create_poster_in_template(
            template_path,
            posters_folder,
            output_base_folder,
            start_color,
            end_color,
            border_width,
            folder_date_str 
        )

        self.Posters.clear()

    
    def reset(self):
        files_to_delete = ["Template.png", "config.json"]
    
        for file in files_to_delete:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")

        self.close()
        subprocess.run([sys.executable, 'main.py'])
        QApplication.quit()

        
def main():
    app = QApplication(sys.argv)

    if os.path.isfile(png_file_path) and os.path.isfile(json_file_path):
        window = Story()
        window.show()
        app.exec_() 
    else:
        subprocess.run([sys.executable, 'main.py'])
        QApplication.quit()
               

if __name__ == "__main__":
    main()
