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
        self.use_interrupt_mode = False  # 인터럽트 방식 비활성화 (문제 해결 시까지)
        
        # 명령 큐 매니저 연결용
        self.command_queue = None
        
        # 읽기 스레드 (지연 초기화)
        self.reader_thread = None

    def get_available_ports(self, usb_only: bool = True) -> List[Dict[str, str]]:
        """연결 가능한 시리얼 포트 목록을 반환하는 함수

        Args:
            usb_only: True면 USB 시리얼 포트만 반환 (기본값),
                      False면 모든 포트 반환

        Returns:
            포트 정보 리스트 [{"device": "/dev/ttyUSB0", "description": "..."}]
        """
        ports = serial.tools.list_ports.comports()

        if usb_only:
            # USB 시리얼 포트만 필터링 (/dev/ttyUSB*, /dev/ttyACM*, COM* 등)
            filtered_ports = []
            for port in ports:
                device = port.device
                # Linux: ttyUSB*, ttyACM* (USB-시리얼 어댑터)
                # Windows: COM* (모두 USB일 가능성 높음)
                if ('ttyUSB' in device or 'ttyACM' in device or
                    device.startswith('COM')):
                    filtered_ports.append({
                        "device": port.device,
                        "description": port.description,
                    })
            return filtered_ports
        else:
            # 모든 포트 반환
            return [{
                "device": port.device,
                "description": port.description,
            } for port in ports]
        
    def connect_serial(self, port: str, baudrate: int = 115200) -> bool:
        """지정된 포트와 보레이트로 시리얼 연결 시도하는 함수"""
        try:
            # 기존 연결 해제
            self.disconnect_serial()

            # USB 시리얼 포트 존재 여부 확인
            available_ports = [p["device"] for p in self.get_available_ports(usb_only=True)]
            if port not in available_ports:
                print(f"[SERIAL] 오류: USB 시리얼 포트 '{port}'가 존재하지 않습니다.")
                print(f"[SERIAL] 사용 가능한 USB 포트: {available_ports if available_ports else '없음'}")
                return False

            # 새 연결 시도
            self.shinho_serial_connection = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1  # 논블로킹에 가까운 타임아웃
            )

            # 연결 후 실제로 포트가 열렸는지 확인
            if not self.shinho_serial_connection.is_open:
                print(f"[SERIAL] 오류: 포트 '{port}' 열기 실패")
                self.shinho_serial_connection = None
                return False

            # 인터럽트 방식 설정 (현재 비활성화)
            if self.use_interrupt_mode and hasattr(self.shinho_serial_connection, 'fileno'):
                try:
                    fd = self.shinho_serial_connection.fileno()
                    self.socket_notifier = QSocketNotifier(fd, QSocketNotifier.Read)
                    self.socket_notifier.activated.connect(self._on_data_ready)
                    self.socket_notifier.setEnabled(True)
                    print(f"[SERIAL] 인터럽트 방식 활성화 (fd: {fd})")
                except Exception as e:
                    print(f"[SERIAL] 인터럽트 방식 설정 실패, 폴링 방식 유지: {e}")
            else:
                print("[SERIAL] 인터럽트 방식 비활성화됨, 폴링 방식 사용")

            print(f"[SERIAL] 연결 성공: {port} @ {baudrate}bps")

            # 읽기 스레드 시작
            self._start_reader_thread()

            return True
        except serial.SerialException as e:
            print(f"[SERIAL] 시리얼 연결 오류: {e}")
            self.shinho_serial_connection = None
            return False
        except Exception as e:
            print(f"[SERIAL] 연결 오류: {e}")
            self.shinho_serial_connection = None
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
        """데이터 읽기 함수 (비블로킹)"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                return None

            # 대기 중인 데이터만 읽기 (논블로킹)
            if self.shinho_serial_connection.in_waiting > 0:
                data = self.shinho_serial_connection.readline()
                if data:
                    return data.decode('ascii', errors='ignore').strip()
        except Exception as e:
            print(f"[READ ERROR] {e}")
        return None 

    def _on_data_ready(self):
        """인터럽트 핸들러: 데이터 수신 가능할 때 호출"""
        try:
            # 소켓 알림자 일시 비활성화 (재진입 방지)
            if self.socket_notifier:
                self.socket_notifier.setEnabled(False)
            
            # 사용 가능한 모든 데이터를 한 번에 읽기
            processed_count = 0
            max_iterations = 100  # 무한 루프 방지
            
            while processed_count < max_iterations:
                data = self._read_available_data()
                if not data:
                    break
                    
                processed_count += 1
                print(f"[INTERRUPT] 수신된 데이터 ({processed_count}): '{data}'")
                
                # 시그널 발생
                self.data_received.emit(data)
                
                # 레거시 콜백 호출 (기존 코드와의 호환성) - 센서 기능 비활성화로 제거
                # if self.sensor_data_callback and '[DSCT]' in data:
                #     self.sensor_data_callback(data)
                # elif self.air_sensor_data_callback and ('[AIR]' in data or '[AIRCON]' in data):
                #     self.air_sensor_data_callback(data)
            
            if processed_count >= max_iterations:
                print(f"[INTERRUPT WARNING] 최대 반복 횟수 도달: {max_iterations}")
                
        except Exception as e:
            print(f"[INTERRUPT ERROR] 데이터 처리 오류: {e}")
        finally:
            # 소켓 알림자 재활성화
            if self.socket_notifier and self.shinho_serial_connection and self.shinho_serial_connection.is_open:
                self.socket_notifier.setEnabled(True)

    def _read_available_data(self) -> Optional[str]:
        """사용 가능한 데이터 즉시 읽기 (논블로킹)"""
        try:
            if not self.shinho_serial_connection or not self.shinho_serial_connection.is_open:
                return None
            
            # 대기 중인 바이트 수 확인
            waiting_bytes = self.shinho_serial_connection.in_waiting
            if waiting_bytes == 0:
                return None
            
            print(f"[READ] 대기 중인 바이트: {waiting_bytes}")
            
            # 논블로킹 읽기: 타임아웃을 매우 짧게 설정
            original_timeout = self.shinho_serial_connection.timeout
            self.shinho_serial_connection.timeout = 0.01  # 10ms
            
            try:
                raw_data = self.shinho_serial_connection.readline()
            finally:
                # 타임아웃 복원
                self.shinho_serial_connection.timeout = original_timeout
                
            if not raw_data:
                return None
            
            print(f"[READ] 원본 바이트: {raw_data}")
                
            # 디코딩
            try:
                decoded = raw_data.decode('ascii').strip()
                if decoded:
                    return decoded
                else:
                    return None
            except UnicodeDecodeError:
                try:
                    decoded = raw_data.decode('utf-8').strip()
                    if decoded:
                        return decoded
                    else:
                        return None
                except:
                    return None
                    
        except Exception as e:
            print(f"[READ ERROR] {e}")
            return None

    def disconnect_serial(self) -> None:
        """시리얼 포트 닫기 함수, 연결 종료"""
        # 읽기 스레드 중지 (예외 발생해도 계속 진행)
        try:
            self._stop_reader_thread()
        except Exception as e:
            print(f"[SERIAL] 읽기 스레드 중지 중 오류 (무시됨): {e}")

        # 소켓 알림자 해제 (예외 발생해도 계속 진행)
        try:
            if self.socket_notifier:
                self.socket_notifier.setEnabled(False)
                self.socket_notifier.deleteLater()
                self.socket_notifier = None
                print("[SERIAL] 인터럽트 방식 해제")
        except Exception as e:
            print(f"[SERIAL] 소켓 알림자 해제 중 오류 (무시됨): {e}")
            self.socket_notifier = None

        # 시리얼 연결 해제
        try:
            if self.shinho_serial_connection:
                if self.shinho_serial_connection.is_open:
                    self.shinho_serial_connection.close()
                    print("[SERIAL] 포트 연결 해제 완료")
                else:
                    print("[SERIAL] 포트가 이미 닫혀있음")
        except Exception as e:
            print(f"[SERIAL] 포트 닫기 중 오류 (무시됨): {e}")
        finally:
            # 연결 객체 초기화 (항상 실행)
            self.shinho_serial_connection = None
    
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
    
    def set_command_queue(self, queue_manager):
        """큐 매니저 설정"""
        self.command_queue = queue_manager
        print("[SERIAL] 명령 큐 매니저 설정 완료")

    def send_serial_command_with_priority(self, command, priority=None):
        """우선순위를 가진 시리얼 명령 전송 (큐 경유)"""
        if self.command_queue:
            # 큐를 통해 전송
            from .command_queue_manager import CommandPriority
            if priority is None:
                priority = CommandPriority.NORMAL
            return self.command_queue.add_command(command, priority)
        else:
            # 기존 방식 (fallback)
            return self.send_serial_command(command)
    
    def _start_reader_thread(self):
        """읽기 스레드 시작"""
        try:
            # 기존 스레드 정리
            self._stop_reader_thread()
            
            # 새 읽기 스레드 생성
            from .serial_reader_thread import SerialReaderThread
            self.reader_thread = SerialReaderThread(self)
            
            # 스레드의 data_received 시그널을 메인 시그널에 연결
            self.reader_thread.data_received.connect(self._on_thread_data_received)
            
            # 스레드 시작
            self.reader_thread.start_reading()
            
            print("[SERIAL] 읽기 스레드 시작됨")
            
        except Exception as e:
            print(f"[SERIAL] 읽기 스레드 시작 실패: {e}")
    
    def _stop_reader_thread(self):
        """읽기 스레드 중지"""
        try:
            if self.reader_thread:
                self.reader_thread.stop_reading()
                self.reader_thread = None
                print("[SERIAL] 읽기 스레드 중지됨")
        except Exception as e:
            print(f"[SERIAL] 읽기 스레드 중지 실패: {e}")
    
    def _on_thread_data_received(self, data):
        """읽기 스레드에서 데이터 수신 시 호출"""
        try:
            # 메인 data_received 시그널 발생
            self.data_received.emit(data)
            
            # 레거시 콜백 호출 (기존 코드와의 호환성)
            if self.sensor_data_callback and '[DSCT]' in data:
                self.sensor_data_callback(data)
            elif self.air_sensor_data_callback and ('[AIR]' in data or '[AIRCON]' in data):
                self.air_sensor_data_callback(data)
                
        except Exception as e:
            print(f"[SERIAL] 스레드 데이터 처리 오류: {e}")