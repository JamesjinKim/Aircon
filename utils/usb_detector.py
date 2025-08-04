"""
USB 장치 자동 감지 및 관리 모듈
라즈베리파이에서 USB 삽입/제거를 감지하고 마운트 포인트를 관리합니다.
"""
import os
import subprocess
import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal
import psutil

class USBDetector(QObject):
    """USB 장치 자동 감지 클래스"""
    
    # 시그널 정의
    usb_connected = pyqtSignal(str)  # USB 연결됨 (마운트 경로)
    usb_disconnected = pyqtSignal()  # USB 연결 해제됨
    
    def __init__(self):
        super().__init__()
        self.current_usb_path = None
        self.monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """USB 모니터링 시작"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_usb, daemon=True)
            self.monitor_thread.start()
            
    def stop_monitoring(self):
        """USB 모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
            
    def get_usb_drives(self):
        """현재 연결된 USB 드라이브 목록 반환"""
        usb_drives = []
        
        try:
            # psutil을 사용하여 마운트된 디스크 확인
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                # USB 장치는 보통 /media 또는 /mnt 아래에 마운트됨
                if ('/media' in partition.mountpoint or 
                    '/mnt' in partition.mountpoint or
                    'usb' in partition.mountpoint.lower()):
                    
                    # 마운트 포인트가 실제로 존재하고 접근 가능한지 확인
                    if os.path.exists(partition.mountpoint) and os.access(partition.mountpoint, os.W_OK):
                        usb_drives.append(partition.mountpoint)
                        
        except Exception as e:
            print(f"USB 드라이브 검색 중 오류: {e}")
            
        # 추가적으로 일반적인 USB 마운트 위치도 확인
        common_usb_paths = ['/media/pi', '/mnt/usb', '/media/usb']
        for path in common_usb_paths:
            if os.path.exists(path) and os.access(path, os.W_OK):
                # 하위 디렉토리 확인
                try:
                    for item in os.listdir(path):
                        full_path = os.path.join(path, item)
                        if os.path.isdir(full_path) and os.access(full_path, os.W_OK):
                            if full_path not in usb_drives:
                                usb_drives.append(full_path)
                except PermissionError:
                    continue
                    
        return usb_drives
    
    def get_current_usb_path(self):
        """현재 사용 가능한 USB 경로 반환"""
        return self.current_usb_path
        
    def _monitor_usb(self):
        """USB 모니터링 루프"""
        previous_drives = set()
        
        while self.monitoring:
            try:
                current_drives = set(self.get_usb_drives())
                
                # 새로운 USB 드라이브가 연결됨
                new_drives = current_drives - previous_drives
                if new_drives:
                    # 가장 최근에 연결된 드라이브 선택
                    latest_drive = sorted(new_drives)[-1]
                    self.current_usb_path = latest_drive
                    self.usb_connected.emit(latest_drive)
                    
                # USB 드라이브가 제거됨
                removed_drives = previous_drives - current_drives
                if removed_drives and self.current_usb_path in removed_drives:
                    self.current_usb_path = None
                    # 다른 USB가 여전히 연결되어 있는지 확인
                    if current_drives:
                        self.current_usb_path = sorted(current_drives)[-1]
                        self.usb_connected.emit(self.current_usb_path)
                    else:
                        self.usb_disconnected.emit()
                        
                previous_drives = current_drives
                
            except Exception as e:
                print(f"USB 모니터링 중 오류: {e}")
                
            time.sleep(2)  # 2초마다 확인
            
    def is_usb_available(self):
        """USB가 사용 가능한지 확인"""
        return self.current_usb_path is not None and os.path.exists(self.current_usb_path)
        
    def create_csv_folder(self, folder_name="AIRCON_CSV"):
        """USB에 CSV 저장용 폴더 생성"""
        if not self.is_usb_available():
            return None
            
        try:
            csv_folder = os.path.join(self.current_usb_path, folder_name)
            os.makedirs(csv_folder, exist_ok=True)
            return csv_folder
        except Exception as e:
            print(f"CSV 폴더 생성 중 오류: {e}")
            return None