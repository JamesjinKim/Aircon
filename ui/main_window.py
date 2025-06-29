import os
import sys
import platform
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QDesktopWidget, QWidget,
                           QAction, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton,
                           QComboBox, QGroupBox, QTextEdit, QFrame, QStatusBar, QTabWidget, QSlider,
                           QGridLayout, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QDateTime, QRect, QMetaObject, QCoreApplication, QSize
from PyQt5.QtGui import QIcon, QDesktopServices, QGuiApplication, QFont

from managers.serial_manager import SerialManager
from managers.button_manager import ButtonManager
from managers.speed_manager import SpeedButtonManager
from managers.auto_manager import AutoSpeedManager

from ui.constants import BUTTON_ON_STYLE, BUTTON_OFF_STYLE
from ui.helpers import get_file_path, configure_display_settings
from ui.ui_components import (create_group_box, create_button_row, create_port_selection_section,
                            create_speed_buttons, create_fan_speed_control,
                            create_auto_control_tab, create_speed_buttons_with_text)
from ui.setup_buttons import setup_button_groups

class ControlWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 창 설정
        self.setWindowTitle('Remote control')
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        
        # 디스플레이 설정
        configure_display_settings(self)
            
        # 시리얼 매니저 초기화
        self.serial_manager = SerialManager()
        
        # AUTO 스피드 매니저 초기화 (UI 요소 생성 전에 초기화)
        self.auto_speed_manager = AutoSpeedManager(
            serial_manager=self.serial_manager,
            SendData_textEdit=None  # UI 요소가 아직 생성되지 않아 None으로 초기화
        )
        
        # UI 요소 생성
        self.setup_ui()
        
        # 메시지 텍스트 에디터 더미 생성 (메시지 기능 제거로 인한 None 처리)
        self.SendData_textEdit = None
        self.ReceiveData_textEdit = None
        self.send_clear = None
        self.receive_clear = None
        
        # SendData_textEdit 설정 (UI 생성 후)
        self.auto_speed_manager.SendData_textEdit = self.SendData_textEdit
        
        # 버튼 매니저 초기화 (UI 요소 생성 후에 초기화 해야 함)
        self.button_manager = ButtonManager(
            serial_manager=self.serial_manager, 
            SendData_textEdit=self.SendData_textEdit, 
            ReceiveData_textEdit=self.ReceiveData_textEdit
        )
        
        # 스피드 버튼 매니저 초기화
        self.speed_button_manager = SpeedButtonManager(
            serial_manager=self.serial_manager,
            SendData_textEdit=self.SendData_textEdit
        )
        
        # 스피드 버튼 매니저에 메인 윈도우 참조 설정
        self.speed_button_manager.set_main_window(self)
        
        # 스피드 버튼 생성 및 연결
        self.speed_button_manager.create_aircon_fan_speed_buttons(
            self, self.spdButton_2, self.spdButton_3, self.spdButton_4
        )
        self.speed_button_manager.create_aircon_con_fan_speed_buttons(
            self, self.spdButton_6, self.spdButton_7, self.spdButton_8
        )
        
        
        # AUTO 탭 컨트롤 연결
        self.connect_auto_controls()
        
        # 포트 스캔 타이머
        self.port_scan_timer = QTimer(self)
        self.port_scan_timer.timeout.connect(self.scan_ports_periodically)
        self.port_scan_timer.start(1000)  # 1초마다 실행 (1000 = 1초 단위)

        # 종료 버튼 연결
        self.exitButton.clicked.connect(self.close)
        self.exitButton.setText("종료")
        
        # 창을 항상 최상위로 유지
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 타이머 및 상태바 초기화
        self.read_timer = QTimer(self)
        self.read_timer.timeout.connect(self.read_serial_data)
        self.read_timer.start(100)

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_time)
        self.status_timer.start(1000)

        self.statusBar().showMessage(QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate))

        # 포트 및 보레이트 설정
        self.scan_ports()
        for rate in self.serial_manager.supported_baudrates:
            self.baudrate_combobox.addItem(str(rate))
        self.baudrate_combobox.setCurrentText("115200")

        # 버튼 연결
        self.connectButton.clicked.connect(self.connect_serial)

        # 상태 표시기 초기화
        self.update_status_indicator("disconnected")
        self.update_connect_button("disconnected")
        
        # 클리어 버튼 연결 제거 (메시지 기능 제거로 인함)
        
        # 버튼 그룹 설정 - 마지막에 실행 (SPD 버튼 제외)
        setup_button_groups(self)
        
        # DESICCANT FAN 스피드 버튼 생성 및 연결 (UI 설정 후에 연결)
        if hasattr(self, 'spdButton_dsct_fan1_dec'):
            self.speed_button_manager.create_dsct_fan_speed_buttons(
                self, 1, self.spdButton_dsct_fan1_dec, self.spdButton_dsct_fan1_val, self.spdButton_dsct_fan1_inc
            )
            self.speed_button_manager.create_dsct_fan_speed_buttons(
                self, 2, self.spdButton_dsct_fan2_dec, self.spdButton_dsct_fan2_val, self.spdButton_dsct_fan2_inc
            )
            self.speed_button_manager.create_dsct_fan_speed_buttons(
                self, 3, self.spdButton_dsct_fan3_dec, self.spdButton_dsct_fan3_val, self.spdButton_dsct_fan3_inc
            )
            self.speed_button_manager.create_dsct_fan_speed_buttons(
                self, 4, self.spdButton_dsct_fan4_dec, self.spdButton_dsct_fan4_val, self.spdButton_dsct_fan4_inc
            )
        
        # DAMPER 위치 버튼 생성 및 연결 (UI 설정 후에 연결)
        if hasattr(self, 'dmpButton_pos_1_dec'):
            # DMP1 위치값 버튼들
            self.speed_button_manager.create_damper_position_buttons(
                self, 1, self.dmpButton_pos_1_dec, self.dmpButton_pos_1_val, self.dmpButton_pos_1_inc
            )
            
            # DMP2 위치값 버튼들
            self.speed_button_manager.create_damper_position_buttons(
                self, 2, self.dmpButton_pos_2_dec, self.dmpButton_pos_2_val, self.dmpButton_pos_2_inc
            )
            
            # DMP3 위치값 버튼들
            self.speed_button_manager.create_damper_position_buttons(
                self, 3, self.dmpButton_pos_3_dec, self.dmpButton_pos_3_val, self.dmpButton_pos_3_inc
            )
            
            # DMP4 위치값 버튼들
            self.speed_button_manager.create_damper_position_buttons(
                self, 4, self.dmpButton_pos_4_dec, self.dmpButton_pos_4_val, self.dmpButton_pos_4_inc
            )
        
        # PUMPER 스피드 버튼 생성 및 연결 (UI 설정 후에 연결)
        if hasattr(self, 'spdButton_pump1_dec'):
            self.speed_button_manager.create_pumper_speed_buttons(
                self, 1, self.spdButton_pump1_dec, self.spdButton_pump1_val, self.spdButton_pump1_inc
            )
            self.speed_button_manager.create_pumper_speed_buttons(
                self, 2, self.spdButton_pump2_dec, self.spdButton_pump2_val, self.spdButton_pump2_inc
            )
        
        # 모든 스피드 버튼의 크기를 균일하게 맞추기 위한 추가 코드
        QTimer.singleShot(100, self.ensure_uniform_button_sizes)

        self.auto_speed_manager.set_speed_button_manager(self.speed_button_manager)
        self.speed_button_manager.set_auto_manager(self.auto_speed_manager)
        
        # ButtonManager와 SpeedButtonManager 연결
        self.button_manager.set_speed_button_manager(self.speed_button_manager)

        
    def connect_auto_controls(self):
        """AUTO 탭의 컨트롤을 연결하는 메서드"""
        if hasattr(self, 'auto_tab'):
            # AUTO 제어 위젯 찾기
            auto_control_widget = self.auto_tab.findChild(QWidget)
            if auto_control_widget and self.auto_speed_manager:
                self.auto_speed_manager.connect_auto_controls(auto_control_widget)
    
    def ensure_uniform_button_sizes(self):
        """모든 버튼 크기를 동일하게 설정"""
        # 스피드 버튼 크기 맞추기
        speed_fan_buttons = [self.spdButton_2, self.spdButton_3, self.spdButton_4]
        speed_con_fan_buttons = [self.spdButton_6, self.spdButton_7, self.spdButton_8]
        
        # DSCT FAN 스피드 버튼들
        dsct_speed_buttons = []
        if hasattr(self, 'spdButton_dsct_fan1_dec'):
            dsct_speed_buttons.extend([
                self.spdButton_dsct_fan1_dec, self.spdButton_dsct_fan1_val, self.spdButton_dsct_fan1_inc,
                self.spdButton_dsct_fan2_dec, self.spdButton_dsct_fan2_val, self.spdButton_dsct_fan2_inc,
                self.spdButton_dsct_fan3_dec, self.spdButton_dsct_fan3_val, self.spdButton_dsct_fan3_inc,
                self.spdButton_dsct_fan4_dec, self.spdButton_dsct_fan4_val, self.spdButton_dsct_fan4_inc
            ])
        
        # DAMPER 위치 버튼들
        damper_buttons = []
        if hasattr(self, 'dmpButton_pos_1_dec'):
            damper_buttons.extend([
                self.dmpButton_pos_1_dec, self.dmpButton_pos_1_val, self.dmpButton_pos_1_inc,
                self.dmpButton_pos_2_dec, self.dmpButton_pos_2_val, self.dmpButton_pos_2_inc,
                self.dmpButton_pos_3_dec, self.dmpButton_pos_3_val, self.dmpButton_pos_3_inc,
                self.dmpButton_pos_4_dec, self.dmpButton_pos_4_val, self.dmpButton_pos_4_inc
            ])
        
        # PUMPER 스피드 버튼들
        pumper_speed_buttons = []
        if hasattr(self, 'spdButton_pump1_dec'):
            pumper_speed_buttons.extend([
                self.spdButton_pump1_dec, self.spdButton_pump1_val, self.spdButton_pump1_inc,
                self.spdButton_pump2_dec, self.spdButton_pump2_val, self.spdButton_pump2_inc
            ])
        
        # 모든 스피드 버튼에 동일한 크기 설정 - 크기 증가
        for button in speed_fan_buttons + speed_con_fan_buttons + dsct_speed_buttons + pumper_speed_buttons:
            button.setFixedSize(50, 45)
            
        # DAMPER 버튼들은 조금 작게 설정 (이미 create_damper_row에서 설정됨)
        for button in damper_buttons:
            button.setFixedSize(40, 45)
        
        # Fan, Con Fan 버튼들 - 스피드 버튼과 동일한 너비 (166px)
        main_fan_buttons = [self.pushButton_1, self.pushButton_5]  # Fan, Con Fan
        for button in main_fan_buttons:
            button.setFixedSize(166, 45)
        
        # 나머지 일반 버튼들 - 기본 크기
        other_buttons = [
            self.pushButton_9, self.pushButton_10, self.pushButton_11, self.pushButton_12,  # DMP 버튼들
            self.pushButton_13, self.pushButton_14,  # INVERTER, CLUCH
        ]
        
        # DSCT FAN 버튼들 추가 (존재하는 경우)
        if hasattr(self, 'pushButton_dsct_fan1'):
            other_buttons.extend([
                self.pushButton_dsct_fan1, self.pushButton_dsct_fan2, 
                self.pushButton_dsct_fan3, self.pushButton_dsct_fan4
            ])
        
        # PUMPER & SOL 버튼들 추가 (존재하는 경우)
        if hasattr(self, 'pushButton_pump1'):
            other_buttons.extend([
                self.pushButton_pump1, self.pushButton_pump2
            ])
        if hasattr(self, 'pushButton_sol1'):
            other_buttons.extend([
                self.pushButton_sol1, self.pushButton_sol2, 
                self.pushButton_sol3, self.pushButton_sol4
            ])
        
        # 나머지 버튼들에 기본 크기 설정
        for button in other_buttons:
            button.setFixedSize(140, 45)
            
    def setup_ui(self):
        """UI 요소 생성 - 800x480 크기에 최적화된 그리드 레이아웃"""
        # 메인 레이아웃
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        
        # 상단 영역 생성
        top_layout, self.port_combobox, self.baudrate_combobox, self.connectButton, self.status_label, self.exitButton = create_port_selection_section()
        
        # 탭 위젯 생성
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #C2C7CB;
                background: #f0f0f0; 
            }
            QTabBar::tab {
                background: #e0e0e0;
                min-width: 8ex;
                padding: 8px 15px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #f0f0f0;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # 탭 폰트 사이즈 조정
        font = self.tab_widget.font()
        font.setPointSize(10)
        font.setBold(True)
        self.tab_widget.setFont(font)
        
        # 첫 번째 탭 - AIRCON
        self.aircon_tab = QWidget()
        self.setup_aircon_tab()
        self.tab_widget.addTab(self.aircon_tab, "AIRCON")
        
        # 두 번째 탭 - DESICCANT
        self.desiccant_tab = QWidget()
        self.setup_desiccant_tab()
        self.tab_widget.addTab(self.desiccant_tab, "DESICCANT")
        
        # 세 번째 탭 - DAMPER
        self.damper_tab = QWidget()
        self.setup_damper_tab()
        self.tab_widget.addTab(self.damper_tab, "DAMPER")
        
        # 네 번째 탭 - PUMPER & SOL
        self.pumper_sol_tab = QWidget()
        self.setup_pumper_sol_tab()
        self.tab_widget.addTab(self.pumper_sol_tab, "PUMPER & SOL")
        
        # 다섯 번째 탭 - AUTO 모드
        self.auto_tab = QWidget()
        self.setup_auto_tab()
        self.tab_widget.addTab(self.auto_tab, "AUTO")
        
        # 메인 레이아웃에 모든 영역 추가
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.tab_widget, 1)  # 탭이 나머지 공간을 모두 차지하도록 설정
        
        # 상태바 추가
        self.statusBar()
    
    def setup_aircon_tab(self):
        """AIRCON 탭 설정 - 2컬럼 레이아웃"""
        # AIRCON 탭 메인 레이아웃
        main_grid = QGridLayout(self.aircon_tab)
        main_grid.setContentsMargins(10, 10, 10, 10)  # 마진 증가
        main_grid.setSpacing(15)  # 그룹 간 간격 증가
        
        # 왼쪽 그룹: Fan Controls - 여백 조정
        left_group, left_layout = create_group_box("FAN CONTROLS", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aircon Fan - 스피드 버튼과 동일한 너비 (50*3 + 8*2 = 166)
        self.pushButton_1 = create_button_row("Fan", QPushButton("OFF"), left_layout, button_width=166)
        
        # Aircon Fan Speed 
        self.spdButton_2, self.spdButton_3, self.spdButton_4 = create_speed_buttons_with_text(
            left_layout, "Fan SPD", "<", "0", ">"
        )
        
        # Aircon Con Fan - 스피드 버튼과 동일한 너비 (50*3 + 8*2 = 166)
        self.pushButton_5 = create_button_row("Con Fan", QPushButton("OFF"), left_layout, button_width=166)
        
        # Aircon Con Fan Speed
        self.spdButton_6, self.spdButton_7, self.spdButton_8 = create_speed_buttons_with_text(
            left_layout, "Con Fan SPD", "<", "0", ">"
        )
        
        # 왼쪽 그룹 여백 최소화
        left_layout.addStretch(1)  # 최소 여백만 추가
        
        # 오른쪽 그룹: DMP & Other Controls - 여백 조정
        right_group, right_layout = create_group_box("DMP CONTROLS", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Aircon Left Top DMP
        self.pushButton_9 = create_button_row("Left Top DMP", QPushButton("CLOSE"), right_layout)
        
        # Aircon Left Bottom DMP
        self.pushButton_10 = create_button_row("Left Bottom DMP", QPushButton("CLOSE"), right_layout)
        
        # Aircon Right Top DMP
        self.pushButton_11 = create_button_row("Right Top DMP", QPushButton("CLOSE"), right_layout)
        
        # Aircon Right Bottom DMP
        self.pushButton_12 = create_button_row("Right Bottom DMP", QPushButton("CLOSE"), right_layout)
        
        # Inverter
        self.pushButton_13 = create_button_row("INVERTER", QPushButton("OFF"), right_layout)
        
        # CLUCH
        self.pushButton_14 = create_button_row("CLUCH", QPushButton("OFF"), right_layout)
        
        # 오른쪽 그룹 여백 최소화
        right_layout.addStretch(1)  # 최소 여백만 추가
        
        # 2컬럼 그리드에 위젯 배치 (왼쪽:오른쪽 = 1:1)
        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)
        
        # 컬럼 너비 비율 설정 (1:1)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)
    
    def setup_desiccant_tab(self):
        """DESICCANT 탭 설정 - 가로 배치 레이아웃"""
        # DESICCANT 탭 레이아웃
        desiccant_grid = QGridLayout(self.desiccant_tab)
        desiccant_grid.setContentsMargins(5, 5, 5, 5)
        desiccant_grid.setSpacing(5)
        
        # DESICCANT 컨트롤 영역
        desiccant_group, desiccant_layout = create_group_box("DESICCANT CONTROLS", margins=(15, 30, 15, 15))
        desiccant_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # FAN1 제어 - 가로 배치
        self.create_dsct_fan_row(desiccant_layout, 1)
        
        # FAN2 제어 - 가로 배치
        self.create_dsct_fan_row(desiccant_layout, 2)
        
        # FAN3 제어 - 가로 배치
        self.create_dsct_fan_row(desiccant_layout, 3)
        
        # FAN4 제어 - 가로 배치
        self.create_dsct_fan_row(desiccant_layout, 4)
        
        # 여백 추가
        desiccant_layout.addStretch()
        
        # 그리드에 위젯 배치
        desiccant_grid.addWidget(desiccant_group, 0, 0)
    
    def create_dsct_fan_row(self, parent_layout, fan_num):
        """DESICCANT FAN 행 생성 - 가로 배치"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 8, 5, 8)
        row_layout.setSpacing(10)  # 버튼 간 간격
        
        # FAN 라벨
        fan_label = QLabel(f"FAN{fan_num}")
        fan_label.setFixedWidth(60)
        fan_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        fan_label.setAlignment(Qt.AlignCenter)
        
        # ON/OFF 토글 버튼
        toggle_button = QPushButton("OFF")
        toggle_button.setFixedSize(80, 45)
        toggle_button.setStyleSheet("font-size: 14px; font-weight: bold; background-color: rgb(186,186,186); color: rgb(0,0,0);")
        
        # 버튼을 self에 저장
        setattr(self, f"pushButton_dsct_fan{fan_num}", toggle_button)
        
        # SPD 버튼들 생성
        dec_button = QPushButton("<")
        val_button = QPushButton("0")
        inc_button = QPushButton(">")
        
        # SPD 버튼 스타일 및 크기 설정
        for button in [dec_button, val_button, inc_button]:
            button.setFixedSize(50, 45)
            button.setStyleSheet("background-color: rgb(186,186,186); font-size: 14px; font-weight: bold;")
        
        # 버튼들을 self에 저장
        setattr(self, f"spdButton_dsct_fan{fan_num}_dec", dec_button)
        setattr(self, f"spdButton_dsct_fan{fan_num}_val", val_button)
        setattr(self, f"spdButton_dsct_fan{fan_num}_inc", inc_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(fan_label)
        row_layout.addWidget(toggle_button)
        row_layout.addSpacing(15)  # 토글 버튼과 SPD 버튼 사이 간격
        row_layout.addWidget(dec_button)
        row_layout.addWidget(val_button)
        row_layout.addWidget(inc_button)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)
    
    def setup_auto_tab(self):
        """AUTO 모드 탭 설정 - 그리드 레이아웃 기반"""
        # AUTO 탭 레이아웃 - 그리드로 설정
        auto_grid = QGridLayout(self.auto_tab)
        auto_grid.setContentsMargins(5, 5, 5, 5)
        auto_grid.setSpacing(5)
        
        # AUTO 제어 영역 생성
        auto_control_widget = create_auto_control_tab(self)
        
        # 그리드에 위젯 배치 (1x1 그리드)
        auto_grid.addWidget(auto_control_widget, 0, 0)
        
        # 필요한 객체 저장
        self.auto_control_widget = auto_control_widget
        
        # 풍량 슬라이더 저장
        self.auto_fan_speed_slider = auto_control_widget.fan_speed_slider
        self.auto_fan_speed_value = auto_control_widget.fan_speed_value
        
        # 온도 슬라이더 저장
        self.auto_temp_slider = auto_control_widget.temp_slider
        self.auto_temp_value = auto_control_widget.temp_value
        
        # 버튼 저장
        self.auto_mode_button = auto_control_widget.auto_mode_button

    def setup_damper_tab(self):
        """DAMPER 탭 설정 - 이중 위치값 방식"""
        # DAMPER 탭 레이아웃
        damper_grid = QGridLayout(self.damper_tab)
        damper_grid.setContentsMargins(5, 5, 5, 5)
        damper_grid.setSpacing(5)
        
        # DAMPER 컨트롤 영역
        damper_group, damper_layout = create_group_box("DAMPER CONTROLS", margins=(15, 30, 15, 15))
        damper_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # DMP1 제어 - 이중 위치값
        self.create_damper_row(damper_layout, 1)
        
        # DMP2 제어 - 이중 위치값
        self.create_damper_row(damper_layout, 2)
        
        # DMP3 제어 - 이중 위치값
        self.create_damper_row(damper_layout, 3)
        
        # DMP4 제어 - 이중 위치값
        self.create_damper_row(damper_layout, 4)
        
        # 여백 추가
        damper_layout.addStretch()
        
        # 그리드에 위젯 배치
        damper_grid.addWidget(damper_group, 0, 0)
    
    def create_damper_row(self, parent_layout, dmp_num):
        """DAMPER 행 생성 - 라벨 방식"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 8, 5, 8)
        row_layout.setSpacing(8)  # 버튼 간 간격
        
        # DMP 라벨
        dmp_label = QLabel(f"DMP{dmp_num}")
        dmp_label.setFixedWidth(60)
        dmp_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        dmp_label.setAlignment(Qt.AlignCenter)
        
        # CLOSE 라벨 (클릭 불가능)
        close_label = QLabel("CLOSE")
        close_label.setFixedWidth(60)
        close_label.setStyleSheet("font-size: 12px; font-weight: bold; color: rgb(0,0,0);")
        close_label.setAlignment(Qt.AlignCenter)
        
        # 위치값 버튼들 생성
        pos_dec_button = QPushButton("<")
        pos_val_button = QPushButton("0")
        pos_inc_button = QPushButton(">")
        
        # 위치값 버튼 스타일 및 크기 설정
        for button in [pos_dec_button, pos_val_button, pos_inc_button]:
            button.setFixedSize(40, 45)
            button.setStyleSheet("background-color: rgb(186,186,186); font-size: 12px; font-weight: bold;")
        
        # OPEN 라벨 (클릭 불가능)
        open_label = QLabel("OPEN")
        open_label.setFixedWidth(60)
        open_label.setStyleSheet("font-size: 12px; font-weight: bold; color: rgb(0,0,0);")
        open_label.setAlignment(Qt.AlignCenter)
        
        # 버튼들을 self에 저장 (위치값 버튼만)
        setattr(self, f"dmpButton_pos_{dmp_num}_dec", pos_dec_button)
        setattr(self, f"dmpButton_pos_{dmp_num}_val", pos_val_button)
        setattr(self, f"dmpButton_pos_{dmp_num}_inc", pos_inc_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(dmp_label)
        row_layout.addSpacing(8)
        row_layout.addWidget(close_label)
        row_layout.addSpacing(10)  # CLOSE와 위치값 버튼 사이 간격
        row_layout.addWidget(pos_dec_button)
        row_layout.addWidget(pos_val_button)
        row_layout.addWidget(pos_inc_button)
        row_layout.addSpacing(10)  # 위치값 버튼과 OPEN 사이 간격
        row_layout.addWidget(open_label)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)

    def setup_pumper_sol_tab(self):
        """PUMPER & SOL 탭 설정 - 2컬럼 레이아웃"""
        # PUMPER & SOL 탭 메인 레이아웃
        main_grid = QGridLayout(self.pumper_sol_tab)
        main_grid.setContentsMargins(10, 10, 10, 10)
        main_grid.setSpacing(15)
        
        # 왼쪽 그룹: PUMPER CONTROLS
        left_group, left_layout = create_group_box("PUMPER CONTROLS", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # PUMP1 제어 - FAN과 동일한 패턴
        self.create_pumper_row(left_layout, 1)
        
        # PUMP2 제어 - FAN과 동일한 패턴
        self.create_pumper_row(left_layout, 2)
        
        # 왼쪽 그룹 여백
        left_layout.addStretch(1)
        
        # 오른쪽 그룹: SOL CONTROLS
        right_group, right_layout = create_group_box("SOL CONTROLS", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # SOL1 제어
        self.pushButton_sol1 = create_button_row("SOL1", QPushButton("OFF"), right_layout)
        
        # SOL2 제어
        self.pushButton_sol2 = create_button_row("SOL2", QPushButton("OFF"), right_layout)
        
        # SOL3 제어
        self.pushButton_sol3 = create_button_row("SOL3", QPushButton("OFF"), right_layout)
        
        # SOL4 제어
        self.pushButton_sol4 = create_button_row("SOL4", QPushButton("OFF"), right_layout)
        
        # 오른쪽 그룹 여백
        right_layout.addStretch(1)
        
        # 2컬럼 그리드에 위젯 배치 (왼쪽:오른쪽 = 1:1)
        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)
        
        # 컬럼 너비 비율 설정 (1:1)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)

    def create_pumper_row(self, parent_layout, pump_num):
        """PUMPER 행 생성 - DSCT FAN과 동일한 패턴"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 8, 5, 8)
        row_layout.setSpacing(10)  # 버튼 간 간격
        
        # PUMP 라벨
        pump_label = QLabel(f"PUMP{pump_num}")
        pump_label.setFixedWidth(80)
        pump_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        pump_label.setAlignment(Qt.AlignCenter)
        
        # PUMP ON/OFF 토글 버튼
        pump_button = QPushButton("OFF")
        pump_button.setFixedSize(140, 45)
        pump_button.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal;")
        
        # 스피드 버튼들 생성
        spd_dec_button = QPushButton("<")
        spd_val_button = QPushButton("0")
        spd_inc_button = QPushButton(">")
        
        # 스피드 버튼 스타일 및 크기 설정 (DSCT FAN과 동일)
        for button in [spd_dec_button, spd_val_button, spd_inc_button]:
            button.setFixedSize(50, 45)
            button.setStyleSheet("background-color: rgb(186,186,186); font-size: 12px; font-weight: bold;")
        
        # 버튼들을 self에 저장
        setattr(self, f"pushButton_pump{pump_num}", pump_button)
        setattr(self, f"spdButton_pump{pump_num}_dec", spd_dec_button)
        setattr(self, f"spdButton_pump{pump_num}_val", spd_val_button)
        setattr(self, f"spdButton_pump{pump_num}_inc", spd_inc_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(pump_label)
        row_layout.addSpacing(8)
        row_layout.addWidget(pump_button)
        row_layout.addSpacing(15)  # ON/OFF와 스피드 버튼 사이 간격
        row_layout.addWidget(spd_dec_button)
        row_layout.addWidget(spd_val_button)
        row_layout.addWidget(spd_inc_button)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)

    def update_status_time(self):
        """상태바 시간 업데이트"""
        current_time = QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate)
        self.statusBar().showMessage(current_time)

    def scan_ports(self):
        """포트 스캔 및 콤보박스 업데이트"""
        self.port_combobox.clear()
        ports = self.serial_manager.get_available_ports()
        for port in ports:
            self.port_combobox.addItem(f"{port['device']} - {port['description']}")

    def scan_ports_periodically(self):
        """주기적으로 포트 목록 갱신"""
        current_ports = {self.port_combobox.itemText(i) for i in range(self.port_combobox.count())}
        detected_ports = set()

        ports = self.serial_manager.get_available_ports()
        for port in ports:
            text = f"{port['device']} - {port['description']}"
            detected_ports.add(text)
            # Port 폰트 크기 조절
            self.port_combobox.setStyleSheet("font-size: 12px;")

        if current_ports != detected_ports:
            self.port_combobox.blockSignals(True)
            self.port_combobox.clear()
            for port in ports:
                self.port_combobox.addItem(f"{port['device']} - {port['description']}")                
            self.port_combobox.blockSignals(False)

    def connect_serial(self):
        """시리얼 연결/해제 토글"""
        if self.serial_manager.is_connected():
            # 현재 연결되어 있으면 해제
            self.disconnect_serial()
        else:
            # 현재 연결되지 않았으면 연결 시도
            self.attempt_connection()
    
    def attempt_connection(self):
        """시리얼 연결 시도"""
        if self.port_combobox.currentText():
            selected_port = self.port_combobox.currentText().split(" - ")[0]
            selected_baudrate = int(self.baudrate_combobox.currentText())
            
            try:
                if self.serial_manager.connect_serial(selected_port, selected_baudrate):
                    self.update_status_indicator("connected")
                    self.update_connect_button("connected")
                    # 시리얼 연결 성공 시 버튼 상태 업데이트
                    self.update_button_states()
                    QMessageBox.information(self, "연결 성공", f"포트 {selected_port}에 연결되었습니다.")
                else:
                    self.update_status_indicator("disconnected")
                    self.update_connect_button("disconnected")
                    # 시리얼 연결 실패 시 버튼 상태 업데이트
                    self.update_button_states()
                    QMessageBox.warning(self, "연결 실패", f"포트 연결에 실패했습니다.")
            except Exception as e:
                import traceback
                traceback.print_exc()  # 터미널에 전체 에러 로그 출력
                self.update_status_indicator("disconnected")
                self.update_connect_button("disconnected")
                # 시리얼 연결 실패 시 버튼 상태 업데이트
                self.update_button_states()
                QMessageBox.critical(self, "오류 발생", f"연결 중 예외 발생:\n{e}")
        else:
            QMessageBox.warning(self, "포트 없음", "연결 가능한 포트가 없습니다.")
    
    def disconnect_serial(self):
        """시리얼 연결 해제"""
        try:
            if self.serial_manager.is_connected():
                self.serial_manager.disconnect_serial()
                self.update_status_indicator("disconnected")
                self.update_connect_button("disconnected")
                # 시리얼 연결 해제 시 버튼 상태 업데이트
                self.update_button_states()
                QMessageBox.information(self, "연결 해제", "시리얼 포트 연결이 해제되었습니다.")
        except Exception as e:
            QMessageBox.critical(self, "오류 발생", f"연결 해제 중 예외 발생:\n{e}")
    
    def update_connect_button(self, status):
        """연결 버튼 텍스트 및 색상 업데이트"""
        if status == "connected":
            self.connectButton.setText("Discon")
            self.connectButton.setStyleSheet("background-color: rgb(43, 179, 43); color: rgb(255,255,255); font-weight: bold;")
        else:
            self.connectButton.setText("연결")
            self.connectButton.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal;")

    def update_status_indicator(self, status):
        """상태 인디케이터 업데이트"""
        if status == "connected":
            self.status_label.setStyleSheet("background-color: rgb(43, 179, 43); color: rgb(0,0,0); font-weight: normal;")
            self.status_label.setText("Connected")
        else:
            self.status_label.setStyleSheet("background-color: rgb(250, 0, 25); color: rgb(0,0,0); font-weight: normal;")
            self.status_label.setText("Disconnected")

    def update_button_states(self):
        """모든 버튼 상태 업데이트"""
        # 시리얼 연결이 끊어진 경우 모든 버튼을 초기 상태로 리셋
        if not self.serial_manager.is_connected():
            self.reset_all_buttons_to_initial_state()
    
    def reset_all_buttons_to_initial_state(self):
        """모든 버튼을 초기 상태로 리셋"""
        # 일반 버튼들 리셋
        if hasattr(self, 'button_manager') and self.button_manager:
            for group_data in self.button_manager.button_groups.values():
                group_data['active'] = None if len(group_data['buttons']) > 1 else False
                
                for button in group_data['buttons'].keys():
                    # 버튼 텍스트와 스타일 초기화
                    if "OPEN" in str(group_data['buttons'][button].get('on', '')).upper():
                        button.setText("CLOSE")
                    else:
                        button.setText("OFF")
                    button.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal;")
        
        # 스피드 버튼들 리셋
        if hasattr(self, 'speed_button_manager') and self.speed_button_manager:
            # Fan SPD 버튼들 리셋
            self.speed_button_manager.current_fan_speed = 0
            if self.speed_button_manager.center_button:
                self.speed_button_manager.center_button.setText("0")
            
            # Con Fan SPD 버튼들 리셋  
            self.speed_button_manager.current_con_fan_speed = 0
            if hasattr(self, 'spdButton_7'):
                self.spdButton_7.setText("0")
                
            # DSCT FAN SPD 버튼들 리셋
            self.speed_button_manager.current_dsct_fan1_speed = 0
            self.speed_button_manager.current_dsct_fan2_speed = 0
            self.speed_button_manager.current_dsct_fan3_speed = 0
            self.speed_button_manager.current_dsct_fan4_speed = 0
            if hasattr(self, 'spdButton_dsct_fan1_val'):
                self.spdButton_dsct_fan1_val.setText("0")
            if hasattr(self, 'spdButton_dsct_fan2_val'):
                self.spdButton_dsct_fan2_val.setText("0")
            if hasattr(self, 'spdButton_dsct_fan3_val'):
                self.spdButton_dsct_fan3_val.setText("0")
            if hasattr(self, 'spdButton_dsct_fan4_val'):
                self.spdButton_dsct_fan4_val.setText("0")
                
            # PUMPER SPD 버튼들 리셋
            self.speed_button_manager.current_pump1_speed = 0
            self.speed_button_manager.current_pump2_speed = 0
            if hasattr(self, 'spdButton_pump1_val'):
                self.spdButton_pump1_val.setText("0")
            if hasattr(self, 'spdButton_pump2_val'):
                self.spdButton_pump2_val.setText("0")

    def read_serial_data(self):
        """시리얼 데이터 읽기"""
        try: 
            if not self.serial_manager.is_connected():
                self.update_status_indicator("disconnected")
                self.update_connect_button("disconnected")
                # 연결이 끊어진 경우 버튼 상태 업데이트
                self.update_button_states()
                return
                
            data = self.serial_manager.read_data()
            if data:
                print(f"수신된 데이터: {data}")
                self.saved_data_to_file(data)
                # 메시지 텍스트 에디터 제거로 인한 로그만 유지
        except IOError as e:
            self.update_status_indicator("disconnected")
            self.update_connect_button("disconnected")
            # 연결이 끊어진 경우 버튼 상태 업데이트
            self.update_button_states()
            print(f"시리얼 데이터 읽기 오류: {e}")
            # 메시지 텍스트 에디터 제거로 인한 로그만 유지

    def saved_data_to_file(self, data):
        """수신된 데이터 파일에 저장"""
        try: 
            file_path = os.path.join(os.path.dirname(__file__), '..', 'serial_data_log.txt')
            with open(file_path, "a") as file:
                file.write(data + "\n")
        except Exception as e:
            print(f"파일 저장 오류: {e}")

    def center(self):
        """창을 화면 중앙에 위치"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        """프로그램 종료 시 정리"""
        if self.serial_manager.is_connected():
            self.serial_manager.disconnect_serial()
            print("종료 시 시리얼 포트 연결 해제")
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()