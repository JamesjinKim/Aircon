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
        
        # 연결 상태 관리
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
                timeout=0.01 #짧은 timeout (10ms) - UI 멈춤 방지하면서 완전한 라인 대기
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
        """짧은 timeout을 가진 readline 방식으로 UI 멈춤 방지하면서 완전한 라인 읽기"""
        try:
            if not self.shinho_serial_connection:
                return None
            if not self.shinho_serial_connection.is_open:
                return None
            
            # 데이터가 있는지 확인
            if self.shinho_serial_connection.in_waiting:
                print(f"[RX LOG] {time.time():.4f} - in_waiting: {self.shinho_serial_connection.in_waiting} bytes")
                
                # 원본 방식: readline()으로 완전한 라인 읽기 (짧은 timeout으로 UI 멈춤 방지)
                raw_data = self.shinho_serial_connection.readline()
                print(f"[RX RAW] 수신된 원본 바이트: {raw_data}")
                print(f"[RX RAW] 바이트 길이: {len(raw_data)}")
                
                # 디코딩 시도
                try:
                    decoded_data = raw_data.decode('ascii').strip()
                    print(f"[RX DECODED] 디코딩된 데이터: '{decoded_data}'")
                    print(f"[RX DECODED] 디코딩 길이: {len(decoded_data)}")
                except UnicodeDecodeError as decode_error:
                    print(f"[RX ERROR] 디코딩 실패: {decode_error}")
                    # UTF-8로 재시도
                    try:
                        decoded_data = raw_data.decode('utf-8').strip()
                        print(f"[RX UTF8] UTF-8 디코딩 성공: '{decoded_data}'")
                    except:
                        decoded_data = str(raw_data)
                        print(f"[RX FALLBACK] 바이트 문자열로 처리: {decoded_data}")
                
                # 빈 문자열도 로그 출력
                if not decoded_data:
                    print("[RX] 빈 문자열 수신됨")
                    return None
                
                # 센서 데이터 체크 및 콜백 호출 - 원본 로직 복원
                print(f"[RX CALLBACK] 센서 데이터 콜백 체크 중: '{decoded_data}'")
                
                # DSCT 센서 데이터 처리
                if '[DSCT]' in decoded_data and self.sensor_data_callback:
                    print(f"[RX CALLBACK] DSCT 콜백 호출")
                    self.sensor_data_callback(decoded_data)
                
                # AIR/AIRCON 센서 데이터 처리
                elif ('[AIR]' in decoded_data or '[AIRCON]' in decoded_data) and self.air_sensor_data_callback:
                    print(f"[RX CALLBACK] AIR/AIRCON 콜백 호출")
                    self.air_sensor_data_callback(decoded_data)
                
                else:
                    print(f"[RX CALLBACK] 콜백 조건 미충족 - DSCT: {('[DSCT]' in decoded_data, self.sensor_data_callback is not None)}, AIR: {('[AIR]' in decoded_data or '[AIRCON]' in decoded_data, self.air_sensor_data_callback is not None)}")
                
                return decoded_data
            else:
                # 대기 중인 데이터가 없음
                return None
                
        except Exception as e:
            print(f"[RX ERROR] 시리얼 데이터 읽기 오류: {e}")
            return None 

    def disconnect_serial(self) -> None:
        """시리얼 포트 닫기 함수, 연결 종료"""
        try:
            if self.shinho_serial_connection and self.shinho_serial_connection.is_open:
                self.shinho_serial_connection.close()
                print("Serial port closed.")
        except Exception as e:
            print(f"Disconnect error: {e}")
    
    def is_connection_healthy(self) -> bool:
        """연결 상태가 건강한지 확인 (포트 열림 상태만 체크)"""
        return self.is_connected() and self.connection_healthy
    
    def send_serial_command(self, command):
        """시리얼 명령 전송 함수 (종료 문자 자동 추가)"""
        if self.is_connected():
            full_command = f"{command}\r\n"
            result = self.send_data(full_command)
            if result:
                print(f"[TX] 시리얼 명령 전송: {command} (with <CR><LF>)")
            else:
                print(f"[TX ERROR] 시리얼 명령 전송 실패: {command}")
            return result
        else:
            print(f"[TX ERROR] 시리얼 연결 안됨, 명령 전송 실패: {command}")
        return False
    
    def set_sensor_data_callback(self, callback):
        """센서 데이터 수신 콜백 설정"""
        self.sensor_data_callback = callback
    
    def set_air_sensor_data_callback(self, callback):
        """AIR 센서 데이터 수신 콜백 설정"""
        self.air_sensor_data_callback = callback