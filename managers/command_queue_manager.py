"""
명령 전송 큐 시스템
UI hang 방지를 위한 비동기 명령 처리
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QMutex, QMutexLocker
from collections import deque
from typing import Optional, Callable, Any, Dict
import time
from dataclasses import dataclass
from enum import Enum

class CommandPriority(Enum):
    """명령 우선순위"""
    LOW = 0      # 센서 데이터 요청
    NORMAL = 1   # 일반 버튼 명령
    HIGH = 2     # 긴급 명령 (정지 등)

@dataclass
class Command:
    """명령 데이터 클래스"""
    command: str
    priority: CommandPriority = CommandPriority.NORMAL
    callback: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3
    timestamp: float = 0

class CommandQueueManager(QObject):
    """명령 큐 관리자"""
    
    # 시그널 정의
    command_sent = pyqtSignal(str)
    command_failed = pyqtSignal(str, str)  # command, error
    queue_status_changed = pyqtSignal(int)  # queue size
    
    def __init__(self, serial_manager=None):
        super().__init__()
        self.serial_manager = serial_manager
        
        # 우선순위별 큐
        self.high_queue = deque()
        self.normal_queue = deque()
        self.low_queue = deque()
        
        # 스레드 안전성을 위한 뮤텍스
        self.mutex = QMutex()
        
        # 처리 타이머
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_queue)
        self.process_timer.start(50)  # 50ms마다 처리
        
        # 상태 관리
        self.is_processing = False
        self.last_command_time = 0
        self.min_command_interval = 0.05  # 최소 명령 간격 (50ms)
        
        # 통계
        self.total_sent = 0
        self.total_failed = 0
        
        print("[QUEUE] 명령 큐 매니저 초기화 완료")
        
    def set_serial_manager(self, serial_manager):
        """시리얼 매니저 설정"""
        self.serial_manager = serial_manager
        print("[QUEUE] 시리얼 매니저 설정 완료")
        
    def add_command(self, command: str, priority: CommandPriority = CommandPriority.NORMAL, 
                   callback: Optional[Callable] = None) -> bool:
        """명령을 큐에 추가"""
        with QMutexLocker(self.mutex):
            cmd = Command(
                command=command,
                priority=priority,
                callback=callback,
                timestamp=time.time()
            )
            
            # 우선순위별로 큐에 추가
            if priority == CommandPriority.HIGH:
                self.high_queue.append(cmd)
            elif priority == CommandPriority.NORMAL:
                self.normal_queue.append(cmd)
            else:
                self.low_queue.append(cmd)
                
            # 큐 상태 업데이트
            self._update_queue_status()
            return True
            
    def add_urgent_command(self, command: str, callback: Optional[Callable] = None):
        """긴급 명령 추가 (최우선 처리)"""
        return self.add_command(command, CommandPriority.HIGH, callback)
        
    def clear_queue(self, priority: Optional[CommandPriority] = None):
        """큐 비우기"""
        with QMutexLocker(self.mutex):
            if priority is None:
                # 모든 큐 비우기
                self.high_queue.clear()
                self.normal_queue.clear()
                self.low_queue.clear()
            elif priority == CommandPriority.HIGH:
                self.high_queue.clear()
            elif priority == CommandPriority.NORMAL:
                self.normal_queue.clear()
            else:
                self.low_queue.clear()
                
            self._update_queue_status()
            
    def _process_queue(self):
        """큐 처리 (타이머에서 호출)"""
        if self.is_processing:
            return
            
        # 시리얼 연결 확인
        if not self.serial_manager or not self.serial_manager.is_connected():
            return
            
        # 최소 명령 간격 체크
        current_time = time.time()
        if current_time - self.last_command_time < self.min_command_interval:
            return
            
        # 다음 명령 가져오기
        command = self._get_next_command()
        if command:
            self.is_processing = True
            self._send_command(command)
            self.is_processing = False
            self.last_command_time = current_time
            
    def _get_next_command(self) -> Optional[Command]:
        """우선순위에 따라 다음 명령 가져오기"""
        with QMutexLocker(self.mutex):
            # 우선순위 순서대로 확인
            if self.high_queue:
                return self.high_queue.popleft()
            elif self.normal_queue:
                return self.normal_queue.popleft()
            elif self.low_queue:
                return self.low_queue.popleft()
            return None
            
    def _send_command(self, cmd: Command):
        """실제 명령 전송"""
        try:
            # 명령 전송
            success = self.serial_manager.send_serial_command(cmd.command)
            
            if success:
                self.total_sent += 1
                self.command_sent.emit(cmd.command)
                
                # 콜백 실행
                if cmd.callback:
                    try:
                        cmd.callback(True, cmd.command)
                    except Exception as e:
                        print(f"[QUEUE] 콜백 실행 오류: {e}")
                        
            else:
                # 전송 실패 시 재시도
                self._handle_send_failure(cmd)
                
        except Exception as e:
            self._handle_send_failure(cmd, str(e))
            
    def _handle_send_failure(self, cmd: Command, error: str = "전송 실패"):
        """전송 실패 처리"""
        cmd.retry_count += 1
        
        if cmd.retry_count < cmd.max_retries:
            # 재시도 큐에 다시 추가
            with QMutexLocker(self.mutex):
                if cmd.priority == CommandPriority.HIGH:
                    self.high_queue.appendleft(cmd)  # 앞쪽에 추가
                elif cmd.priority == CommandPriority.NORMAL:
                    self.normal_queue.append(cmd)
                else:
                    self.low_queue.append(cmd)
                    
            print(f"[QUEUE] 재시도 {cmd.retry_count}/{cmd.max_retries}: {cmd.command}")
            
        else:
            # 최대 재시도 초과
            self.total_failed += 1
            self.command_failed.emit(cmd.command, error)
            
            # 실패 콜백 실행
            if cmd.callback:
                try:
                    cmd.callback(False, error)
                except Exception as e:
                    print(f"[QUEUE] 실패 콜백 오류: {e}")
                    
    def _update_queue_status(self):
        """큐 상태 업데이트"""
        total_size = len(self.high_queue) + len(self.normal_queue) + len(self.low_queue)
        self.queue_status_changed.emit(total_size)
        
    def get_queue_info(self) -> Dict[str, Any]:
        """큐 정보 반환"""
        with QMutexLocker(self.mutex):
            return {
                'high_queue_size': len(self.high_queue),
                'normal_queue_size': len(self.normal_queue),
                'low_queue_size': len(self.low_queue),
                'total_sent': self.total_sent,
                'total_failed': self.total_failed,
                'is_processing': self.is_processing
            }
            
    def set_command_interval(self, interval: float):
        """명령 간격 설정 (초)"""
        self.min_command_interval = max(0.01, min(1.0, interval))
        print(f"[QUEUE] 명령 간격 설정: {self.min_command_interval}초")