# AIRCON 온습도 센서 8개를 관리하는 매니저 클래스
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from datetime import datetime
import re
import os
import csv

class AirSensorManager(QObject):
    """AIRCON 온습도 센서 8개의 데이터를 관리하는 매니저 클래스"""
    
    # 센서 데이터 업데이트 시그널
    sensor_data_updated = pyqtSignal(str, dict)  # sensor_id, data
    all_sensors_updated = pyqtSignal(dict)  # all sensor data
    
    def __init__(self, serial_manager=None, test_mode=False):
        super().__init__()
        self.serial_manager = serial_manager
        self.test_mode = test_mode  # 테스트 모드 플래그
        print(f"[AIRCON] AirSensorManager 초기화 - test_mode: {test_mode}")
        
        # 6개 센서 데이터 저장소 (AIRCON은 6개만 사용)
        self.sensor_data = {}
        for i in range(1, 7):  # 1부터 6까지 (ID01~ID06)
            sensor_id = f"ID{i:02d}"
            self.sensor_data[sensor_id] = {
                'temp': None,
                'humi': None,
                'status': 'unknown',
                'last_update': None
            }
        
        # 파싱 패턴 ([AIRCON] 태그로 표준화)
        self.data_pattern = re.compile(r'\[AIRCON\]\s+(ID\d{2}),TEMP:\s*([\d.]+),\s*HUMI:\s*([\d.]+)')
        self.timeout_pattern = re.compile(r'\[AIRCON\]\s+(ID\d{2}),Sensor Check TIMEOUT!')
        self.scan_complete_pattern = re.compile(r'\[AIRCON\]\s*SEQUENTIAL SCAN COMPLETE:.*Total:\s*(\d+).*Success:\s*(\d+).*Error:\s*(\d+).*Time:\s*(\d+)ms')
        
        # 스캔 진행 상태
        self.is_scanning = False
        
        # 테스트 모드용 더미 데이터 생성기
        if self.test_mode:
            from test.dummy_air_sensor_generator import DummyAirSensorGenerator
            self.dummy_generator = DummyAirSensorGenerator()
        
        # CSV 저장 설정
        self.csv_enabled = True
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self._ensure_data_directory()
        
        # CSV 정리기 초기화
        from utils.csv_cleaner import CSVCleaner
        self.csv_cleaner = CSVCleaner(self.data_dir)
        self.save_count = 0  # 저장 횟수 카운터 (20회마다 정리)
        
    def set_serial_manager(self, serial_manager):
        """시리얼 매니저 설정 (자동 요청 제거, 스케줄러가 관리)"""
        self.serial_manager = serial_manager
        print("[AIRCON] 시리얼 매니저 설정 완료 (스케줄러 관리 모드)")
        
        
    def request_sensor_data(self):
        """센서 데이터 요청 (테스트 모드 지원)"""
        print(f"[AIRCON] request_sensor_data() 호출됨 - test_mode: {self.test_mode}")
        if self.test_mode:
            print("[AIRCON] 테스트 모드: 더미 센서 데이터 생성")
            self._generate_test_data()
            return
            
        if not self.serial_manager or not self.serial_manager.is_connected():
            print("[AIRCON] 시리얼 연결되지 않음")
            return
            
        print("[AIRCON] 센서 데이터 요청 전송: $CMD,AIR,TH")
        self.serial_manager.send_serial_command("$CMD,AIR,TH")
            
    def _generate_test_data(self):
        """테스트 모드용 더미 데이터 생성"""
        if not hasattr(self, 'dummy_generator'):
            print("[AIRCON] ERROR: dummy_generator 없음!")
            return
            
        try:
            # 더미 데이터 생성
            all_data = self.dummy_generator.generate_all_sensors_data()
            
            # 센서 데이터 저장 및 시그널 발생
            for sensor_data in all_data:
                sensor_id = sensor_data['sensor_id']
                
                if sensor_data['status'] == 'active':
                    self.sensor_data[sensor_id] = {
                        'temp': sensor_data['temp'],
                        'humi': sensor_data['humi'],
                        'status': 'active',
                        'last_update': sensor_data['timestamp']
                    }
                    
                    # CSV 저장
                    self._save_to_csv(sensor_id, self.sensor_data[sensor_id])
                    
                    print(f"[AIRCON TEST] {sensor_id} 더미 데이터: {sensor_data['temp']}°C, {sensor_data['humi']}%")
                else:
                    self.sensor_data[sensor_id] = {
                        'temp': None,
                        'humi': None,
                        'status': 'timeout',
                        'last_update': sensor_data['timestamp']
                    }
                    print(f"[AIRCON TEST] {sensor_id} 타임아웃 시뮬레이션")
                
                # 개별 센서 업데이트 시그널
                self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
            
            # 전체 센서 업데이트 시그널
            self.all_sensors_updated.emit(self.sensor_data.copy())
            print(f"[AIRCON TEST] 전체 센서 데이터 업데이트 완료: {len(self.sensor_data)}개")
            
        except Exception as e:
            print(f"[AIRCON TEST] 더미 데이터 생성 오류: {e}")

    def parse_sensor_data(self, data):
        """시리얼 데이터 파싱 (비활성화됨)"""
        print(f"[AIRCON RX] 데이터 파싱 비활성화로 건너뜀: {data}")
        return
            
        # 정상 데이터 파싱
        match = self.data_pattern.match(data)
        if match:
            sensor_id = match.group(1)
            temp = float(match.group(2))
            humi = float(match.group(3))
            
            # ID01~ID06만 처리 (ID07, ID08 무시)
            if sensor_id in self.sensor_data:
                print(f"[AIRCON RX] {sensor_id} 센서 데이터 파싱 성공: 온도={temp}°C, 습도={humi}%")
                
                self.sensor_data[sensor_id] = {
                    'temp': temp,
                    'humi': humi,
                    'status': 'active',
                    'last_update': datetime.now()
                }
                
                # CSV 저장
                self._save_to_csv(sensor_id, self.sensor_data[sensor_id])
                
                # 주기적 CSV 정리 (20회 저장마다)
                self.save_count += 1
                if self.save_count >= 20:
                    self.save_count = 0
                    self._cleanup_old_csv_files()
                
                # 개별 센서 업데이트 시그널
                self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
            else:
                print(f"[AIRCON RX] {sensor_id} 센서 무시됨 (ID07, ID08 제외됨)")
            return
            
        # 타임아웃 파싱
        timeout_match = self.timeout_pattern.match(data)
        if timeout_match:
            sensor_id = timeout_match.group(1)
            
            # ID01~ID06만 처리 (ID07, ID08 무시)
            if sensor_id in self.sensor_data:
                print(f"[AIRCON RX] {sensor_id} 센서 타임아웃 파싱")
                
                self.sensor_data[sensor_id] = {
                    'temp': None,
                    'humi': None,
                    'status': 'timeout',
                    'last_update': datetime.now()
                }
                
                # 개별 센서 업데이트 시그널
                self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
            else:
                print(f"[AIRCON RX] {sensor_id} 센서 타임아웃 무시됨 (ID07, ID08 제외됨)")
            return
            
        # 스캔 완료 파싱
        complete_match = self.scan_complete_pattern.match(data)
        if complete_match:
            total = complete_match.group(1)
            success = complete_match.group(2)
            error = complete_match.group(3)
            time_ms = complete_match.group(4)
            
            print(f"[AIRCON RX] 스캔 완료: 총 {total}개, 성공 {success}개, 오류 {error}개, 소요시간 {time_ms}ms")
            
            self.is_scanning = False
            # 전체 센서 데이터 업데이트 시그널
            self.all_sensors_updated.emit(self.sensor_data)
            return
            
        # 기타 메시지 로그
        if '[AIRCON]' in data:
            print(f"[AIRCON RX] 기타 메시지: {data}")
        else:
            print(f"[AIRCON RX] 파싱되지 않은 데이터: {data}")
    
    def _ensure_data_directory(self):
        """데이터 디렉토리 확인 및 생성"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_csv_filename(self):
        """현재 날짜와 파일 크기를 고려하여 CSV 파일명 생성"""
        today = datetime.now().strftime('%Y-%m-%d')
        base_filename = f'AIRCON_{today}'
        
        # 기존 파일들 확인
        file_index = 0
        while True:
            if file_index == 0:
                filename = os.path.join(self.data_dir, f'{base_filename}.csv')
            else:
                filename = os.path.join(self.data_dir, f'{base_filename}_{file_index:03d}.csv')
            
            # 파일이 없으면 이 파일명 사용
            if not os.path.exists(filename):
                return filename
            
            # 파일 크기 확인 (10MB = 10 * 1024 * 1024 bytes)
            file_size = os.path.getsize(filename)
            if file_size < 10 * 1024 * 1024:  # 10MB 미만이면 이 파일 사용
                return filename
            
            # 10MB 이상이면 다음 인덱스로
            file_index += 1
    
    def _save_to_csv(self, sensor_id, data):
        """센서 데이터를 CSV 파일로 저장"""
        if not self.csv_enabled or data['status'] != 'active':
            return
            
        # 적절한 파일명 가져오기
        filename = self._get_csv_filename()
        
        # 파일이 없으면 헤더 작성
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'sensor_id', 'temperature', 'humidity']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': data['last_update'].strftime('%Y-%m-%d %H:%M:%S'),
                'sensor_id': sensor_id,
                'temperature': data['temp'],
                'humidity': data['humi']
            })
    
    def _cleanup_old_csv_files(self):
        """오래된 CSV 파일 정리 (AIRCON 파일만)"""
        try:
            _, aircon_deleted = self.csv_cleaner.auto_cleanup(max_files=20)
            if aircon_deleted:
                print(f"[AIRCON] CSV 정리 완료: {len(aircon_deleted)}개 파일 삭제")
        except Exception as e:
            print(f"[AIRCON] CSV 정리 중 오류: {e}")
    
    def _generate_dummy_data(self):
        """테스트 모드: 더미 데이터 생성 및 처리"""
        if not hasattr(self, 'dummy_generator'):
            return
            
        # 모든 센서의 더미 데이터 생성
        all_data = self.dummy_generator.generate_all_sensors_data()
        
        # 각 센서 데이터 처리
        for data in all_data:
            sensor_id = data['sensor_id']
            
            if data['status'] == 'active':
                self.sensor_data[sensor_id] = {
                    'temp': data['temp'],
                    'humi': data['humi'],
                    'status': 'active',
                    'last_update': data['timestamp']
                }
            else:
                self.sensor_data[sensor_id] = {
                    'temp': None,
                    'humi': None,
                    'status': 'timeout',
                    'last_update': data['timestamp']
                }
            
            # CSV 저장
            self._save_to_csv(sensor_id, self.sensor_data[sensor_id])
            
            # 개별 센서 업데이트 시그널
            self.sensor_data_updated.emit(sensor_id, self.sensor_data[sensor_id])
        
        # 스캔 완료 처리
        self.is_scanning = False
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