import os
import serial
import serial.tools.list_ports
import time
from typing import Optional, List, Dict
from PyQt5.QtCore import QObject, pyqtSignal, QSocketNotifier

class SerialManager(QObject):
    # 데이터 수신 시그널
    data_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # 시리얼 연결 객체, 연결 전이나 연결 해제 시 None으로, 연결 성공 시 Serial 객체로 설정 
        self.shinho_serial_connection: Optional[serial.Serial] = None
        self.supported_baudrates = [9600, 14400, 19200, 28800, 38400, 57600, 115200]
        
        # 연결 상태 관리
        self.connection_healthy = True
        
        # 센서 데이터 콜백 (레거시 호환성)
        self.sensor_data_callback = None
        self.air_sensor_data_callback = None
        
        # 소켓 알림자 (인터럽트 방식)
        self.socket_notifier: Optional[QSocketNotifier] = None

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
            # 기존 연결 해제
            self.disconnect_serial()
            
            # 새 연결 시도 
            self.shinho_serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1  # 논블로킹에 가까운 타임아웃
            )
            
            # 인터럽트 방식 설정 (Unix 계열에서만 가능)
            if hasattr(self.shinho_serial_connection, 'fileno'):
                try:
                    fd = self.shinho_serial_connection.fileno()
                    self.socket_notifier = QSocketNotifier(fd, QSocketNotifier.Read)
                    self.socket_notifier.activated.connect(self._on_data_ready)
                    self.socket_notifier.setEnabled(True)
                    print(f"[SERIAL] 인터럽트 방식 활성화 (fd: {fd})")
                except Exception as e:
                    print(f"[SERIAL] 인터럽트 방식 설정 실패, 폴링 방식 유지: {e}")
            
            print("Serial port connected to", port)
            return True
        except Exception as e:
            print("Connection error:", e)
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
            print("Error sending serial data:", e)
            return False 

    def read_data(self) -> Optional[str]:
        """데이터 읽기(수신) 함수 / 시리얼 포트로부터 데이터를 읽어옴"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                return None
            
            # 대기 중인 데이터가 없으면 즉시 반환
            if not self.shinho_serial_connection.in_waiting:
                return None
                
            # 대기 중인 데이터가 있을 때만 읽기 시도
            raw_data = self.shinho_serial_connection.readline()
            if not raw_data:
                return None
                
            print("[RX RAW] 수신된 원본 바이트: %s" % raw_data)
            print("[RX RAW] 바이트 길이: %d" % len(raw_data))
            
            # 디코딩 시도
            try:
                decoded_data = raw_data.decode('ascii').strip()
                print("[RX DECODED] 디코딩된 데이터: '%s'" % decoded_data)
                print("[RX DECODED] 디코딩 길이: %d" % len(decoded_data))
            except UnicodeDecodeError as decode_error:
                print("[RX ERROR] 디코딩 실패: %s" % decode_error)
                # UTF-8로 재시도
                try:
                    decoded_data = raw_data.decode('utf-8').strip()
                    print("[RX UTF8] UTF-8 디코딩 성공: '%s'" % decoded_data)
                except:
                    decoded_data = str(raw_data)
                    print("[RX FALLBACK] 바이트 문자열로 처리: %s" % decoded_data)
            
            # 빈 문자열도 로그 출력
            if not decoded_data:
                print("[RX] 빈 문자열 수신됨")
            
            # 센서 데이터 체크 및 콜백 호출 - 센서 기능 비활성화로 콜백 호출 안 함
            # 이전 콜백 로직은 센서 데이터 처리 비활성화로 제거됨
            
            return decoded_data
        except Exception as e:
            print("[RX ERROR] 시리얼 데이터 읽기 오류: %s" % e)
            return None 

    def _on_data_ready(self):
        """인터럽트 핸들러: 데이터 수신 가능할 때 호출"""
        try:
            data = self._read_available_data()
            if data:
                print(f"[INTERRUPT] 수신된 데이터: '{data}'")
                # 시그널 발생
                self.data_received.emit(data)
                
                # 레거시 콜백 호출 (기존 코드와의 호환성)
                if self.sensor_data_callback and '[DSCT]' in data:
                    self.sensor_data_callback(data)
                elif self.air_sensor_data_callback and ('[AIR]' in data or '[AIRCON]' in data):
                    self.air_sensor_data_callback(data)
        except Exception as e:
            print(f"[INTERRUPT ERROR] 데이터 처리 오류: {e}")

    def _read_available_data(self) -> Optional[str]:
        """사용 가능한 데이터 즉시 읽기 (논블로킹)"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                return None
                
            if not self.shinho_serial_connection.in_waiting:
                return None
                
            raw_data = self.shinho_serial_connection.readline()
            if not raw_data:
                return None
                
            # 디코딩
            try:
                return raw_data.decode('ascii').strip()
            except UnicodeDecodeError:
                try:
                    return raw_data.decode('utf-8').strip()
                except:
                    return str(raw_data)
                    
        except Exception as e:
            print(f"[READ ERROR] {e}")
            return None

    def disconnect_serial(self) -> None:
        """시리얼 포트 닫기 함수, 연결 종료"""
        try:
            # 소켓 알림자 해제
            if self.socket_notifier:
                self.socket_notifier.setEnabled(False)
                self.socket_notifier.deleteLater()
                self.socket_notifier = None
                print("[SERIAL] 인터럽트 방식 해제")
                
            # 시리얼 연결 해제
            if self.shinho_serial_connection and self.shinho_serial_connection.is_open:
                self.shinho_serial_connection.close()
                print("Serial port closed.")
        except Exception as e:
            print("Disconnect error:", e)
    
    def is_connection_healthy(self) -> bool:
        """연결 상태가 건강한지 확인 (포트 열림 상태만 체크)"""
        return self.is_connected() and self.connection_healthy
    
    def send_serial_command(self, command):
        """시리얼 명령 전송 함수 (종료 문자 자동 추가)"""
        if self.is_connected():
            full_command = command + "\r\n"
            result = self.send_data(full_command)
            if result:
                print("[TX] 시리얼 명령 전송: %s (with <CR><LF>)" % command)
            else:
                print("[TX ERROR] 시리얼 명령 전송 실패:", command)
            return result
        else:
            print("[TX ERROR] 시리얼 연결 안됨, 명령 전송 실패:", command)
        return False
    
    def set_sensor_data_callback(self, callback):
        """센서 데이터 수신 콜백 설정"""
        self.sensor_data_callback = callback
    
    def set_air_sensor_data_callback(self, callback):
        """AIR 센서 데이터 수신 콜백 설정"""
        self.air_sensor_data_callback = callback