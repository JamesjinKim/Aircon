# 센서 스케줄러 - AIRCON과 DSCT 센서를 순차적으로 관리
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from enum import Enum
from datetime import datetime
import time

class SchedulerState(Enum):
    """스케줄러 상태 정의"""
    IDLE = "idle"
    AIRCON_REQUESTING = "aircon_requesting" 
    AIRCON_WAITING = "aircon_waiting"
    DSCT_REQUESTING = "dsct_requesting"
    DSCT_WAITING = "dsct_waiting"
    INTERVAL_WAITING = "interval_waiting"
    PAUSED = "paused"

class SensorScheduler(QObject):
    """AIRCON과 DSCT 센서를 순차적으로 관리하는 중앙 스케줄러"""
    
    # 스케줄러 상태 변경 시그널
    state_changed = pyqtSignal(str)  # state name
    
    # 개별 센서 데이터 업데이트 시그널 (UI로 전달)
    aircon_sensor_updated = pyqtSignal(str, dict)  # sensor_id, data
    aircon_all_sensors_updated = pyqtSignal(dict)  # all sensor data
    dsct_sensor_updated = pyqtSignal(str, dict)  # sensor_id, data  
    dsct_all_sensors_updated = pyqtSignal(dict)  # all sensor data
    
    def __init__(self, serial_manager=None, test_mode=False):
        super().__init__()
        self.serial_manager = serial_manager
        self.test_mode = test_mode
        
        # 센서 매니저들 (나중에 설정)
        self.aircon_manager = None
        self.dsct_manager = None
        
        # 스케줄러 상태
        self.current_state = SchedulerState.IDLE
        self.is_running = False
        
        # 타이머 설정
        self.main_timer = QTimer()
        self.main_timer.timeout.connect(self._process_state_machine)
        
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._handle_timeout)
        self.timeout_timer.setSingleShot(True)
        
        # 설정 가능한 옵션들 - UI에서 설정되기 전까지의 초기값
        self.cycle_interval = 5.0  # 전체 주기 간격 (초) - UI에서 덮어씀
        self.response_timeout = 10.0  # 응답 대기 시간 (초)
        self.aircon_enabled = True
        self.dsct_enabled = True
        
        # 상태 추적
        self.current_request_start_time = None
        self.last_cycle_time = None
        
        # 연결 상태 체크 최적화 (시간 기반 - 5초마다)
        self.last_connection_check_time = 0
        self.connection_check_interval = 5.0
        
        print("[SCHEDULER] 센서 스케줄러 초기화 완료")
        
    def set_sensor_managers(self, aircon_manager, dsct_manager):
        """센서 매니저들 설정"""
        self.aircon_manager = aircon_manager
        self.dsct_manager = dsct_manager
        
        # 센서 매니저들의 시그널을 스케줄러로 연결
        if self.aircon_manager:
            self.aircon_manager.sensor_data_updated.connect(self._on_aircon_sensor_updated)
            self.aircon_manager.all_sensors_updated.connect(self._on_aircon_all_updated)
            
        if self.dsct_manager:
            self.dsct_manager.sensor_data_updated.connect(self._on_dsct_sensor_updated)
            self.dsct_manager.all_sensors_updated.connect(self._on_dsct_all_updated)
            
        print("[SCHEDULER] 센서 매니저들 연결 완료")
        
    def set_serial_manager(self, serial_manager):
        """시리얼 매니저 설정"""
        self.serial_manager = serial_manager
        
        # 센서 매니저들에도 전달
        if self.aircon_manager:
            self.aircon_manager.set_serial_manager(serial_manager)
        if self.dsct_manager:
            self.dsct_manager.set_serial_manager(serial_manager)
            
        print("[SCHEDULER] 시리얼 매니저 설정 완료")
        
    def start_scheduling(self):
        """스케줄링 시작"""
        if self.is_running:
            print("[SCHEDULER] 이미 실행 중입니다")
            return
            
        if not self.serial_manager or not self.serial_manager.is_connection_healthy():
            print("[SCHEDULER] 시리얼 연결 상태 불량, 스케줄링 시작 실패")
            return
            
        self.is_running = True
        self._set_state(SchedulerState.IDLE)
        self.main_timer.start(100)  # 100ms마다 상태 머신 처리
        self.last_cycle_time = time.time()
        
        print("[SCHEDULER] 스케줄링 시작")
        
    def stop_scheduling(self):
        """스케줄링 중지"""
        self.is_running = False
        self.main_timer.stop()
        self.timeout_timer.stop()
        self._set_state(SchedulerState.PAUSED)
        
        print("[SCHEDULER] 스케줄링 중지")
        
    def pause_scheduling(self):
        """스케줄링 일시정지"""
        if self.is_running:
            self.main_timer.stop()
            self.timeout_timer.stop()
            self._set_state(SchedulerState.PAUSED)
            print("[SCHEDULER] 스케줄링 일시정지")
            
    def resume_scheduling(self):
        """스케줄링 재개"""
        if self.is_running and self.current_state == SchedulerState.PAUSED:
            self._set_state(SchedulerState.IDLE)
            self.main_timer.start(100)
            print("[SCHEDULER] 스케줄링 재개")
            
    def manual_request_aircon(self):
        """수동 AIRCON 데이터 요청"""
        if self.aircon_manager:
            print("[SCHEDULER] 수동 AIRCON 데이터 요청")
            self.aircon_manager.request_sensor_data()
            
    def manual_request_dsct(self):
        """수동 DSCT 데이터 요청"""
        if self.dsct_manager:
            print("[SCHEDULER] 수동 DSCT 데이터 요청")
            self.dsct_manager.request_sensor_data()
            
    def set_cycle_interval(self, seconds):
        """주기 간격 설정"""
        self.cycle_interval = max(1.0, min(360.0, seconds))
        print(f"[SCHEDULER] 주기 간격 설정: {self.cycle_interval}초")
        
    def _set_state(self, new_state):
        """상태 변경"""
        if self.current_state != new_state:
            old_state = self.current_state
            self.current_state = new_state
            print(f"[SCHEDULER] 상태 변경: {old_state.value} → {new_state.value}")
            self.state_changed.emit(new_state.value)
            
    def _process_state_machine(self):
        """상태 머신 처리"""
        if not self.is_running:
            return
            
        current_time = time.time()
        
        # 연결 상태 체크 (5초마다만 실행)
        if current_time - self.last_connection_check_time >= self.connection_check_interval:
            self.last_connection_check_time = current_time
            if not self.serial_manager or not self.serial_manager.is_connection_healthy():
                print("[SCHEDULER] 연결 상태 불량, 스케줄링 일시정지")
                self.pause_scheduling()
                return
            
        if self.current_state == SchedulerState.IDLE:
            # 주기 간격 체크
            if self.last_cycle_time and (current_time - self.last_cycle_time) < self.cycle_interval:
                return
                
            # 새 주기 시작
            print(f"[SCHEDULER] 새 주기 시작 - 간격: {self.cycle_interval}초")
            if self.aircon_enabled:
                self._start_aircon_request()
            elif self.dsct_enabled:
                self._start_dsct_request()
            else:
                # 둘 다 비활성화된 경우 대기
                self._set_state(SchedulerState.INTERVAL_WAITING)
                
        elif self.current_state == SchedulerState.AIRCON_REQUESTING:
            # AIRCON 요청 완료 대기
            pass
            
        elif self.current_state == SchedulerState.AIRCON_WAITING:
            # AIRCON 응답 완료 대기 (타임아웃은 별도 타이머에서 처리)
            pass
            
        elif self.current_state == SchedulerState.DSCT_REQUESTING:
            # DSCT 요청 완료 대기
            pass
            
        elif self.current_state == SchedulerState.DSCT_WAITING:
            # DSCT 응답 완료 대기 (타임아웃은 별도 타이머에서 처리)
            pass
            
        elif self.current_state == SchedulerState.INTERVAL_WAITING:
            # 주기 간격 대기 완료 후 새 주기 시작
            self.last_cycle_time = current_time
            print(f"[SCHEDULER] 주기 대기 완료, 다음 주기까지 {self.cycle_interval}초 대기")
            self._set_state(SchedulerState.IDLE)
            
    def _start_aircon_request(self):
        """AIRCON 데이터 요청 시작"""
        if not self.aircon_manager:
            self._move_to_dsct()
            return
            
        print("[SCHEDULER] AIRCON 데이터 요청 시작")
        self._set_state(SchedulerState.AIRCON_REQUESTING)
        self.current_request_start_time = time.time()
        
        # 타임아웃 타이머 시작
        self.timeout_timer.start(int(self.response_timeout * 1000))
        
        # AIRCON 데이터 요청
        self.aircon_manager.request_sensor_data()
        self._set_state(SchedulerState.AIRCON_WAITING)
        
    def _start_dsct_request(self):
        """DSCT 데이터 요청 시작"""
        if not self.dsct_manager:
            print("[SCHEDULER] DSCT 매니저가 없음, 주기 대기로 이동")
            self._set_state(SchedulerState.INTERVAL_WAITING)
            return
            
        print("[SCHEDULER] DSCT 데이터 요청 시작")
        self._set_state(SchedulerState.DSCT_REQUESTING)
        self.current_request_start_time = time.time()
        
        # 타임아웃 타이머 시작
        self.timeout_timer.start(int(self.response_timeout * 1000))
        print(f"[SCHEDULER] DSCT 타임아웃 타이머 시작: {self.response_timeout}초")
        
        # DSCT 데이터 요청
        print("[SCHEDULER] DSCT 매니저에 데이터 요청 호출")
        self.dsct_manager.request_sensor_data()
        self._set_state(SchedulerState.DSCT_WAITING)
        print("[SCHEDULER] DSCT 응답 대기 상태로 변경")
        
    def _move_to_dsct(self):
        """DSCT로 이동"""
        if self.dsct_enabled:
            self._start_dsct_request()
        else:
            self._set_state(SchedulerState.INTERVAL_WAITING)
            
    def _handle_timeout(self):
        """응답 타임아웃 처리"""
        current_time = time.time()
        elapsed = current_time - (self.current_request_start_time or current_time)
        
        if self.current_state == SchedulerState.AIRCON_WAITING:
            print(f"[SCHEDULER] AIRCON 응답 타임아웃 ({elapsed:.1f}초), DSCT로 이동")
            self._move_to_dsct()
        elif self.current_state == SchedulerState.DSCT_WAITING:
            print(f"[SCHEDULER] DSCT 응답 타임아웃 ({elapsed:.1f}초), 주기 대기로 이동")
            self._set_state(SchedulerState.INTERVAL_WAITING)
            
    def _on_aircon_sensor_updated(self, sensor_id, data):
        """AIRCON 개별 센서 업데이트"""
        self.aircon_sensor_updated.emit(sensor_id, data)
        
    def _on_aircon_all_updated(self, all_data):
        """AIRCON 전체 센서 업데이트 완료"""
        print(f"[SCHEDULER] AIRCON 응답 완료, {len(all_data)}개 센서 → UI로 시그널 전송")
        self.timeout_timer.stop()
        self.aircon_all_sensors_updated.emit(all_data)
        print("[SCHEDULER] AIRCON aircon_all_sensors_updated 시그널 전송 완료")
        self._move_to_dsct()
        
    def _on_dsct_sensor_updated(self, sensor_id, data):
        """DSCT 개별 센서 업데이트"""
        self.dsct_sensor_updated.emit(sensor_id, data)
        
    def _on_dsct_all_updated(self, all_data):
        """DSCT 전체 센서 업데이트 완료"""
        print(f"[SCHEDULER] DSCT 응답 완료, {len(all_data)}개 센서 → UI로 시그널 전송")
        self.timeout_timer.stop()
        self.dsct_all_sensors_updated.emit(all_data)
        print("[SCHEDULER] DSCT dsct_all_sensors_updated 시그널 전송 완료")
        self._set_state(SchedulerState.INTERVAL_WAITING)
        
    def get_status_info(self):
        """현재 상태 정보 반환"""
        return {
            'state': self.current_state.value,
            'is_running': self.is_running,
            'cycle_interval': self.cycle_interval,
            'aircon_enabled': self.aircon_enabled,
            'dsct_enabled': self.dsct_enabled,
            'last_cycle_time': self.last_cycle_time
        }