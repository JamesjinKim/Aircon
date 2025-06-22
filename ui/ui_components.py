import os
from PyQt5.QtWidgets import (QGroupBox, QLabel, QPushButton, QComboBox, QTextEdit,
                           QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, QWidget, QSizePolicy,
                           QSlider, QGridLayout, QToolButton, QButtonGroup)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

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

def create_button_row(label_text, button, layout, button_width=140):
    """버튼 행 생성 헬퍼 함수"""
    row_layout = QHBoxLayout()
    row_layout.setContentsMargins(5, 8, 5, 8)  # 상하 마진 증가
    
    label = QLabel(label_text)
    label.setMinimumWidth(100)  # 레이블 최소 너비 증가
    label.setStyleSheet("font-size: 15px; font-weight: bold;")  # 폰트 크기와 굵기 증가

    # 모든 버튼에 동일한 고정 크기 적용 - 크기 증가
    button.setFixedSize(button_width, 45)  # 너비와 높이 증가
    button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    button.setStyleSheet("font-size: 14px; font-weight: bold;")  # 버튼 폰트 크기 증가
    
    row_layout.addWidget(label)
    row_layout.addStretch()
    row_layout.addWidget(button)
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
    
    port_combobox = QComboBox()
    port_combobox.setFixedWidth(150)
    
    baudrate_label = QLabel("Baudrate")
    baudrate_label.setAlignment(Qt.AlignCenter)
    baudrate_label.setFixedWidth(70)
    
    baudrate_combobox = QComboBox()
    baudrate_combobox.setFixedWidth(120)
    
    connection_label = QLabel("Connect")
    connection_label.setAlignment(Qt.AlignCenter)
    connection_label.setFixedWidth(70)
    
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
        button.setStyleSheet("background-color: rgb(186,186,186);")
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
    speed_label.setMinimumWidth(100)  # 레이블 최소 너비 증가
    speed_label.setStyleSheet("font-size: 15px; font-weight: bold;")  # 폰트 크기와 굵기 증가
    speed_layout.addWidget(speed_label)
    speed_layout.addStretch()
    
    buttons_layout = QHBoxLayout()
    buttons_layout.setSpacing(8)  # 버튼 사이 간격 증가
    
    # 버튼 생성 - 사용자 정의 텍스트 사용
    button1 = QPushButton(left_text)
    button2 = QPushButton(center_text)
    button3 = QPushButton(right_text)
    
    # 초기 크기 설정 - 크기 증가
    for button in [button1, button2, button3]:
        button.setStyleSheet("background-color: rgb(186,186,186); font-size: 14px; font-weight: bold;")
        button.setFixedSize(50, 45)  # 크기 증가
    
    buttons_layout.addWidget(button1)
    buttons_layout.addWidget(button2)
    buttons_layout.addWidget(button3)
    speed_layout.addLayout(buttons_layout)
    
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
    """AUTO 제어 탭 생성 - 3등분 수평 그리드 레이아웃"""
    # AUTO 탭 전체 위젯
    auto_widget = QWidget()
    
    # 그리드 레이아웃 설정 - 3x1 그리드 (3개의 열, 1개의 행)
    main_grid = QGridLayout(auto_widget)
    main_grid.setContentsMargins(5, 5, 5, 5)
    main_grid.setSpacing(10)  # 그리드 간 간격 증가
    
    # 1. 오른쪽(첫 번째) 그리드: 에어컨 풍량과 온도 조절
    aircon_group, aircon_layout = create_group_box("AIRCON AUTO CONTROL")
    aircon_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    # 풍량 제어 영역
    fan_speed_layout = QVBoxLayout()
    fan_speed_layout.setContentsMargins(10, 10, 10, 10)  # 패딩 추가
    
    # 풍량 제어 헤더
    fan_speed_header = QHBoxLayout()
    
    # 텍스트 레이블 대신 이미지 레이블 생성
    from ui.helpers import get_file_path
    from PyQt5.QtGui import QPixmap
    
    # 이미지 경로 설정
    fan_image_path = get_file_path("images/fan.png")
    
    # 이미지 레이블 생성
    fan_image_label = QLabel()
    fan_image_label.setFixedSize(20, 20)  # 레이블 크기 설정
    pixmap = QPixmap(fan_image_path)
    fan_image_label.setPixmap(pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))  # 이미지 크기 자동 조절    
    
    # 레이아웃에 이미지 레이블 추가
    fan_speed_header.addWidget(fan_image_label)
    
    fan_speed_header.addStretch()
    
    # 풍량 값 표시 레이블
    fan_speed_value = QLabel("0")
    fan_speed_value.setObjectName("fan_speed_value")
    fan_speed_value.setAlignment(Qt.AlignCenter)
    fan_speed_value.setStyleSheet("""
        font-size: 15px;
        font-weight: bold;
        min-width: 40px;  /* 너비 증가 */
        padding: 5px;     /* 패딩 증가 */
        background-color: #f0f0f0;
        border-radius: 4px;
        border: 1px solid #ddd;
    """)
    fan_speed_value.setFixedHeight(30) # 풍량값 txtbox  높이조절 
    fan_speed_header.addWidget(QLabel("속도:"))
    fan_speed_header.addWidget(fan_speed_value)
    
    fan_speed_layout.addLayout(fan_speed_header)
    fan_speed_layout.addSpacing(10)
    
    # 풍량 조절 슬라이더 생성
    fan_speed_slider = QSlider(Qt.Horizontal)
    fan_speed_slider.setMinimum(0)  # 0부터 시작 (꺼짐 상태 포함)
    fan_speed_slider.setMaximum(10)
    fan_speed_slider.setValue(0)  # 초기값 0으로 설정
    fan_speed_slider.setTickPosition(QSlider.TicksBelow)
    fan_speed_slider.setTickInterval(1)
    fan_speed_slider.setObjectName("auto_fan_speed_slider")
    fan_speed_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #2979ff;
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::add-page:horizontal {
            background: #e0e0e0;
            border-radius: 4px;
        }
        
        QSlider::sub-page:horizontal {
            background: #2979ff;
            border-radius: 4px;
        }
    """)
    
    # 슬라이더 추가
    fan_speed_layout.addWidget(fan_speed_slider)
    
    # 속도 표시기 생성 - 간격 조정
    speed_indicator_layout = QHBoxLayout()
    speed_indicator_layout.setSpacing(5)  # 인디케이터 간 간격 조정
    
    # 0부터 10까지 표시 (0: 꺼짐, 1-10: 속도)
    for i in range(0, 11):
        speed_label = QLabel(str(i))
        speed_label.setAlignment(Qt.AlignCenter)
        speed_label.setMinimumWidth(15)  # 최소 너비 설정
        speed_label.setObjectName(f"speed_indicator_{i}")
        # 0번 인디케이터에 초기 강조 스타일 적용
        if i == 0:
            speed_label.setStyleSheet("""
                font-weight: bold;
                color: #2979ff;
                background-color: #e3f2fd;
                border-radius: 4px;
                padding: 3px;
            """)
        speed_indicator_layout.addWidget(speed_label)
    
    fan_speed_layout.addLayout(speed_indicator_layout)
    fan_speed_layout.addSpacing(20)  # 구분선 추가
    
    # 온도 제어 영역도 동일하게 이미지 추가
    temp_layout = QVBoxLayout()
    temp_header = QHBoxLayout()
    
    # 온도 이미지 추가
    temp_image_path = get_file_path("images/thormo-48.png")  # 온도 이미지 파일이 있다고 가정
    temp_image_label = QLabel()
    pixmap = QPixmap(temp_image_path)
    temp_image_label.setPixmap(pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    #temp_image_label.setFixedSize(20, 20)  # 레이블 자체 크기도 맞춰주면 좋음

    # 온도 이미지 파일이 없을 경우를 대비한 예외 처리
    try:
        temp_image_label.setPixmap(QPixmap(temp_image_path))
    except:
        # 이미지 파일이 없으면 텍스트로 대체
        temp_text_label = QLabel("에어컨 온도 설정")
        temp_text_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        temp_header.addWidget(temp_text_label)
    else:
        temp_image_label.setToolTip("에어컨 온도 설정")
        temp_header.addWidget(temp_image_label)
    
    temp_header.addStretch()
    
    # 온도 값 표시 레이블
    temp_value = QLabel("22°C")
    temp_value.setObjectName("temp_value")
    temp_value.setAlignment(Qt.AlignCenter)
    temp_value.setStyleSheet("""
        font-size: 15px;
        font-weight: bold;
        min-width: 60px;  /* 너비 증가 */
        padding: 5px;     /* 패딩 증가 */
        background-color: #f0f0f0;
        border-radius: 4px;
        border: 1px solid #ddd;
    """)
    temp_value.setFixedHeight(30) # 높이 조절
    temp_header.addWidget(QLabel("온도:"))
    temp_header.addWidget(temp_value)
    
    temp_layout.addLayout(temp_header)
    temp_layout.addSpacing(10)
    
    # 온도 조절 슬라이더
    temp_slider = QSlider(Qt.Horizontal)
    temp_slider.setObjectName("temp_slider")
    temp_slider.setMinimum(16)
    temp_slider.setMaximum(30)
    temp_slider.setValue(22)
    temp_slider.setTickPosition(QSlider.TicksBelow)
    temp_slider.setTickInterval(1)
    temp_slider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background: #ff5722;
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::add-page:horizontal {
            background: #e0e0e0;
            border-radius: 4px;
        }
        
        QSlider::sub-page:horizontal {
            background: #ff5722;
            border-radius: 4px;
        }
    """)
    
    temp_layout.addWidget(temp_slider)
    
    # 온도 표시기
    temp_indicator_layout = QHBoxLayout()
    temp_indicator_layout.setSpacing(10)  # 간격 조정
    
    # 온도는 많으므로 몇 개만 표시 (16, 19, 22, 25, 28, 30)
    temp_values = [16, 19, 22, 25, 27, 30]
    for temp in temp_values:
        temp_label = QLabel(str(temp))
        temp_label.setObjectName(f"temp_indicator_{temp}")
        temp_label.setAlignment(Qt.AlignCenter)
        temp_label.setMinimumWidth(20)  # 최소 너비 설정
        # 22도에 초기 강조 스타일 적용
        if temp == 22:
            temp_label.setStyleSheet("""
                font-weight: bold;
                color: #f44336;
                background-color: #ffebee;
                border-radius: 4px;
                padding: 3px;
            """)
        temp_indicator_layout.addWidget(temp_label)
    
    temp_layout.addLayout(temp_indicator_layout)
    
    # AUTO 모드 버튼 추가
    auto_mode_button = QPushButton("AUTO 모드 시작")
    auto_mode_button.setStyleSheet("""
        QPushButton {
            background-color: #2979ff;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            border-radius: 4px;
            margin-top: 15px;
        }
        QPushButton:hover {
            background-color: #2962ff;
        }
        QPushButton:pressed {
            background-color: #1565c0;
        }
    """)
    
    # 에어컨 제어 레이아웃에 요소 추가
    aircon_layout.addLayout(fan_speed_layout)
    aircon_layout.addLayout(temp_layout)
    aircon_layout.addWidget(auto_mode_button)
    aircon_layout.addStretch()  # 남은 공간 채우기
    
    # 2. 중간 그리드: 환기 제어 (외기유입, 내기순환 버튼 추가)
    middle_group, middle_layout = create_group_box("환기 제어")
    middle_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    # 환기 제어 설명 텍스트
    ventilation_description = QLabel("환기 모드를 선택하세요")
    ventilation_description.setAlignment(Qt.AlignCenter)
    ventilation_description.setStyleSheet("""
        font-size: 14px;
        font-weight: bold;
        margin-bottom: 10px;
        padding: 5px;
    """)
    middle_layout.addWidget(ventilation_description)
    
    # 이미지 로딩 경로 설정
    outdoor_image_path = get_file_path("images/out-30.png")
    indoor_image_path = get_file_path("images/in-50.png")
    
    # 버튼 스타일시트 정의
    vent_button_style = """
        QToolButton {
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 15px 10px;
            text-align: center;
            min-height: 80px;
            min-width: 80px;
            font-size: 14px;
        }
        QToolButton:hover {
            background-color: #e0e0e0;
        }
        QToolButton:pressed {
            background-color: #d0d0d0;
        }
        QToolButton:checked {
            background-color: #bbdefb;
            border: 2px solid #2979ff;
        }
    """
    
    # 그리드 레이아웃 설정
    ventilation_grid = QGridLayout()
    ventilation_grid.setSpacing(15)  # 그리드 간격
    
    # 외기유입 버튼 생성 (QToolButton 사용)
    outdoor_button = QToolButton()
    outdoor_button.setText("외기유입")
    outdoor_button.setIcon(QIcon(outdoor_image_path))
    outdoor_button.setIconSize(QSize(32, 32))  # 이미지 크기 키움
    outdoor_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트 배치
    outdoor_button.setObjectName("outdoor_button")
    outdoor_button.setCheckable(True)
    outdoor_button.setStyleSheet(vent_button_style)
    
    # 내기순환 버튼 생성
    indoor_button = QToolButton()
    indoor_button.setText("내기순환")
    indoor_button.setIcon(QIcon(indoor_image_path))
    indoor_button.setIconSize(QSize(32, 32))  # 이미지 크기 키움
    indoor_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # 아이콘 아래 텍스트 배치
    indoor_button.setObjectName("indoor_button")
    indoor_button.setCheckable(True)
    indoor_button.setStyleSheet(vent_button_style)
    
    # 버튼과 설명을 담을 컨테이너 위젯 생성
    outdoor_container = QWidget()
    outdoor_layout = QVBoxLayout(outdoor_container)
    outdoor_layout.setContentsMargins(5, 5, 5, 5)
    outdoor_layout.setSpacing(2)
    outdoor_layout.addWidget(outdoor_button, 1)  # 버튼에 더 많은 공간 할당
    #outdoor_layout.addWidget(outdoor_desc, 0)   # 설명에 더 적은 공간 할당
    
    indoor_container = QWidget()
    indoor_layout = QVBoxLayout(indoor_container)
    indoor_layout.setContentsMargins(5, 5, 5, 5)
    indoor_layout.setSpacing(2)
    indoor_layout.addWidget(indoor_button, 1)
    #indoor_layout.addWidget(indoor_desc, 0)
    
    # 그리드에 컨테이너 추가
    ventilation_grid.addWidget(outdoor_container, 0, 0)
    ventilation_grid.addWidget(indoor_container, 0, 1)
    
    # 버튼 그룹으로 묶어 하나만 선택되도록 설정
    vent_button_group = QButtonGroup(auto_widget)
    vent_button_group.addButton(outdoor_button)
    vent_button_group.addButton(indoor_button)
    vent_button_group.setExclusive(True)  # 한 번에 하나만 선택 가능
    
    # 버튼 토글 시 명령어 전송 함수
    def toggle_outdoor_vent(checked):
        if checked:
            print("외기유입 모드 활성화")

        else:
            print("외기유입 모드 비활성화")
    
    def toggle_indoor_vent(checked):
        if checked:
            print("내기순환 모드 활성화")
        else:
            print("내기순환 모드 비활성화")
    
    # 버튼에 토글 이벤트 연결
    outdoor_button.toggled.connect(toggle_outdoor_vent)
    indoor_button.toggled.connect(toggle_indoor_vent)
    
    # 환기 모드 설명 텍스트
    mode_description = QLabel("* 한 가지 모드만 작동시킬 수 있습니다.")
    mode_description.setAlignment(Qt.AlignCenter)
    mode_description.setStyleSheet("""
        font-size: 12px;
        color: #777;
        margin-top: 10px;
        font-style: italic;
    """)
    
    # 환기 제어 레이아웃에 추가
    middle_layout.addLayout(ventilation_grid)
    middle_layout.addWidget(mode_description)
    middle_layout.addStretch()  # 남은 공간 채우기
    
    # 3. 맨 우측 그리드: 시스템 상태 정보
    status_group, status_layout = create_group_box("시스템 상태 정보")
    status_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    
    # 상태 테이블 스타일
    status_style = """
        QLabel {
            padding: 8px;
            font-size: 14px;
            min-width: 80px;  /* 최소 너비 설정 */
        }
    """
    
    # 상태 그리드
    status_grid = QGridLayout()
    status_grid.setVerticalSpacing(12)  # 세로 간격 증가
    status_grid.setHorizontalSpacing(15)
    status_grid.setContentsMargins(10, 10, 10, 10)  # 여백 추가
    
    # 상태 레이블 추가
    def add_status_row(row, title, value, value_color="#333"):
        title_label = QLabel(title)
        title_label.setStyleSheet(status_style)
        title_label.setMinimumWidth(90)  # 제목 레이블 최소 너비
        title_label.setFixedHeight(40)  # 높이 조절
        
        value_label = QLabel(value)
        value_label.setObjectName(f"status_{row}")
        value_label.setStyleSheet(f"{status_style} font-weight: bold; color: {value_color};")
        value_label.setMinimumWidth(80)  # 값 레이블 최소 너비
        value_label.setFixedHeight(40)  # 높이 조절
        
        status_grid.addWidget(title_label, row, 0)
        status_grid.addWidget(value_label, row, 1)
        return value_label
    
    # 상태 항목 추가
    status_value = add_status_row(0, "현재 상태:", "대기 중", "#2962ff")
    target_temp = add_status_row(1, "목표 온도:", "22°C")
    current_temp = add_status_row(2, "현재 온도:", "25°C")
    fan_speed_status = add_status_row(3, "풍량 설정:", "0단계")
    humidity_status = add_status_row(4, "현재 습도:", "45%")
    operation_time = add_status_row(5, "작동 시간:", "00:00:00")
    
    # 추가 정보 라벨
    extra_info = QLabel("자동 제어 모드는 설정된 온도와 풍량에 따라 에어컨과 제습기를 자동으로 제어합니다.")
    extra_info.setWordWrap(True)
    extra_info.setStyleSheet("""
        font-size: 13px;
        color: #555;
        padding: 7px;
        margin-top: 10px;
        background-color: #f0f0f0;
        border-radius: 4px;
    """)
    
    status_layout.addLayout(status_grid)
    status_layout.addWidget(extra_info)
    status_layout.addStretch()  # 남은 공간 채우기
    
    # 그리드에 위젯 배치 (3x1 그리드)
    main_grid.addWidget(aircon_group, 0, 0)     # 첫 번째 열
    main_grid.addWidget(middle_group, 0, 1)     # 두 번째 열
    main_grid.addWidget(status_group, 0, 2)     # 세 번째 열
    
    # 각 컬럼의 너비 비율 설정 (균등하게)
    main_grid.setColumnStretch(0, 1)  # 첫 번째 열
    main_grid.setColumnStretch(1, 1)  # 두 번째 열
    main_grid.setColumnStretch(2, 1)  # 세 번째 열
    
    # 필요한 객체 속성으로 저장
    auto_widget.auto_mode_button = auto_mode_button
    auto_widget.fan_speed_slider = fan_speed_slider
    auto_widget.temp_slider = temp_slider
    auto_widget.fan_speed_value = fan_speed_value
    auto_widget.temp_value = temp_value
    
    # 환기 버튼 저장
    auto_widget.outdoor_vent_button = outdoor_button
    auto_widget.indoor_vent_button = indoor_button
    
    # 상태 레이블 저장
    auto_widget.status_value = status_value
    auto_widget.target_temp = target_temp
    auto_widget.current_temp = current_temp
    auto_widget.fan_speed_status = fan_speed_status
    auto_widget.humidity_status = humidity_status
    auto_widget.operation_time = operation_time
    
    # 이미지 레이블 저장
    auto_widget.fan_image_label = fan_image_label
    
    # 이전 코드와의 호환성 유지
    auto_widget.minus_button = None
    auto_widget.plus_button = None
    auto_widget.temp_minus_button = None
    auto_widget.temp_plus_button = None
    
    return auto_widget