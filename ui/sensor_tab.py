# SENSORS 탭의 전체 레이아웃을 관리하는 모듈
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from ui.sensor_widget import SensorWidget

class SensorTab(QWidget):
    """SENSORS 탭 위젯"""
    
    def __init__(self, sensor_manager=None, parent=None):
        super().__init__(parent)
        self.sensor_manager = sensor_manager
        self.sensor_widgets = {}  # sensor_id: widget 매핑
        
        self.setup_ui()
        
        # 센서 매니저 연결
        if self.sensor_manager:
            self.connect_sensor_manager()
            
    def setup_ui(self):
        """UI 설정"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 상단 제어 영역
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        # 제목 레이블
        title_label = QLabel("온습도 센서 모니터링")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        control_layout.addWidget(title_label)
        
        control_layout.addStretch()
        
        # 새로고침 버튼
        self.refresh_button = QPushButton("수동 새로고침")
        self.refresh_button.setFixedSize(120, 35)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
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
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        control_layout.addWidget(self.refresh_button)
        
        # 자동 새로고침 상태 레이블
        self.auto_refresh_label = QLabel("자동 새로고침: OFF")
        self.auto_refresh_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
        control_layout.addWidget(self.auto_refresh_label)
        
        main_layout.addLayout(control_layout)
        
        # 센서 그룹박스
        sensor_group = QGroupBox("센서 상태")
        sensor_group_layout = QVBoxLayout()
        
        # 센서 그리드 레이아웃 (4x3)
        sensor_grid = QGridLayout()
        sensor_grid.setSpacing(10)
        
        # 12개 센서 위젯 생성
        for i in range(12):
            row = i // 4
            col = i % 4
            sensor_id = f"ID{i+1:02d}"
            
            sensor_widget = SensorWidget(sensor_id)
            self.sensor_widgets[sensor_id] = sensor_widget
            sensor_grid.addWidget(sensor_widget, row, col)
            
        sensor_group_layout.addLayout(sensor_grid)
        sensor_group.setLayout(sensor_group_layout)
        main_layout.addWidget(sensor_group)
        
        # 하단 정보 영역
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        
        # 요약 정보
        self.summary_label = QLabel("정상: 0개, 타임아웃: 0개, 대기중: 12개")
        self.summary_label.setStyleSheet("QLabel { font-size: 12px; }")
        info_layout.addWidget(self.summary_label)
        
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
        if self.sensor_manager:
            # 개별 센서 업데이트
            self.sensor_manager.sensor_data_updated.connect(self.on_sensor_data_updated)
            # 전체 센서 업데이트
            self.sensor_manager.all_sensors_updated.connect(self.on_all_sensors_updated)
            
    def set_sensor_manager(self, sensor_manager):
        """센서 매니저 설정"""
        self.sensor_manager = sensor_manager
        self.connect_sensor_manager()
        
    @pyqtSlot()
    def on_refresh_clicked(self):
        """새로고침 버튼 클릭"""
        if self.sensor_manager:
            self.sensor_manager.request_sensor_data()
            self.refresh_button.setText("새로고침 중...")
            self.refresh_button.setEnabled(False)
            
    @pyqtSlot(str, dict)
    def on_sensor_data_updated(self, sensor_id, data):
        """개별 센서 데이터 업데이트"""
        if sensor_id in self.sensor_widgets:
            self.sensor_widgets[sensor_id].update_sensor_data(data)
            
    @pyqtSlot(dict)
    def on_all_sensors_updated(self, all_data):
        """전체 센서 데이터 업데이트 완료"""
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
        
        # 새로고침 버튼 복원
        self.refresh_button.setText("수동 새로고침")
        self.refresh_button.setEnabled(True)
        
    def set_auto_refresh_status(self, is_active):
        """자동 새로고침 상태 표시"""
        if is_active:
            self.auto_refresh_label.setText("자동 새로고침: ON (5초)")
            self.auto_refresh_label.setStyleSheet("QLabel { font-size: 12px; color: green; }")
        else:
            self.auto_refresh_label.setText("자동 새로고침: OFF")
            self.auto_refresh_label.setStyleSheet("QLabel { font-size: 12px; color: #666; }")
            
    def reset_all_sensors(self):
        """모든 센서 위젯 초기화"""
        for sensor_widget in self.sensor_widgets.values():
            sensor_widget.update_sensor_data({
                'temp': None,
                'humi': None,
                'status': 'unknown',
                'last_update': None
            })
        
        self.summary_label.setText("정상: 0개, 타임아웃: 0개, 대기중: 12개")
        self.last_scan_label.setText("마지막 스캔: -")