import random
import time
from datetime import datetime
from typing import Dict, List

class DummySensorGenerator:
    """가상의 온습도 센서 데이터를 생성하는 클래스"""
    
    def __init__(self):
        # 센서별 기준값 설정 (실제 센서처럼 각각 다른 특성을 가지도록)
        self.sensor_base_values = {}
        for i in range(12):
            sensor_id = f"ID{i+1:02d}"
            self.sensor_base_values[sensor_id] = {
                'temp_base': random.uniform(20.0, 25.0),  # 기준 온도 20-25도
                'humi_base': random.uniform(40.0, 60.0),  # 기준 습도 40-60%
                'temp_variation': random.uniform(0.5, 2.0),  # 온도 변동폭
                'humi_variation': random.uniform(2.0, 5.0),  # 습도 변동폭
                'error_rate': random.uniform(0.0, 0.1)  # 0-10% 오류율
            }
    
    def generate_sensor_data(self, sensor_id: str) -> Dict:
        """특정 센서의 데이터 생성"""
        if sensor_id not in self.sensor_base_values:
            return None
            
        base = self.sensor_base_values[sensor_id]
        
        # 오류 발생 여부 결정
        if random.random() < base['error_rate']:
            return {
                'sensor_id': sensor_id,
                'status': 'timeout',
                'temp': None,
                'humi': None,
                'timestamp': datetime.now()
            }
        
        # 정상 데이터 생성 (기준값에서 약간의 변동)
        temp = base['temp_base'] + random.uniform(-base['temp_variation'], base['temp_variation'])
        humi = base['humi_base'] + random.uniform(-base['humi_variation'], base['humi_variation'])
        
        # 범위 제한
        temp = max(0.0, min(50.0, temp))  # 0-50도
        humi = max(0.0, min(100.0, humi))  # 0-100%
        
        return {
            'sensor_id': sensor_id,
            'status': 'active',
            'temp': round(temp, 1),
            'humi': round(humi, 1),
            'timestamp': datetime.now()
        }
    
    def generate_all_sensors_data(self) -> List[Dict]:
        """모든 센서의 데이터 생성"""
        data_list = []
        for sensor_id in self.sensor_base_values.keys():
            data = self.generate_sensor_data(sensor_id)
            if data:
                data_list.append(data)
                # 실제 센서처럼 약간의 지연 추가
                time.sleep(random.uniform(0.01, 0.05))
        return data_list
    
    def format_dsct_response(self, sensor_data: Dict) -> str:
        """DSCT 프로토콜 형식으로 응답 포맷"""
        if sensor_data['status'] == 'active':
            # [DSCT]ID00 TH:012D01F3,OK형식
            temp_hex = format(int(sensor_data['temp'] * 10), '04X')
            humi_hex = format(int(sensor_data['humi'] * 10), '04X')
            return f"[DSCT]{sensor_data['sensor_id']} TH:{temp_hex}{humi_hex},OK"
        else:
            return f"[DSCT]{sensor_data['sensor_id']} TH:,ERROR_TIMEOUT"
    
    def simulate_serial_responses(self) -> List[str]:
        """시리얼 통신 응답 시뮬레이션"""
        responses = []
        all_data = self.generate_all_sensors_data()
        
        for data in all_data:
            response = self.format_dsct_response(data)
            responses.append(response)
            
        return responses