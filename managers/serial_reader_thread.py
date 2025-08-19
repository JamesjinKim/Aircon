"""
시리얼 데이터 읽기 전용 스레드
메인 스레드 블로킹 방지를 위한 별도 스레드에서 시리얼 데이터 읽기 처리
"""

from PyQt5.QtCore import QThread, pyqtSignal
import time

class SerialReaderThread(QThread):
    """시리얼 데이터 읽기 전용 스레드"""
    
    # 데이터 수신 시그널
    data_received = pyqtSignal(str)
    
    def __init__(self, serial_manager):
        super().__init__()
        self.serial_manager = serial_manager
        self.is_running = False
        self.read_interval = 0.01  # 10ms 간격
        
    def start_reading(self):
        """읽기 스레드 시작"""
        if not self.is_running:
            self.is_running = True
            self.start()
            print("[READER_THREAD] 시리얼 읽기 스레드 시작")
            
    def stop_reading(self):
        """읽기 스레드 중지"""
        self.is_running = False
        if self.isRunning():
            self.quit()
            self.wait()
            print("[READER_THREAD] 시리얼 읽기 스레드 중지")
            
    def run(self):
        """스레드 실행 메인 루프"""
        print("[READER_THREAD] 읽기 스레드 시작됨")
        
        while self.is_running:
            try:
                # 시리얼 연결 확인
                if not self.serial_manager or not self.serial_manager.is_connected():
                    self.msleep(100)  # 100ms 대기
                    continue
                
                # 데이터 읽기 시도
                data = self.serial_manager.read_data()
                if data:
                    print(f"[READER_THREAD] 수신된 데이터: '{data}'")
                    self.data_received.emit(data)
                    
                # 짧은 대기 (CPU 사용량 조절)
                self.msleep(int(self.read_interval * 1000))
                
            except Exception as e:
                print(f"[READER_THREAD ERROR] {e}")
                self.msleep(100)  # 에러 시 100ms 대기
                
        print("[READER_THREAD] 읽기 스레드 종료됨")
        
    def set_read_interval(self, interval_ms: int):
        """읽기 간격 설정 (밀리초)"""
        self.read_interval = max(1, min(1000, interval_ms)) / 1000.0
        print(f"[READER_THREAD] 읽기 간격 설정: {self.read_interval * 1000:.0f}ms")