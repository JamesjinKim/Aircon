import os
import serial
import serial.tools.list_ports
import time
from typing import Optional, List, Dict

class SerialManager:
    def __init__(self):
        # 시리얼 연결 객체, 연결 전이나 연결 해제 시 None으로, 연결 성공 시 Serial 객체로 설정 
        self.shinho_serial_connection: Optional[serial.Serial] = None
        self.supported_baudrates = [9600, 14400, 19200, 28800, 38400, 57600, 115200]
        
        # 하트비트 관련 변수
        self.last_heartbeat_time = 0
        self.heartbeat_timeout = 10.0  # 10초 타임아웃
        self.connection_healthy = True
        
        # 센서 데이터 콜백
        self.sensor_data_callback = None
        self.air_sensor_data_callback = None

    def get_available_ports(self) -> List[Dict[str, str]]:
        """연결 가능한 시리얼 포트 목록을 반환하는 함수"""
        ports = serial.tools.list_ports.comports()
        return [{ 
            "device": port.device, #포트 이름, COM2
            "description": port.description, #포트 설명, USB Serial Port
        } for port in ports]
        
    def connect_serial(self, port: str, baudrate: int = 115200) -> bool:
        """지정된 포트와 보레이트로 시리얼 연결 시도하는 함수"""
        try:
            #기존 연결 
            if self.shinho_serial_connection and self.shinho_serial_connection.is_open:
                self.shinho_serial_connection.close() # 새 연결 전에 기존 연결 닫기 
            
            #새 연결 시도 
            self.shinho_serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1 #읽기 시도 시 대기 시간(초)
            )
            print(f"Serial port connected to {port}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
        
    def is_connected(self) -> bool:
        """현재 시리얼 포트 연결 상태를 확인하는 함수"""
        return self.shinho_serial_connection and self.shinho_serial_connection.is_open
        
    def send_data(self, data: str) -> bool:
        """데이터 전송 함수"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                raise Exception("Serial port is not connected")
            
            self.shinho_serial_connection.write(data.encode('ascii'))
            # 하트비트 업데이트 비활성화 (정상 연결 끊김 문제 해결)
            # self.update_heartbeat()
            return True
        except Exception as e:
            print(f"Error sending serial data: {e}")
            return False 

    def read_data(self) -> Optional[str]:
        """데이터 읽기(수신) 함수 / 시리얼 포트로부터 데이터를 읽어옴"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                raise Exception("Serial port is not connected")
            
            if self.shinho_serial_connection.in_waiting:
                data = self.shinho_serial_connection.readline()
                decoded_data = data.decode('ascii').strip()
                
                # 센서 데이터 체크 및 콜백 호출
                if self.sensor_data_callback and decoded_data:
                    if '[DSCT]' in decoded_data:
                        self.sensor_data_callback(decoded_data)
                    elif '[AIR]' in decoded_data and hasattr(self, 'air_sensor_data_callback'):
                        self.air_sensor_data_callback(decoded_data)
                
                return decoded_data
            return None
        except Exception as e:
            print(f"Error reading serial data: {e}")
            return None 

    def disconnect_serial(self) -> None:
        """시리얼 포트 닫기 함수, 연결 종료"""
        try:
            if self.shinho_serial_connection and self.shinho_serial_connection.is_open:
                self.shinho_serial_connection.close()
                print("Serial port closed.")
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    def update_heartbeat(self):
        """하트비트 업데이트 - 정상 통신 시 호출"""
        self.last_heartbeat_time = time.time()
        self.connection_healthy = True
    
    def check_heartbeat_timeout(self) -> bool:
        """하트비트 타임아웃 체크 - 연결 상태 확인"""
        if self.last_heartbeat_time == 0:
            return True  # 아직 하트비트 시작 안함 (연결 직후)
        
        current_time = time.time()
        time_since_last_heartbeat = current_time - self.last_heartbeat_time
        
        # 연결 후 충분한 시간(5초) 경과 후에만 타임아웃 체크
        if time_since_last_heartbeat > 5.0 and time_since_last_heartbeat > self.heartbeat_timeout:
            if self.connection_healthy:  # 처음 타임아웃 감지 시에만 로그
                print(f"하트비트 타임아웃: {time_since_last_heartbeat:.1f}초 무활동")
            self.connection_healthy = False
            return False
        
        return True
    
    def is_connection_healthy(self) -> bool:
        """연결 상태가 건강한지 확인 (포트 열림 + 하트비트 정상)"""
        return (self.is_connected() and 
                self.connection_healthy and 
                self.check_heartbeat_timeout())
    
    def send_serial_command(self, command):
        """시리얼 명령 전송 함수 (종료 문자 자동 추가)"""
        if self.is_connected():
            full_command = f"{command}\r"
            return self.send_data(full_command)
        return False
    
    def set_sensor_data_callback(self, callback):
        """센서 데이터 수신 콜백 설정"""
        self.sensor_data_callback = callback
    
    def set_air_sensor_data_callback(self, callback):
        """AIR 센서 데이터 수신 콜백 설정"""
        self.air_sensor_data_callback = callback