import sys
import argparse
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from ui.main_window import ControlWindow  # main_window.py 파일을 사용

if __name__ == '__main__':
    # 명령행 인자 파서 설정
    parser = argparse.ArgumentParser(description='Aircon Remote Control')
    parser.add_argument('--test', action='store_true', 
                       help='테스트 모드로 실행 (가상 센서 데이터 사용)')
    args = parser.parse_args()
    # 고해상도 디스플레이 지원
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    QtWidgets.QApplication.setStyle("Fusion")  # 라즈베리파이 스타일 고정

    app = QtWidgets.QApplication(sys.argv)
    myWindow = ControlWindow(test_mode=args.test)
    myWindow.setWindowTitle('Aircon Remote control')
    if args.test:
        myWindow.setWindowTitle('Aircon Remote control [TEST MODE]')
    myWindow.show()
    sys.exit(app.exec_())