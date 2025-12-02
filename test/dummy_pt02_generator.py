import random
from datetime import datetime
from typing import Dict


class DummyPT02Generator:
    """PT02 센서의 가상 데이터를 생성하는 클래스

    PT02 센서는 1분 주기로 온도, CO2, PM2.5 데이터를 전송합니다.
    테스트 모드에서 실제 센서 없이 개발/테스트할 수 있도록 합니다.
    """

    def __init__(self):
        # 기준값 설정 (실제 환경과 유사하게)
        self.base_values = {
            'temp_base': random.uniform(22.0, 26.0),    # 기준 온도 22-26도
            'temp_variation': 1.0,                       # 온도 변동폭 ±1도
            'co2_base': random.uniform(600, 900),        # 기준 CO2 600-900ppm
            'co2_variation': 100,                        # CO2 변동폭 ±100ppm
            'pm25_base': random.uniform(15, 35),         # 기준 PM2.5 15-35µg/m³
            'pm25_variation': 10                         # PM2.5 변동폭 ±10µg/m³
        }

        # 트렌드 시뮬레이션 (시간에 따른 자연스러운 변화)
        self.trend_direction = {
            'temp': random.choice([-1, 1]),
            'co2': random.choice([-1, 1]),
            'pm25': random.choice([-1, 1])
        }
        self.trend_counter = 0

    def generate_data(self) -> Dict:
        """PT02 센서 데이터 생성

        Returns:
            dict: {temp, co2, pm25, timestamp}
        """
        # 트렌드 업데이트 (약 10회마다 방향 변경)
        self.trend_counter += 1
        if self.trend_counter >= 10:
            self.trend_counter = 0
            for key in self.trend_direction:
                if random.random() < 0.3:  # 30% 확률로 방향 변경
                    self.trend_direction[key] *= -1

        # 온도 생성 (자연스러운 변동)
        temp_drift = self.trend_direction['temp'] * random.uniform(0, 0.2)
        self.base_values['temp_base'] = max(18.0, min(32.0,
            self.base_values['temp_base'] + temp_drift))
        temp = self.base_values['temp_base'] + random.uniform(
            -self.base_values['temp_variation'],
            self.base_values['temp_variation']
        )
        temp = max(15.0, min(35.0, temp))  # 범위 제한

        # CO2 생성
        co2_drift = self.trend_direction['co2'] * random.uniform(0, 20)
        self.base_values['co2_base'] = max(400, min(1500,
            self.base_values['co2_base'] + co2_drift))
        co2 = self.base_values['co2_base'] + random.uniform(
            -self.base_values['co2_variation'],
            self.base_values['co2_variation']
        )
        co2 = int(max(400, min(2000, co2)))  # 범위 제한

        # PM2.5 생성
        pm25_drift = self.trend_direction['pm25'] * random.uniform(0, 3)
        self.base_values['pm25_base'] = max(5, min(80,
            self.base_values['pm25_base'] + pm25_drift))
        pm25 = self.base_values['pm25_base'] + random.uniform(
            -self.base_values['pm25_variation'],
            self.base_values['pm25_variation']
        )
        pm25 = int(max(0, min(100, pm25)))  # 범위 제한

        return {
            'temp': round(temp, 1),
            'co2': co2,
            'pm25': pm25,
            'timestamp': datetime.now()
        }

    def format_aircon_response(self, data: Dict = None) -> str:
        """AIRCON 프로토콜 형식으로 응답 포맷

        형식: [AIRCON] CO2,PM2.5,TEMP (온도는 10배)
        예: [AIRCON] 850,35,253

        Args:
            data: 센서 데이터 (없으면 새로 생성)

        Returns:
            str: 시리얼 응답 형식 문자열
        """
        if data is None:
            data = self.generate_data()

        temp_int = int(data['temp'] * 10)  # 온도는 10배로 인코딩
        return f"[AIRCON] {data['co2']},{data['pm25']},{temp_int}"

    def simulate_serial_response(self) -> str:
        """시리얼 통신 응답 시뮬레이션

        Returns:
            str: 시리얼 응답 문자열
        """
        return self.format_aircon_response()
