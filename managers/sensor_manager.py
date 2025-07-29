# 온습도 센서 12개를 관리하는 매니저 클래스
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
import re

class SensorManager(QObject):
    """온습도 센서 12개의 데이터를 관리하는 매니저 클래스"""
    
    # 센서 데이터 업데이트 시그널
    sensor_data_updated = pyqtSignal(str, dict)  # sensor_id, data
    all_sensors_updated = pyqtSignal(dict)  # all sensor data
    
    def __init__(self, serial_manager=None):
        super().__init__()
        self.serial_manager = serial_manager
        
        # 12개 센서 데이터 저장소
        self.sensor_data = {}
        for i in range(1, 13):
            sensor_id = f"ID{i:02d}"
            self.sensor_data[sensor_id] = {
                'temp': None,
                'humi': None,
                'status': 'unknown',
                'last_update': None
            }
        
        # 파싱 패턴
        self.data_pattern = re.compile(r'\[DSCT\]\s+(ID\d{2}),TEMP:\s*([\d.]+),\s*HUMI:\s*([\d.]+)')
        self.timeout_pattern = re.compile(r'\[DSCT\]\s+(ID\d{2}),Sensor Check TIMEOUT!')
        self.scan_complete_pattern = re.compile(r'\[DSCT\]\s*SEQUENTIAL SCAN COMPLETE:.*Total:\s*(\d+).*Success:\s*(\d+).*Error:\s*(\d+).*Time:\s*(\d+)ms')
        
        # 자동 갱신 타이머
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.request_sensor_data)
        self.auto_refresh_interval = 5000  # 5초
        
        # 스캔 진행 상태
        self.is_scanning = False
        
    def set_serial_manager(self, serial_manager):
        """시리얼 매니저 설정"""
        self.serial_manager = serial_manager
        
    def start_auto_refresh(self):
        """자동 갱신 시작"""
        if self.serial_manager and self.serial_manager.is_connection_healthy():
            self.auto_refresh_timer.start(self.auto_refresh_interval)
            self.request_sensor_data()  # 즉시 첫 요청
            
    def stop_auto_refresh(self):
        """자동 갱신 중지"""
        self.auto_refresh_timer.stop()
        
    def request_sensor_data(self):
        """센서 데이터 요청"""
        if self.serial_manager and self.serial_manager.is_connection_healthy():
            command = "$CMD,DSCT,TH"
            self.serial_manager.send_serial_command(command)
            self.is_scanning = True
            
    def parse_sensor_data(self, data):
        """시리얼 데이터 파싱"""
        if not self.is_scanning:
            return
            
        # 정상 데이터 파싱
        match = self.data_pattern.match(data)
        if match:
            sensor_id = match.group(1)
            temp = float(match.group(2))
            humi = float(match.group(3))
            
            self.sensor_data[sensor_id] = {
                'temp': temp,
                'humi': humi,
                'status': 'active',
                'last_update': datetime.now()
            }
            
            # 개별 센서 업데이트 시그널
            self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
            return
            
        # 타임아웃 파싱
        timeout_match = self.timeout_pattern.match(data)
        if timeout_match:
            sensor_id = timeout_match.group(1)
            
            self.sensor_data[sensor_id] = {
                'temp': None,
                'humi': None,
                'status': 'timeout',
                'last_update': datetime.now()
            }
            
            # 개별 센서 업데이트 시그널
            self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
            return
            
        # 스캔 완료 파싱
        complete_match = self.scan_complete_pattern.match(data)
        if complete_match:
            self.is_scanning = False
            # 전체 센서 데이터 업데이트 시그널
            self.all_sensors_updated.emit(self.sensor_data)
            
    def get_sensor_data(self, sensor_id):
        """특정 센서 데이터 반환"""
        return self.sensor_data.get(sensor_id, None)
        
    def get_all_sensor_data(self):
        """전체 센서 데이터 반환"""
        return self.sensor_data.copy()
        
    def reset_all_sensors(self):
        """모든 센서 데이터 초기화"""
        for sensor_id in self.sensor_data:
            self.sensor_data[sensor_id] = {
                'temp': None,
                'humi': None,
                'status': 'unknown',
                'last_update': None
            }
        self.all_sensors_updated.emit(self.sensor_data)