import time
import cv2
import pyautogui
import sys
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QCheckBox, QMessageBox, QFileDialog
from qt_material import apply_stylesheet


class TemplateMatchingWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle('模板匹配')
        self.setGeometry(100, 100, 390, 160)

        # 创建选择模板图像的标签、输入框和浏览按钮
        self.label_template = QLabel('模板文件:', self)
        self.label_template.setGeometry(10, 10, 100, 20)
        self.label_template.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))

        self.entry_template = QLineEdit(self)
        self.entry_template.setGeometry(80, 10, 220, 20)

        self.button_browse_template = QPushButton('浏览', self)
        self.button_browse_template.setGeometry(310, 10, 70, 20)
        self.button_browse_template.clicked.connect(self.select_template_file)

        # 创建选择目标图像的标签、输入框和浏览按钮
        self.label_target = QLabel('目标文件:', self)
        self.label_target.setGeometry(10, 40, 100, 20)
        self.label_target.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))

        self.entry_target = QLineEdit(self)
        self.entry_target.setGeometry(80, 40, 220, 20)

        self.button_browse_target = QPushButton('浏览', self)
        self.button_browse_target.setGeometry(310, 40, 70, 20)
        self.button_browse_target.clicked.connect(self.select_target_file)

        # 创建Debug复选框
        self.checkbox_debug = QCheckBox('Debug', self)
        self.checkbox_debug.setGeometry(10, 70, 100, 20)

        # 创建运行按钮
        self.button_run = QPushButton('Run', self)
        self.button_run.setGeometry(10, 100, 370, 50)
        self.button_run.setStyleSheet('background-color: #0078D7; color: white; font-weight: bold;')
        self.button_run.clicked.connect(self.run_template_matching)

        # 创建置顶复选框
        self.checkbox_top = QCheckBox('Top', self)
        self.checkbox_top.setGeometry(90, 70, 100, 20)
        self.checkbox_top.setFont(QtGui.QFont('Segoe UI', 12, QtGui.QFont.Bold))
        self.checkbox_top.stateChanged.connect(self.toggle_window_top)

        # 创建水印标签
        self.label_watermark = QLabel('@Minshenyao', self)
        self.label_watermark.setGeometry(280, 130, 100, 20)
        self.label_watermark.setStyleSheet('color: gray; font-size: 10px;')

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

    def select_target_file(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter('Image files (*.jpg *.jpeg *.png)')
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            if len(file_paths) > 0:
                self.entry_target.setText(file_paths[0])

    def run_template_matching(self):
        template_path = self.entry_template.text()
        target_path = self.entry_target.text()
        debug = self.checkbox_debug.isChecked()

        if template_path and target_path:
            self.button_run.setEnabled(False)
            self.button_run.setText('Waiting...')

            try:
                success = self.template_matching(template_path, target_path, debug)
                if success:
                    self.button_run.setText('Run')
                    self.button_run.setEnabled(True)
            except Exception as e:
                self.button_run.setText('Run')
                self.button_run.setEnabled(True)
                QMessageBox.critical(self, '错误', str(e))
        else:
            QMessageBox.critical(self, '错误', '请先选择模板文件和目标文件。')

    def template_matching(self, templateImage: str, targetImage: str, debug: bool):
        # 加载模板图像和待匹配图像
        template_image = cv2.imread(templateImage)
        target_image = cv2.imread(targetImage)

        # 将模板图像与目标图像进行模板匹配
        result = cv2.matchTemplate(target_image, template_image, cv2.TM_CCOEFF_NORMED)
        if result is None:
            return False

        # 获取匹配结果中的最大值和位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 在目标图像上绘制矩形框显示匹配区域
        template_height, template_width = template_image.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(target_image, top_left, bottom_right, (0, 0, 255), 2)

        # 计算矩形的中心点坐标
        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2

        if debug:
            # 打印中心点坐标
            print("中心点坐标：", center_x, center_y)
            # 显示结果
            cv2.imshow('Result', target_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        time.sleep(0.5)
        pyautogui.click(center_x, center_y)
        return True


if __name__ == '__main__':
    # 创建应用程序和窗口
    app = QApplication(sys.argv)
    window = TemplateMatchingWindow()

    # 应用Qt-Material主题
    apply_stylesheet(app, theme='dark_teal.xml')

    # 显示窗口
    window.show()

    # 运行应用程序
    sys.exit(app.exec_())
