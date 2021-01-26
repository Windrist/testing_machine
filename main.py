#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import cv2
import numpy as np
import sys
import time

import detectYesNo
import read_file

def receive_from_plc():
    pass # Code sau

class Thread(QThread):
    # Declare Input Signal to QT
    img = pyqtSignal(np.ndarray)
    data = pyqtSignal(np.ndarray)
    statistic = pyqtSignal(str)
    
    def run(self):
        # Khai báo USB Camera Config
        cap = cv2.VideoCapture(0)

        while True:
            cmd = receive_from_plc()
            if cmd == '9':
                result = np.zeros(84)
                # Thử 3 ảnh để kiểm tra có camera trên Tray hay không
                for _ in range(3):
                    ret, image = cap.read() # Lấy dữ liệu từ camera
                    resize_img = cv2.resize(image, (972,729)) # Cần sửa resize phù hợp với PJ mới

                    result += detectYesNo.runDetectImage(resize_img) # Check YES/NO cho camera trên Tray
                    time.sleep(0.04) # Thu ảnh 25Hz
                    if _ == 2:
                        self.img.emit(resize_img) # Đưa ảnh lên giao diện
                
                # Đưa kết quả Check lên giao diện
                result = np.rint(result / 3)
                result = np.array(result, dtype=int)
                self.data.emit(result)
            elif cmd == "1":
                self.statistic.emit("1")
            elif cmd == "0":
                self.statistic.emit("0")

            time.sleep(0.1) # Delay 10Hz

class App(QWidget):
    def __init__(self):
        super().__init__()
        # QT Config
        self.title = "MCNEX"

        # Declare Check Variable
        self.number_total = 0
        self.number_success = 0
        self.number_error = 0
        self.count = 0
        
        # Save Data
        self.date, self.time = read_file.get_date_time()
        # self.number_total, self.number_success, self.number_error = read_file.get_data_from_file(self.date, self.time)
        read_file.save_current_time(self.date, self.time)

        # Run QT
        self.initUI()
    
    def initUI(self):
        # Config main window
        self.setWindowTitle(self.title)
        self.setWindowState(Qt.WindowFullScreen)
        self.setStyleSheet("background-color: rgb(171, 171, 171);")
        
        # Logo
        self.mcnex_logo = QLabel(self)
        self.mcnex_pixmap = QPixmap('logo/mcnex.png').scaled(273,130,Qt.KeepAspectRatio)
        self.mcnex_logo.setPixmap(self.mcnex_pixmap)
        self.mcnex_logo.setGeometry(120, 20, 273, 130)
        self.uet_logo = QLabel(self)
        self.uet_pixmap = QPixmap('logo/uet.png').scaled(128,130,Qt.KeepAspectRatio)
        self.uet_logo.setPixmap(self.uet_pixmap)
        self.uet_logo.setGeometry(440, 20, 128, 130)

        # Show current time
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setGeometry(1090, 30, 430, 120)
        font_timer = QFont('', 60, QFont.Bold)
        self.time_label.setFont(font_timer)
        timer = QTimer(self)
        timer.timeout.connect(self.updateTimer)
        timer.start(1000)
        self.time_label.setStyleSheet("color: rgb(255, 255, 255);")

        # Camera area
        self.cam_name = QLabel("CAMERA", self)
        self.cam_name.setGeometry(65, 204, 570, 55)
        self.cam_name.setAlignment(Qt.AlignCenter)
        self.cam_name.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 14pt;")
        self.cam = QLabel(self)
        self.cam.setGeometry(65, 259, 570, 760)
        self.th = Thread(self)
        self.th.img.connect(self.update_image)
        self.th.data.connect(self.update_data)
        self.th.statistic.connect(self.update_statistic)
        self.cam.setStyleSheet("border-color: rgb(50, 130, 184);"
                                "border-width: 5px;"
                                "border-style: inset;")

        # Start button
        self.start_button = QPushButton("START",self)
        self.start_button.setGeometry(1615, 780, 220, 240)
        self.start_button.clicked.connect(self.clickStartButton)
        self.start_button.setStyleSheet("background-color: rgb(67, 138, 94);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(67, 138, 94);"
                                        "border-radius: 5px;")

        # Stop button
        self.stop_button = QPushButton("STOP",self)
        self.stop_button.setGeometry(1400, 780, 180, 100)
        self.stop_button.clicked.connect(self.clickStopButton)
        self.stop_button.setStyleSheet("background-color: rgb(232, 80, 91);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(232, 80, 91);"
                                        "border-radius: 5px;")

        # Home button
        self.home_button = QPushButton("HOME",self)
        self.home_button.setGeometry(1400, 920, 180, 100)
        self.home_button.clicked.connect(self.clickHomeButton)
        self.home_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(50, 130, 184);"
                                        "border-radius: 5px;")

        # Reset button
        self.reset_button = QPushButton("RESET",self)
        self.reset_button.setGeometry(1185, 780, 180, 100)
        self.reset_button.clicked.connect(self.clickResetButton)
        self.reset_button.setStyleSheet("background-color: rgb(249, 210, 118);"
                                        "font: bold 20px;"
                                        "color:rgb(255, 255, 255);"
                                        "border-width: 5px;"
                                        "border-color: rgb(249, 210, 118);"
                                        "border-radius: 5px;")

        # Calibrate button
        self.calibrate_button = QPushButton("CALIBRATE",self)
        self.calibrate_button.setGeometry(1185, 920, 180, 100)
        self.calibrate_button.clicked.connect(self.clickAlignButton)
        self.calibrate_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                            "font: bold 20px;"
                                            "color:rgb(255, 255, 255);"
                                            "border-width: 5px;"
                                            "border-color: rgb(249, 210, 118);"
                                            "border-radius: 5px;")

        # Set font
        self.font = QFont()
        self.font.setPointSize(14)
        self.font.setBold(True)

        # Table area
        self.table_area = QLabel(self)
        self.table_area.setGeometry(695, 204, 1140, 543)
        self.table_area.setStyleSheet("background-color: rgb(196, 196, 196);"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-width: 5px;"
                                    "border-style: inset;")
        self.table_name = QLabel("INFORMATION", self)
        self.table_name.setGeometry(695, 204, 1140, 55)
        self.table_name.setAlignment(Qt.AlignCenter)
        self.table_name.setStyleSheet("background-color:rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 14pt;")

        # Trays information
        self.tray = []
        for i in range(4):
            tray_name = QLabel("TRAY{}".format(i+1), self)
            tray_name.setGeometry(735+275*i, 303, 242, 55)
            tray_name.setAlignment(Qt.AlignCenter)
            tray_name.setStyleSheet("background-color:rgb(50, 130, 184);"
                                    "color: rgb(255, 255, 255);"
                                    "font: bold 14pt;")
            table = QTableWidget(7,3,self)
            table.setGeometry(735+275*i,358,242,352)
            table.horizontalHeader().hide()
            table.verticalHeader().hide()
            for j in range(3):
                table.setColumnWidth(j,80)
            for j in range(7):
                table.setRowHeight(j,50)
            table.setFont(self.font)
            table.setStyleSheet("color: rgb(255, 255, 255);")
            self.tray.append(table)

        # Statistics table
        self.statistic_table = QTableWidget(3,2,self)
        self.statistic_table.setGeometry(695, 780, 420, 240)
        self.statistic_table.horizontalHeader().hide()
        self.statistic_table.verticalHeader().hide()
        self.statistic_table.setFont(self.font)
        self.statistic_table.setStyleSheet("color: rgb(255, 255, 255);"
                                            "text-align: center;"
                                            "border-width: 5px;"
                                            "border-style: inset;"
                                            "border-color: rgb(50, 130, 184);")
        for j in range(2):
            self.statistic_table.setColumnWidth(j,205)
        for j in range(3):
            self.statistic_table.setRowHeight(j,76)
        total_item = QTableWidgetItem("TOTAL")
        total_item.setTextAlignment(Qt.AlignCenter)
        self.statistic_table.setItem(0,0,total_item)
        success_item = QTableWidgetItem("SUCCESS")
        success_item.setTextAlignment(Qt.AlignCenter)
        self.statistic_table.setItem(1,0,success_item)
        error_item = QTableWidgetItem("ERROR")
        error_item.setTextAlignment(Qt.AlignCenter)
        self.statistic_table.setItem(2,0,error_item)

        self.show()

    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        roi = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        rgbImage = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(570, 760, Qt.KeepAspectRatio)
        self.cam.setPixmap(QPixmap.fromImage(p))
    
    def update_statistic(self, data):
        self.number_total += 1
        if(self.count == 84):
            self.count = 0
        
        while(self.cam_data[self.count] != 1):
            self.count += 1
            
        total = QTableWidgetItem("{}".format(self.number_total))
        total.setTextAlignment(Qt.AlignCenter)
        self.statistic_table.setItem(0,1,total)
        
        tray_idx = self.count // 21
        row = 6 - self.count % 21 % 7
        col = self.count % 21 // 7
        if(data == "1"):
            self.number_success += 1
            success = QTableWidgetItem("{}".format(self.number_success))
            success.setTextAlignment(Qt.AlignCenter)
            self.statistic_table.setItem(1,1,success)
            
            ok = QTableWidgetItem("OK")
            ok.setTextAlignment(Qt.AlignCenter)
            self.tray[tray_idx].setItem(row, col, ok)
            self.tray[tray_idx].item(row,col).setBackground(QColor(67, 138, 94))
        else:
            self.number_error += 1
            error = QTableWidgetItem("{}".format(self.number_error))
            error.setTextAlignment(Qt.AlignCenter)
            self.statistic_table.setItem(2,1,error)

            ng = QTableWidgetItem("NG")
            ng.setTextAlignment(Qt.AlignCenter)
            self.tray[tray_idx].setItem(row, col, ng)
            self.tray[tray_idx].item(row,col).setBackground(QColor(232, 80, 91))
        self.count += 1

    def update_data(self, data):
        # Update data to table
        c = 0
        for k in range(4):
            for j in range(3):
                for i in range(6,-1,-1):
                    self.tray[k].setItem(i,j,QTableWidgetItem())
                    if(int(data[c])):
                        self.tray[k].item(i,j).setBackground(QColor(67, 138, 94))
                    c += 1
        # Update current data
        for i in range(self.count):
            if(data[i] == 1):
                tray_idx = i // 21
                row = 6 - i % 21 % 7
                col = i % 21 // 7
                
                ok = QTableWidgetItem("OK")
                ok.setTextAlignment(Qt.AlignCenter)
                self.tray[tray_idx].setItem(row, col, ok)
                self.tray[tray_idx].item(row,col).setBackground(QColor(67, 138, 94))
        data[:self.count] = 0
        data_cam = str(data)[1:-1].replace(", ", '').replace(' ', '').replace('\n','')
        self.cam_data = data
        pass # Gửi "data_cam"
        print(data_cam)
        
    def updateTimer(self):
        cr_time = QTime.currentTime()
        time = cr_time.toString('hh:mm AP')
        self.time_label.setText(time)

    def clickStartButton(self):
        print("START")
        self.th.start()
        
        pass # Gửi Lệnh "a"

    def clickStopButton(self):
        print("STOP")
        self.th.quit()
        pass # Gửi Lệnh "o"
        read_file.write_data_to_file(self.date, self.time, (self.number_total, self.number_success, self.number_error))

    def clickResetButton(self):
        self.date, self.time = read_file.get_date_time()
        read_file.save_current_time(self.date, self.time)
        self.count = 0

        # Rest information table
        for k in range(4):
            for i in range(7):
                for j in range(3):
                    self.tray[k].setItem(i,j,QTableWidgetItem(""))
                    self.tray[k].item(i,j).setBackground(QColor(196, 196, 196))

    def clickHomeButton(self):
        print("HOME")
        pass # Gửi Lệnh "h"
    
    def clickAlignButton(self):
        print("CALIBRATE")
        pass # Gửi Lệnh "t"
        self.alignWindow = AlignWindow()
        self.alignWindow.show()

class AlignWindow(QWidget):
    def __init__(self):
        super(AlignWindow, self).__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.title = "CALIBRATION"
        self.left = 1300; self.top = 550
        self.width = 500; self.height = 500

        self.initUI()
    
    def initUI(self):
        
        # Config alignment window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color: rgb(171, 171, 171);")

        # OK button
        self.up_button = QPushButton("⇧",self)
        self.up_button.setGeometry(190, 70, 120, 120)
        self.up_button.clicked.connect(self.clickUpButton)
        self.up_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "font: bold 50px;"
                                    "color:rgb(255, 255, 255);"
                                    "border-width: 5px;"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-radius: 5px;")
        
        self.down_button = QPushButton("⇩",self)
        self.down_button.setGeometry(190, 310, 120, 120)
        self.down_button.clicked.connect(self.clickDownButton)
        self.down_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "font: bold 50px;"
                                    "color:rgb(255, 255, 255);"
                                    "border-width: 5px;"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-radius: 5px;")
        
        self.left_button = QPushButton("⇦",self)
        self.left_button.setGeometry(70, 190, 120, 120)
        self.left_button.clicked.connect(self.clickLeftButton)
        self.left_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "font: bold 50px;"
                                    "color:rgb(255, 255, 255);"
                                    "border-width: 5px;"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-radius: 5px;")
        
        self.right_button = QPushButton("⇨",self)
        self.right_button.setGeometry(310, 190, 120, 120)
        self.right_button.clicked.connect(self.clickRightButton)
        self.right_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "font: bold 50px;"
                                    "color:rgb(255, 255, 255);"
                                    "border-width: 5px;"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-radius: 5px;")

        self.ok_button = QPushButton("OK",self)
        self.ok_button.setGeometry(10, 390, 100, 100)
        self.ok_button.clicked.connect(self.clickOKButton)
        self.ok_button.setStyleSheet("background-color: rgb(50, 130, 184);"
                                    "font: bold 50px;"
                                    "color:rgb(255, 255, 255);"
                                    "border-width: 5px;"
                                    "border-color: rgb(50, 130, 184);"
                                    "border-radius: 5px;")

        self.show()
    
    @pyqtSlot()

    def clickOKButton(self):
        print("OK")
        pass # Gửi lệnh "d"
        self.hide()

    def clickUpButton(self):
        print("UP")
        pass # Gửi lệnh "u"

    def clickDownButton(self):
        print("DOWN")
        pass # Gửi lệnh "d"

    def clickLeftButton(self):
        print("LEFT")
        pass # Gửi lệnh "l"

    def clickRightButton(self):
        print("RIGHT")
        pass # Gửi lệnh "r"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
