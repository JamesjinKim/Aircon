class SpeedButtonManager:
    def __init__(self, serial_manager, SendData_textEdit):
        self.serial_manager = serial_manager
        self.SendData_textEdit = SendData_textEdit
        self.button_groups = {}
        self.current_fan_speed = 0  # 현재 팬 속도 값 저장
        self.current_con_fan_speed = 0  # 현재 Con 팬 속도 값 저장
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
            command_prefix="$CMD,FSPD,",
            speed_var_name="current_fan_speed"
        ))
        
        # 시그널 연결 - 중앙 버튼 (0으로 리셋)
        center_button.clicked.connect(lambda: self.handle_reset_button(
            button=center_button,
            command_prefix="$CMD,FSPD,",
            speed_var_name="current_fan_speed"
        ))
        
        # 시그널 연결 - 오른쪽 버튼 (증가)
        right_button.clicked.connect(lambda: self.handle_increase_button(
            button=center_button,
            command_prefix="$CMD,FSPD,",
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
            command_prefix="$CMD,CON_SPD,",
            speed_var_name="current_con_fan_speed"
        ))
        
        # 시그널 연결 - 중앙 버튼 (0으로 리셋)
        center_button.clicked.connect(lambda: self.handle_reset_button(
            button=center_button,
            command_prefix="$CMD,CON_SPD,",
            speed_var_name="current_con_fan_speed"
        ))
        
        # 시그널 연결 - 오른쪽 버튼 (증가)
        right_button.clicked.connect(lambda: self.handle_increase_button(
            button=center_button,
            command_prefix="$CMD,CON_SPD,",
            speed_var_name="current_con_fan_speed"
        ))
    
    # 새로운 헬퍼 메서드 추가
    def _configure_uniform_button_size(self, buttons):
        """모든 버튼에 동일한 크기 및 스타일 설정"""
        from PyQt5.QtWidgets import QSizePolicy
        
        for button in buttons:
            # 크기 설정
            button.setMinimumWidth(40)
            button.setMinimumHeight(30)
            button.setMaximumWidth(60)
            button.setFixedSize(40, 30)  # 모든 버튼의 크기를 완전히 동일하게 설정
            
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
        
        # 1씩 감소 (최소값 0)
        if current_speed > 0:
            current_speed -= 1
            setattr(self, speed_var_name, current_speed)
            
            # 버튼 텍스트 업데이트
            button.setText(str(current_speed))
            
            # 명령 전송 (0인 경우 None으로 전송)
            if current_speed == 0:
                command = f"{command_prefix}None\r"
            else:
                command = f"{command_prefix}{current_speed}\r"
                
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
        
        # 1씩 증가 (최대값 10)
        if current_speed < 10:
            current_speed += 1
            setattr(self, speed_var_name, current_speed)
            
            # 버튼 텍스트 업데이트
            button.setText(str(current_speed))
            
            # 명령 전송 - 항상 새로운 값을 즉시 전송
            command = f"{command_prefix}{current_speed}\r"
            self.send_command(command)
            
            # 팬 속도 변경 시 AUTO 탭과 동기화
            if speed_var_name == "current_fan_speed" and not self.is_updating:
                self.sync_to_auto_tab(current_speed)
    
    def handle_reset_button(self, button, command_prefix, speed_var_name):
        """중앙 버튼 핸들러 (값 버튼) - 0으로 리셋"""
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
        
        # 속도 변수를 0으로 설정
        setattr(self, speed_var_name, 0)
        
        # 버튼 텍스트 업데이트
        button.setText("0")
        
        # None 명령 전송
        command = f"{command_prefix}None\r"
        self.send_command(command)
        
        # 팬 속도 변경 시 AUTO 탭과 동기화
        if speed_var_name == "current_fan_speed":
            self.sync_to_auto_tab(0)
    
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
    
    def reset_fan_speed_buttons(self):
        """FAN이 OFF될 때 Fan SPD 버튼들 초기화"""
        print("FAN이 OFF되어 Fan SPD 버튼들을 초기화합니다.")
        
        # 속도 값 초기화
        self.current_fan_speed = 0
        
        # 중앙 버튼(값 표시 버튼) 텍스트 초기화
        if self.center_button:
            self.center_button.setText("0")
        
        # None 명령어 전송
        command = "$CMD,FSPD,None\r"
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
    
    def reset_con_fan_speed_buttons(self):
        """Con Fan이 OFF될 때 Con Fan SPD 버튼들 초기화"""
        print("Con Fan이 OFF되어 Con Fan SPD 버튼들을 초기화합니다.")
        
        # 속도 값 초기화
        self.current_con_fan_speed = 0
        
        # Con Fan SPD 중앙 버튼 찾아서 텍스트 초기화 (spdButton_7)
        if len(self.con_fan_speed_buttons) >= 2:
            center_button = self.con_fan_speed_buttons[1]  # 중앙 버튼 (인덱스 1)
            center_button.setText("0")
        
        # None 명령어 전송
        command = "$CMD,CON_SPD,None\r"
        if self.serial_manager.is_connected():
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"Con Fan SPD 초기화 명령 전송: {command}")
            
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )