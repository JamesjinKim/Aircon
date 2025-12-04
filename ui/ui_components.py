import os
from PyQt5.QtWidgets import (QGroupBox, QLabel, QPushButton, QComboBox, QTextEdit,
                           QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, QWidget, QSizePolicy,
                           QSlider, QGridLayout, QToolButton, QButtonGroup)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from ui.constants import BUTTON_ON_STYLE, BUTTON_OFF_STYLE

def create_group_box(title, background_color="#f0f0f0", margins=(10, 25, 10, 10)):
    """그룹박스 생성 헬퍼 함수"""
    group = QGroupBox(title)
    group.setStyleSheet(f"""
        QGroupBox {{ 
            background-color: {background_color}; 
            border-radius: 5px; 
            font-size: 16px; 
            font-weight: bold; 
        }}
    """)
    layout = QVBoxLayout(group)
    layout.setContentsMargins(*margins)
    return group, layout

def create_button_row(label_text, button, layout, button_width=140, spacing=20):
    """버튼 행 생성 헬퍼 함수"""
    row_layout = QHBoxLayout()
    row_layout.setContentsMargins(5, 8, 5, 8)  # 상하 마진 증가
    
    label = QLabel(label_text)
    label.setFixedWidth(140)  # 레이블 고정 너비로 정렬 개선
    label.setStyleSheet("font-size: 15px; font-weight: bold;")  # 폰트 크기와 굵기 증가

    # 모든 버튼에 동일한 고정 크기 적용 - 크기 증가
    button.setFixedSize(button_width, 45)  # 너비와 높이 증가
    button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    button.setStyleSheet("font-size: 14px; font-weight: bold;")  # 버튼 폰트 크기 증가
    
    row_layout.addWidget(label)
    row_layout.addSpacing(spacing)  # 조정 가능한 간격
    row_layout.addWidget(button)
    row_layout.addStretch()  # 오른쪽 여백
    layout.addLayout(row_layout)
    return button

def create_port_selection_section():
    """포트 선택 섹션 생성"""
    layout = QHBoxLayout()
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(5)
    
    port_label = QLabel("Port")
    port_label.setAlignment(Qt.AlignCenter)
    port_label.setFixedWidth(30)
    port_label.setStyleSheet("font-weight: bold;")
    
    port_combobox = QComboBox()
    port_combobox.setFixedWidth(150)
    
    baudrate_label = QLabel("Baudrate")
    baudrate_label.setAlignment(Qt.AlignCenter)
    baudrate_label.setFixedWidth(70)
    baudrate_label.setStyleSheet("font-weight: bold;")
    
    baudrate_combobox = QComboBox()
    baudrate_combobox.setFixedWidth(120)
    
    connection_label = QLabel("Connect")
    connection_label.setAlignment(Qt.AlignCenter)
    connection_label.setFixedWidth(70)
    connection_label.setStyleSheet("font-weight: bold;")
    
    connect_button = QPushButton("연결")
    connect_button.setFixedWidth(50)
    
    status_label = QLabel("Disconnected")
    status_label.setAlignment(Qt.AlignCenter)
    status_label.setFixedWidth(110)
    status_label.setStyleSheet("background-color: rgb(250, 0, 25); color: rgb(0,0,0);")
    
    exit_button = QPushButton("종료")
    exit_button.setFixedWidth(50)
    
    layout.addWidget(port_label)
    layout.addWidget(port_combobox)
    layout.addWidget(baudrate_label)
    layout.addWidget(baudrate_combobox)
    layout.addStretch()
    layout.addWidget(connection_label)
    layout.addWidget(connect_button)
    layout.addWidget(status_label)
    layout.addWidget(exit_button)
    
    return layout, port_combobox, baudrate_combobox, connect_button, status_label, exit_button

def create_message_section():
    """메시지 섹션 생성"""
    message_group = QGroupBox("메시지")
    message_layout = QVBoxLayout(message_group)
    message_layout.setContentsMargins(5, 15, 5, 5)
    message_layout.setSpacing(5)
    
    # Send Data 그룹박스
    send_group = QGroupBox("Send Data")
    send_layout = QVBoxLayout(send_group)
    send_layout.setContentsMargins(5, 15, 5, 5)
    send_data_text_edit = QTextEdit()
    send_data_text_edit.setMaximumHeight(120)  # 높이 제한
    send_data_text_edit.setStyleSheet("font-size: 10px;")  # 폰트 크기 고정

    
    send_clear = QPushButton("Clear")
    send_clear.setFixedWidth(60)
    send_header_layout = QHBoxLayout()
    send_header_layout.addStretch()
    send_header_layout.addWidget(send_clear)
    send_layout.addLayout(send_header_layout)
    send_layout.addWidget(send_data_text_edit)
    
    # Receive Data 그룹박스
    receive_group = QGroupBox("Receive Data")
    receive_layout = QVBoxLayout(receive_group)
    receive_layout.setContentsMargins(5, 15, 5, 5)
    receive_data_text_edit = QTextEdit()
    receive_data_text_edit.setMaximumHeight(120)  # 높이 제한
    receive_data_text_edit.setStyleSheet("font-size: 10px;")  # 폰트 크기 고정

    
    receive_clear = QPushButton("Clear")
    receive_clear.setFixedWidth(60)
    receive_header_layout = QHBoxLayout()
    receive_header_layout.addStretch()
    receive_header_layout.addWidget(receive_clear)
    receive_layout.addLayout(receive_header_layout)
    receive_layout.addWidget(receive_data_text_edit)
    
    # 메시지 그룹에 Send/Receive 영역 추가
    message_layout.addWidget(send_group)
    message_layout.addWidget(receive_group)
    
    return message_group, send_data_text_edit, receive_data_text_edit, send_clear, receive_clear

def create_speed_buttons(layout, label_text):
    """스피드 버튼 영역 생성"""
    speed_layout = QHBoxLayout()
    speed_label = QLabel(label_text)
    speed_layout.addWidget(speed_label)
    speed_layout.addStretch()
    
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(5)  # 버튼 사이 간격 설정
    
    # 모든 버튼에 일관된 초기 설정
    button1 = QPushButton("1")
    button2 = QPushButton("2")
    button3 = QPushButton("3")
    
    # 초기 크기 설정 (SpeedButtonManager에서 재설정됨)
    for button in [button1, button2, button3]:
        button.setStyleSheet(BUTTON_OFF_STYLE)
        button.setFixedSize(40, 30)  # 고정 크기로 설정
    
    buttons_layout.addWidget(button1)
    buttons_layout.addWidget(button2)
    buttons_layout.addWidget(button3)
    speed_layout.addLayout(buttons_layout)
    
    layout.addLayout(speed_layout)
    
    return button1, button2, button3

def create_speed_buttons_with_text(layout, label_text, left_text, center_text, right_text):
    """스피드 버튼 영역 생성 - 사용자 지정 텍스트"""
    speed_layout = QHBoxLayout()
    speed_layout.setContentsMargins(5, 8, 5, 8)  # 상하 마진 증가
    
    speed_label = QLabel(label_text)
    speed_label.setFixedWidth(140)  # 레이블 고정 너비로 정렬 개선
    speed_label.setStyleSheet("font-size: 15px; font-weight: bold;")  # 폰트 크기와 굵기 증가
    speed_layout.addWidget(speed_label)
    speed_layout.addSpacing(20)  # 고정된 적당한 간격
    
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(8)  # 버튼 사이 간격 증가
    
    # 버튼 생성 - 사용자 정의 텍스트 사용
    button1 = QPushButton(left_text)
    button2 = QPushButton(center_text)
    button3 = QPushButton(right_text)
    
    # 초기 크기 설정 - 크기 증가
    for button in [button1, button2, button3]:
        button.setStyleSheet("background-color: rgb(186,186,186); font-size: 14px;")
        button.setFixedSize(50, 45)  # 크기 증가
    
    buttons_layout.addWidget(button1)
    buttons_layout.addWidget(button2)
    buttons_layout.addWidget(button3)
    speed_layout.addLayout(buttons_layout)
    speed_layout.addStretch()  # 오른쪽 여백
    
    layout.addLayout(speed_layout)
    
    return button1, button2, button3

def create_fan_speed_control(min_value=1, max_value=10, default_value=1):
    """팬 속도 컨트롤 생성 (- 속도 +)"""
    control_widget = QWidget()
    layout = QHBoxLayout(control_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # 마이너스 버튼
    minus_button = QPushButton("-")
    minus_button.setFixedSize(40, 40)
    minus_button.setStyleSheet("""
        QPushButton {
            background-color: #e0e0e0;
            border-radius: 20px;
            font-size: 20px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
    """)
    
    # 팬 이모티콘/아이콘
    fan_label = QLabel("❋")  # 팬 모양 이모티콘 (또는 원하는 이모티콘으로 변경)
    fan_label.setAlignment(Qt.AlignCenter)
    fan_label.setStyleSheet("""
        font-size: 28px;
        margin: 0 10px;
        min-width: 40px;
    """)
    
    # 플러스 버튼
    plus_button = QPushButton("+")
    plus_button.setFixedSize(40, 40)
    plus_button.setStyleSheet("""
        QPushButton {
            background-color: #e0e0e0;
            border-radius: 20px;
            font-size: 20px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d0d0d0;
        }
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
    """)
    
    # 숫자 레이블 (현재 속도 표시)
    value_label = QLabel(str(default_value))
    value_label.setAlignment(Qt.AlignCenter)
    value_label.setStyleSheet("""
        font-size: 22px;
        font-weight: bold;
        background-color: #f8f8f8;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 5px;
        min-width: 40px;
    """)
    
    # 슬라이더
    slider = QSlider(Qt.Horizontal)
    slider.setMinimum(min_value)
    slider.setMaximum(max_value)
    slider.setValue(default_value)
    slider.setTickPosition(QSlider.TicksBelow)
    slider.setTickInterval(1)
    slider.setObjectName("fan_speed_slider")  # 객체 이름 설정
    
    # 레이아웃에 위젯 추가
    layout.addWidget(minus_button)
    layout.addWidget(fan_label)
    layout.addWidget(plus_button)
    layout.addStretch()
    layout.addWidget(value_label)
    layout.addWidget(slider)
    
    # 연결을 위한 객체 저장
    control_widget.minus_button = minus_button
    control_widget.plus_button = plus_button
    control_widget.value_label = value_label
    control_widget.slider = slider
    control_widget.fan_label = fan_label
    
    return control_widget


def create_group_box(title, background_color="#f0f0f0", margins=(10, 25, 10, 10)):
    """그룹박스 생성 헬퍼 함수"""
    group = QGroupBox(title)
    group.setStyleSheet(f"""
        QGroupBox {{ 
            background-color: {background_color}; 
            border-radius: 5px; 
            font-size: 16px; 
            font-weight: bold; 
        }}
    """)
    layout = QVBoxLayout(group)
    layout.setContentsMargins(*margins)
    return group, layout

def create_auto_control_tab(parent):
    """AUTO 제어 탭 생성 - 2컬럼 컴팩트 레이아웃 (AUTOMODE 명령어 지원)"""
    # AUTO 탭 전체 위젯
    auto_widget = QWidget()

    # 그리드 레이아웃 설정 - 2x1 그리드 (2개의 열)
    main_grid = QGridLayout(auto_widget)
    main_grid.setContentsMargins(10, 10, 10, 10)
    main_grid.setSpacing(15)

    # ============================================
    # 1. 왼쪽 컬럼: AUTO MODE CONTROL
    # ============================================
    left_group, left_layout = create_group_box("AUTO MODE CONTROL", margins=(15, 30, 15, 15))
    left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # --- AUTO START/STOP 버튼 ---
    auto_button_layout = QHBoxLayout()
    auto_button_layout.setContentsMargins(5, 10, 5, 10)

    auto_mode_button = QPushButton("AUTO START")
    auto_mode_button.setObjectName("auto_mode_button")
    auto_mode_button.setFixedSize(180, 60)
    auto_mode_button.setStyleSheet("""
        QPushButton {
            background-color: #2979ff;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #2962ff;
        }
        QPushButton:pressed {
            background-color: #1565c0;
        }
    """)
    auto_button_layout.addWidget(auto_mode_button)
    auto_button_layout.addStretch()

    # 상태 표시 레이블
    status_label = QLabel("대기중")
    status_label.setObjectName("auto_status_label")
    status_label.setStyleSheet("""
        font-size: 16px;
        font-weight: bold;
        color: #666;
        padding: 8px 15px;
        background-color: #e0e0e0;
        border-radius: 5px;
    """)
    auto_button_layout.addWidget(status_label)

    left_layout.addLayout(auto_button_layout)
    left_layout.addSpacing(15)

    # --- 모드 동작 상태 표시 ---
    mode_status_layout = QHBoxLayout()
    mode_status_layout.setContentsMargins(5, 5, 5, 5)
    mode_status_layout.setSpacing(15)

    # 자동(온도) 상태
    auto_temp_indicator = QLabel("자동")
    auto_temp_indicator.setObjectName("auto_temp_indicator")
    auto_temp_indicator.setStyleSheet("font-size: 14px; color: #888; padding: 5px 10px; background-color: #f5f5f5; border-radius: 3px;")
    auto_temp_indicator.setFixedSize(70, 35)
    auto_temp_indicator.setAlignment(Qt.AlignCenter)

    # 환기(CO2) 상태
    vent_indicator = QLabel("환기")
    vent_indicator.setObjectName("vent_indicator")
    vent_indicator.setStyleSheet("font-size: 14px; color: #888; padding: 5px 10px; background-color: #f5f5f5; border-radius: 3px;")
    vent_indicator.setFixedSize(70, 35)
    vent_indicator.setAlignment(Qt.AlignCenter)

    # 순환(PM2.5) 상태
    circulation_indicator = QLabel("순환")
    circulation_indicator.setObjectName("circulation_indicator")
    circulation_indicator.setStyleSheet("font-size: 14px; color: #888; padding: 5px 10px; background-color: #f5f5f5; border-radius: 3px;")
    circulation_indicator.setFixedSize(70, 35)
    circulation_indicator.setAlignment(Qt.AlignCenter)

    mode_status_layout.addWidget(auto_temp_indicator)
    mode_status_layout.addWidget(vent_indicator)
    mode_status_layout.addWidget(circulation_indicator)
    mode_status_layout.addStretch()

    left_layout.addLayout(mode_status_layout)
    left_layout.addSpacing(20)

    # --- 구분선 ---
    separator1 = QFrame()
    separator1.setFrameShape(QFrame.HLine)
    separator1.setStyleSheet("background-color: #bbb;")
    separator1.setFixedHeight(2)
    left_layout.addWidget(separator1)
    left_layout.addSpacing(15)

    # --- PT02 센서 데이터 표시 ---
    sensor_title = QLabel("PT02 센서 (1분 주기)")
    sensor_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #444;")
    left_layout.addWidget(sensor_title)
    left_layout.addSpacing(10)

    sensor_data_layout = QHBoxLayout()
    sensor_data_layout.setContentsMargins(5, 5, 5, 5)
    sensor_data_layout.setSpacing(20)

    # 온도 표시
    temp_display = QLabel("--.-°C")
    temp_display.setObjectName("pt02_temp_display")
    temp_display.setStyleSheet("font-size: 20px; font-weight: bold; color: #ff5722; padding: 5px;")

    # CO2 표시
    co2_display = QLabel("---- ppm")
    co2_display.setObjectName("pt02_co2_display")
    co2_display.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3; padding: 5px;")

    # PM2.5 표시
    pm25_display = QLabel("-- µg/m³")
    pm25_display.setObjectName("pt02_pm25_display")
    pm25_display.setStyleSheet("font-size: 20px; font-weight: bold; color: #9C27B0; padding: 5px;")

    sensor_data_layout.addWidget(temp_display)
    sensor_data_layout.addWidget(co2_display)
    sensor_data_layout.addWidget(pm25_display)
    sensor_data_layout.addStretch()

    left_layout.addLayout(sensor_data_layout)
    left_layout.addStretch()

    # ============================================
    # 2. 오른쪽 컬럼: 설정 & 버튼
    # ============================================
    right_group, right_layout = create_group_box("설정값 입력", margins=(8, 30, 8, 10))
    right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    # 설정 입력 행 생성 헬퍼 함수
    def create_setting_row(label_text, unit_text, default_val, default_hyst, obj_prefix):
        """설정 입력 행 생성: 라벨 [-][값][+] ±[-][범위][+] 단위"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 6, 0, 6)
        row_layout.setSpacing(2)

        # 라벨
        label = QLabel(label_text)
        label.setFixedWidth(50)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        row_layout.addWidget(label)

        # 값 감소 버튼
        minus_btn = QPushButton("-")
        minus_btn.setObjectName(f"{obj_prefix}_minus")
        minus_btn.setFixedSize(36, 36)
        minus_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        row_layout.addWidget(minus_btn)

        # 값 표시
        value_btn = QPushButton(str(default_val))
        value_btn.setObjectName(f"{obj_prefix}_value")
        value_btn.setFixedSize(60, 36)
        value_btn.setStyleSheet("font-size: 13px; font-weight: bold; background-color: #f5f5f5;")
        row_layout.addWidget(value_btn)

        # 값 증가 버튼
        plus_btn = QPushButton("+")
        plus_btn.setObjectName(f"{obj_prefix}_plus")
        plus_btn.setFixedSize(36, 36)
        plus_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        row_layout.addWidget(plus_btn)

        # ± 라벨
        pm_label = QLabel("±")
        pm_label.setFixedWidth(18)
        pm_label.setAlignment(Qt.AlignCenter)
        pm_label.setStyleSheet("font-size: 13px; font-weight: bold;")
        row_layout.addWidget(pm_label)

        # 히스테리시스 감소 버튼
        hyst_minus_btn = QPushButton("-")
        hyst_minus_btn.setObjectName(f"{obj_prefix}_hyst_minus")
        hyst_minus_btn.setFixedSize(32, 36)
        hyst_minus_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        row_layout.addWidget(hyst_minus_btn)

        # 히스테리시스 값 표시
        hyst_value_btn = QPushButton(str(default_hyst))
        hyst_value_btn.setObjectName(f"{obj_prefix}_hyst_value")
        hyst_value_btn.setFixedSize(48, 36)
        hyst_value_btn.setStyleSheet("font-size: 12px; font-weight: bold; background-color: #fff3e0;")
        row_layout.addWidget(hyst_value_btn)

        # 히스테리시스 증가 버튼
        hyst_plus_btn = QPushButton("+")
        hyst_plus_btn.setObjectName(f"{obj_prefix}_hyst_plus")
        hyst_plus_btn.setFixedSize(32, 36)
        hyst_plus_btn.setStyleSheet("font-size: 14px; font-weight: bold;")
        row_layout.addWidget(hyst_plus_btn)

        # 단위
        unit_label = QLabel(unit_text)
        unit_label.setFixedWidth(45)
        unit_label.setStyleSheet("font-size: 11px; color: #555;")
        row_layout.addWidget(unit_label)

        return row_layout, {
            'minus': minus_btn,
            'value': value_btn,
            'plus': plus_btn,
            'hyst_minus': hyst_minus_btn,
            'hyst_value': hyst_value_btn,
            'hyst_plus': hyst_plus_btn
        }

    # 시간 설정 행 생성 헬퍼 함수 (히스테리시스 없음)
    def create_time_setting_row(label_text, unit_text, default_val, obj_prefix):
        """시간 설정 입력 행 생성: 라벨 [-][값][+] 단위"""
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 6, 0, 6)
        row_layout.setSpacing(2)

        # 라벨
        label = QLabel(label_text)
        label.setFixedWidth(50)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        row_layout.addWidget(label)

        # 값 감소 버튼
        minus_btn = QPushButton("-")
        minus_btn.setObjectName(f"{obj_prefix}_minus")
        minus_btn.setFixedSize(36, 36)
        minus_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        row_layout.addWidget(minus_btn)

        # 값 표시
        value_btn = QPushButton(str(default_val))
        value_btn.setObjectName(f"{obj_prefix}_value")
        value_btn.setFixedSize(60, 36)
        value_btn.setStyleSheet("font-size: 13px; font-weight: bold; background-color: #f5f5f5;")
        row_layout.addWidget(value_btn)

        # 값 증가 버튼
        plus_btn = QPushButton("+")
        plus_btn.setObjectName(f"{obj_prefix}_plus")
        plus_btn.setFixedSize(36, 36)
        plus_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        row_layout.addWidget(plus_btn)

        # 단위
        unit_label = QLabel(unit_text)
        unit_label.setStyleSheet("font-size: 11px; color: #555;")
        row_layout.addWidget(unit_label)

        row_layout.addStretch()

        return row_layout, {
            'minus': minus_btn,
            'value': value_btn,
            'plus': plus_btn
        }

    # 온도 설정 (목표온도 * 10, 히스테리시스 * 10)
    temp_row, temp_buttons = create_setting_row("온도", "°C", "25.0", "2.0", "temp_set")
    right_layout.addLayout(temp_row)

    # CO2 설정 (ppm)
    co2_row, co2_buttons = create_setting_row("CO2", "ppm", "1500", "800", "co2_set")
    right_layout.addLayout(co2_row)

    # PM2.5 설정 (µg/m³)
    pm25_row, pm25_buttons = create_setting_row("PM2.5", "µg/m³", "35", "5", "pm25_set")
    right_layout.addLayout(pm25_row)

    # SEMI 동작시간 설정 (초)
    time_row, time_buttons = create_time_setting_row("시간", "초", "300", "semi_time")
    right_layout.addLayout(time_row)

    right_layout.addSpacing(10)

    # --- 구분선 ---
    separator2 = QFrame()
    separator2.setFrameShape(QFrame.HLine)
    separator2.setStyleSheet("background-color: #bbb;")
    separator2.setFixedHeight(2)
    right_layout.addWidget(separator2)
    right_layout.addSpacing(10)

    # --- Refresh / SAVE 버튼 ---
    button_row = QHBoxLayout()
    button_row.setContentsMargins(0, 5, 0, 5)
    button_row.setSpacing(10)

    refresh_button = QPushButton("Refresh")
    refresh_button.setObjectName("auto_refresh_button")
    refresh_button.setFixedSize(100, 40)
    refresh_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-size: 13px;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)

    save_button = QPushButton("SAVE")
    save_button.setObjectName("auto_save_button")
    save_button.setFixedSize(100, 40)
    save_button.setStyleSheet("""
        QPushButton {
            background-color: #ff9800;
            color: white;
            font-size: 13px;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #f57c00;
        }
    """)

    button_row.addWidget(refresh_button)
    button_row.addWidget(save_button)
    button_row.addStretch()

    right_layout.addLayout(button_row)
    right_layout.addStretch()

    # ============================================
    # 그리드에 위젯 배치 (2x1 그리드)
    # ============================================
    main_grid.addWidget(left_group, 0, 0)
    main_grid.addWidget(right_group, 0, 1)

    # 컬럼 너비 비율 설정 (1:1)
    main_grid.setColumnStretch(0, 1)
    main_grid.setColumnStretch(1, 1)

    # ============================================
    # 필요한 객체 속성으로 저장
    # ============================================
    # AUTO 모드 버튼
    auto_widget.auto_mode_button = auto_mode_button
    auto_widget.auto_status_label = status_label

    # 모드 상태 인디케이터
    auto_widget.auto_temp_indicator = auto_temp_indicator
    auto_widget.vent_indicator = vent_indicator
    auto_widget.circulation_indicator = circulation_indicator

    # PT02 센서 표시
    auto_widget.pt02_temp_display = temp_display
    auto_widget.pt02_co2_display = co2_display
    auto_widget.pt02_pm25_display = pm25_display

    # 설정 버튼들
    auto_widget.temp_buttons = temp_buttons
    auto_widget.co2_buttons = co2_buttons
    auto_widget.pm25_buttons = pm25_buttons
    auto_widget.time_buttons = time_buttons

    # Refresh / SAVE 버튼
    auto_widget.refresh_button = refresh_button
    auto_widget.save_button = save_button

    # 이전 코드와의 호환성 유지 (기존 속성들)
    auto_widget.fan_speed_slider = None
    auto_widget.temp_slider = None
    auto_widget.fan_speed_value = None
    auto_widget.temp_value = None
    auto_widget.outdoor_vent_button = None
    auto_widget.indoor_vent_button = None
    auto_widget.status_value = status_label
    auto_widget.target_temp = None
    auto_widget.current_temp = temp_display
    auto_widget.fan_speed_status = None
    auto_widget.humidity_status = None
    auto_widget.operation_time = None
    auto_widget.fan_image_label = None
    auto_widget.minus_button = None
    auto_widget.plus_button = None
    auto_widget.temp_minus_button = None
    auto_widget.temp_plus_button = None

    return auto_widget

def create_button_row_with_number(label_text, button, layout, button_width=140, spacing=20):
    """버튼 행 생성 헬퍼 함수 - 숫자 버튼 포함"""
    row_layout = QHBoxLayout()
    row_layout.setContentsMargins(5, 8, 5, 8)  # 상하 마진 증가
    
    label = QLabel(label_text)
    label.setFixedWidth(140)  # 레이블 고정 너비로 정렬 개선
    label.setStyleSheet("font-size: 15px; font-weight: bold;")  # 폰트 크기와 굵기 증가

    # 메인 버튼에 동일한 고정 크기 적용
    button.setFixedSize(button_width, 45)  # 너비와 높이 증가
    button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    button.setStyleSheet("font-size: 14px; font-weight: bold;")  # 버튼 폰트 크기 증가
    
    # 숫자 버튼 생성
    number_button = QPushButton("0")
    number_button.setFixedSize(45, 45)  # 정사각형 숫자 버튼
    number_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    number_button.setStyleSheet("font-size: 14px; font-weight: bold;")
    
    row_layout.addWidget(label)
    row_layout.addSpacing(spacing)  # 조정 가능한 간격
    row_layout.addWidget(button)
    row_layout.addSpacing(10)  # 메인 버튼과 숫자 버튼 사이 간격
    row_layout.addWidget(number_button)
    row_layout.addStretch()  # 오른쪽 여백
    layout.addLayout(row_layout)
    return button, number_button

def create_oa_damper_three_button_row(label_text, layout, button_width=65, spacing=20):
    """OA.DAMP 전용 3버튼 행 생성 - OPEN + 숫자 + CLOSE 동일 크기"""
    row_layout = QHBoxLayout()
    row_layout.setContentsMargins(5, 8, 5, 8)
    
    # 라벨
    label = QLabel(label_text)
    label.setFixedWidth(140)
    label.setStyleSheet("font-size: 15px; font-weight: bold;")
    
    # OPEN 버튼 - 고정 크기
    open_button = QPushButton("OPEN")
    open_button.setFixedSize(button_width, 45)
    open_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    open_button.setStyleSheet("font-size: 14px; font-weight: bold;")
    
    # 숫자 버튼 - 정사각형
    number_button = QPushButton("0")
    number_button.setFixedSize(45, 45)
    number_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    number_button.setStyleSheet("font-size: 14px; font-weight: bold;")
    
    # CLOSE 버튼 - OPEN과 동일한 크기
    close_button = QPushButton("CLOSE")
    close_button.setFixedSize(button_width, 45)  # OPEN과 동일한 크기
    close_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    close_button.setStyleSheet("font-size: 14px; font-weight: bold;")
    
    # 레이아웃에 추가
    row_layout.addWidget(label)
    row_layout.addSpacing(spacing)
    row_layout.addWidget(open_button)
    row_layout.addSpacing(5)
    row_layout.addWidget(number_button)
    row_layout.addSpacing(5)
    row_layout.addWidget(close_button)
    row_layout.addStretch()
    
    layout.addLayout(row_layout)
    
    return open_button, number_button, close_button