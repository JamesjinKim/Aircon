# AUTO 모드의 AUTOMODE 명령어 처리 매니저 클래스 manager/auto_manager.py
# 새로운 명령어: AUTOMODE ON/OFF, TEMPSET, CO2SET, PM25SET, SEMITIME, GETSET
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from ui.constants import CMD_PREFIX, TERMINATOR, AIR_SYSTEM


class AutoModeManager:
    """AUTO 모드 제어 매니저 - AUTOMODE 명령어 처리"""

    def __init__(self, serial_manager, SendData_textEdit, test_mode=False):
        """초기화"""
        self.serial_manager = serial_manager
        self.SendData_textEdit = SendData_textEdit
        self.test_mode = test_mode

        # AUTO 모드 상태
        self.auto_mode_active = False

        # 설정값 (기본값)
        self.temp_value = 25.0       # 목표 온도 (°C)
        self.temp_hyst = 2.0         # 온도 히스테리시스 (±°C)
        self.co2_value = 1000        # CO2 기준값 (ppm)
        self.co2_hyst = 100          # CO2 히스테리시스 (±ppm)
        self.pm25_value = 35         # PM2.5 기준값 (µg/m³)
        self.pm25_hyst = 5           # PM2.5 히스테리시스 (±µg/m³)
        self.semi_time = 300         # SEMI AUTO 동작 시간 (초)

        # PT02 센서 매니저 연동
        self.pt02_sensor_manager = None

        # PT02 센서 데이터 (수신된 값)
        self.pt02_temp = None
        self.pt02_co2 = None
        self.pt02_pm25 = None

        # UI 위젯 참조
        self.auto_widget = None
        self.auto_mode_button = None
        self.status_label = None

        # 설정 버튼 참조
        self.temp_buttons = None
        self.co2_buttons = None
        self.pm25_buttons = None
        self.time_buttons = None

        # 연속 클릭 타이머
        self.repeat_timers = {}

    def log_message(self, message):
        """Send Data 로그에 메시지 기록"""
        print(f"[AUTO] {message}")
        if self.SendData_textEdit:
            self.SendData_textEdit.append(f"[AUTO] {message}")
            self.SendData_textEdit.verticalScrollBar().setValue(
                self.SendData_textEdit.verticalScrollBar().maximum()
            )

    def send_command(self, command):
        """시리얼 명령어 전송 및 로그 기록"""
        full_command = f"{command}{TERMINATOR}"

        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(full_command.encode())
            self.log_message(f"TX: {command}")
            return True
        else:
            self.log_message(f"TX 실패 (연결 안됨): {command}")
            return False

    def connect_auto_controls(self, auto_widget):
        """AUTO 탭의 컨트롤을 연결"""
        self.auto_widget = auto_widget

        # AUTO 모드 버튼 연결
        if hasattr(auto_widget, 'auto_mode_button'):
            self.auto_mode_button = auto_widget.auto_mode_button
            self._connect_auto_mode_button()

        # 상태 레이블 참조
        if hasattr(auto_widget, 'auto_status_label'):
            self.status_label = auto_widget.auto_status_label

        # 설정 버튼들 연결
        if hasattr(auto_widget, 'temp_buttons'):
            self.temp_buttons = auto_widget.temp_buttons
            self._connect_setting_buttons('temp', self.temp_buttons, 0.5, 18.0, 35.0, 0.5, 0.5, 5.0)

        if hasattr(auto_widget, 'co2_buttons'):
            self.co2_buttons = auto_widget.co2_buttons
            self._connect_setting_buttons('co2', self.co2_buttons, 50, 400, 2000, 10, 10, 500)

        if hasattr(auto_widget, 'pm25_buttons'):
            self.pm25_buttons = auto_widget.pm25_buttons
            self._connect_setting_buttons('pm25', self.pm25_buttons, 5, 10, 100, 1, 1, 50)

        if hasattr(auto_widget, 'time_buttons'):
            self.time_buttons = auto_widget.time_buttons
            self._connect_time_buttons()

        # Refresh / SAVE 버튼 연결
        if hasattr(auto_widget, 'refresh_button'):
            auto_widget.refresh_button.clicked.connect(self.handle_refresh)

        if hasattr(auto_widget, 'save_button'):
            auto_widget.save_button.clicked.connect(self.handle_save)

        self.log_message("AUTO 탭 컨트롤 연결 완료")

    def _connect_auto_mode_button(self):
        """AUTO 모드 버튼 이벤트 연결"""
        if not self.auto_mode_button:
            return

        try:
            self.auto_mode_button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass

        self.auto_mode_button.clicked.connect(self._toggle_auto_mode)

    def _toggle_auto_mode(self):
        """AUTO 모드 토글"""
        self.auto_mode_active = not self.auto_mode_active

        if self.auto_mode_active:
            # AUTO ON 명령 전송
            command = f"{CMD_PREFIX},{AIR_SYSTEM},AUTOMODE,ON"
            success = self.send_command(command)

            if success:
                self._update_auto_button_style(True)
                self._update_status_label("동작중", "#4CAF50")
        else:
            # AUTO OFF 명령 전송
            command = f"{CMD_PREFIX},{AIR_SYSTEM},AUTOMODE,OFF"
            success = self.send_command(command)

            if success:
                self._update_auto_button_style(False)
                self._update_status_label("대기중", "#666")

    def _update_auto_button_style(self, is_active):
        """AUTO 버튼 스타일 업데이트"""
        if not self.auto_mode_button:
            return

        if is_active:
            self.auto_mode_button.setText("AUTO STOP")
            self.auto_mode_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
            """)
        else:
            self.auto_mode_button.setText("AUTO START")
            self.auto_mode_button.setStyleSheet("""
                QPushButton {
                    background-color: #2979ff;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2962ff;
                }
            """)

    def _update_status_label(self, text, color):
        """상태 레이블 업데이트"""
        if self.status_label:
            self.status_label.setText(text)
            self.status_label.setStyleSheet(f"""
                font-size: 14px;
                font-weight: bold;
                color: white;
                padding: 5px 10px;
                background-color: {color};
                border-radius: 3px;
            """)

    def _connect_setting_buttons(self, setting_type, buttons, step, min_val, max_val, hyst_step, hyst_min, hyst_max):
        """설정 버튼들 연결 (연속 클릭 지원)"""
        if not buttons:
            return

        # 값 감소 버튼
        if 'minus' in buttons:
            self._setup_repeat_button(buttons['minus'], lambda: self._adjust_value(setting_type, 'value', -step, min_val, max_val))

        # 값 증가 버튼
        if 'plus' in buttons:
            self._setup_repeat_button(buttons['plus'], lambda: self._adjust_value(setting_type, 'value', step, min_val, max_val))

        # 히스테리시스 감소 버튼
        if 'hyst_minus' in buttons:
            self._setup_repeat_button(buttons['hyst_minus'], lambda: self._adjust_value(setting_type, 'hyst', -hyst_step, hyst_min, hyst_max))

        # 히스테리시스 증가 버튼
        if 'hyst_plus' in buttons:
            self._setup_repeat_button(buttons['hyst_plus'], lambda: self._adjust_value(setting_type, 'hyst', hyst_step, hyst_min, hyst_max))

    def _connect_time_buttons(self):
        """시간 설정 버튼 연결"""
        if not self.time_buttons:
            return

        # 값 감소 버튼
        if 'minus' in self.time_buttons:
            self._setup_repeat_button(self.time_buttons['minus'], lambda: self._adjust_time(-10, 10, 9999))

        # 값 증가 버튼
        if 'plus' in self.time_buttons:
            self._setup_repeat_button(self.time_buttons['plus'], lambda: self._adjust_time(10, 10, 9999))

    def _setup_repeat_button(self, button, callback):
        """연속 클릭 지원 버튼 설정"""
        timer_key = id(button)

        def on_pressed():
            callback()
            # 연속 클릭 타이머 시작
            if timer_key not in self.repeat_timers:
                self.repeat_timers[timer_key] = QTimer()
                self.repeat_timers[timer_key].timeout.connect(callback)
            self.repeat_timers[timer_key].start(150)  # 150ms 간격

        def on_released():
            if timer_key in self.repeat_timers:
                self.repeat_timers[timer_key].stop()

        button.pressed.connect(on_pressed)
        button.released.connect(on_released)

    def _adjust_value(self, setting_type, value_type, delta, min_val, max_val):
        """설정값 조정"""
        if setting_type == 'temp':
            if value_type == 'value':
                self.temp_value = max(min_val, min(max_val, self.temp_value + delta))
                self._update_button_text(self.temp_buttons, 'value', f"{self.temp_value:.1f}")
            else:
                self.temp_hyst = max(min_val, min(max_val, self.temp_hyst + delta))
                self._update_button_text(self.temp_buttons, 'hyst_value', f"{self.temp_hyst:.1f}")

        elif setting_type == 'co2':
            if value_type == 'value':
                self.co2_value = int(max(min_val, min(max_val, self.co2_value + delta)))
                self._update_button_text(self.co2_buttons, 'value', str(self.co2_value))
            else:
                self.co2_hyst = int(max(min_val, min(max_val, self.co2_hyst + delta)))
                self._update_button_text(self.co2_buttons, 'hyst_value', str(self.co2_hyst))

        elif setting_type == 'pm25':
            if value_type == 'value':
                self.pm25_value = int(max(min_val, min(max_val, self.pm25_value + delta)))
                self._update_button_text(self.pm25_buttons, 'value', str(self.pm25_value))
            else:
                self.pm25_hyst = int(max(min_val, min(max_val, self.pm25_hyst + delta)))
                self._update_button_text(self.pm25_buttons, 'hyst_value', str(self.pm25_hyst))

    def _adjust_time(self, delta, min_val, max_val):
        """시간 설정값 조정"""
        self.semi_time = int(max(min_val, min(max_val, self.semi_time + delta)))
        self._update_button_text(self.time_buttons, 'value', str(self.semi_time))

    def _update_button_text(self, buttons, key, text):
        """버튼 텍스트 업데이트"""
        if buttons and key in buttons:
            buttons[key].setText(text)

    def handle_refresh(self):
        """Refresh 버튼 클릭 - 현재 설정값 조회"""
        command = f"{CMD_PREFIX},{AIR_SYSTEM},GETSET"
        self.send_command(command)
        self.log_message("설정값 조회 요청")

    def handle_save(self):
        """SAVE 버튼 클릭 - 모든 설정값 전송 (딜레이 적용)"""
        self.log_message("설정값 저장 시작...")

        # 명령어 대기열 생성
        self._save_command_queue = []

        # 1. 온도 설정 (값 * 10으로 전송)
        temp_val_int = int(self.temp_value * 10)
        temp_hyst_int = int(self.temp_hyst * 10)
        cmd_temp = f"{CMD_PREFIX},{AIR_SYSTEM},TEMPSET,{temp_val_int},{temp_hyst_int}"
        self._save_command_queue.append(cmd_temp)

        # 2. CO2 설정
        cmd_co2 = f"{CMD_PREFIX},{AIR_SYSTEM},CO2SET,{self.co2_value},{self.co2_hyst}"
        self._save_command_queue.append(cmd_co2)

        # 3. PM2.5 설정
        cmd_pm25 = f"{CMD_PREFIX},{AIR_SYSTEM},PM25SET,{self.pm25_value},{self.pm25_hyst}"
        self._save_command_queue.append(cmd_pm25)

        # 4. SEMI 동작시간 설정
        cmd_time = f"{CMD_PREFIX},{AIR_SYSTEM},SEMITIME,{self.semi_time}"
        self._save_command_queue.append(cmd_time)

        # 명령어 인덱스 초기화 후 순차 전송 시작
        self._save_command_index = 0
        self._send_next_save_command()

    def _send_next_save_command(self):
        """대기열에서 다음 명령어 전송 (200ms 딜레이)"""
        if self._save_command_index < len(self._save_command_queue):
            cmd = self._save_command_queue[self._save_command_index]
            self.send_command(cmd)
            self._save_command_index += 1

            # 다음 명령어는 200ms 후 전송
            QTimer.singleShot(200, self._send_next_save_command)
        else:
            # 모든 명령어 전송 완료
            self.log_message("설정값 저장 완료")

    def update_pt02_sensor_display(self, temp=None, co2=None, pm25=None):
        """PT02 센서 데이터 UI 업데이트"""
        if not self.auto_widget:
            return

        if temp is not None:
            self.pt02_temp = temp
            if hasattr(self.auto_widget, 'pt02_temp_display'):
                self.auto_widget.pt02_temp_display.setText(f"{temp:.1f}°C")

        if co2 is not None:
            self.pt02_co2 = co2
            if hasattr(self.auto_widget, 'pt02_co2_display'):
                self.auto_widget.pt02_co2_display.setText(f"{co2} ppm")

        if pm25 is not None:
            self.pt02_pm25 = pm25
            if hasattr(self.auto_widget, 'pt02_pm25_display'):
                self.auto_widget.pt02_pm25_display.setText(f"{pm25} µg/m³")

    def update_mode_indicators(self, auto_active=False, vent_active=False, circ_active=False):
        """모드 동작 상태 인디케이터 업데이트"""
        if not self.auto_widget:
            return

        # 자동(온도) 인디케이터
        if hasattr(self.auto_widget, 'auto_temp_indicator'):
            style = "font-size: 12px; padding: 2px 5px; border-radius: 3px; "
            if auto_active:
                style += "color: white; background-color: #4CAF50;"
            else:
                style += "color: #888; background-color: transparent;"
            self.auto_widget.auto_temp_indicator.setStyleSheet(style)

        # 환기(CO2) 인디케이터
        if hasattr(self.auto_widget, 'vent_indicator'):
            style = "font-size: 12px; padding: 2px 5px; border-radius: 3px; "
            if vent_active:
                style += "color: white; background-color: #2196F3;"
            else:
                style += "color: #888; background-color: transparent;"
            self.auto_widget.vent_indicator.setStyleSheet(style)

        # 순환(PM2.5) 인디케이터
        if hasattr(self.auto_widget, 'circulation_indicator'):
            style = "font-size: 12px; padding: 2px 5px; border-radius: 3px; "
            if circ_active:
                style += "color: white; background-color: #9C27B0;"
            else:
                style += "color: #888; background-color: transparent;"
            self.auto_widget.circulation_indicator.setStyleSheet(style)

    def set_pt02_sensor_manager(self, pt02_manager):
        """PT02 센서 매니저 설정"""
        self.pt02_sensor_manager = pt02_manager
        self.log_message("PT02 센서 매니저 연결됨")

    def parse_pt02_response(self, data):
        """PT02 센서 응답 데이터 파싱
        형식: [AIRCON] CO2,PM2.5,TEMP (예: [AIRCON] 850,35,253)
        """
        try:
            if "[AIRCON]" in data:
                # [AIRCON] 이후 데이터 추출
                parts = data.split("[AIRCON]")[1].strip()
                values = parts.split(",")

                if len(values) >= 3:
                    co2 = int(values[0].strip())
                    pm25 = int(values[1].strip())
                    temp = float(values[2].strip()) / 10.0  # 온도는 10으로 나눔

                    # UI 업데이트
                    self.update_pt02_sensor_display(temp=temp, co2=co2, pm25=pm25)

                    # PT02 센서 매니저를 통해 CSV 저장
                    if self.pt02_sensor_manager:
                        self.pt02_sensor_manager.save_sensor_data(temp, co2, pm25)

                    self.log_message(f"PT02 센서: 온도={temp}°C, CO2={co2}ppm, PM2.5={pm25}µg/m³")
                    return True
        except Exception as e:
            self.log_message(f"PT02 응답 파싱 오류: {e}")

        return False

    def parse_getset_response(self, data):
        """GETSET 응답 데이터 파싱
        형식: AIRCON,TEMPSET,250,20 / AIRCON,CO2SET,1000,100 등
        """
        try:
            if "AIRCON,TEMPSET," in data:
                parts = data.split(",")
                if len(parts) >= 4:
                    self.temp_value = float(parts[2]) / 10.0
                    self.temp_hyst = float(parts[3]) / 10.0
                    self._update_button_text(self.temp_buttons, 'value', f"{self.temp_value:.1f}")
                    self._update_button_text(self.temp_buttons, 'hyst_value', f"{self.temp_hyst:.1f}")
                    self.log_message(f"온도 설정 수신: {self.temp_value}±{self.temp_hyst}°C")
                    return True

            elif "AIRCON,CO2SET," in data:
                parts = data.split(",")
                if len(parts) >= 4:
                    self.co2_value = int(parts[2])
                    self.co2_hyst = int(parts[3])
                    self._update_button_text(self.co2_buttons, 'value', str(self.co2_value))
                    self._update_button_text(self.co2_buttons, 'hyst_value', str(self.co2_hyst))
                    self.log_message(f"CO2 설정 수신: {self.co2_value}±{self.co2_hyst}ppm")
                    return True

            elif "AIRCON,PM25SET," in data:
                parts = data.split(",")
                if len(parts) >= 4:
                    self.pm25_value = int(parts[2])
                    self.pm25_hyst = int(parts[3])
                    self._update_button_text(self.pm25_buttons, 'value', str(self.pm25_value))
                    self._update_button_text(self.pm25_buttons, 'hyst_value', str(self.pm25_hyst))
                    self.log_message(f"PM2.5 설정 수신: {self.pm25_value}±{self.pm25_hyst}µg/m³")
                    return True

            elif "AIRCON,SEMITIME," in data:
                parts = data.split(",")
                if len(parts) >= 3:
                    self.semi_time = int(parts[2])
                    self._update_button_text(self.time_buttons, 'value', str(self.semi_time))
                    self.log_message(f"SEMI 시간 수신: {self.semi_time}초")
                    return True

        except Exception as e:
            self.log_message(f"GETSET 응답 파싱 오류: {e}")

        return False


    # ============================================
    # 기존 코드와의 호환성을 위한 메서드들
    # ============================================
    def set_speed_button_manager(self, speed_manager):
        """기존 코드 호환성 - SpeedButtonManager 참조 (현재 사용 안함)"""
        pass

    def update_from_manual(self, fan_speed):
        """기존 코드 호환성 - MANUAL 탭에서 호출 (현재 사용 안함)"""
        pass


# 기존 AutoSpeedManager와의 호환성을 위한 별칭
AutoSpeedManager = AutoModeManager
