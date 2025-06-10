import os
import sys
import platform
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QWidget

def get_file_path(filename):
    """파일 경로 가져오기"""
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우
        return os.path.join(sys._MEIPASS, filename)
    else:
        # 개발 환경에서는 현재 파일 경로 사용
        return os.path.join(os.path.dirname(__file__), '..', filename)

def is_arm_platform():
    """ARM 플랫폼 체크"""
    return "arm" in platform.machine()

def configure_display_settings(window):
    """화면 설정 구성 - 항상 800x480으로 고정"""
    # 항상 800x480 크기로 고정
    window.setFixedSize(800, 480)
    
    # 타이틀바 제거 설정 (전체화면 모드)
    if is_arm_platform():
        window.setWindowFlags(window.windowFlags() | Qt.FramelessWindowHint)
        QGuiApplication.setOverrideCursor(Qt.BlankCursor)  # 커서 숨기기
        # 전체화면 모드로 설정
        window.showFullScreen()
    else:
        QGuiApplication.setOverrideCursor(Qt.ArrowCursor)
        # 창 크기는 고정 전체화면은 적용하지 않음
        window.setWindowFlags(window.windowFlags() & ~Qt.FramelessWindowHint)

def suppress_qt_warnings():
    """Qt 경고 메시지 억제"""
    from os import environ
    environ['QT_DEVICE_PIXEL_RATIO'] = '0'
    environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    environ['QT_SCREEN_SCALE_FACTORS'] = '1'
    environ['QT_SCALE_FACTOR'] = '1'