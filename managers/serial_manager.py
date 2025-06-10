import os
import serial
import serial.tools.list_ports
from typing import Optional, List, Dict

class SerialManager:
    def __init__(self):
        # 시리얼 연결 객체, 연결 전이나 연결 해제 시 None으로, 연결 성공 시 Serial 객체로 설정 
        self.shinho_serial_connection: Optional[serial.Serial] = None
        self.supported_baudrates = [9600, 14400, 19200, 28800, 38400, 57600, 115200]

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
                return data.decode('ascii').strip()
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