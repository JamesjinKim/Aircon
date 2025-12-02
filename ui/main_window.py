import os
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QDesktopWidget, QWidget,
                           QAction, QVBoxLayout, QHBoxLayout, QScrollArea, QLabel, QPushButton,
                           QComboBox, QGroupBox, QTextEdit, QFrame, QStatusBar, QTabWidget, QSlider,
                           QGridLayout, QSizePolicy)
from PyQt5.QtCore import QTimer, Qt, QDateTime, QSize
from PyQt5.QtGui import QFont

from managers.serial_manager import SerialManager
from managers.button_manager import ButtonManager
from managers.speed_manager import SpeedButtonManager
from managers.auto_manager import AutoSpeedManager
from managers.sensor_manager import SensorManager
from managers.air_sensor_manager import AirSensorManager
from managers.pt02_sensor_manager import PT02SensorManager
from managers.sensor_scheduler import SensorScheduler
from managers.command_queue_manager import CommandQueueManager, CommandPriority

from ui.constants import BUTTON_ON_STYLE, BUTTON_OFF_STYLE, BUTTON_DEFAULT_STYLE, BUTTON_SPEED_STYLE, BUTTON_PUMP_STYLE, BUTTON_STANDARD_STYLE
from ui.helpers import get_file_path, configure_display_settings
from ui.ui_components import (create_group_box, create_button_row, create_port_selection_section,
                            create_speed_buttons, create_fan_speed_control,
                            create_auto_control_tab, create_speed_buttons_with_text, create_button_row_with_number, create_oa_damper_three_button_row)
from ui.setup_buttons import setup_button_groups, setup_reload_buttons
from ui.sensor_tab import SensorTab
from ui.aircon_sensor_tab import AirconSensorTab

class ControlWindow(QtWidgets.QMainWindow):
    def __init__(self, test_mode=False):
        super().__init__()
        self.test_mode = test_mode
        
        # 창 설정
        self.setWindowTitle('Aircon Remote Control')
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        
        # 디스플레이 설정
        configure_display_settings(self)
            
        # 시리얼 매니저 초기화
        self.serial_manager = SerialManager()
        
        # 명령 큐 매니저 생성 및 연결
        self.command_queue = CommandQueueManager(self.serial_manager)
        self.serial_manager.set_command_queue(self.command_queue)
        
        # 센서 매니저 초기화
        print(f"[MAIN] 센서 매니저 초기화 시작 - test_mode: {self.test_mode}")
        self.sensor_manager = SensorManager(self.serial_manager, test_mode=self.test_mode)
        
        # AIR 센서 매니저 초기화
        self.air_sensor_manager = AirSensorManager(self.serial_manager, test_mode=self.test_mode)
        print(f"[MAIN] 센서 매니저 초기화 완료")

        # PT02 센서 매니저 초기화 (1분 주기 온도/CO2/PM2.5 CSV 저장)
        self.pt02_sensor_manager = PT02SensorManager(test_mode=self.test_mode)
        print(f"[MAIN] PT02 센서 매니저 초기화 완료")

        # 센서 스케줄러 초기화 (중앙 관리)
        self.sensor_scheduler = SensorScheduler(self.serial_manager, test_mode=self.test_mode)
        self.sensor_scheduler.set_sensor_managers(self.air_sensor_manager, self.sensor_manager)

        # AUTO 스피드 매니저 초기화 (UI 요소 생성 전에 초기화)
        self.auto_speed_manager = AutoSpeedManager(
            serial_manager=self.serial_manager,
            SendData_textEdit=None,  # UI 요소가 아직 생성되지 않아 None으로 초기화
            test_mode=self.test_mode
        )

        # PT02 센서 매니저를 AUTO 매니저에 연결
        self.auto_speed_manager.set_pt02_sensor_manager(self.pt02_sensor_manager)
        
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
            ReceiveData_textEdit=self.ReceiveData_textEdit,
            test_mode=self.test_mode
        )

        # RELOAD 기능을 위한 시그널 연결
        self.serial_manager.data_received.connect(self.button_manager.parse_reload_response)

        # 스피드 버튼 매니저 초기화
        self.speed_button_manager = SpeedButtonManager(
            serial_manager=self.serial_manager,
            SendData_textEdit=self.SendData_textEdit
        )
        
        # 스피드 버튼 매니저에 메인 윈도우 참조 설정
        self.speed_button_manager.set_main_window(self)
        
        # 연결 상태 관리 변수
        self.last_connection_check = 0
        self.connection_check_interval = 1.0  # 1초
        self.last_error_log_time = 0
        self.error_log_interval = 1.0  # 1초
        self.was_connected = False
        
        # 연결 에러 카운터
        self.connection_error_count = 0
        self.max_connection_errors = 5  # 5회 연속 에러 시 자동 해제
        
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

        # 시리얼 데이터 수신 완전 비활성화 (행 걸림 문제 해결)
        print("[MAIN] 시리얼 데이터 수신 비활성화 - 명령 전송만 사용")

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
        # [비활성화] 센서 탭들의 상태 표시 초기화 (T/H 탭 비활성화)
        # self.sensors_tab.update_status_indicator("disconnected")
        # self.aircon_sensors_tab.update_status_indicator("disconnected")
        
        # 클리어 버튼 연결 제거 (메시지 기능 제거로 인함)
        
        # 버튼 그룹 설정 - 마지막에 실행 (SPD 버튼 제외)
        setup_button_groups(self)

        # RELOAD 버튼 이벤트 연결
        setup_reload_buttons(self)

        # 새로운 DESICCANT FAN 순환 스피드 버튼 연결
        if hasattr(self, 'speedButton_dsct_fan1'):
            self.speed_button_manager.create_cyclic_dsct_fan_button(1, self.speedButton_dsct_fan1)
            self.speed_button_manager.create_cyclic_dsct_fan_button(2, self.speedButton_dsct_fan2)
            self.speed_button_manager.create_cyclic_dsct_fan_button(3, self.speedButton_dsct_fan3)
            self.speed_button_manager.create_cyclic_dsct_fan_button(4, self.speedButton_dsct_fan4)
        
        # 새로운 DAMPER 버튼들 연결
        if hasattr(self, 'positionButton_dmp1'):
            # DAMPER 순환 위치 버튼들
            self.speed_button_manager.create_cyclic_damper_button(1, self.positionButton_dmp1, self.toggleButton_dmp1)
            self.speed_button_manager.create_cyclic_damper_button(2, self.positionButton_dmp2, self.toggleButton_dmp2)
            self.speed_button_manager.create_cyclic_damper_button(3, self.positionButton_dmp3, self.toggleButton_dmp3)
            self.speed_button_manager.create_cyclic_damper_button(4, self.positionButton_dmp4, self.toggleButton_dmp4)
            
            # DAMPER 토글 버튼들
            self.speed_button_manager.create_damper_toggle_button(1, self.toggleButton_dmp1, self.positionButton_dmp1)
            self.speed_button_manager.create_damper_toggle_button(2, self.toggleButton_dmp2, self.positionButton_dmp2)
            self.speed_button_manager.create_damper_toggle_button(3, self.toggleButton_dmp3, self.positionButton_dmp3)
            self.speed_button_manager.create_damper_toggle_button(4, self.toggleButton_dmp4, self.positionButton_dmp4)
        
        # 새로운 PUMP 스피드 버튼 생성 및 연결 (새로운 터치 친화적 디자인)
        if hasattr(self, 'speedButton_pump1'):
            self.speed_button_manager.create_new_pump_buttons(1, self.speedButton_pump1)
            self.speed_button_manager.create_new_pump_buttons(2, self.speedButton_pump2)
        # 기존 PUMP 스피드 버튼 (호환성을 위해 유지)
        elif hasattr(self, 'spdButton_pump1_dec'):
            self.speed_button_manager.create_pumper_speed_buttons(
                self, 1, self.spdButton_pump1_dec, self.spdButton_pump1_val, self.spdButton_pump1_inc
            )
            self.speed_button_manager.create_pumper_speed_buttons(
                self, 2, self.spdButton_pump2_dec, self.spdButton_pump2_val, self.spdButton_pump2_inc
            )
        
        # EVA FAN 순환 버튼들 연결 (새로운 AIRCON 탭) - 새로운 네이밍 우선 사용
        if hasattr(self, 'aircon_eva_fan_button'):
            self.speed_button_manager.create_eva_fan_cycle_button("EVA FAN", self.aircon_eva_fan_button)
        elif hasattr(self, 'evaFanButton_1'):
            self.speed_button_manager.create_eva_fan_cycle_button("EVA FAN", self.evaFanButton_1)
            
        if hasattr(self, 'aircon_condensor_fan_button'):
            self.speed_button_manager.create_eva_fan_cycle_button("CONDENSOR FAN", self.aircon_condensor_fan_button)
        elif hasattr(self, 'conFanButton_5'):
            self.speed_button_manager.create_eva_fan_cycle_button("CONDENSOR FAN", self.conFanButton_5)
        
        # 모든 스피드 버튼의 크기를 균일하게 맞추기 위한 추가 코드
        QTimer.singleShot(100, self.ensure_uniform_button_sizes)

        self.auto_speed_manager.set_speed_button_manager(self.speed_button_manager)
        self.speed_button_manager.set_auto_manager(self.auto_speed_manager)
        
        # ButtonManager와 SpeedButtonManager 연결
        self.button_manager.set_speed_button_manager(self.speed_button_manager)
        
        # OA DAMPER 3버튼 컨트롤 연결 (새로운 요구사항)
        if hasattr(self, 'aircon_oa_damper_left_open_button'):
            self.speed_button_manager.create_new_oa_damper_controls(
                "L", 
                self.aircon_oa_damper_left_open_button,
                self.aircon_oa_damper_left_number_button, 
                self.aircon_oa_damper_left_close_button
            )
        if hasattr(self, 'aircon_oa_damper_right_open_button'):
            self.speed_button_manager.create_new_oa_damper_controls(
                "R", 
                self.aircon_oa_damper_right_open_button,
                self.aircon_oa_damper_right_number_button, 
                self.aircon_oa_damper_right_close_button
            )

        # [비활성화] 테스트 모드에서는 자동으로 스케줄러 시작 (T/H 탭 비활성화로 중지)
        # if self.test_mode:
        #     print("[MAIN] 테스트 모드: 자동으로 센서 스케줄러 시작")
        #     self.sensor_scheduler.start_scheduling()
        #     # 센서 탭들의 상태 표시를 녹색으로 설정
        #     self.sensors_tab.update_status_indicator("active")
        #     self.aircon_sensors_tab.update_status_indicator("active")

        
    def connect_auto_controls(self):
        """AUTO 탭의 컨트롤을 연결하는 메서드"""
        if hasattr(self, 'auto_control_widget') and self.auto_speed_manager:
            # 새로운 AUTO 탭 위젯 연결
            self.auto_speed_manager.connect_auto_controls(self.auto_control_widget)
    
    def ensure_uniform_button_sizes(self):
        """모든 버튼 크기를 동일하게 설정"""
        # 기존 스피드 버튼 배열 제거됨 (이전 오래된 리퍼런스)
        
        # 새로운 DSCT FAN 스피드 버튼들 (순환 버튼)
        new_dsct_speed_buttons = []
        if hasattr(self, 'speedButton_dsct_fan1'):
            new_dsct_speed_buttons.extend([
                self.speedButton_dsct_fan1, self.speedButton_dsct_fan2,
                self.speedButton_dsct_fan3, self.speedButton_dsct_fan4
            ])
        
        # 새로운 DAMPER 버튼들 (토글 + 위치 버튼)
        new_damper_toggle_buttons = []
        new_damper_position_buttons = []
        if hasattr(self, 'toggleButton_dmp1'):
            new_damper_toggle_buttons.extend([
                self.toggleButton_dmp1, self.toggleButton_dmp2,
                self.toggleButton_dmp3, self.toggleButton_dmp4
            ])
            new_damper_position_buttons.extend([
                self.positionButton_dmp1, self.positionButton_dmp2,
                self.positionButton_dmp3, self.positionButton_dmp4
            ])
        
        # PUMP 스피드 버튼들
        pump_speed_buttons = []
        if hasattr(self, 'spdButton_pump1_dec'):
            pump_speed_buttons.extend([
                self.spdButton_pump1_dec, self.spdButton_pump1_val, self.spdButton_pump1_inc,
                self.spdButton_pump2_dec, self.spdButton_pump2_val, self.spdButton_pump2_inc
            ])
        
        # PUMP 스피드 버튼들에 동일한 크기 설정
        for button in pump_speed_buttons:
            button.setFixedSize(50, 45)
            
        # 새로운 DSCT FAN 순환 스피드 버튼들 - 터치 친화적 크기 (이미 설정됨)
        # 새로운 DAMPER 토글 및 위치 버튼들 - 터치 친화적 크기 (이미 설정됨)
        
        # 기존 Fan, Con Fan 버튼들 - 스피드 버튼과 동일한 너비 (EVA FAN CONTROLS에서는 다른 크기)
        main_fan_buttons = []
        if hasattr(self, 'pushButton_1') and hasattr(self, 'spdButton_2'):  # 기존 AIRCON 방식인 경우만
            main_fan_buttons = [self.pushButton_1, self.pushButton_5]  # Fan, Con Fan
            for button in main_fan_buttons:
                button.setFixedSize(166, 45)
        
        # 나머지 일반 버튼들 - 기본 크기
        other_buttons = []
        
        # DMP 버튼들 (항상 존재)
        if hasattr(self, 'pushButton_9'):
            other_buttons.extend([
                self.pushButton_9, self.pushButton_10, self.pushButton_11, self.pushButton_12
            ])
        
        # COMPRESSOR, CLUCH 버튼들 (EVA FAN CONTROLS에 포함) - 새로운 네이밍 우선 사용
        if hasattr(self, 'aircon_compresure_button'):
            other_buttons.extend([
                self.aircon_compresure_button, self.aircon_comp_cluch_button
            ])
        elif hasattr(self, 'pushButton_13'):
            other_buttons.extend([
                self.pushButton_13, self.pushButton_14
            ])
        
        # DSCT FAN 버튼들 추가 (존재하는 경우)
        if hasattr(self, 'pushButton_dsct_fan1'):
            other_buttons.extend([
                self.pushButton_dsct_fan1, self.pushButton_dsct_fan2, 
                self.pushButton_dsct_fan3, self.pushButton_dsct_fan4
            ])
        
        # PUMP & SOL 버튼들 추가 (존재하는 경우)
        if hasattr(self, 'pushButton_pump1'):
            other_buttons.extend([
                self.pushButton_pump1, self.pushButton_pump2
            ])
        if hasattr(self, 'pushButton_sol1'):
            other_buttons.append(self.pushButton_sol1)
        
        # 나머지 버튼들에 기본 크기 설정
        for button in other_buttons:
            button.setFixedSize(140, 45)
            
        # OA.DAMP 버튼들은 별도로 65px 크기로 재설정 (3버튼 구조)
        if hasattr(self, 'aircon_oa_damper_left_open_button'):
            self.aircon_oa_damper_left_open_button.setFixedSize(65, 45)
            self.aircon_oa_damper_left_close_button.setFixedSize(65, 45)
        if hasattr(self, 'aircon_oa_damper_right_open_button'):
            self.aircon_oa_damper_right_open_button.setFixedSize(65, 45)
            self.aircon_oa_damper_right_close_button.setFixedSize(65, 45)
            
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
                background: #969696;
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
        
        # 첫 번째 탭 - AUTO 모드
        self.auto_tab = QWidget()
        self.setup_auto_tab()
        self.tab_widget.addTab(self.auto_tab, "AUTO")

        # 두 번째 탭 - SEMI AUTO
        self.semi_auto_tab = QWidget()
        self.setup_semi_auto_tab()
        self.tab_widget.addTab(self.semi_auto_tab, "SEMI AUTO")

        # 세 번째 탭 - AIRCON
        self.aircon_tab = QWidget()
        self.setup_aircon_tab()
        self.tab_widget.addTab(self.aircon_tab, "AIRCON")

        # 네 번째 탭 - PUMP & SOL
        self.pumper_sol_tab = QWidget()
        self.setup_pumper_sol_tab()
        self.tab_widget.addTab(self.pumper_sol_tab, "PUMP && SOL")

        # 다섯 번째 탭 - DESICCANT (DAMPER 포함)
        self.desiccant_tab = QWidget()
        self.setup_desiccant_tab()
        self.tab_widget.addTab(self.desiccant_tab, "DESICCANT")

        # [비활성화] 여섯 번째 탭 - DSCT T/H (당분간 사용 안함)
        # self.sensors_tab = SensorTab(self.sensor_manager, self.sensor_scheduler)
        # self.tab_widget.addTab(self.sensors_tab, "DSCT T/H")
        self.sensors_tab = None  # 호환성 유지

        # [비활성화] 일곱 번째 탭 - AIRCON T/H (당분간 사용 안함)
        # self.aircon_sensors_tab = AirconSensorTab(self.air_sensor_manager, self.sensor_scheduler)
        # self.tab_widget.addTab(self.aircon_sensors_tab, "AIRCON T/H")
        self.aircon_sensors_tab = None  # 호환성 유지
        
        
        # 메인 레이아웃에 모든 영역 추가
        self.main_layout.addLayout(top_layout)
        self.main_layout.addWidget(self.tab_widget, 1)  # 탭이 나머지 공간을 모두 차지하도록 설정
        
        # 상태바 추가
        self.statusBar()
    
    def setup_aircon_tab(self):
        """AIRCON 탭 설정 - 좌우 2컬럼 레이아웃 (EVA FAN CONTROLS | DMP CONTROLS)"""
        # AIRCON 탭 메인 레이아웃 - 그리드 레이아웃
        main_grid = QGridLayout(self.aircon_tab)
        main_grid.setContentsMargins(10, 10, 10, 10)
        main_grid.setSpacing(15)  # 그룹 간 간격
        
        # 왼쪽 그룹: EVA FAN CONTROLS
        left_group, left_layout = create_group_box("AIRCON CONTROLS", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # EVA FAN - 순환 버튼 (OFF,1,2,3,4,5,6,7,8)
        self.create_eva_fan_row(left_layout, "EVA FAN", 1)
        
        # COMPRESSOR - 토글 버튼 (기존 INVERTER)
        compresure_button = create_button_row("COMPRESSOR", QPushButton("OFF"), left_layout, button_width=140)
        self.aircon_compresure_button = compresure_button  # 새로운 네이밍
        self.pushButton_13 = compresure_button  # 기존 호환성 유지
        
        
        # COMP CLUCH - 토글 버튼
        comp_cluch_button = create_button_row("COMP CLUCH", QPushButton("OFF"), left_layout, button_width=140)
        self.aircon_comp_cluch_button = comp_cluch_button  # 새로운 네이밍
        self.pushButton_14 = comp_cluch_button  # 기존 호환성 유지
        
        # CONDENSOR FAN - 순환 버튼 (OFF,1,2,3,4,5,6,7,8)  
        self.create_eva_fan_row(left_layout, "CONDENSOR FAN", 5)
        
        
        # 왼쪽 그룹 여백
        left_layout.addStretch(1)
        
        # 오른쪽 그룹: DAMP CONTROLS
        right_group, right_layout = create_group_box("DAMP CONTROLS", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # OA.DAMPER(L) - Outside Air Damper Left - 3버튼 구조 (OPEN + 숫자 + CLOSE)
        oa_l_open, oa_l_number, oa_l_close = create_oa_damper_three_button_row("OA.DAMP(L)", right_layout)
        self.aircon_oa_damper_left_open_button = oa_l_open  # OPEN 버튼
        self.aircon_oa_damper_left_number_button = oa_l_number  # 숫자 버튼
        self.aircon_oa_damper_left_close_button = oa_l_close  # CLOSE 버튼
        # 기존 호환성 유지
        self.aircon_oa_damper_left_button = oa_l_close  # 기존 참조는 CLOSE 버튼으로
        self.aircon_oa_damper_left_number = oa_l_number  # 숫자 버튼 호환성
        self.pushButton_9 = oa_l_close  # 기존 호환성 유지
        
        # OA.DAMPER(R) - Outside Air Damper Right - 3버튼 구조 (OPEN + 숫자 + CLOSE)
        oa_r_open, oa_r_number, oa_r_close = create_oa_damper_three_button_row("OA.DAMP(R)", right_layout)
        self.aircon_oa_damper_right_open_button = oa_r_open  # OPEN 버튼
        self.aircon_oa_damper_right_number_button = oa_r_number  # 숫자 버튼
        self.aircon_oa_damper_right_close_button = oa_r_close  # CLOSE 버튼
        # 기존 호환성 유지
        self.aircon_oa_damper_right_button = oa_r_close  # 기존 참조는 CLOSE 버튼으로
        self.aircon_oa_damper_right_number = oa_r_number  # 숫자 버튼 호환성
        self.pushButton_11 = oa_r_close  # 기존 호환성 유지
        
        # RA.DAMPER(L) - Return Air Damper Left - 내기 댐퍼
        ra_damper_left_button = create_button_row("RA.DAMP(L)", QPushButton("CLOSE"), right_layout)
        self.aircon_ra_damper_left_button = ra_damper_left_button  # 새로운 네이밍
        self.pushButton_10 = ra_damper_left_button  # 기존 호환성 유지
        
        # RA.DAMPER(R) - Return Air Damper Right
        ra_damper_right_button = create_button_row("RA.DAMP(R)", QPushButton("CLOSE"), right_layout)
        self.aircon_ra_damper_right_button = ra_damper_right_button  # 새로운 네이밍
        self.pushButton_12 = ra_damper_right_button  # 기존 호환성 유지

        # 오른쪽 그룹 여백
        right_layout.addStretch(1)

        # AIR RELOAD 버튼 추가 (장비 상태 동기화)
        air_reload_button = create_button_row("🔄 RELOAD", QPushButton("AIR Refresh"), right_layout, button_width=140)
        air_reload_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 2px solid #45a049;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.aircon_reload_button = air_reload_button
        
        # 2컬럼 그리드에 위젯 배치 (왼쪽:오른쪽 = 1:1)
        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)
        
        # 컬럼 너비 비율 설정 (1:1 균등 분배)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)
    
    def create_eva_fan_row(self, parent_layout, label_text, button_id):
        """EVA FAN 행 생성 - 순환 버튼 (OFF,1,2,3,4,5,6,7,8)"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 8, 5, 8)  # create_button_row와 동일한 마진
        
        # 라벨
        label = QLabel(label_text)
        label.setFixedWidth(140)  # 통일된 라벨 너비
        label.setStyleSheet("font-size: 15px; font-weight: bold;")  # create_button_row와 동일한 스타일
        
        # 순환 버튼 - COMPRESSOR 버튼과 동일한 스타일
        cycle_button = QPushButton("OFF")
        cycle_button.setFixedSize(140, 45)  # 통일된 버튼 크기
        cycle_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        cycle_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # create_button_row와 동일
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        if label_text == "EVA FAN":
            # 새로운 네이밍
            self.aircon_eva_fan_button = cycle_button
            # 기존 호환성 유지
            setattr(self, f"pushButton_{button_id}", cycle_button)  # pushButton_1
            setattr(self, f"evaFanButton_{button_id}", cycle_button)
        elif label_text == "CONDENSOR FAN":
            # 새로운 네이밍  
            self.aircon_condensor_fan_button = cycle_button
            # 기존 호환성 유지
            setattr(self, f"pushButton_{button_id}", cycle_button)  # pushButton_5
            setattr(self, f"conFanButton_{button_id}", cycle_button)
        
        # 행에 위젯들 추가 - create_button_row와 동일한 방식
        row_layout.addWidget(label)
        row_layout.addSpacing(20)  # 고정된 적당한 간격 (create_button_row와 동일)
        row_layout.addWidget(cycle_button)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)
    
    def setup_desiccant_tab(self):
        """DESICCANT 탭 설정 - 좌우 2분할 레이아웃 (DESICCANT + DAMP)"""
        # DESICCANT 탭 메인 레이아웃
        main_grid = QGridLayout(self.desiccant_tab)
        main_grid.setContentsMargins(10, 10, 10, 10)
        main_grid.setSpacing(15)
        
        # 왼쪽 그룹: FAN Control
        left_group, left_layout = create_group_box("FAN Control", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # FAN1~4 제어 - 새로운 단순화된 디자인 (라벨 변경된 순서)
        self.create_new_dsct_fan_row(left_layout, 1)  # 배기L (FAN1 CMD)
        self.create_new_dsct_fan_row(left_layout, 3)  # 배기R (FAN3 CMD)
        self.create_new_dsct_fan_row(left_layout, 2)  # 급기L (FAN2 CMD)
        self.create_new_dsct_fan_row(left_layout, 4)  # 급기R (FAN4 CMD)
        
        # 왼쪽 그룹 여백
        left_layout.addStretch(1)
        
        # 오른쪽 그룹: DAMPER CONTROLS
        right_group, right_layout = create_group_box("DAMP CONTROLS", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # DMP1~4 제어 - 새로운 토글 + 숫자 버튼 디자인 (라벨 변경된 순서)
        self.create_new_damper_row(right_layout, 2)  # L DMP H (DMP2 CMD)
        self.create_new_damper_row(right_layout, 1)  # L DMP L (DMP1 CMD)
        self.create_new_damper_row(right_layout, 4)  # R DMP H (DMP4 CMD)
        self.create_new_damper_row(right_layout, 3)  # R DMP L (DMP3 CMD)

        # 오른쪽 그룹 여백
        right_layout.addStretch(1)

        # DSCT RELOAD 버튼 추가 (장비 상태 동기화)
        dsct_reload_button = create_button_row("🔄 RELOAD", QPushButton("DSCT Refresh"), right_layout, button_width=140)
        dsct_reload_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 2px solid #1976D2;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.desiccant_reload_button = dsct_reload_button
        
        # 2컬럼 그리드에 위젯 배치 (왼쪽:오른쪽 = 1:1)
        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)
        
        # 컬럼 너비 비율 설정 (1:1)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)
    
    def create_dsct_fan_row(self, parent_layout, fan_num):
        """DESICCANT FAN 행 생성 - 가로 배치"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 8, 5, 8)
        row_layout.setSpacing(10)  # 버튼 간 간격

        # FAN 라벨 - 번호별 한글 라벨 매핑
        fan_labels = {1: "배기FAN1", 2: "급기FAN2", 3: "배기FAN3", 4: "급기FAN4"}
        fan_label_text = fan_labels.get(fan_num, f"FAN{fan_num}")
        fan_label = QLabel(fan_label_text)
        fan_label.setFixedWidth(80)
        fan_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        fan_label.setAlignment(Qt.AlignCenter)
        
        # ON/OFF 토글 버튼
        toggle_button = QPushButton("OFF")
        toggle_button.setFixedSize(80, 45)
        toggle_button.setStyleSheet(BUTTON_DEFAULT_STYLE)
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"desiccant_fan{fan_num}_toggle_button", toggle_button)  # 새로운 네이밍
        setattr(self, f"pushButton_dsct_fan{fan_num}", toggle_button)  # 기존 호환성 유지
        
        # SPD 버튼들 생성
        dec_button = QPushButton("<")
        val_button = QPushButton("0")
        inc_button = QPushButton(">")
        
        # SPD 버튼 스타일 및 크기 설정
        for button in [dec_button, val_button, inc_button]:
            button.setFixedSize(50, 45)
            button.setStyleSheet(BUTTON_SPEED_STYLE)
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"desiccant_fan{fan_num}_speed_dec_button", dec_button)  # 새로운 네이밍
        setattr(self, f"desiccant_fan{fan_num}_speed_val_button", val_button)  # 새로운 네이밍  
        setattr(self, f"desiccant_fan{fan_num}_speed_inc_button", inc_button)  # 새로운 네이밍
        # 기존 호환성 유지
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
    
    def create_new_dsct_fan_row(self, parent_layout, fan_num):
        """새로운 DESICCANT FAN 행 생성 - 터치 친화적 디자인 (FAN + 순환 숫자 버튼)"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 10, 5, 10)
        row_layout.setSpacing(15)  # 버튼 간 충분한 간격
        
        # FAN 라벨 - 새로운 명명 규칙
        fan_labels = {1: "배기L", 2: "급기L", 3: "배기R", 4: "급기R"}
        fan_label_text = fan_labels.get(fan_num, f"FAN{fan_num}")
        fan_label = QLabel(fan_label_text)
        fan_label.setFixedWidth(80)
        fan_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        fan_label.setAlignment(Qt.AlignCenter)
        
        # ON/OFF 토글 버튼 - COMPRESSOR 버튼과 동일한 스타일
        toggle_button = QPushButton("OFF")
        toggle_button.setFixedSize(120, 50)  # 터치하기 편한 크기
        toggle_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 순환 숫자 버튼 - COMPRESSOR 버튼과 동일한 스타일
        speed_button = QPushButton("0")
        speed_button.setFixedSize(80, 50)  # 터치하기 편한 크기
        speed_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"desiccant_fan{fan_num}_new_toggle_button", toggle_button)  # 새로운 네이밍
        setattr(self, f"desiccant_fan{fan_num}_new_speed_button", speed_button)  # 새로운 네이밍
        # 기존 호환성 유지
        setattr(self, f"pushButton_dsct_fan{fan_num}", toggle_button)  
        setattr(self, f"speedButton_dsct_fan{fan_num}", speed_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(fan_label)
        row_layout.addWidget(toggle_button)
        row_layout.addWidget(speed_button)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)
    
    def create_new_damper_row(self, parent_layout, dmp_num):
        """새로운 DAMPER 행 생성 - 터치 친화적 디자인 (토글 + 순환 숫자 버튼)"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 10, 5, 10)
        row_layout.setSpacing(15)  # 버튼 간 충분한 간격
        
        # DMP 라벨 - 새로운 명명 규칙
        dmp_labels = {1: "L DMP L", 2: "L DMP H", 3: "R DMP L", 4: "R DMP H"}
        dmp_label = QLabel(dmp_labels[dmp_num])
        dmp_label.setFixedWidth(80)
        dmp_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        dmp_label.setAlignment(Qt.AlignCenter)
        
        # CLOSE/OPEN 토글 버튼 - COMPRESSOR 버튼과 동일한 스타일
        toggle_button = QPushButton("CLOSE")
        toggle_button.setFixedSize(120, 50)  # 터치하기 편한 크기
        toggle_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 순환 숫자 버튼 - COMPRESSOR 버튼과 동일한 스타일
        position_button = QPushButton("0")
        position_button.setFixedSize(80, 50)  # 터치하기 편한 크기
        position_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"desiccant_damper{dmp_num}_toggle_button", toggle_button)  # 새로운 네이밍
        setattr(self, f"desiccant_damper{dmp_num}_position_button", position_button)  # 새로운 네이밍
        # 기존 호환성 유지
        setattr(self, f"toggleButton_dmp{dmp_num}", toggle_button)
        setattr(self, f"positionButton_dmp{dmp_num}", position_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(dmp_label)
        row_layout.addWidget(toggle_button)
        row_layout.addWidget(position_button)
        row_layout.addStretch()  # 오른쪽 여백
        
        # 부모 레이아웃에 행 추가
        parent_layout.addLayout(row_layout)
    
    def setup_semi_auto_tab(self):
        """SEMI AUTO 탭 설정 - 좌우 2컬럼 레이아웃"""
        # SEMI AUTO 탭 메인 레이아웃 - 그리드로 설정
        main_grid = QGridLayout(self.semi_auto_tab)
        main_grid.setContentsMargins(5, 5, 5, 5)
        main_grid.setSpacing(15)  # 그룹 간 간격
        
        # 좌측 그룹: DESICCANT SEMI AUTO
        left_group, left_layout = self.create_group_box("DESICCANT SEMI AUTO", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # DESICCANT RUN [RUN/STOP] 버튼
        run_row_layout = QHBoxLayout()
        run_row_layout.setContentsMargins(5, 10, 5, 10)
        run_label = QLabel("DESICCANT RUN")
        run_label.setFixedWidth(120)
        run_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        run_button = QPushButton("RUN")
        run_button.setFixedSize(120, 50)
        run_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        run_row_layout.addWidget(run_label)
        run_row_layout.addSpacing(10)
        run_row_layout.addWidget(run_button)
        run_row_layout.addStretch()
        left_layout.addLayout(run_row_layout)
        
        # 주기(Sec) [-] [200] [+] 버튼들
        period_row_layout = QHBoxLayout()
        period_row_layout.setContentsMargins(5, 10, 5, 10)
        period_label = QLabel("주기(Sec)")
        period_label.setFixedWidth(120)
        period_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        
        minus_button = QPushButton("-")
        minus_button.setFixedSize(50, 50)
        minus_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        value_button = QPushButton("200")
        value_button.setFixedSize(80, 50)
        value_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        plus_button = QPushButton("+")
        plus_button.setFixedSize(50, 50)
        plus_button.setStyleSheet("font-size: 20px; font-weight: bold;")
        
        period_row_layout.addWidget(period_label)
        period_row_layout.addSpacing(10)
        period_row_layout.addWidget(minus_button)
        period_row_layout.addSpacing(5)
        period_row_layout.addWidget(value_button)
        period_row_layout.addSpacing(5)
        period_row_layout.addWidget(plus_button)
        period_row_layout.addStretch()
        left_layout.addLayout(period_row_layout)
        
        # 좌측 그룹 여백
        left_layout.addStretch(1)
        
        # 우측 그룹: DAMP TEST
        right_group, right_layout = self.create_group_box("DAMP TEST", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # DAMP [RUN/STOP] 버튼
        damp_row_layout = QHBoxLayout()
        damp_row_layout.setContentsMargins(5, 10, 5, 10)
        damp_label = QLabel("DAMP")
        damp_label.setFixedWidth(80)
        damp_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        damp_button = QPushButton("RUN")
        damp_button.setFixedSize(120, 50)
        damp_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        damp_row_layout.addWidget(damp_label)
        damp_row_layout.addSpacing(10)
        damp_row_layout.addWidget(damp_button)
        damp_row_layout.addStretch()
        right_layout.addLayout(damp_row_layout)
        
        # 우측 그룹 여백
        right_layout.addStretch(1)
        
        # 2컬럼 그리드에 위젯 배치 (왼쪽:오른쪽 = 1:1)
        main_grid.addWidget(left_group, 0, 0)
        main_grid.addWidget(right_group, 0, 1)
        
        # 컬럼 너비 비율 설정 (1:1)
        main_grid.setColumnStretch(0, 1)
        main_grid.setColumnStretch(1, 1)
        
        # 버튼들을 인스턴스 변수로 저장
        self.semi_auto_run_button = run_button
        self.semi_auto_period_minus_button = minus_button
        self.semi_auto_period_value_button = value_button
        self.semi_auto_period_plus_button = plus_button
        self.damp_test_button = damp_button
        
        # 버튼 이벤트 연결
        self.setup_semi_auto_button_events()
    
    def create_group_box(self, title, margins=(10, 10, 10, 10)):
        """그룹 박스 생성 헬퍼 메서드"""
        group = QGroupBox(title)
        group.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(*margins)
        layout.setSpacing(10)
        return group, layout
    
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


    def setup_pumper_sol_tab(self):
        """PUMP & SOL 탭 설정 - 2컬럼 레이아웃"""
        # PUMP & SOL 탭 메인 레이아웃
        main_grid = QGridLayout(self.pumper_sol_tab)
        main_grid.setContentsMargins(10, 10, 10, 10)
        main_grid.setSpacing(15)
        
        # 왼쪽 그룹: PUMP CONTROLS
        left_group, left_layout = create_group_box("PUMP CONTROLS", margins=(15, 30, 15, 15))
        left_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # PUMP1 제어 - DESICCANT FAN과 동일한 새로운 패턴
        self.create_new_pump_row(left_layout, 1)
        
        # PUMP2 제어 - DESICCANT FAN과 동일한 새로운 패턴
        self.create_new_pump_row(left_layout, 2)
        
        # 왼쪽 그룹 여백
        left_layout.addStretch(1)
        
        # 오른쪽 그룹: SOL CONTROLS
        right_group, right_layout = create_group_box("SOL CONTROLS", margins=(15, 30, 15, 15))
        right_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # SOL ALL 제어 (SOL1 명령으로 1~4 전체 제어)
        sol1_row_layout = QHBoxLayout()
        sol1_row_layout.setContentsMargins(5, 8, 5, 8)
        sol1_label = QLabel("SOL 1~4")
        sol1_label.setFixedWidth(70)  # 레이블 너비 조정
        sol1_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        sol1_button = QPushButton("OFF")
        sol1_button.setFixedSize(140, 45)
        sol1_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        sol1_row_layout.addWidget(sol1_label)
        sol1_row_layout.addSpacing(5)  # 작은 간격
        sol1_row_layout.addWidget(sol1_button)
        sol1_row_layout.addStretch()
        right_layout.addLayout(sol1_row_layout)
        self.sol_sol1_button = sol1_button  # 새로운 네이밍
        self.pushButton_sol1 = sol1_button  # 기존 호환성 유지
        
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
        
        # PUMP ON/OFF 토글 버튼 - COMPRESSOR 버튼과 동일한 스타일
        pump_button = QPushButton("OFF")
        pump_button.setFixedSize(140, 45)
        pump_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 스피드 버튼들 생성
        spd_dec_button = QPushButton("<")
        spd_val_button = QPushButton("0")
        spd_inc_button = QPushButton(">")
        
        # 스피드 버튼 스타일 및 크기 설정 (DSCT FAN과 동일)
        for button in [spd_dec_button, spd_val_button, spd_inc_button]:
            button.setFixedSize(50, 45)
            button.setStyleSheet("background-color: rgb(186,186,186); font-size: 12px;")
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"pumper_pump{pump_num}_toggle_button", pump_button)  # 새로운 네이밍
        setattr(self, f"pumper_pump{pump_num}_speed_dec_button", spd_dec_button)  # 새로운 네이밍
        setattr(self, f"pumper_pump{pump_num}_speed_val_button", spd_val_button)  # 새로운 네이밍
        setattr(self, f"pumper_pump{pump_num}_speed_inc_button", spd_inc_button)  # 새로운 네이밍
        # 기존 호환성 유지
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
    
    def create_new_pump_row(self, parent_layout, pump_num):
        """새로운 PUMP 행 생성 - DESICCANT FAN과 동일한 터치 친화적 디자인"""
        # 행 레이아웃 생성
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(5, 10, 5, 10)
        row_layout.setSpacing(15)  # 버튼 간 충분한 간격
        
        # PUMP 라벨
        pump_label = QLabel(f"PUMP{pump_num}")
        pump_label.setFixedWidth(80)
        pump_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        pump_label.setAlignment(Qt.AlignCenter)
        
        # ON/OFF 토글 버튼 - COMPRESSOR 버튼과 동일한 스타일
        toggle_button = QPushButton("OFF")
        toggle_button.setFixedSize(120, 50)  # 터치하기 편한 크기
        toggle_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 순환 숫자 버튼 - COMPRESSOR 버튼과 동일한 스타일
        speed_button = QPushButton("0")
        speed_button.setFixedSize(80, 50)  # 터치하기 편한 크기
        speed_button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 새로운 직관적 네이밍과 기존 호환성 유지
        setattr(self, f"pumper_pump{pump_num}_new_toggle_button", toggle_button)  # 새로운 네이밍
        setattr(self, f"pumper_pump{pump_num}_new_speed_button", speed_button)  # 새로운 네이밍
        # 기존 호환성 유지
        setattr(self, f"pushButton_pump{pump_num}", toggle_button)
        setattr(self, f"speedButton_pump{pump_num}", speed_button)
        
        # 행에 위젯들 추가
        row_layout.addWidget(pump_label)
        row_layout.addWidget(toggle_button)
        row_layout.addWidget(speed_button)
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
                    # 연결 성공 시 상태 초기화
                    self.was_connected = True
                    self.connection_error_count = 0  # 에러 카운터 리셋
                    
                    # [비활성화] 센서 매니저 콜백 설정 (T/H 탭 비활성화로 중지)
                    # self.serial_manager.set_sensor_data_callback(self.sensor_manager.parse_sensor_data)
                    # self.serial_manager.set_air_sensor_data_callback(self.air_sensor_manager.parse_sensor_data)

                    # [비활성화] 센서 스케줄러 시작 (T/H 탭 비활성화로 중지)
                    # self.sensor_scheduler.set_serial_manager(self.serial_manager)
                    # self.sensor_scheduler.start_scheduling()

                    # UI 상태 업데이트
                    # [비활성화] T/H 탭 관련 상태 업데이트 중지
                    # self.sensors_tab.set_auto_refresh_status(True)
                    # self.aircon_sensors_tab.set_auto_refresh_status(True)
                    self.last_connection_check = time.time()
                    self.last_error_log_time = 0
                    self.update_status_indicator("connected")
                    self.update_connect_button("connected")
                    # 시리얼 연결 성공 시 버튼 상태 업데이트
                    self.update_button_states()
                    # [비활성화] 센서 탭들의 상태 표시 업데이트 중지
                    # self.sensors_tab.update_status_indicator("active")
                    # self.aircon_sensors_tab.update_status_indicator("active")
                    QMessageBox.information(self, "연결 성공", f"포트 {selected_port}에 연결되었습니다.")
                else:
                    self.update_status_indicator("disconnected")
                    self.update_connect_button("disconnected")
                    # 시리얼 연결 실패 시 버튼 상태 업데이트
                    self.update_button_states()
                    # [비활성화] 센서 탭들의 상태 표시 업데이트 중지
                    # self.sensors_tab.update_status_indicator("disconnected")
                    # self.aircon_sensors_tab.update_status_indicator("disconnected")
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
                # [비활성화] 센서 스케줄러 중지 (T/H 탭 비활성화로 이미 중지됨)
                # self.sensor_scheduler.stop_scheduling()

                # [비활성화] UI 상태 초기화 (T/H 탭 비활성화)
                # self.sensors_tab.set_auto_refresh_status(False)
                # self.sensors_tab.reset_all_sensors()
                # self.aircon_sensors_tab.set_auto_refresh_status(False)
                # self.aircon_sensors_tab.reset_all_sensors()

                self.serial_manager.disconnect_serial()
                # 연결 상태 초기화
                self.was_connected = False
                self.connection_error_count = 0
                self.last_connection_check = 0
                self.last_error_log_time = 0
                self.update_status_indicator("disconnected")
                self.update_connect_button("disconnected")
                # 시리얼 연결 해제 시 버튼 상태 업데이트
                self.update_button_states()
                # 센서 탭들의 상태 표시 업데이트
                self.sensors_tab.update_status_indicator("disconnected")
                self.aircon_sensors_tab.update_status_indicator("disconnected")
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
                    button.setStyleSheet(BUTTON_STANDARD_STYLE)
        
        # 스피드 버튼들 리셋
        if hasattr(self, 'speed_button_manager') and self.speed_button_manager:
            # Fan SPD 버튼들 리셋
            self.speed_button_manager.current_fan_speed = 0
            if self.speed_button_manager.center_button:
                self.speed_button_manager.center_button.setText("0")
            
            # Con Fan SPD 버튼들 리셋  
            self.speed_button_manager.current_con_fan_speed = 0
            # 이전 spdButton_7 리퍼런스 제거됨 (사용되지 않는 버튼)
                
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
                
            # PUMP SPD 버튼들 리셋
            self.speed_button_manager.current_pump1_speed = 0
            self.speed_button_manager.current_pump2_speed = 0
            if hasattr(self, 'spdButton_pump1_val'):
                self.spdButton_pump1_val.setText("0")
            if hasattr(self, 'spdButton_pump2_val'):
                self.spdButton_pump2_val.setText("0")
                
            # OA DAMPER 숫자 버튼들 리셋
            self.speed_button_manager.reset_oa_damper_number_buttons()
        
        # SEMI AUTO 버튼들 리셋 (예외 - 그대로 유지)
        if hasattr(self, 'semi_auto_run_button'):
            self.semi_auto_run_button.setText("RUN")
            self.semi_auto_run_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        if hasattr(self, 'damp_test_button'):
            self.damp_test_button.setText("RUN")
            self.damp_test_button.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        if hasattr(self, 'semi_auto_period_value_button'):
            self.semi_auto_period_value_button.setText("200")

    def read_serial_data(self):
        """시리얼 데이터 읽기 (완전 비활성화)"""
        # 행 걸림 문제 해결을 위해 시리얼 데이터 읽기 완전 비활성화
        return

    def handle_received_data(self, data: str):
        """인터럽트 방식으로 수신된 데이터 처리"""
        # 연결된 상태에서만 처리
        if not self.was_connected:
            return
            
        try: 
            # 데이터 수신 성공 - 에러 카운터 리셋
            self.connection_error_count = 0
            print(f"[MAIN INTERRUPT] ✅ 수신된 데이터: '{data}'")
            self.saved_data_to_file(data)
                    
        except Exception as e:
            # 에러 발생 - 카운터 증가
            self.connection_error_count += 1
            
            # 5회까지만 에러 메시지 출력
            if self.connection_error_count <= 5:
                print(f"[MAIN ERROR] 시리얼 데이터 처리 오류: {e} (에러 {self.connection_error_count}/5)")
            
            # 5회 도달 시 즉시 처리
            if self.connection_error_count >= 5:
                print("[MAIN ERROR] 갑작스런 연결 끊김 감지 (5회) - 연결 해제 및 초기화")
                self.handle_sudden_disconnect_simple()
                return

    def saved_data_to_file(self, data):
        """수신된 데이터 파일에 저장 (비활성화)"""
        # 시리얼 데이터 수신 비활성화로 파일 저장도 비활성화
        pass
    
    def handle_sudden_disconnect_simple(self):
        """간단하고 확실한 갑작스런 연결 끊김 처리"""
        print("=== 간단한 연결 끊김 처리 시작 ===")
        
        # 1. 즉시 was_connected를 False로 설정 (가장 중요!)
        self.was_connected = False
        print("연결 상태 즉시 False 설정")
        
        # [비활성화] 2. 센서 스케줄러 중지 (T/H 탭 비활성화로 이미 중지됨)
        # try:
        #     self.sensor_scheduler.stop_scheduling()
        #     print("센서 스케줄러 중지 완료")
        # except Exception as e:
        #     print(f"센서 스케줄러 중지 오류: {e}")
        
        # 3. Serial 포트 강제 닫기
        try:
            if hasattr(self.serial_manager, 'shinho_serial_connection') and self.serial_manager.shinho_serial_connection:
                self.serial_manager.shinho_serial_connection.close()
                self.serial_manager.shinho_serial_connection = None
                print("Serial port 강제 닫기 성공")
        except Exception as e:
            print(f"Serial port 닫기 오류: {e}")
        
        # 4. 모든 상태 변수 리셋
        self.connection_error_count = 0
        self.last_connection_check = 0
        self.last_error_log_time = 0
        print("상태 변수 초기화 완료")
        
        # 5. UI 업데이트
        self.update_status_indicator("disconnected")
        self.update_connect_button("disconnected")
        self.update_button_states()
        print("UI 초기화 완료")
        
        print("=== 연결 끊김 처리 완료 - 재연결 준비됨 ===")
    
    def handle_sudden_disconnect(self):
        """갑작스런 연결 끊김 처리 - 즉시 serial close 및 프로그램 초기화"""
        try:
            print("=== 갑작스런 연결 끊김 처리 시작 ===")
            
            # 즉시 was_connected를 False로 설정하여 추가 에러 메시지 방지
            self.was_connected = False
            print("연결 상태를 즉시 False로 설정 - 추가 에러 메시지 방지")
            
            # Serial 포트 즉시 강제 닫기
            if self.serial_manager.shinho_serial_connection:
                print("Serial connection 발견 - 강제 닫기 실행")
                self.serial_manager.shinho_serial_connection.close()
                self.serial_manager.shinho_serial_connection = None
                print("Serial port 강제 닫기 완료")
            else:
                print("Serial connection이 이미 None 상태")
            
            # 연결 관련 모든 상태 프로그램 초기 실행 상태로 완전 초기화
            self.connection_error_count = 0
            self.last_connection_check = 0
            self.last_error_log_time = 0
            print("연결 상태 변수 초기화 완료")
            
            # Serial Manager 상태 초기화
            if hasattr(self.serial_manager, 'connection_healthy'):
                self.serial_manager.connection_healthy = True
            print("Serial Manager 상태 초기화 완료")
            
            # UI를 프로그램 초기 실행 상태로 완전 초기화
            self.update_status_indicator("disconnected")
            self.update_connect_button("disconnected")
            self.update_button_states()  # 모든 버튼 비활성화
            print("UI 상태 초기화 완료")
            
            print("=== 프로그램 초기화 완료 - 재연결 준비됨 ===")
            
        except Exception as e:
            print(f"갑작스런 연결 끊김 처리 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def force_disconnect(self):
        """강제 연결 해제 및 상태 초기화"""
        try:
            # Serial 포트 강제 닫기
            if self.serial_manager.shinho_serial_connection:
                self.serial_manager.shinho_serial_connection.close()
                print("Serial port 강제 닫기 완료")
            
            # 연결 상태 초기화
            self.was_connected = False
            self.connection_error_count = 0
            self.last_connection_check = 0
            self.last_error_log_time = 0
            
            # UI 상태 업데이트
            self.update_status_indicator("disconnected")
            self.update_connect_button("disconnected")
            self.update_button_states()
            
        except Exception as e:
            print(f"강제 연결 해제 오류: {e}")
    
    def force_disconnect_and_reset(self):
        """연결 문제 시 즉시 연결 해제 및 완전 초기화"""
        try:
            print("연결 문제 감지 - Serial 강제 닫기 시작")
            
            # Serial 포트 즉시 강제 닫기
            if self.serial_manager.shinho_serial_connection:
                self.serial_manager.shinho_serial_connection.close()
                self.serial_manager.shinho_serial_connection = None
                print("Serial port 즉시 닫기 완료")
            
            # 연결 상태 완전 초기화
            self.serial_manager.connection_healthy = True
            
            # 연결 상태 완전 초기화
            self.was_connected = False
            self.connection_error_count = 0
            self.last_connection_check = 0
            self.last_error_log_time = 0
            
            # UI 상태 즉시 업데이트
            self.update_status_indicator("disconnected")
            self.update_connect_button("disconnected")
            self.update_button_states()
            
            print("연결 상태 완전 초기화 완료")
            
        except Exception as e:
            print(f"연결 문제 처리 오류: {e}")

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
    
    def setup_semi_auto_button_events(self):
        """SEMI AUTO 탭 버튼 이벤트 설정"""
        # DESICCANT RUN/STOP 토글 버튼
        self.semi_auto_run_button.clicked.connect(self.toggle_desiccant_semi_auto)
        
        # DAMP TEST RUN/STOP 토글 버튼
        self.damp_test_button.clicked.connect(self.toggle_damp_test)
        
        # 주기 조절 버튼들 (연속 클릭 지원)
        self.setup_period_buttons()
    
    def toggle_desiccant_semi_auto(self):
        """DESICCANT SEMI AUTO RUN/STOP 토글"""
        if not self.serial_manager.is_connected():
            print("시리얼 포트가 연결되지 않음 - DESICCANT SEMI AUTO 버튼 동작 차단")
            return
            
        if self.semi_auto_run_button.text() == "RUN":
            # RUN 실행
            period = int(self.semi_auto_period_value_button.text())
            cmd = f"$CMD,DSCT,SEMIAUTO,RUN,{period}\r\n"
            success = self.serial_manager.send_data(cmd)
            if success:
                self.semi_auto_run_button.setText("STOP")
                self.semi_auto_run_button.setStyleSheet("background-color: rgb(255, 0, 0); color: white; font-size: 14px; font-weight: bold;")
                print(f"DESICCANT SEMI AUTO RUN 명령 전송: {cmd.strip()}")
        else:
            # STOP 실행
            cmd = f"$CMD,DSCT,SEMIAUTO,STOP\r\n"
            success = self.serial_manager.send_data(cmd)
            if success:
                self.semi_auto_run_button.setText("RUN")
                self.semi_auto_run_button.setStyleSheet("font-size: 14px; font-weight: bold;")
                print(f"DESICCANT SEMI AUTO STOP 명령 전송: {cmd.strip()}")
    
    def toggle_damp_test(self):
        """DAMP TEST RUN/STOP 토글"""
        if not self.serial_manager.is_connected():
            print("시리얼 포트가 연결되지 않음 - DAMP TEST 버튼 동작 차단")
            return
            
        if self.damp_test_button.text() == "RUN":
            # RUN 실행
            cmd = f"$CMD,DSCT,DMPTEST,RUN\r\n"
            success = self.serial_manager.send_data(cmd)
            if success:
                self.damp_test_button.setText("STOP")
                self.damp_test_button.setStyleSheet("background-color: rgb(255, 0, 0); color: white; font-size: 14px; font-weight: bold;")
                print(f"DAMP TEST RUN 명령 전송: {cmd.strip()}")
        else:
            # STOP 실행
            cmd = f"$CMD,DSCT,DMPTEST,STOP\r\n"
            success = self.serial_manager.send_data(cmd)
            if success:
                self.damp_test_button.setText("RUN")
                self.damp_test_button.setStyleSheet("font-size: 14px; font-weight: bold;")
                print(f"DAMP TEST STOP 명령 전송: {cmd.strip()}")
    
    def setup_period_buttons(self):
        """주기 조절 버튼 설정 (연속 클릭 지원)"""
        # 타이머 초기화
        self.period_decrease_timer = QTimer()
        self.period_increase_timer = QTimer()
        
        # 타이머 이벤트 연결
        self.period_decrease_timer.timeout.connect(self.decrease_period)
        self.period_increase_timer.timeout.connect(self.increase_period)
        
        # 마우스 이벤트 연결
        self.semi_auto_period_minus_button.pressed.connect(self.start_decreasing_period)
        self.semi_auto_period_minus_button.released.connect(self.stop_decreasing_period)
        
        self.semi_auto_period_plus_button.pressed.connect(self.start_increasing_period)
        self.semi_auto_period_plus_button.released.connect(self.stop_increasing_period)
    
    def start_decreasing_period(self):
        """주기 감소 시작 (연속 클릭)"""
        self.decrease_period()  # 즉시 1회 실행
        self.period_decrease_timer.start(200)  # 200ms마다 반복
    
    def stop_decreasing_period(self):
        """주기 감소 정지"""
        self.period_decrease_timer.stop()
    
    def start_increasing_period(self):
        """주기 증가 시작 (연속 클릭)"""
        self.increase_period()  # 즉시 1회 실행
        self.period_increase_timer.start(200)  # 200ms마다 반복
    
    def stop_increasing_period(self):
        """주기 증가 정지"""
        self.period_increase_timer.stop()
    
    def decrease_period(self):
        """주기 값 1 감소 (1~999 범위)"""
        current_value = int(self.semi_auto_period_value_button.text())
        if current_value > 1:
            new_value = current_value - 1
            self.semi_auto_period_value_button.setText(str(new_value))
    
    def increase_period(self):
        """주기 값 1 증가 (1~999 범위)"""
        current_value = int(self.semi_auto_period_value_button.text())
        if current_value < 999:
            new_value = current_value + 1
            self.semi_auto_period_value_button.setText(str(new_value))