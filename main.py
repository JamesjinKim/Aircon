import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.main_window import ControlWindow  # main_window.py 파일을 사용

if __name__ == '__main__':
    # 고해상도 디스플레이 지원
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    QtWidgets.QApplication.setStyle("Fusion")  # 라즈베리파이 스타일 고정

    app = QtWidgets.QApplication(sys.argv)
    myWindow = ControlWindow()
    myWindow.setWindowTitle('Remote control')
    myWindow.show()
    sys.exit(app.exec_())