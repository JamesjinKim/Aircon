class ButtonManager:
    def __init__(self, serial_manager, SendData_textEdit, ReceiveData_textEdit):
        self.serial_manager = serial_manager 
        self.SendData_textEdit = SendData_textEdit 
        self.ReceiveData_textEdit = ReceiveData_textEdit 
        self.button_groups = {}
        self.speed_button_manager = None  # SpeedButtonManager 참조 
    
    def set_speed_button_manager(self, speed_button_manager):
        """SpeedButtonManager 참조 설정"""
        self.speed_button_manager = speed_button_manager
        
    def add_group(self, name, buttons):
        """버튼 그룹 추가"""
        try: 
            self.button_groups[name] = {
                'buttons': buttons,
                'active': None
            }
            
            for button, commands in buttons.items():
                # 기존 연결된 시그널 제거
                try:
                    button.clicked.disconnect()
                except TypeError:
                    pass
                
                print(f"연결 중: 버튼={button.objectName()}, 명령어={commands}")
                
                # 슬롯 연결
                button.clicked.connect(
                    lambda checked, b=button, cmds=commands, n=name: self._toggle_button(n, b, cmds)
                )
        except Exception as e:
            print(f"버튼 그룹 추가 중 오류 발생: {e}")

    def _toggle_button(self, group_name, button, commands):
        """버튼 토글 처리"""
        print(f"_toggle_button 호출됨: 그룹={group_name}, 버튼={button.objectName()}")
        
        # 시리얼 포트 연결 확인
        if not self.serial_manager.is_connected():
            print("시리얼 포트가 연결되지 않음 - 버튼 동작 차단")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("시리얼 포트가 연결되지 않음 - 버튼 동작 차단")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            return
        
        try:
            group = self.button_groups[group_name]
            
            # 원래 크기 저장
            original_size = button.size()
            
            # 명령어 문자열에 따라 버튼 텍스트 결정
            if "OPEN" in commands.get('on', '').upper():
                on_text = "OPEN"
                off_text = "CLOSE"
            else:
                on_text = "ON"
                off_text = "OFF"

            # 단일 버튼 토글인 경우 (버튼이 1개만 등록된 그룹)
            if len(group['buttons']) == 1:
                # group['active']를 Boolean으로 사용 (False: OFF, True: ON)
                if group.get('active', False) is not True:
                    # OFF 상태 -> ON 상태로 전환
                    button.setStyleSheet("background-color: rgb(43, 179, 43); color: rgb(255,255,255); font-weight: bold;")  
                    button.setText(on_text)
                    self.send_command(commands.get('on'))
                    group['active'] = True
                else:
                    # ON 상태 -> OFF 상태로 전환
                    button.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal")
                    button.setText(off_text)
                    self.send_command(commands.get('off'))
                    group['active'] = False
                    
                    # FAN이나 Con Fan이 OFF될 때 해당 SPD 버튼들 초기화
                    self._handle_fan_off_callback(group_name)
            else:
                # 다중 버튼 그룹인 경우
                if group['active'] == button:
                    # 같은 버튼을 다시 눌렀을 때 -> OFF 상태로 전환
                    button.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal;")
                    self.send_command(commands.get('off'))
                    group['active'] = None
                    
                    # FAN이나 Con Fan이 OFF될 때 해당 SPD 버튼들 초기화
                    self._handle_fan_off_callback(group_name)
                else:
                    # 다른 버튼을 다시 눌렀을 때 -> 이전 버튼은 OFF, 현재 버튼은 ON
                    for other_btn in group['buttons'].keys():
                        other_btn.setStyleSheet("background-color: rgb(186,186,186); color: rgb(0,0,0); font-weight: normal;")
                    button.setStyleSheet("background-color: rgb(43, 179, 43); color: rgb(255,255,255); font-weight: bold;")
                    self.send_command(commands.get('on'))
                    group['active'] = button
                    
            # 버튼 크기 유지 - 스타일시트 변경 후 다시 크기 적용
            button.setFixedSize(original_size)
            
        except Exception as e:
            print(f"버튼 토글 처리 중 오류 발생: {e}")
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"버튼 토글 오류: {e}")

    def send_command(self, command):
        """명령어 전송"""
        try:
            if self.serial_manager.is_connected():
                self.serial_manager.shinho_serial_connection.write(f"{command}\r".encode())
                print(f"명령 전송: {command}")
                
                if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                    self.SendData_textEdit.append(f"{command.rstrip()}")
                    # 스크롤을 맨 아래로 이동
                    self.SendData_textEdit.verticalScrollBar().setValue(
                        self.SendData_textEdit.verticalScrollBar().maximum()
                    )
            else:
                print("시리얼 포트 연결되지 않음.")
                if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                    self.SendData_textEdit.append("시리얼 포트 연결되지 않음.")
                    # 스크롤을 맨 아래로 이동
                    self.SendData_textEdit.verticalScrollBar().setValue(
                        self.SendData_textEdit.verticalScrollBar().maximum()
                    )
        except Exception as e:
            print(f"명령 전송 실패 - 장치 연결 상태 확인 필요: {e}")
            if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                self.SendData_textEdit.append(f"명령 전송 실패 - 장치 연결 상태 확인 필요: {e}")
                # 스크롤을 맨 아래로 이동
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
    
    def _handle_fan_off_callback(self, group_name):
        """FAN이나 Con Fan이 OFF될 때 해당 SPD 버튼들 초기화 콜백"""
        if not self.speed_button_manager:
            return
            
        if group_name == 'aircon_fan':
            # FAN이 OFF될 때 Fan SPD 버튼들 초기화
            self.speed_button_manager.reset_fan_speed_buttons()
        elif group_name == 'aircon_con_fan':
            # Con Fan이 OFF될 때 Con Fan SPD 버튼들 초기화
            self.speed_button_manager.reset_con_fan_speed_buttons()