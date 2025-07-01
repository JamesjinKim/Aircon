from ui.constants import (CMD_PREFIX, TERMINATOR, AIR_SYSTEM, DSCT_SYSTEM, FSPD_CMD, CON_SPD_CMD, OFF_STATE, ON_STATE,
                         FAN_CMD, FAN1_CMD, FAN2_CMD, FAN3_CMD, FAN4_CMD, SPD_CMD,
                         DMP1_OPEN_CMD, DMP1_CLOSE_CMD, DMP2_OPEN_CMD, DMP2_CLOSE_CMD,
                         DMP3_OPEN_CMD, DMP3_CLOSE_CMD, DMP4_OPEN_CMD, DMP4_CLOSE_CMD,
                         PUMP1_CMD, PUMP2_CMD, BUTTON_ON_STYLE, BUTTON_OFF_STYLE)

class SpeedButtonManager:
    def __init__(self, serial_manager, SendData_textEdit):
        self.serial_manager = serial_manager
        self.SendData_textEdit = SendData_textEdit
        self.button_groups = {}
        self.current_fan_speed = 0  # 현재 팬 속도 값 저장
        self.current_con_fan_speed = 0  # 현재 Con 팬 속도 값 저장
        
        # DESICCANT FAN 속도 값들
        self.current_dsct_fan1_speed = 0
        self.current_dsct_fan2_speed = 0
        self.current_dsct_fan3_speed = 0
        self.current_dsct_fan4_speed = 0
        
        # DAMPER 위치 값들 (단일 위치값)
        self.current_dmp1_pos = 0
        self.current_dmp2_pos = 0
        self.current_dmp3_pos = 0
        self.current_dmp4_pos = 0
        
        # PUMPER 속도 값들
        self.current_pump1_speed = 0
        self.current_pump2_speed = 0
        self.auto_speed_manager = None  # AUTO 매니저 참조 추가
        self.is_updating = False  # 동기화 중 무한 루프 방지용 플래그
        self.center_button = None  # 중앙 버튼(팬 속도 표시) 저장
        
        # 의존성 관리를 위한 변수들
        self.main_window = None  # 메인 윈도우 참조
        self.fan_speed_buttons = []  # Fan SPD 버튼들
        self.con_fan_speed_buttons = []  # Con Fan SPD 버튼들
        
    def set_auto_manager(self, auto_manager):
        """AUTO 모드 매니저 참조 설정"""
        self.auto_speed_manager = auto_manager
    
    def set_main_window(self, main_window):
        """메인 윈도우 참조 설정"""
        self.main_window = main_window
        
    # REMOVED: create_aircon_fan_speed_buttons 및 create_aircon_con_fan_speed_buttons 메소드
    # 이전 spdButton_2,3,4 및 spdButton_6,7,8 버튼들이 더 이상 생성되지 않아 사용되지 않는 메소드
    
    # 새로운 헬퍼 메서드 추가
    def _configure_uniform_button_size(self, buttons):
        """모든 버튼에 동일한 크기 및 스타일 설정"""
        from PyQt5.QtWidgets import QSizePolicy
        
        for button in buttons:
            # 크기 설정 - 크기 증가
            button.setMinimumWidth(50)
            button.setMinimumHeight(45)
            button.setMaximumWidth(70)
            button.setFixedSize(50, 45)  # 모든 버튼의 크기를 완전히 동일하게 설정
            
            # 크기 정책 설정
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            
            # 스타일 설정 (기존 스타일시트 유지)
            button.setStyleSheet("background-color: rgb(186,186,186);")
    
    def _can_operate_fan_speed_buttons(self):
        """Fan SPD 버튼들이 작동 가능한지 확인"""
        # 시리얼 포트 연결 확인
        if not self.serial_manager.is_connected():
            return False
            
        # FAN 버튼 상태 확인
        if self.main_window and hasattr(self.main_window, 'button_manager'):
            fan_group = self.main_window.button_manager.button_groups.get('aircon_fan')
            if fan_group and fan_group.get('active') is not True:
                return False
                
        return True
    
    def _can_operate_con_fan_speed_buttons(self):
        """Con Fan SPD 버튼들이 작동 가능한지 확인"""
        # 시리얼 포트 연결 확인
        if not self.serial_manager.is_connected():
            return False
            
        # Con Fan 버튼 상태 확인
        if self.main_window and hasattr(self.main_window, 'button_manager'):
            con_fan_group = self.main_window.button_manager.button_groups.get('aircon_con_fan')
            if con_fan_group and con_fan_group.get('active') is not True:
                return False
                
        return True

    def handle_decrease_button(self, button, command_prefix, speed_var_name):
        """감소 버튼 핸들러 (< 버튼)"""
        # 의존성 확인
        if speed_var_name == "current_fan_speed" and not self._can_operate_fan_speed_buttons():
            print("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
            
        if speed_var_name == "current_con_fan_speed" and not self._can_operate_con_fan_speed_buttons():
            print("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
        
        # 현재 값 가져오기
        current_speed = getattr(self, speed_var_name)
        
        # 최소값을 1로 제한 (FAN이 ON인 상태에서는 1이 최소값)
        if current_speed > 1:
            current_speed -= 1
            setattr(self, speed_var_name, current_speed)
            
            # 버튼 텍스트 업데이트
            button.setText(str(current_speed))
            
            # 명령 전송
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
                
            self.send_command(command)
            
            # 팬 속도 변경 시 AUTO 탭과 동기화
            if speed_var_name == "current_fan_speed":
                self.sync_to_auto_tab(current_speed)
    
    def handle_increase_button(self, button, command_prefix, speed_var_name):
        """증가 버튼 핸들러 (> 버튼)"""
        # 의존성 확인
        if speed_var_name == "current_fan_speed" and not self._can_operate_fan_speed_buttons():
            print("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
            
        if speed_var_name == "current_con_fan_speed" and not self._can_operate_con_fan_speed_buttons():
            print("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
        
        # 현재 값 가져오기
        current_speed = getattr(self, speed_var_name)
        
        # 1씩 증가 (최대값 8)
        if current_speed < 8:
            current_speed += 1
            setattr(self, speed_var_name, current_speed)
            
            # 버튼 텍스트 업데이트
            button.setText(str(current_speed))
            
            # 명령 전송 - 항상 새로운 값을 즉시 전송
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
            self.send_command(command)
            
            # 팬 속도 변경 시 AUTO 탭과 동기화
            if speed_var_name == "current_fan_speed" and not self.is_updating:
                self.sync_to_auto_tab(current_speed)
    
    def handle_reset_button(self, button, command_prefix, speed_var_name):
        """중앙 버튼 핸들러 (값 버튼) - FAN이 ON인 상태에서는 1로 리셋"""
        # 의존성 확인
        if speed_var_name == "current_fan_speed" and not self._can_operate_fan_speed_buttons():
            print("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("FAN이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
            
        if speed_var_name == "current_con_fan_speed" and not self._can_operate_con_fan_speed_buttons():
            print("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("Con Fan이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - Con Fan SPD 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
        
        # FAN이 ON인 상태에서는 최소값이 1이므로 1로 설정
        setattr(self, speed_var_name, 1)
        
        # 버튼 텍스트 업데이트
        button.setText("1")
        
        # 1 명령 전송
        command = f"{command_prefix}1{TERMINATOR}"
        self.send_command(command)
        
        # 팬 속도 변경 시 AUTO 탭과 동기화
        if speed_var_name == "current_fan_speed":
            self.sync_to_auto_tab(1)
    
    def send_command(self, command):
        """명령어 전송"""
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"스피드 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command.rstrip()}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
        else:
            print("시리얼 포트 연결되지 않음.")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("시리얼 포트 연결되지 않음.")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )

    def create_dsct_fan_speed_buttons(self, parent, fan_num, left_button, center_button, right_button):
        """DESICCANT FAN 스피드 버튼 설정"""
        fan_commands = {
            1: FAN1_CMD,
            2: FAN2_CMD,
            3: FAN3_CMD,
            4: FAN4_CMD
        }
        
        fan_cmd = fan_commands.get(fan_num)
        if not fan_cmd:
            return
            
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{fan_cmd},{SPD_CMD},"
        
        # 감소 버튼 (< 버튼)
        left_button.clicked.connect(
            lambda: self.handle_dsct_decrease_button(center_button, command_prefix, speed_var_name, fan_num)
        )
        
        # 중앙 버튼 (값 표시/리셋 버튼)
        center_button.clicked.connect(
            lambda: self.handle_dsct_reset_button(center_button, command_prefix, speed_var_name, fan_num)
        )
        
        # 증가 버튼 (> 버튼)
        right_button.clicked.connect(
            lambda: self.handle_dsct_increase_button(center_button, command_prefix, speed_var_name, fan_num)
        )

    def handle_dsct_decrease_button(self, button, command_prefix, speed_var_name, fan_num):
        """DSCT FAN 감소 버튼 핸들러"""
        if not self._can_operate_dsct_fan_buttons(fan_num):
            self._log_dsct_blocked_message(fan_num)
            return
            
        current_speed = getattr(self, speed_var_name)
        # 최소값을 1로 제한 (FAN이 ON인 상태에서는 1이 최소값)
        if current_speed > 1:
            current_speed -= 1
            setattr(self, speed_var_name, current_speed)
            button.setText(str(current_speed))
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
            self.send_command(command)

    def handle_dsct_increase_button(self, button, command_prefix, speed_var_name, fan_num):
        """DSCT FAN 증가 버튼 핸들러"""
        if not self._can_operate_dsct_fan_buttons(fan_num):
            self._log_dsct_blocked_message(fan_num)
            return
            
        current_speed = getattr(self, speed_var_name)
        if current_speed < 8:
            current_speed += 1
            setattr(self, speed_var_name, current_speed)
            button.setText(str(current_speed))
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
            self.send_command(command)

    def handle_dsct_reset_button(self, button, command_prefix, speed_var_name, fan_num):
        """DSCT FAN 리셋 버튼 핸들러 - FAN이 ON인 상태에서는 1로 설정"""
        if not self._can_operate_dsct_fan_buttons(fan_num):
            self._log_dsct_blocked_message(fan_num)
            return
            
        # FAN이 ON인 상태에서는 최소값이 1이므로 1로 설정
        setattr(self, speed_var_name, 1)
        button.setText("1")
        command = f"{command_prefix}1{TERMINATOR}"
        self.send_command(command)

    def _can_operate_dsct_fan_buttons(self, fan_num):
        """DSCT FAN 버튼 작동 가능 여부 확인"""
        if not self.main_window or not self.serial_manager or not self.serial_manager.is_connected():
            return False
            
        fan_button_name = f"pushButton_dsct_fan{fan_num}"
        fan_button = getattr(self.main_window, fan_button_name, None)
        if not fan_button:
            return False
            
        return fan_button.text() == "ON"

    def _log_dsct_blocked_message(self, fan_num):
        """DSCT FAN 버튼 차단 메시지 로깅"""
        message = f"FAN{fan_num}이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - FAN{fan_num} SPD 버튼 동작 차단"
        print(message)
        if self.SendData_textEdit:
            self.SendData_textEdit.append(message)
            self.SendData_textEdit.verticalScrollBar().setValue(
                self.SendData_textEdit.verticalScrollBar().maximum()
            )

    def reset_dsct_fan_speed_buttons(self, fan_num):
        """DSCT FAN 스피드 버튼 초기화"""
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        button_name = f"spdButton_dsct_fan{fan_num}_val"
        
        # 속도 값 초기화
        setattr(self, speed_var_name, 0)
        
        # 중앙 버튼 텍스트 초기화
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("0")
            
        print(f"DSCT FAN{fan_num} 스피드 버튼 초기화됨")
    
    def set_dsct_fan_speed_to_one(self, fan_num):
        """DSCT FAN이 ON될 때 스피드 버튼을 1로 설정"""
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        button_name = f"spdButton_dsct_fan{fan_num}_val"
        
        # 속도 값을 1로 설정
        setattr(self, speed_var_name, 1)
        
        # 중앙 버튼 텍스트를 1로 변경
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("1")
        
        # 스피드 1 명령 전송
        fan_commands = {
            1: FAN1_CMD,
            2: FAN2_CMD,
            3: FAN3_CMD,
            4: FAN4_CMD
        }
        
        fan_cmd = fan_commands.get(fan_num)
        if fan_cmd:
            command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{fan_cmd},{SPD_CMD},"
            command = f"{command_prefix}1{TERMINATOR}"
            self.send_command(command)
            
        print(f"DSCT FAN{fan_num} 스피드 버튼을 1로 설정됨")

    def create_damper_position_buttons(self, parent, dmp_num, left_button, center_button, right_button):
        """DAMPER 위치 버튼 설정"""
        pos_var_name = f"current_dmp{dmp_num}_pos"
        
        # 감소 버튼 (< 버튼)
        left_button.clicked.connect(
            lambda: self.handle_damper_decrease_button(center_button, pos_var_name, dmp_num)
        )
        
        # 중앙 버튼 (값 표시/리셋 버튼)
        center_button.clicked.connect(
            lambda: self.handle_damper_reset_button(center_button, pos_var_name, dmp_num)
        )
        
        # 증가 버튼 (> 버튼)
        right_button.clicked.connect(
            lambda: self.handle_damper_increase_button(center_button, pos_var_name, dmp_num)
        )

    def handle_damper_decrease_button(self, button, pos_var_name, dmp_num):
        """DAMPER 감소 버튼 핸들러"""
        # 시리얼 포트 연결 상태 확인
        if not self.serial_manager or not self.serial_manager.is_connected():
            self._log_damper_blocked_message(dmp_num)
            return
            
        current_pos = getattr(self, pos_var_name)
        if current_pos > 0:
            current_pos -= 1
            setattr(self, pos_var_name, current_pos)
            button.setText(str(current_pos))
            self._send_damper_command(dmp_num, current_pos)

    def handle_damper_increase_button(self, button, pos_var_name, dmp_num):
        """DAMPER 증가 버튼 핸들러"""
        # 시리얼 포트 연결 상태 확인
        if not self.serial_manager or not self.serial_manager.is_connected():
            self._log_damper_blocked_message(dmp_num)
            return
            
        current_pos = getattr(self, pos_var_name)
        if current_pos < 4:
            current_pos += 1
            setattr(self, pos_var_name, current_pos)
            button.setText(str(current_pos))
            self._send_damper_command(dmp_num, current_pos)

    def handle_damper_reset_button(self, button, pos_var_name, dmp_num):
        """DAMPER 리셋 버튼 핸들러"""
        # 시리얼 포트 연결 상태 확인
        if not self.serial_manager or not self.serial_manager.is_connected():
            self._log_damper_blocked_message(dmp_num)
            return
            
        setattr(self, pos_var_name, 0)
        button.setText("0")
        self._send_damper_command(dmp_num, 0)
    
    def _send_damper_command(self, dmp_num, position):
        """DAMPER 명령 전송 - position에 따라 OPEN/CLOSE 구분"""
        # position이 0이면 CLOSE, 1~4이면 OPEN 명령 전송
        if position == 0:
            dmp_commands = {
                1: DMP1_CLOSE_CMD,
                2: DMP2_CLOSE_CMD,
                3: DMP3_CLOSE_CMD,
                4: DMP4_CLOSE_CMD
            }
        else:
            dmp_commands = {
                1: DMP1_OPEN_CMD,
                2: DMP2_OPEN_CMD,
                3: DMP3_OPEN_CMD,
                4: DMP4_OPEN_CMD
            }
        
        dmp_cmd = dmp_commands.get(dmp_num)
        if dmp_cmd:
            command = f"{CMD_PREFIX},{DSCT_SYSTEM},{dmp_cmd},{position}{TERMINATOR}"
            self.send_command(command)

    def _log_damper_blocked_message(self, dmp_num):
        """DAMPER 버튼 차단 메시지 로깅"""
        message = f"시리얼 포트가 연결되지 않음 - DMP{dmp_num} 위치값 버튼 동작 차단"
        print(message)
        if self.SendData_textEdit:
            self.SendData_textEdit.append(message)
            self.SendData_textEdit.verticalScrollBar().setValue(
                self.SendData_textEdit.verticalScrollBar().maximum()
            )
                
    # AUTO 탭과 동기화하는 메서드
    def sync_to_auto_tab(self, fan_speed):
        """MANUAL 탭의 팬 속도를 AUTO 탭과 동기화"""
        if self.is_updating:
            return
            
        if self.auto_speed_manager and hasattr(self.auto_speed_manager, 'update_from_manual'):
            print(f"Manual -> Auto 동기화: {fan_speed}")
            self.is_updating = True
            self.auto_speed_manager.update_from_manual(fan_speed)
            self.is_updating = False
    
    # AUTO 탭에서 호출될 메서드
    def update_from_auto(self, fan_speed):
        """AUTO 탭에서의 변경을 MANUAL 탭에 반영"""
        if self.is_updating:
            return
            
        self.is_updating = True
        
        # current_fan_speed 업데이트
        self.current_fan_speed = fan_speed
        
        # 중앙 버튼(값 표시 버튼) 업데이트
        if self.center_button:
            self.center_button.setText(str(fan_speed))
        
        self.is_updating = False
    
    def set_fan_speed_to_one(self):
        """FAN이 ON될 때 스피드 버튼을 1로 설정"""
        print("FAN이 ON되어 Fan SPD 버튼을 1로 설정합니다.")
        
        # 속도 값을 1로 설정
        self.current_fan_speed = 1
        
        # 중앙 버튼(값 표시 버튼) 텍스트를 1로 변경
        if self.center_button:
            self.center_button.setText("1")
        
        # 1 명령어 전송
        command = f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},1{TERMINATOR}"
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"Fan SPD 1 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
        
        # AUTO 탭과 동기화
        self.sync_to_auto_tab(1)

    def reset_fan_speed_buttons(self):
        """FAN이 OFF될 때 Fan SPD 버튼들 초기화"""
        print("FAN이 OFF되어 Fan SPD 버튼들을 초기화합니다.")
        
        # 속도 값 초기화
        self.current_fan_speed = 0
        
        # 중앙 버튼(값 표시 버튼) 텍스트 초기화
        if self.center_button:
            self.center_button.setText("0")
        
        # 0 명령어 전송
        command = f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},0{TERMINATOR}"
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"Fan SPD 초기화 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
        
        # AUTO 탭과 동기화
        self.sync_to_auto_tab(0)

    def create_pumper_speed_buttons(self, parent, pump_num, left_button, center_button, right_button):
        """PUMPER 스피드 버튼 설정"""
        pump_commands = {
            1: PUMP1_CMD,
            2: PUMP2_CMD
        }
        
        pump_cmd = pump_commands.get(pump_num)
        if not pump_cmd:
            return
            
        speed_var_name = f"current_pump{pump_num}_speed"
        command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{pump_cmd},{SPD_CMD},"
        
        # 감소 버튼 (< 버튼)
        left_button.clicked.connect(
            lambda: self.handle_pumper_decrease_button(center_button, command_prefix, speed_var_name, pump_num)
        )
        
        # 중앙 버튼 (값 표시/리셋 버튼)
        center_button.clicked.connect(
            lambda: self.handle_pumper_reset_button(center_button, command_prefix, speed_var_name, pump_num)
        )
        
        # 증가 버튼 (> 버튼)
        right_button.clicked.connect(
            lambda: self.handle_pumper_increase_button(center_button, command_prefix, speed_var_name, pump_num)
        )

    def handle_pumper_decrease_button(self, button, command_prefix, speed_var_name, pump_num):
        """PUMPER 감소 버튼 핸들러"""
        if not self._can_operate_pumper_buttons(pump_num):
            self._log_pumper_blocked_message(pump_num)
            return
            
        current_speed = getattr(self, speed_var_name)
        if current_speed > 0:
            current_speed -= 1
            setattr(self, speed_var_name, current_speed)
            button.setText(str(current_speed))
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
            self.send_command(command)

    def handle_pumper_increase_button(self, button, command_prefix, speed_var_name, pump_num):
        """PUMPER 증가 버튼 핸들러"""
        if not self._can_operate_pumper_buttons(pump_num):
            self._log_pumper_blocked_message(pump_num)
            return
            
        current_speed = getattr(self, speed_var_name)
        if current_speed < 8:
            current_speed += 1
            setattr(self, speed_var_name, current_speed)
            button.setText(str(current_speed))
            command = f"{command_prefix}{current_speed}{TERMINATOR}"
            self.send_command(command)

    def handle_pumper_reset_button(self, button, command_prefix, speed_var_name, pump_num):
        """PUMPER 리셋 버튼 핸들러"""
        if not self._can_operate_pumper_buttons(pump_num):
            self._log_pumper_blocked_message(pump_num)
            return
            
        setattr(self, speed_var_name, 0)
        button.setText("0")
        command = f"{command_prefix}0{TERMINATOR}"
        self.send_command(command)

    def _can_operate_pumper_buttons(self, pump_num):
        """PUMPER 버튼 작동 가능 여부 확인"""
        if not self.main_window or not self.serial_manager or not self.serial_manager.is_connected():
            return False
            
        pump_button_name = f"pushButton_pump{pump_num}"
        pump_button = getattr(self.main_window, pump_button_name, None)
        if not pump_button:
            return False
            
        return pump_button.text() == "ON"

    def _log_pumper_blocked_message(self, pump_num):
        """PUMPER 버튼 차단 메시지 로깅"""
        message = f"PUMP{pump_num}이 OFF 상태이거나 시리얼 포트가 연결되지 않음 - PUMP{pump_num} SPD 버튼 동작 차단"
        print(message)
        if self.SendData_textEdit:
            self.SendData_textEdit.append(message)
            self.SendData_textEdit.verticalScrollBar().setValue(
                self.SendData_textEdit.verticalScrollBar().maximum()
            )

    def reset_pumper_speed_buttons(self, pump_num):
        """PUMPER 스피드 버튼 초기화"""
        speed_var_name = f"current_pump{pump_num}_speed"
        button_name = f"spdButton_pump{pump_num}_val"
        
        # 속도 값 초기화
        setattr(self, speed_var_name, 0)
        
        # 중앙 버튼 텍스트 초기화
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("0")
            
        print(f"PUMP{pump_num} 스피드 버튼 초기화됨")
    
    def set_con_fan_speed_to_one(self):
        """Con Fan이 ON될 때 스피드 버튼을 1로 설정"""
        print("Con Fan이 ON되어 Con Fan SPD 버튼을 1로 설정합니다.")
        
        # 속도 값을 1로 설정
        self.current_con_fan_speed = 1
        
        # Con Fan SPD 중앙 버튼 찾아서 텍스트를 1로 변경
        if len(self.con_fan_speed_buttons) >= 2:
            center_button = self.con_fan_speed_buttons[1]  # 중앙 버튼 (인덱스 1)
            center_button.setText("1")
        
        # 1 명령어 전송
        command = f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},1{TERMINATOR}"
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"Con Fan SPD 1 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )

    def reset_con_fan_speed_buttons(self):
        """Con Fan이 OFF될 때 Con Fan SPD 버튼들 초기화"""
        print("Con Fan이 OFF되어 Con Fan SPD 버튼들을 초기화합니다.")
        
        # 속도 값 초기화
        self.current_con_fan_speed = 0
        
        # Con Fan SPD 중앙 버튼 찾아서 텍스트 초기화 (spdButton_7)
        if len(self.con_fan_speed_buttons) >= 2:
            center_button = self.con_fan_speed_buttons[1]  # 중앙 버튼 (인덱스 1)
            center_button.setText("0")
        
        # OFF 명령어 전송
        command = f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},{OFF_STATE}{TERMINATOR}"
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"Con Fan SPD 초기화 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )

    # 새로운 순환 클릭 메서드들
    def create_cyclic_dsct_fan_button(self, fan_num, speed_button):
        """DESICCANT FAN 순환 스피드 버튼 설정 (FAN ON시 0~8 순환, FAN OFF시 변경 차단)"""
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        
        def cyclic_click():
            # 시리얼 연결 상태 확인
            if not self.serial_manager or not self.serial_manager.is_connected():
                print(f"시리얼 포트가 연결되지 않음 - FAN{fan_num} 동작 차단")
                if self.SendData_textEdit:
                    self.SendData_textEdit.append(f"시리얼 포트가 연결되지 않음 - FAN{fan_num} 동작 차단")
                    self.SendData_textEdit.verticalScrollBar().setValue(
                        self.SendData_textEdit.verticalScrollBar().maximum()
                    )
                return
            
            # FAN 상태 확인
            fan_button_name = f"pushButton_dsct_fan{fan_num}"
            fan_button = getattr(self.main_window, fan_button_name, None)
            
            if not fan_button:
                return
                
            current_speed = getattr(self, speed_var_name)
            current_fan_state = fan_button.text()
            
            if current_fan_state == "OFF":
                # FAN이 OFF 상태일 때: FAN 토글 버튼 클릭을 시뮬레이션하여 button_manager 통해 처리
                fan_button.click()  # button_manager의 토글 로직 실행
                
                # 토글 후 숫자를 1로 설정
                new_speed = 1
                setattr(self, speed_var_name, new_speed)
                speed_button.setText(str(new_speed))
                
                print(f"FAN{fan_num} OFF->ON 변경, 스피드 {new_speed}로 설정")
            else:
                # FAN이 ON일 때: 0~8 순환
                new_speed = (current_speed + 1) % 9
                setattr(self, speed_var_name, new_speed)
                speed_button.setText(str(new_speed))
                
                if new_speed == 0:
                    # 숫자가 0이 되면 FAN을 OFF로 변경
                    fan_button.click()  # button_manager의 토글 로직으로 OFF 처리
                    print(f"FAN{fan_num} 스피드 0 - 자동으로 OFF로 변경")
                else:
                    # SPD 명령 전송 (0이 아닐 때만)
                    fan_commands = {1: FAN1_CMD, 2: FAN2_CMD, 3: FAN3_CMD, 4: FAN4_CMD}
                    fan_cmd = fan_commands.get(fan_num)
                    if fan_cmd:
                        command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{fan_cmd},{SPD_CMD},"
                        command = f"{command_prefix}{new_speed}{TERMINATOR}"
                        self.send_command(command)
        
        speed_button.clicked.connect(cyclic_click)

    def create_cyclic_damper_button(self, dmp_num, position_button, toggle_button):
        """DAMPER 순환 위치 버튼 설정 (0~4 순환)"""
        pos_var_name = f"current_dmp{dmp_num}_pos"
        
        def cyclic_click():
            if not self.serial_manager or not self.serial_manager.is_connected():
                self._log_damper_blocked_message(dmp_num)
                return
                
            current_pos = getattr(self, pos_var_name)
            # 0~4 순환: 4 다음에는 0
            new_pos = (current_pos + 1) % 5
            setattr(self, pos_var_name, new_pos)
            position_button.setText(str(new_pos))
            
            # 토글 버튼 상태 및 색상 업데이트
            if new_pos == 0:
                toggle_button.setText("CLOSE")
                toggle_button.setStyleSheet(BUTTON_OFF_STYLE)
            else:
                toggle_button.setText("OPEN")
                toggle_button.setStyleSheet(BUTTON_ON_STYLE)
            
            # 명령 전송
            self._send_damper_command(dmp_num, new_pos)
        
        position_button.clicked.connect(cyclic_click)

    def create_damper_toggle_button(self, dmp_num, toggle_button, position_button):
        """DAMPER 토글 버튼 설정 (CLOSE/OPEN 토글)"""
        pos_var_name = f"current_dmp{dmp_num}_pos"
        
        def toggle_click():
            if not self.serial_manager or not self.serial_manager.is_connected():
                self._log_damper_blocked_message(dmp_num)
                return
            
            current_pos = getattr(self, pos_var_name)
            current_text = toggle_button.text()
            
            if current_text == "CLOSE":
                # CLOSE -> OPEN으로 변경, position을 1로 설정
                toggle_button.setText("OPEN")
                toggle_button.setStyleSheet(BUTTON_ON_STYLE)  # Green 색상
                if current_pos == 0:
                    new_pos = 1
                    setattr(self, pos_var_name, new_pos)
                    position_button.setText(str(new_pos))
                    self._send_damper_command(dmp_num, new_pos)
            else:
                # OPEN -> CLOSE로 변경, position을 0으로 설정
                toggle_button.setText("CLOSE")
                toggle_button.setStyleSheet(BUTTON_OFF_STYLE)  # 기본 색상
                setattr(self, pos_var_name, 0)
                position_button.setText("0")
                self._send_damper_command(dmp_num, 0)
        
        toggle_button.clicked.connect(toggle_click)

    def reset_new_dsct_fan_speed_button(self, fan_num):
        """새로운 DSCT FAN 스피드 버튼 초기화 (OFF일 때 0으로)"""
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        button_name = f"speedButton_dsct_fan{fan_num}"
        
        # 속도 값 초기화
        setattr(self, speed_var_name, 0)
        
        # 스피드 버튼 텍스트 초기화
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("0")
            
        print(f"DSCT FAN{fan_num} 새로운 스피드 버튼 초기화됨")
    
    def set_new_dsct_fan_speed_to_one(self, fan_num):
        """새로운 DSCT FAN이 ON될 때 스피드 버튼을 1로 설정"""
        speed_var_name = f"current_dsct_fan{fan_num}_speed"
        button_name = f"speedButton_dsct_fan{fan_num}"
        
        # 속도 값을 1로 설정
        setattr(self, speed_var_name, 1)
        
        # 스피드 버튼 텍스트를 1로 변경
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("1")
        
        # 스피드 1 명령 전송
        fan_commands = {1: FAN1_CMD, 2: FAN2_CMD, 3: FAN3_CMD, 4: FAN4_CMD}
        fan_cmd = fan_commands.get(fan_num)
        if fan_cmd:
            command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{fan_cmd},{SPD_CMD},"
            command = f"{command_prefix}1{TERMINATOR}"
            self.send_command(command)
            
        print(f"DSCT FAN{fan_num} 새로운 스피드 버튼을 1로 설정됨")
    
    def set_pump_speed_to_one(self, pump_num):
        """PUMP이 ON될 때 스피드 버튼을 1로 설정"""
        speed_var_name = f"current_pump{pump_num}_speed"
        button_name = f"spdButton_pump{pump_num}_val"
        
        # 속도 값을 1로 설정
        setattr(self, speed_var_name, 1)
        
        # 스피드 버튼 텍스트를 1로 변경
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("1")
        
        # 스피드 1 명령 전송
        pump_commands = {1: PUMP1_CMD, 2: PUMP2_CMD}
        pump_cmd = pump_commands.get(pump_num)
        if pump_cmd:
            command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{pump_cmd},{SPD_CMD},"
            command = f"{command_prefix}1{TERMINATOR}"
            self.send_command(command)
            
        print(f"PUMP{pump_num} 스피드 버튼을 1로 설정됨")
    
    def create_cyclic_pump_button(self, pump_num, speed_button):
        """PUMP 순환 스피드 버튼 설정 (0~8 순환) - DESICCANT FAN과 동일한 동작"""
        speed_var_name = f"current_pump{pump_num}_speed"
        
        def cyclic_click():
            if not self.serial_manager or not self.serial_manager.is_connected():
                print(f"PUMP{pump_num} 시리얼 포트 연결되지 않음 - 버튼 동작 차단")
                if self.SendData_textEdit:
                    self.SendData_textEdit.append(f"PUMP{pump_num} 시리얼 포트 연결되지 않음 - 버튼 동작 차단")
                return
                
            # PUMP 버튼 상태 확인
            pump_button = getattr(self.main_window, f"pushButton_pump{pump_num}", None)
            if not pump_button:
                return
                
            # button_manager에서 PUMP 상태 확인
            if self.main_window and hasattr(self.main_window, 'button_manager'):
                pump_group = self.main_window.button_manager.button_groups.get(f'pump{pump_num}')
                current_pump_state = pump_group.get('active', False) if pump_group else False
            else:
                current_pump_state = False
                
            current_speed = getattr(self, speed_var_name)
            
            if current_pump_state is not True:
                # PUMP가 OFF 상태에서 숫자 버튼 클릭 시 자동으로 ON + 1로 설정
                pump_button.click()  # Auto-toggle to ON
                new_speed = 1
            else:
                # PUMP가 ON 상태에서는 0~8 순환
                new_speed = (current_speed + 1) % 9
                if new_speed == 0:
                    # 숫자가 0이 되면 PUMP를 OFF로 변경
                    pump_button.click()  # button_manager의 토글 로직으로 OFF 처리
                    print(f"PUMP{pump_num} 스피드 0 - 자동으로 OFF로 변경")
                else:
                    # SPD 명령 전송 (0이 아닐 때만)
                    pump_commands = {1: PUMP1_CMD, 2: PUMP2_CMD}
                    pump_cmd = pump_commands.get(pump_num)
                    if pump_cmd:
                        command_prefix = f"{CMD_PREFIX},{DSCT_SYSTEM},{pump_cmd},{SPD_CMD},"
                        command = f"{command_prefix}{new_speed}{TERMINATOR}"
                        self.send_command(command)
            
            # 버튼 텍스트 및 내부 변수 업데이트
            setattr(self, speed_var_name, new_speed)
            speed_button.setText(str(new_speed))
            print(f"PUMP{pump_num} 스피드 변경: {new_speed}")
        
        speed_button.clicked.connect(cyclic_click)
    
    def create_new_pump_buttons(self, pump_num, speed_button):
        """새로운 PUMP 버튼 설정 - DESICCANT FAN과 동일한 패턴"""
        # 순환 스피드 버튼 설정
        self.create_cyclic_pump_button(pump_num, speed_button)
        
        print(f"PUMP{pump_num} 새로운 버튼 설정 완료")
    
    def reset_new_pump_speed_button(self, pump_num):
        """새로운 PUMP 스피드 버튼 초기화 (OFF일 때 0으로)"""
        speed_var_name = f"current_pump{pump_num}_speed"
        button_name = f"speedButton_pump{pump_num}"
        
        # 속도 값 초기화
        setattr(self, speed_var_name, 0)
        
        # 스피드 버튼 텍스트 초기화
        if self.main_window and hasattr(self.main_window, button_name):
            button = getattr(self.main_window, button_name)
            button.setText("0")
            
        print(f"PUMP{pump_num} 새로운 스피드 버튼 초기화됨")
    
    def create_eva_fan_cycle_button(self, fan_type, button):
        """EVA FAN 순환 버튼 설정 (OFF,1,2,3,4,5,6,7,8)"""
        
        def cycle_click():
            if not self.serial_manager or not self.serial_manager.is_connected():
                print(f"{fan_type} 시리얼 포트 연결되지 않음 - 버튼 동작 차단")
                if self.SendData_textEdit:
                    self.SendData_textEdit.append(f"{fan_type} 시리얼 포트 연결되지 않음 - 버튼 동작 차단")
                return
            
            current_text = button.text()
            
            if current_text == "OFF":
                # OFF → 1
                new_value = 1
                button.setText("1")
                # ON 명령 전송
                if fan_type == "EVA FAN":
                    on_command = f"{CMD_PREFIX},{AIR_SYSTEM},{FAN_CMD},{ON_STATE}{TERMINATOR}"
                    speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},{new_value}{TERMINATOR}"
                elif fan_type == "CONDENSOR FAN":
                    on_command = f"{CMD_PREFIX},{AIR_SYSTEM},CON_F,{ON_STATE}{TERMINATOR}"
                    speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},{new_value}{TERMINATOR}"
                
                self.send_command(on_command)
                self.send_command(speed_command)
            elif current_text == "ON":
                # button_manager에 의해 ON으로 변경된 경우 → 1로 설정
                button.setText("1")
                # 스피드 1 명령 전송
                if fan_type == "EVA FAN":
                    speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},1{TERMINATOR}"
                elif fan_type == "CONDENSOR FAN":
                    speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},1{TERMINATOR}"
                
                self.send_command(speed_command)
            else:
                # 1~5 순환, 5 다음에는 OFF
                try:
                    current_value = int(current_text)
                except ValueError:
                    # 숫자가 아닌 경우 1로 리셋
                    current_value = 1
                    button.setText("1")
                
                if current_value == 5:  # 5 → OFF
                    button.setText("OFF")
                    # OFF 명령 전송
                    if fan_type == "EVA FAN":
                        off_command = f"{CMD_PREFIX},{AIR_SYSTEM},{FAN_CMD},{OFF_STATE}{TERMINATOR}"
                    elif fan_type == "CONDENSOR FAN":
                        off_command = f"{CMD_PREFIX},{AIR_SYSTEM},CON_F,{OFF_STATE}{TERMINATOR}"
                    
                    self.send_command(off_command)
                else:
                    # 1~4 → 2~5
                    new_value = current_value + 1
                    button.setText(str(new_value))
                    # 스피드 명령 전송
                    if fan_type == "EVA FAN":
                        speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},{new_value}{TERMINATOR}"
                    elif fan_type == "CONDENSOR FAN":
                        speed_command = f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},{new_value}{TERMINATOR}"
                    
                    self.send_command(speed_command)
            
            print(f"{fan_type} 값 변경: {button.text()}")
        
        button.clicked.connect(cycle_click)