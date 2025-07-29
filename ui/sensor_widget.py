# 개별 온습도 센서를 표시하는 위젯
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from datetime import datetime

class SensorWidget(QFrame):
    """개별 온습도 센서 표시 위젯"""
    
    def __init__(self, sensor_id, parent=None):
        super().__init__(parent)
        self.sensor_id = sensor_id
        
        # 프레임 스타일 설정
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setFixedSize(180, 120)
        
        # 레이아웃 설정
        self.setup_ui()
        
        # 초기 상태 설정
        self.update_sensor_data({
            'temp': None,
            'humi': None,
            'status': 'unknown',
            'last_update': None
        })
        
    def setup_ui(self):
        """UI 설정"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 센서 ID 레이블
        self.id_label = QLabel(self.sensor_id)
        self.id_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.id_label.setFont(font)
        layout.addWidget(self.id_label)
        
        # 온도 표시
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(5)
        
        temp_title = QLabel("온도:")
        temp_title.setFixedWidth(40)
        temp_layout.addWidget(temp_title)
        
        self.temp_value = QLabel("--.-")
        self.temp_value.setAlignment(Qt.AlignRight)
        temp_layout.addWidget(self.temp_value)
        
        self.temp_unit = QLabel("°C")
        self.temp_unit.setFixedWidth(20)
        temp_layout.addWidget(self.temp_unit)
        
        layout.addLayout(temp_layout)
        
        # 습도 표시
        humi_layout = QHBoxLayout()
        humi_layout.setSpacing(5)
        
        humi_title = QLabel("습도:")
        humi_title.setFixedWidth(40)
        humi_layout.addWidget(humi_title)
        
        self.humi_value = QLabel("--.-")
        self.humi_value.setAlignment(Qt.AlignRight)
        humi_layout.addWidget(self.humi_value)
        
        self.humi_unit = QLabel("%")
        self.humi_unit.setFixedWidth(20)
        humi_layout.addWidget(self.humi_unit)
        
        layout.addLayout(humi_layout)
        
        # 상태 표시
        self.status_label = QLabel("대기중")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("QLabel { font-size: 10px; }")
        layout.addWidget(self.status_label)
        
        # 마지막 업데이트 시간
        self.update_time_label = QLabel("")
        self.update_time_label.setAlignment(Qt.AlignCenter)
        self.update_time_label.setStyleSheet("QLabel { font-size: 9px; color: #666; }")
        layout.addWidget(self.update_time_label)
        
        self.setLayout(layout)
        
    @pyqtSlot(dict)
    def update_sensor_data(self, data):
        """센서 데이터 업데이트"""
        status = data.get('status', 'unknown')
        
        if status == 'active':
            # 정상 데이터
            temp = data.get('temp')
            humi = data.get('humi')
            
            if temp is not None:
                self.temp_value.setText(f"{temp:.1f}")
            else:
                self.temp_value.setText("--.-")
                
            if humi is not None:
                self.humi_value.setText(f"{humi:.1f}")
            else:
                self.humi_value.setText("--.-")
                
            self.status_label.setText("정상")
            self.status_label.setStyleSheet("QLabel { font-size: 10px; color: green; }")
            self.setStyleSheet("""
                SensorWidget {
                    background-color: #f0fff0;
                    border: 2px solid green;
                }
            """)
            
        elif status == 'timeout':
            # 타임아웃
            self.temp_value.setText("--.-")
            self.humi_value.setText("--.-")
            self.status_label.setText("타임아웃")
            self.status_label.setStyleSheet("QLabel { font-size: 10px; color: red; }")
            self.setStyleSheet("""
                SensorWidget {
                    background-color: #fff0f0;
                    border: 2px solid red;
                }
            """)
            
        else:
            # 대기중 또는 알 수 없음
            self.temp_value.setText("--.-")
            self.humi_value.setText("--.-")
            self.status_label.setText("대기중")
            self.status_label.setStyleSheet("QLabel { font-size: 10px; color: #666; }")
            self.setStyleSheet("""
                SensorWidget {
                    background-color: #f5f5f5;
                    border: 2px solid #ccc;
                }
            """)
            
        # 업데이트 시간 표시
        last_update = data.get('last_update')
        if last_update:
            time_str = last_update.strftime("%H:%M:%S")
            self.update_time_label.setText(f"업데이트: {time_str}")
        else:
            self.update_time_label.setText("")