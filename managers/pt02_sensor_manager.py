# PT02 센서 데이터 관리 매니저 클래스
# 1분 주기 PT02 센서 데이터(온도, CO2, PM2.5)를 CSV 파일로 저장
from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
import os
import csv


class PT02SensorManager(QObject):
    """PT02 센서 데이터를 관리하고 CSV로 저장하는 매니저 클래스"""

    # 센서 데이터 업데이트 시그널
    sensor_data_updated = pyqtSignal(dict)  # {temp, co2, pm25, humidity, timestamp}

    def __init__(self, test_mode=False):
        super().__init__()
        self.test_mode = test_mode
        print(f"[PT02] PT02SensorManager 초기화 - test_mode: {test_mode}")

        # 센서 데이터 저장소
        self.sensor_data = {
            'temp': None,      # 온도 (°C)
            'co2': None,       # CO2 (ppm)
            'pm25': None,      # PM2.5 (µg/m³)
            'humidity': None,  # 습도 (%)
            'status': 'unknown',
            'last_update': None
        }

        # CSV 저장 설정
        self.csv_enabled = True
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        self._ensure_data_directory()

        # CSV 정리기 초기화
        from utils.csv_cleaner import CSVCleaner
        self.csv_cleaner = CSVCleaner(self.data_dir)
        self.save_count = 0  # 저장 횟수 카운터 (50회마다 정리 - 1분 주기이므로 약 50분)

        # 테스트 모드용 더미 데이터 생성기
        if self.test_mode:
            from test.dummy_pt02_generator import DummyPT02Generator
            self.dummy_generator = DummyPT02Generator()

    def _ensure_data_directory(self):
        """데이터 디렉토리 확인 및 생성"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            print(f"[PT02] 데이터 디렉토리 생성: {self.data_dir}")

    def _get_csv_filename(self):
        """현재 날짜와 파일 크기를 고려하여 CSV 파일명 생성

        파일명 형식: PT02_YYYY-MM-DD.csv
        10MB 초과 시: PT02_YYYY-MM-DD_001.csv, PT02_YYYY-MM-DD_002.csv, ...
        """
        today = datetime.now().strftime('%Y-%m-%d')
        base_filename = f'PT02_{today}'

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

    def save_sensor_data(self, temp, co2, pm25, humidity=None):
        """센서 데이터를 내부 저장소에 저장하고 CSV에 기록

        Args:
            temp: 온도 (°C)
            co2: CO2 농도 (ppm)
            pm25: PM2.5 농도 (µg/m³)
            humidity: 습도 (%) - 선택적
        """
        timestamp = datetime.now()

        # 내부 데이터 업데이트
        self.sensor_data = {
            'temp': temp,
            'co2': co2,
            'pm25': pm25,
            'humidity': humidity,
            'status': 'active',
            'last_update': timestamp
        }

        # CSV 파일에 저장
        self._save_to_csv(temp, co2, pm25, humidity, timestamp)

        # 주기적 CSV 정리 (50회 저장마다, 약 50분)
        self.save_count += 1
        if self.save_count >= 50:
            self.save_count = 0
            self._cleanup_old_csv_files()

        # 시그널 발생
        self.sensor_data_updated.emit(self.sensor_data.copy())

        if humidity is not None:
            print(f"[PT02] 데이터 저장: 온도={temp}°C, CO2={co2}ppm, PM2.5={pm25}µg/m³, 습도={humidity}%")
        else:
            print(f"[PT02] 데이터 저장: 온도={temp}°C, CO2={co2}ppm, PM2.5={pm25}µg/m³")

    def _save_to_csv(self, temp, co2, pm25, humidity, timestamp):
        """센서 데이터를 CSV 파일로 저장"""
        if not self.csv_enabled:
            return

        # 적절한 파일명 가져오기
        filename = self._get_csv_filename()

        # 파일이 없으면 헤더 작성
        file_exists = os.path.exists(filename)

        try:
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['timestamp', 'temperature', 'co2', 'pm25', 'humidity']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if not file_exists:
                    writer.writeheader()
                    print(f"[PT02] 새 CSV 파일 생성: {filename}")

                writer.writerow({
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': temp,
                    'co2': co2,
                    'pm25': pm25,
                    'humidity': humidity if humidity is not None else ''
                })
        except Exception as e:
            print(f"[PT02] CSV 저장 오류: {e}")

    def _cleanup_old_csv_files(self):
        """오래된 CSV 파일 정리 (PT02 파일만)"""
        try:
            # CSVCleaner를 사용하여 오래된 파일 정리
            # PT02 파일은 max_files=30 (약 1달치)
            deleted_files = self._cleanup_pt02_files(max_files=30)
            if deleted_files:
                print(f"[PT02] CSV 정리 완료: {len(deleted_files)}개 파일 삭제")
        except Exception as e:
            print(f"[PT02] CSV 정리 중 오류: {e}")

    def _cleanup_pt02_files(self, max_files=30):
        """PT02 CSV 파일만 정리"""
        deleted = []
        try:
            # PT02_ 로 시작하는 CSV 파일 목록
            pt02_files = []
            for f in os.listdir(self.data_dir):
                if f.startswith('PT02_') and f.endswith('.csv'):
                    filepath = os.path.join(self.data_dir, f)
                    pt02_files.append((filepath, os.path.getmtime(filepath)))

            # 수정 시간 기준 정렬 (오래된 것 먼저)
            pt02_files.sort(key=lambda x: x[1])

            # max_files 초과분 삭제
            while len(pt02_files) > max_files:
                filepath, _ = pt02_files.pop(0)
                os.remove(filepath)
                deleted.append(filepath)
                print(f"[PT02] 오래된 파일 삭제: {filepath}")

        except Exception as e:
            print(f"[PT02] 파일 정리 중 오류: {e}")

        return deleted

    def parse_pt02_response(self, data):
        """PT02 센서 응답 데이터 파싱 (통합)

        지원 형식:
        1. PT02 CO2,PM2.5,온도,습도 (예: PT02 587,0,13.3,10.9)
        2. [AIRCON] CO2,PM2.5,TEMP (예: [AIRCON] 850,35,253) - 레거시

        Args:
            data: 시리얼로 수신된 원시 데이터

        Returns:
            bool: 파싱 성공 여부
        """
        try:
            # 형식 1: PT02 CO2,PM2.5,온도,습도 (1분 주기 데이터)
            if data.startswith("PT02 ") or data.startswith("PT02\t"):
                return self._parse_pt02_format(data)

            # 형식 2: [AIRCON] CO2,PM2.5,TEMP (레거시)
            if "[AIRCON]" in data:
                return self._parse_aircon_format(data)

        except Exception as e:
            print(f"[PT02] 응답 파싱 오류: {e}")

        return False

    def _parse_pt02_format(self, data):
        """PT02 형식 파싱: PT02 CO2,PM2.5,온도,습도

        예시: PT02 587,0,13.3,10.9
        """
        try:
            # "PT02 " 이후 데이터 추출
            parts = data.split("PT02")[1].strip()
            values = parts.split(",")

            if len(values) >= 3:
                co2 = int(values[0].strip())
                pm25 = int(values[1].strip())
                temp = float(values[2].strip())
                humidity = float(values[3].strip()) if len(values) >= 4 else None

                # 데이터 저장 및 CSV 기록
                self.save_sensor_data(temp, co2, pm25, humidity)
                return True

        except Exception as e:
            print(f"[PT02] PT02 형식 파싱 오류: {e}, data='{data}'")

        return False

    def _parse_aircon_format(self, data):
        """[AIRCON] 형식 파싱 (레거시): [AIRCON] CO2,PM2.5,TEMP

        예시: [AIRCON] 850,35,253 (온도는 10배 값)
        """
        try:
            # [AIRCON] 이후 데이터 추출
            parts = data.split("[AIRCON]")[1].strip()
            values = parts.split(",")

            if len(values) >= 3:
                co2 = int(values[0].strip())
                pm25 = int(values[1].strip())
                temp = float(values[2].strip()) / 10.0  # 온도는 10으로 나눔

                # 데이터 저장 및 CSV 기록 (습도 없음)
                self.save_sensor_data(temp, co2, pm25, None)
                return True

        except Exception as e:
            print(f"[PT02] AIRCON 형식 파싱 오류: {e}")

        return False

    def generate_test_data(self):
        """테스트 모드용 더미 데이터 생성"""
        if not self.test_mode:
            print("[PT02] 테스트 모드가 아닙니다")
            return

        if not hasattr(self, 'dummy_generator'):
            print("[PT02] ERROR: dummy_generator 없음!")
            return

        try:
            # 더미 데이터 생성
            data = self.dummy_generator.generate_data()

            # 데이터 저장
            self.save_sensor_data(data['temp'], data['co2'], data['pm25'])
            print(f"[PT02 TEST] 더미 데이터: 온도={data['temp']}°C, CO2={data['co2']}ppm, PM2.5={data['pm25']}µg/m³")

        except Exception as e:
            print(f"[PT02 TEST] 더미 데이터 생성 오류: {e}")

    def get_sensor_data(self):
        """현재 센서 데이터 반환"""
        return self.sensor_data.copy()

    def get_latest_values(self):
        """최신 센서 값만 반환 (temp, co2, pm25)"""
        return {
            'temp': self.sensor_data['temp'],
            'co2': self.sensor_data['co2'],
            'pm25': self.sensor_data['pm25']
        }

    def reset_sensor_data(self):
        """센서 데이터 초기화"""
        self.sensor_data = {
            'temp': None,
            'co2': None,
            'pm25': None,
            'status': 'unknown',
            'last_update': None
        }
        print("[PT02] 센서 데이터 초기화")

    def enable_csv_logging(self, enabled=True):
        """CSV 로깅 활성화/비활성화"""
        self.csv_enabled = enabled
        print(f"[PT02] CSV 로깅: {'활성화' if enabled else '비활성화'}")

    def get_csv_file_info(self):
        """현재 CSV 파일 정보 반환"""
        filename = self._get_csv_filename()
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filename))
            return {
                'filename': os.path.basename(filename),
                'path': filename,
                'size_bytes': size,
                'size_kb': size / 1024,
                'last_modified': mtime
            }
        return {
            'filename': os.path.basename(filename),
            'path': filename,
            'size_bytes': 0,
            'size_kb': 0,
            'last_modified': None
        }
