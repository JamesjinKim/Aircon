# AIRCON T/H 탭의 전체 레이아웃을 관리하는 모듈
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.sensor_widget import SensorWidget
from utils.usb_detector import USBDetector
from config.config_manager import get_config_manager

class AirconSensorTab(QWidget):
    """AIRCON T/H 탭 위젯"""
    
    def __init__(self, air_sensor_manager=None, sensor_scheduler=None, parent=None):
        super().__init__(parent)
        self.air_sensor_manager = air_sensor_manager
        self.sensor_scheduler = sensor_scheduler  # 스케줄러 참조 추가
        self.sensor_widgets = {}  # sensor_id: widget 매핑
        
        # 설정 관리자 초기화
        self.config_manager = get_config_manager()
        
        # 저장된 새로고침 간격 로드 (기본값: 5초)
        self.refresh_interval = self.config_manager.load_refresh_interval('aircon_sensor')
        
        # USB 감지기 초기화
        self.usb_detector = USBDetector()
        self.usb_detector.usb_connected.connect(self.on_usb_connected)
        self.usb_detector.usb_disconnected.connect(self.on_usb_disconnected)
        self.usb_detector.start_monitoring()
        
        self.setup_ui()
        
        # 센서 매니저 연결
        if self.air_sensor_manager:
            self.connect_sensor_manager()
            
        # 센서 스케줄러 연결
        if self.sensor_scheduler:
            self.set_sensor_scheduler(self.sensor_scheduler)
            
    def setup_ui(self):
        """UI 설정"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)
        
        # 상단 제어 영역
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        # 제목 레이블
        title_label = QLabel("AIRCON 온습도 모니터링")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        control_layout.addWidget(title_label)
        
        control_layout.addStretch()
        
        # CSV 파일 저장 버튼
        self.csv_save_button = QPushButton("CSV 파일 저장")
        self.csv_save_button.setFixedSize(120, 35)
        self.csv_save_button.setEnabled(False)  # 초기에는 비활성화
        self.csv_save_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.csv_save_button.clicked.connect(self.on_csv_save_clicked)
        control_layout.addWidget(self.csv_save_button)
        
        # 새로고침 버튼
        #self.refresh_button = QPushButton("명령 전송")
        #self.refresh_button.setFixedSize(100, 35)
        #self.refresh_button.setStyleSheet("""
        #    QPushButton {
        #        font-size: 12px;
        #        font-weight: bold;
        #        background-color: #4CAF50;
        #        color: white;
        #        border: none;
        #        border-radius: 4px;
        #    }
        #    QPushButton:hover {
        #        background-color: #45a049;
        #    }
        #    QPushButton:pressed {
        #        background-color: #3d8b40;
        #    }
        #""")
        #self.refresh_button.clicked.connect(self.on_refresh_clicked)
        #control_layout.addWidget(self.refresh_button)
        
        # USB 상태 레이블
        self.usb_status_label = QLabel("USB: 연결 안됨")
        self.usb_status_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
        control_layout.addWidget(self.usb_status_label)
        
        # 자동 새로고침 상태 레이블
        #self.auto_refresh_label = QLabel("자동 새로고침: OFF")
        #self.auto_refresh_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
        #control_layout.addWidget(self.auto_refresh_label)
        
        main_layout.addLayout(control_layout)
        
        # 시간 간격 조절 영역
        time_control_layout = QHBoxLayout()
        time_control_layout.setSpacing(5)
        
        # 왼쪽 빈 공간 추가 (오른쪽 정렬을 위해)
        time_control_layout.addStretch()
        
        # 시간 간격 레이블
        time_label = QLabel("새로고침 간격:")
        time_label.setStyleSheet("QLabel { font-size: 12px; font-weight: bold; }")
        time_control_layout.addWidget(time_label)
        
        # 감소 버튼
        self.decrease_button = QPushButton("-")
        self.decrease_button.setFixedSize(30, 30)
        self.decrease_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #FF5722;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E64A19;
            }
            QPushButton:pressed {
                background-color: #D84315;
            }
        """)
        self.decrease_button.clicked.connect(self.on_decrease_interval)
        time_control_layout.addWidget(self.decrease_button)
        
        # 시간 표시 레이블
        self.interval_label = QPushButton(f"{self.refresh_interval}")
        self.interval_label.setFixedSize(50, 30)
        self.interval_label.setEnabled(False)
        self.interval_label.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                background-color: #E0E0E0;
                color: black;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
        time_control_layout.addWidget(self.interval_label)
        
        # 증가 버튼
        self.increase_button = QPushButton("+")
        self.increase_button.setFixedSize(30, 30)
        self.increase_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.increase_button.clicked.connect(self.on_increase_interval)
        time_control_layout.addWidget(self.increase_button)
        
        # 초 단위 레이블
        seconds_label = QLabel("초")
        seconds_label.setStyleSheet("QLabel { font-size: 12px; }")
        time_control_layout.addWidget(seconds_label)
        
        main_layout.addLayout(time_control_layout)
        
        # 센서 그룹박스
        sensor_group = QGroupBox("센서 상태")
        sensor_group_layout = QVBoxLayout()
        
        # 센서 그리드 레이아웃 (4x2 - AIRCON은 6개만, ID07, ID08 제거)
        sensor_grid = QGridLayout()
        sensor_grid.setSpacing(5)
        
        # 센서 라벨 매핑
        sensor_labels = {
            "ID01": "L_RA1",
            "ID02": "L_RA2", 
            "ID03": "L_실내",
            "ID04": "R_실내",
            "ID05": "R_RA2",
            "ID06": "R_RA1"
        }
        
        # 6개 센서 위젯 생성 (ID01~ID06)
        for i in range(6):
            row = i // 4
            col = i % 4
            sensor_id = f"ID{i+1:02d}"
            display_label = sensor_labels[sensor_id]
            
            sensor_widget = SensorWidget(sensor_id, display_label)
            self.sensor_widgets[sensor_id] = sensor_widget
            sensor_grid.addWidget(sensor_widget, row, col)
            
        sensor_group_layout.addLayout(sensor_grid)
        sensor_group.setLayout(sensor_group_layout)
        main_layout.addWidget(sensor_group)
        
        # 하단 정보 영역
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        # 요약 정보
        self.summary_label = QLabel("정상: 0개, 타임아웃: 0개, 대기중: 6개")
        self.summary_label.setStyleSheet("QLabel { font-size: 12px; }")
        info_layout.addWidget(self.summary_label)
        
        # 상태 신호등 (원형)
        self.status_indicator = QLabel("●")
        self.status_indicator.setFixedSize(20, 20)
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #CCCCCC;
                background-color: transparent;
                border-radius: 10px;
            }
        """)
        self.status_indicator.setToolTip("AIRCON 센서 통신 상태")
        info_layout.addWidget(self.status_indicator)
        
        info_layout.addStretch()
        
        # 마지막 스캔 시간
        self.last_scan_label = QLabel("마지막 스캔: -")
        self.last_scan_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
        info_layout.addWidget(self.last_scan_label)
        
        main_layout.addLayout(info_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
    def connect_sensor_manager(self):
        """센서 매니저 시그널 연결"""
        if self.air_sensor_manager:
            # 개별 센서 업데이트
            self.air_sensor_manager.sensor_data_updated.connect(self.on_sensor_data_updated)
            # 전체 센서 업데이트
            self.air_sensor_manager.all_sensors_updated.connect(self.on_all_sensors_updated)
            
    def set_sensor_manager(self, air_sensor_manager):
        """센서 매니저 설정"""
        self.air_sensor_manager = air_sensor_manager
        self.connect_sensor_manager()
        
    def set_sensor_scheduler(self, sensor_scheduler):
        """센서 스케줄러 설정"""
        self.sensor_scheduler = sensor_scheduler
        # 스케줄러 시그널 연결
        if self.sensor_scheduler:
            self.sensor_scheduler.aircon_sensor_updated.connect(self.on_sensor_data_updated)
            self.sensor_scheduler.aircon_all_sensors_updated.connect(self.on_all_sensors_updated)
            # 스케줄러 상태 변경 시그널 연결
            self.sensor_scheduler.state_changed.connect(self.on_scheduler_state_changed)
        
    @pyqtSlot()
    def on_csv_save_clicked(self):
        """CSV 파일 저장 버튼 클릭"""
        self.csv_save_to_usb()
            
    @pyqtSlot()
    def on_refresh_clicked(self):
        """수동 명령 전송 버튼 클릭"""
        if self.sensor_scheduler:
            # 스케줄러를 통한 수동 AIRCON 요청
            self.sensor_scheduler.manual_request_aircon()
            self.refresh_button.setText("전송 중...")
            self.refresh_button.setEnabled(False)
        elif self.air_sensor_manager:
            # 스케줄러가 없으면 직접 요청 (호환성)
            self.air_sensor_manager.request_sensor_data()
            self.refresh_button.setText("전송 중...")
            self.refresh_button.setEnabled(False)
            
    @pyqtSlot(str, dict)
    def on_sensor_data_updated(self, sensor_id, data):
        """개별 센서 데이터 업데이트"""
        if sensor_id in self.sensor_widgets:
            self.sensor_widgets[sensor_id].update_sensor_data(data)
            
    @pyqtSlot(dict)
    def on_all_sensors_updated(self, all_data):
        """전체 센서 데이터 업데이트 완료"""
        print(f"[AIRCON UI] 전체 센서 데이터 업데이트: {len(all_data)}개 센서")
        
        # 요약 정보 계산
        active_count = 0
        timeout_count = 0
        unknown_count = 0
        
        for sensor_id, data in all_data.items():
            status = data.get('status', 'unknown')
            if status == 'active':
                active_count += 1
            elif status == 'timeout':
                timeout_count += 1
            else:
                unknown_count += 1
                
        # 요약 정보 업데이트
        self.summary_label.setText(f"정상: {active_count}개, 타임아웃: {timeout_count}개, 대기중: {unknown_count}개")
        
        # 마지막 스캔 시간 업데이트
        from datetime import datetime
        now = datetime.now()
        self.last_scan_label.setText(f"마지막 스캔: {now.strftime('%H:%M:%S')}")
        
        # 상태 신호등을 완료로 변경
        if timeout_count > 0:
            self.update_status_indicator("error")
        else:
            self.update_status_indicator("completed")
        
        # 새로고침 버튼 복원
        #self.refresh_button.setText("명령 전송")
        #self.refresh_button.setEnabled(True)
        
    def set_auto_refresh_status(self, is_active):
        """자동 새로고침 상태 표시 (UI에 표시하지 않음)"""
        pass
            
    def reset_all_sensors(self):
        """모든 센서 위젯 초기화"""
        for sensor_widget in self.sensor_widgets.values():
            sensor_widget.update_sensor_data({
                'temp': None,
                'humi': None,
                'status': 'unknown',
                'last_update': None
            })
        
        self.summary_label.setText("정상: 0개, 타임아웃: 0개, 대기중: 6개")
        self.last_scan_label.setText("마지막 스캔: -")
        
    def csv_save_to_usb(self):
        """CSV 파일을 USB로 저장"""
        import os
        import shutil
        from PyQt5.QtWidgets import QMessageBox
        
        # USB 연결 확인
        if not self.usb_detector.is_usb_available():
            QMessageBox.warning(self, "경고", "USB 저장장치가 연결되지 않았습니다.\nUSB를 연결한 후 다시 시도해주세요.")
            return
            
        # /data 폴더 확인
        data_folder = "/home/shinho/shinho/Aircon/data"
        if not os.path.exists(data_folder):
            QMessageBox.warning(self, "경고", "/data 폴더가 존재하지 않습니다.")
            return
            
        # CSV 파일 찾기
        csv_files = []
        for filename in os.listdir(data_folder):
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(data_folder, filename))
                
        if not csv_files:
            QMessageBox.information(self, "정보", "/data 폴더에 CSV 파일이 없습니다.")
            return
            
        try:
            # USB에 CSV 저장 폴더 생성
            csv_folder = self.usb_detector.create_csv_folder("AIRCON_CSV")
            if not csv_folder:
                QMessageBox.critical(self, "오류", "USB에 폴더를 생성할 수 없습니다.")
                return
                
            # CSV 파일 복사
            copied_count = 0
            for csv_file in csv_files:
                filename = os.path.basename(csv_file)
                dest_path = os.path.join(csv_folder, filename)
                shutil.copy2(csv_file, dest_path)
                copied_count += 1
                
            QMessageBox.information(
                self, 
                "완료", 
                f"{copied_count}개의 CSV 파일이 성공적으로 복사되었습니다.\n저장 위치: {csv_folder}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 복사 중 오류가 발생했습니다:\n{str(e)}")
            
    @pyqtSlot(str)
    def on_usb_connected(self, usb_path):
        """USB 연결됨"""
        import os
        self.usb_status_label.setText(f"USB: 연결됨 ({os.path.basename(usb_path)})")
        self.usb_status_label.setStyleSheet("QLabel { font-size: 12px; color: green; }")
        self.csv_save_button.setEnabled(True)
        
    @pyqtSlot()
    def on_usb_disconnected(self):
        """USB 연결 해제됨"""
        self.usb_status_label.setText("USB: 연결 안됨")
        self.usb_status_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
        self.csv_save_button.setEnabled(False)
        
    @pyqtSlot()
    def on_decrease_interval(self):
        """새로고침 간격 감소"""
        if self.refresh_interval > 1:
            self.refresh_interval -= 1
            self.update_interval_display()
            self.update_sensor_manager_interval()
            # 설정 저장
            self.config_manager.save_refresh_interval('aircon_sensor', self.refresh_interval)
            
    @pyqtSlot()
    def on_increase_interval(self):
        """새로고침 간격 증가"""
        if self.refresh_interval < 360:
            self.refresh_interval += 1
            self.update_interval_display()
            self.update_sensor_manager_interval()
            # 설정 저장
            self.config_manager.save_refresh_interval('aircon_sensor', self.refresh_interval)
            
    def update_interval_display(self):
        """간격 표시 업데이트"""
        self.interval_label.setText(f"{self.refresh_interval}")
        
    def update_sensor_manager_interval(self):
        """센서 스케줄러의 간격 업데이트"""
        if self.sensor_scheduler:
            self.sensor_scheduler.set_cycle_interval(self.refresh_interval)
            # 자동 새로고침이 활성화되어 있다면 레이블 업데이트
            self.set_auto_refresh_status(True)
        # 호환성을 위한 기존 코드 (스케줄러가 없으면)
        elif self.air_sensor_manager and hasattr(self.air_sensor_manager, 'set_refresh_interval'):
            self.air_sensor_manager.set_refresh_interval(self.refresh_interval)
            
    def update_status_indicator(self, status):
        """상태 신호등 업데이트"""
        if status == "requesting":
            # 노랑 - 데이터 수신 중
            self.status_indicator.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #FFC107;
                    background-color: transparent;
                    border-radius: 10px;
                }
            """)
            self.status_indicator.setToolTip("AIRCON 센서 데이터 요청 중...")
        elif status == "completed":
            # 녹색 - 수신 완료
            self.status_indicator.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #4CAF50;
                    background-color: transparent;
                    border-radius: 10px;
                }
            """)
            self.status_indicator.setToolTip("AIRCON 센서 데이터 수신 완료")
        elif status == "error":
            # 빨강 - 에러/타임아웃
            self.status_indicator.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #F44336;
                    background-color: transparent;
                    border-radius: 10px;
                }
            """)
            self.status_indicator.setToolTip("AIRCON 센서 통신 오류 또는 타임아웃")
        elif status == "waiting":
            # 회색 - 대기 상태
            self.status_indicator.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #CCCCCC;
                    background-color: transparent;
                    border-radius: 10px;
                }
            """)
            self.status_indicator.setToolTip("AIRCON 센서 대기 중")
        else:
            # 회색 - 기본 대기 상태
            self.status_indicator.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #CCCCCC;
                    background-color: transparent;
                    border-radius: 10px;
                }
            """)
            self.status_indicator.setToolTip("AIRCON 센서 대기 중")
            
    @pyqtSlot(str)
    def on_scheduler_state_changed(self, state_name):
        """스케줄러 상태 변경 처리"""
        print(f"[AIRCON UI] 스케줄러 상태 변경: {state_name}")
        if state_name == "aircon_requesting":
            self.update_status_indicator("requesting")
        elif state_name == "aircon_waiting":
            self.update_status_indicator("requesting")
        elif state_name == "idle" or state_name == "interval_waiting":
            # 대기 상태로 돌아감
            self.update_status_indicator("waiting")