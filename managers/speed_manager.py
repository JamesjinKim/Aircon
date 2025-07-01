from ui.constants import (CMD_PREFIX, TERMINATOR, AIR_SYSTEM, DSCT_SYSTEM, FSPD_CMD, CON_SPD_CMD, OFF_STATE, 
                         FAN1_CMD, FAN2_CMD, FAN3_CMD, FAN4_CMD, SPD_CMD,
                         DMP1_OPEN_CMD, DMP1_CLOSE_CMD, DMP2_OPEN_CMD, DMP2_CLOSE_CMD,
                         DMP3_OPEN_CMD, DMP3_CLOSE_CMD, DMP4_OPEN_CMD, DMP4_CLOSE_CMD,
                         PUMP1_CMD, PUMP2_CMD)

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
        
    def create_aircon_fan_speed_buttons(self, parent, left_button, center_button, right_button):
        """팬 스피드 버튼 설정 (<, 값, >)"""
        # 버튼 그룹 저장
        button_group = [left_button, center_button, right_button]
        self.center_button = center_button  # 중앙 버튼 저장
        self.fan_speed_buttons = button_group  # Fan SPD 버튼들 저장
        
        # 초기 값 설정
        center_button.setText("0")
        
        # 모든 버튼에 동일한 크기 및 스타일 설정
        self._configure_uniform_button_size(button_group)
        
        # 시그널 연결 - 왼쪽 버튼 (감소)
        left_button.clicked.connect(lambda: self.handle_decrease_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},",
            speed_var_name="current_fan_speed"
        ))
        
        # 시그널 연결 - 중앙 버튼 (0으로 리셋)
        center_button.clicked.connect(lambda: self.handle_reset_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},",
            speed_var_name="current_fan_speed"
        ))
        
        # 시그널 연결 - 오른쪽 버튼 (증가)
        right_button.clicked.connect(lambda: self.handle_increase_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{FSPD_CMD},",
            speed_var_name="current_fan_speed"
        ))
            
    def create_aircon_con_fan_speed_buttons(self, parent, left_button, center_button, right_button):
        """콘 팬 스피드 버튼 설정 (<, 값, >)"""
        # 버튼 그룹 저장
        button_group = [left_button, center_button, right_button]
        self.con_fan_speed_buttons = button_group  # Con Fan SPD 버튼들 저장
        
        # 초기 값 설정
        center_button.setText("0")
        
        # 모든 버튼에 동일한 크기 및 스타일 설정
        self._configure_uniform_button_size(button_group)
        
        # 시그널 연결 - 왼쪽 버튼 (감소)
        left_button.clicked.connect(lambda: self.handle_decrease_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},",
            speed_var_name="current_con_fan_speed"
        ))
        
        # 시그널 연결 - 중앙 버튼 (0으로 리셋)
        center_button.clicked.connect(lambda: self.handle_reset_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},",
            speed_var_name="current_con_fan_speed"
        ))
        
        # 시그널 연결 - 오른쪽 버튼 (증가)
        right_button.clicked.connect(lambda: self.handle_increase_button(
            button=center_button,
            command_prefix=f"{CMD_PREFIX},{AIR_SYSTEM},{CON_SPD_CMD},",
            speed_var_name="current_con_fan_speed"
        ))
    
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