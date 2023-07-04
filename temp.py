import time
import cv2
import pyautogui
import sys
import numpy as np
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QCheckBox, QMessageBox, QFileDialog
from qt_material import apply_stylesheet


class TemplateMatchingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('模板匹配')
        # 设置窗口图标
        icon_path = 'logo.png'  # 替换为你的logo图片文件名
        self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setFixedSize(390, 130)

        # 创建选择模板图像的标签、输入框和浏览按钮
        self.label_template = QLabel('目标图像:', self)
        self.label_template.setGeometry(10, 10, 100, 20)
        self.label_template.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))

        self.entry_template = QLineEdit(self)
        self.entry_template.setGeometry(80, 10, 220, 20)

        self.button_browse_template = QPushButton('浏览', self)
        self.button_browse_template.setGeometry(310, 10, 70, 20)
        self.button_browse_template.clicked.connect(self.select_template_file)

        # 创建Debug复选框
        self.checkbox_debug = QCheckBox('Debug', self)
        self.checkbox_debug.setGeometry(10, 40, 100, 20)
        self.checkbox_debug.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))

        # 创建运行按钮
        self.button_run = QPushButton('Run', self)
        self.button_run.setGeometry(10, 70, 370, 50)
        self.button_run.setStyleSheet('background-color: #0078D7; color: white; font-weight: bold;')
        self.button_run.clicked.connect(self.run_template_matching)

        # 创建置顶复选框
        self.checkbox_top = QCheckBox('Top', self)
        self.checkbox_top.setGeometry(90, 40, 100, 20)
        self.checkbox_top.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))
        self.checkbox_top.stateChanged.connect(self.toggle_window_top)

        # 创建水印标签
        self.label_watermark = QLabel('@Minshenyao', self)
        self.label_watermark.setGeometry(310, 50, 100, 20)
        self.label_watermark.setStyleSheet('color: gray; font-size: 10px;')

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_screen)

    def toggle_window_top(self, state):
        if state == Qt.Checked:
            self.setWindowFlag(Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.show()

    def select_template_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter('Image files (*.jpg *.jpeg *.png)')
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if len(file_paths) > 0:
                self.entry_template.setText(file_paths[0])

    def run_template_matching(self):
        template_path = self.entry_template.text()
        debug = self.checkbox_debug.isChecked()

        if template_path:
            self.button_run.setEnabled(False)
            self.button_run.setText('Waiting...')
            self.timer.start(1000)  # 每隔1秒执行一次屏幕截图和模板匹配
        else:
            QMessageBox.critical(self, '错误', '请先选择模板文件。')

    def capture_screen(self):
        template_path = self.entry_template.text()
        debug = self.checkbox_debug.isChecked()

        # 获取当前屏幕截图
        screen_image = pyautogui.screenshot()
        screen_image_np = cv2.cvtColor(np.array(screen_image), cv2.COLOR_RGB2BGR)

        # 进行模板匹配
        self.template_matching(template_path, screen_image_np, debug)

    def template_matching(self, templateImage: str, targetImage: np.ndarray, debug: bool):
        # 加载模板图像和待匹配图像
        template_image = cv2.imread(templateImage)

        # 将模板图像与目标图像进行模板匹配
        result = cv2.matchTemplate(targetImage, template_image, cv2.TM_CCOEFF_NORMED)
        if result is None:
            return False

        # 获取匹配结果中的最大值和位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= 0.8:  # 设置匹配阈值，这里设为0.8
            # 在目标图像上绘制矩形框显示匹配区域
            template_height, template_width = template_image.shape[:2]
            top_left = max_loc
            bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
            cv2.rectangle(targetImage, top_left, bottom_right, (0, 0, 255), 2)

            # 计算矩形的中心点坐标
            center_x = (top_left[0] + bottom_right[0]) // 2
            center_y = (top_left[1] + bottom_right[1]) // 2

            if debug:
                # 打印中心点坐标
                print("中心点坐标：", center_x, center_y)
                # 显示结果
                cv2.imshow('Result', targetImage)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

            time.sleep(0.5)
            pyautogui.click(center_x, center_y)

            self.timer.stop()  # 停止定时器
            self.button_run.setEnabled(True)
            self.button_run.setText('Run')

        return True


if __name__ == '__main__':
    # 创建应用程序和窗口
    app = QApplication(sys.argv)
    # 设置图标
    app.setWindowIcon(QIcon("applicationICO.ico"))
    window = TemplateMatchingWindow()

    # 应用Qt-Material主题
    apply_stylesheet(app, theme='light_teal.xml')

    # 显示窗口
    window.show()

    # 运行应用程序
    sys.exit(app.exec_())
