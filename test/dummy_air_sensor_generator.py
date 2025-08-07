import random
import time
from datetime import datetime
from typing import Dict, List

class DummyAirSensorGenerator:
    """AIRCON용 가상의 온습도 센서 데이터를 생성하는 클래스"""
    
    def __init__(self):
        # 센서별 기준값 설정 (실제 센서처럼 각각 다른 특성을 가지도록)
        self.sensor_base_values = {}
        for i in range(6):  # AIRCON은 6개 센서만 사용 (ID01~ID06)
            sensor_id = f"ID{i+1:02d}"
            self.sensor_base_values[sensor_id] = {
                'temp_base': random.uniform(25.0, 30.0),  # 기준 온도 25-30도 (에어컨 환경)
                'humi_base': random.uniform(65.0, 75.0),  # 기준 습도 65-75%
                'temp_variation': random.uniform(0.3, 1.0),  # 온도 변동폭 (작게)
                'humi_variation': random.uniform(1.0, 3.0),  # 습도 변동폭 (작게)
                'error_rate': 0.0  # 모든 센서 정상 작동 (ID07, ID08 제거됨)
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
        temp = max(15.0, min(35.0, temp))  # 15-35도 (에어컨 환경)
        humi = max(30.0, min(90.0, humi))  # 30-90%
        
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
    
    def format_air_response(self, sensor_data: Dict) -> str:
        """AIR 프로토콜 형식으로 응답 포맷"""
        if sensor_data['status'] == 'active':
            # [AIR] ID01,TEMP: 28.3, HUMI: 67.7 형식
            return f"[AIR] {sensor_data['sensor_id']},TEMP: {sensor_data['temp']}, HUMI: {sensor_data['humi']}"
        else:
            return f"[AIR] {sensor_data['sensor_id']},Sensor Check TIMEOUT!"
    
    def simulate_serial_responses(self) -> List[str]:
        """시리얼 통신 응답 시뮬레이션"""
        responses = []
        
        # 스캔 시작 메시지
        responses.append("[AIR] Temp/Humi SCAN START!")
        
        all_data = self.generate_all_sensors_data()
        
        success_count = 0
        error_count = 0
        
        for data in all_data:
            response = self.format_air_response(data)
            responses.append(response)
            
            if data['status'] == 'active':
                success_count += 1
            else:
                error_count += 1
        
        # 스캔 완료 메시지
        total = len(all_data)
        scan_time = random.randint(5000, 6000)  # 5-6초 (센서 6개로 줄어서 시간 단축)
        complete_msg = f"[AIR] SEQUENTIAL SCAN COMPLETE: Total: {total}, Success: {success_count}, Error: {error_count}, Time: {scan_time}ms"
        responses.append(complete_msg)
            
        return responses