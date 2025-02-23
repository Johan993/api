import os
import sys

import requests
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGraphicsOpacityEffect, QLineEdit
from PyQt6.QtCore import Qt

SCREEN_SIZE = [700, 450]
STEP = [5, 2, 0.5, 0.025, 0.005, 0.0005, 0.00001]


class ShowGeo(QWidget):
    def __init__(self):
        super().__init__()
        self.l = 0
        self.ll = [37.530887, 55.703118]
        self.z = 17
        self.flag = False
        self.marker = None
        self.initUI()
        self.show_image()

    def getImage(self):
        apikey = '5a54e317-de13-47f2-a30e-b3736c95bdfb'
        th = "dark" if self.flag else "light"
        map_params = {
            "ll": ",".join([str(self.ll[0]), str(self.ll[1])]),
            "apikey": apikey,
            'z': self.z,
            "theme": th
        }
        map_api_server = "https://static-maps.yandex.ru/v1"
        response = requests.get(map_api_server, params=map_params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.btn = QPushButton('Тема', self)
        self.btn.resize(100, 50)
        self.btn.move(605, 5)
        self.btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn.clicked.connect(self.count)
        self.search_input = QLineEdit(self)
        self.search_input.resize(100, 30)
        self.search_input.move(605, 60)
        self.search_input.setPlaceholderText("Введите объект")
        self.search_input.returnPressed.connect(self.search_object)

        self.search_btn = QPushButton('Искать', self)
        self.search_btn.resize(100, 30)
        self.search_btn.move(605, 100)
        self.search_btn.clicked.connect(self.search_object)

    def count(self):
        self.flag = not self.flag
        self.show_image()

    def show_image(self):
        self.getImage()
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def search_object(self):
        place = self.search_input.text()
        if not place:
            return
        apikey = '5a54e317-de13-47f2-a30e-b3736c95bdfb'
        geocoder_api_server = "https://geocode-maps.yandex.ru/1.x/"
        geocoder_params = {
            "apikey": apikey,
            "geocode": place,
            "format": "json",
            "results": 1,
            "lang": "ru_RU"
        }
        response = requests.get(geocoder_api_server, params=geocoder_params)
        if not response:
            print("Ошибка выполнения запроса геокодирования")
            return

        json_response = response.json()
        try:
            feature_member = json_response["response"]["GeoObjectCollection"]["featureMember"]
            if not feature_member:
                print("Объект не найден")
                return
            pos = feature_member[0]["GeoObject"]["Point"]["pos"]
            lon, lat = map(float, pos.split())
            self.ll = [lon, lat]
            self.pt = [lon, lat]
            self.show_image()
        except (IndexError, KeyError):
            print("Объект не найден")

    def closeEvent(self, event):
        os.remove(self.map_file)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.z += 1
            self.z = min(self.z, 21)
            self.show_image()
        if event.key() == Qt.Key.Key_PageDown:
            self.z -= 1
            self.z = max(self.z, 0)
            self.show_image()

        if event.key() == Qt.Key.Key_Left:
            k = STEP[self.z // len(STEP)]
            if -180 <= self.ll[0] - k <= 180:
                self.ll[0] -= k
            self.show_image()
        if event.key() == Qt.Key.Key_Right:
            k = STEP[self.z // len(STEP)]
            if -180 <= self.ll[0] + k <= 180:
                self.ll[0] += k
            self.show_image()
        if event.key() == Qt.Key.Key_Up:
            k = STEP[self.z // len(STEP)]
            if -90 <= self.ll[1] + k <= 90:
                self.ll[1] += k
            self.show_image()
        if event.key() == Qt.Key.Key_Down:
            k = STEP[self.z // len(STEP)]
            if -90 <= self.ll[1] - k <= 90:
                self.ll[1] -= k
            self.show_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ShowGeo()
    ex.show()
    sys.exit(app.exec())