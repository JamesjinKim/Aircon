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
        self.setFixedSize(180, 70)
        
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
        layout.setContentsMargins(6, 3, 6, 3)
        layout.setSpacing(1)
        
        # 센서 ID 레이블
        self.id_label = QLabel(self.sensor_id)
        self.id_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.id_label.setFont(font)
        layout.addWidget(self.id_label)
        
        # 온도 표시
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(3)
        
        temp_title = QLabel("온도:")
        temp_title.setFixedWidth(40)
        temp_title.setStyleSheet("QLabel { font-size: 12px; font-weight: bold; }")
        temp_layout.addWidget(temp_title)
        
        self.temp_value = QLabel("--.-")
        self.temp_value.setAlignment(Qt.AlignRight)
        self.temp_value.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        temp_layout.addWidget(self.temp_value)
        
        self.temp_unit = QLabel("°C")
        self.temp_unit.setFixedWidth(20)
        self.temp_unit.setStyleSheet("QLabel { font-size: 12px; }")
        temp_layout.addWidget(self.temp_unit)
        
        layout.addLayout(temp_layout)
        
        # 습도 표시
        humi_layout = QHBoxLayout()
        humi_layout.setSpacing(3)
        
        humi_title = QLabel("습도:")
        humi_title.setFixedWidth(40)
        humi_title.setStyleSheet("QLabel { font-size: 12px; font-weight: bold; }")
        humi_layout.addWidget(humi_title)
        
        self.humi_value = QLabel("--.-")
        self.humi_value.setAlignment(Qt.AlignRight)
        self.humi_value.setStyleSheet("QLabel { font-size: 14px; font-weight: bold; }")
        humi_layout.addWidget(self.humi_value)
        
        self.humi_unit = QLabel("%")
        self.humi_unit.setFixedWidth(20)
        self.humi_unit.setStyleSheet("QLabel { font-size: 12px; }")
        humi_layout.addWidget(self.humi_unit)
        
        layout.addLayout(humi_layout)
        
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
            self.setStyleSheet("""
                SensorWidget {
                    background-color: #f5f5f5;
                    border: 2px solid #ccc;
                }
            """)