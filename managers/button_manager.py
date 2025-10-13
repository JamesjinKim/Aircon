from ui.constants import CMD_PREFIX, TERMINATOR, BUTTON_ON_STYLE, BUTTON_OFF_STYLE
import time

class ButtonManager:
    def __init__(self, serial_manager, SendData_textEdit, ReceiveData_textEdit, test_mode=False):
        self.serial_manager = serial_manager
        self.SendData_textEdit = SendData_textEdit
        self.ReceiveData_textEdit = ReceiveData_textEdit
        self.button_groups = {}
        self.speed_button_manager = None  # SpeedButtonManager 참조
        self.test_mode = test_mode  # 테스트 모드 플래그

        # RELOAD 기능 관련 변수
        self.dsct_reload_in_progress = False
        self.dsct_reload_data = []
        self.dsct_reload_start_time = None  # DSCT Reload 시작 시간
        self.air_reload_in_progress = False
        self.air_reload_data = []
        self.air_reload_start_time = None   # AIR Reload 시작 시간
        self.dsct_reload_button = None  # DSCT Reload 버튼 참조
        self.air_reload_button = None   # AIR Reload 버튼 참조
        self.dsct_reload_timer = None   # DSCT Reload 타임아웃 타이머
        self.air_reload_timer = None    # AIR Reload 타임아웃 타이머
        self.reload_timeout = 15000     # 타임아웃 시간 (ms) - 15초

        # SOL 제어 관련 변수 (15초 딜레이 + Flicker)
        self.sol_in_progress = False    # SOL 동작 진행 중 플래그
        self.sol_flicker_state = False  # Flicker 상태 토글
        self.sol_flicker_timer = None   # Flicker 타이머
        self.sol_timeout_timer = None   # SOL 타임아웃 타이머
        self.sol_timeout = 20000         # 타임아웃 시간 (ms) - 20초 
    
    def set_speed_button_manager(self, speed_button_manager):
        """SpeedButtonManager 참조 설정"""
        self.speed_button_manager = speed_button_manager

    def set_reload_buttons(self, dsct_button, air_button):
        """Reload 버튼 참조 설정"""
        self.dsct_reload_button = dsct_button
        self.air_reload_button = air_button
        
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
                
                print("연결 중: 버튼=%s, 명령어=%s" % (button.objectName(), commands))
                
                # 슬롯 연결
                button.clicked.connect(
                    lambda checked, b=button, cmds=commands, n=name: self._toggle_button(n, b, cmds)
                )
        except Exception as e:
            print("버튼 그룹 추가 중 오류 발생: %s" % e)

    def _toggle_button(self, group_name, button, commands):
        """버튼 토글 처리"""
        print("_toggle_button 호출됨: 그룹=%s, 버튼=%s" % (group_name, button.objectName()))

        # SOL1 진행 중이면 중복 클릭 방지
        if group_name == 'sol1' and self.sol_in_progress:
            print("[SOL] 이미 진행 중 - 클릭 무시")
            return

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
            
            # 명령어 문자열에 따라 버튼 텍스트 결정 (함수인 경우 처리)
            on_command = commands.get('on')
            if callable(on_command):
                # 함수인 경우 그룹 이름으로 판단
                if group_name == 'inverter':
                    on_text = "ON" 
                    off_text = "OFF"
                else:
                    on_text = "ON"
                    off_text = "OFF"
            else:
                # 문자열인 경우 기존 로직
                if on_command and "OPEN" in str(on_command).upper():
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
                    button.setStyleSheet(BUTTON_ON_STYLE)
                    button.setText(on_text)
                    self.send_command_or_call_function(commands.get('on'), group_name)
                    group['active'] = True

                    # FAN이 ON될 때 해당 SPD 버튼을 1로 설정
                    self._handle_fan_on_callback(group_name)
                else:
                    # ON 상태 -> OFF 상태로 전환
                    button.setStyleSheet(BUTTON_OFF_STYLE)
                    button.setText(off_text)
                    self.send_command_or_call_function(commands.get('off'), group_name)
                    group['active'] = False

                    # FAN이나 Con Fan이 OFF될 때 해당 SPD 버튼들 초기화
                    self._handle_fan_off_callback(group_name)
            else:
                # 다중 버튼 그룹인 경우
                if group['active'] == button:
                    # 같은 버튼을 다시 눌렀을 때 -> OFF 상태로 전환
                    button.setStyleSheet(BUTTON_OFF_STYLE)
                    self.send_command_or_call_function(commands.get('off'), group_name)
                    group['active'] = None

                    # FAN이나 Con Fan이 OFF될 때 해당 SPD 버튼들 초기화
                    self._handle_fan_off_callback(group_name)
                else:
                    # 다른 버튼을 다시 눌렀을 때 -> 이전 버튼은 OFF, 현재 버튼은 ON
                    for other_btn in group['buttons'].keys():
                        other_btn.setStyleSheet(BUTTON_OFF_STYLE)
                    button.setStyleSheet(BUTTON_ON_STYLE)
                    self.send_command_or_call_function(commands.get('on'), group_name)
                    group['active'] = button

                    # FAN이 ON될 때 해당 SPD 버튼을 1로 설정
                    self._handle_fan_on_callback(group_name)
                    
            # 버튼 크기 유지 - 스타일시트 변경 후 다시 크기 적용
            button.setFixedSize(original_size)
            
        except Exception as e:
            print("버튼 토글 처리 중 오류 발생: %s" % e)
            if self.SendData_textEdit:
                self.SendData_textEdit.append("버튼 토글 오류: %s" % e)

    def send_command_or_call_function(self, command_or_function, group_name=None):
        """명령어 전송 또는 함수 호출"""
        try:
            if callable(command_or_function):
                # 함수인 경우 호출
                print("함수 호출: %s" % command_or_function.__name__)
                command_or_function()
            else:
                # 문자열 명령어인 경우 기존 로직 사용
                self.send_command(command_or_function)

                # SOL1 명령인 경우 Flicker 시작
                if group_name == 'sol1' and 'SOL1' in command_or_function:
                    print("[SOL] SOL1 명령 감지 - Flicker 시작")
                    self._start_sol_flicker()
                    self._start_sol_timeout_timer()

                    # 테스트 모드: 더미 응답 시뮬레이션
                    if self.test_mode:
                        if 'ON' in command_or_function:
                            self._simulate_sol_open_response()
                        else:
                            self._simulate_sol_close_response()
        except Exception as e:
            print("명령어 처리 실패: %s" % e)
            if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                self.SendData_textEdit.append("명령어 처리 실패: %s" % e)
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )

    def send_command(self, command):
        """명령어 전송 (HIGH 우선순위)"""
        try:
            if self.serial_manager.is_connected():
                # 우선순위를 가진 명령 전송 시도 (큐 경유)
                if hasattr(self.serial_manager, 'send_serial_command_with_priority'):
                    from .command_queue_manager import CommandPriority
                    result = self.serial_manager.send_serial_command_with_priority(
                        command.rstrip(), CommandPriority.HIGH
                    )
                else:
                    # 레거시 전송 방식 (fallback)
                    result = self.serial_manager.send_serial_command(command.rstrip())
                
                if result:
                    print("[BUTTON] HIGH 우선순위 명령 전송: %s" % command)
                    
                    if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                        self.SendData_textEdit.append("%s" % command.rstrip())
                        # 스크롤을 맨 아래로 이동
                        self.SendData_textEdit.verticalScrollBar().setValue(
                            self.SendData_textEdit.verticalScrollBar().maximum()
                        )
                else:
                    print("명령 전송 실패: %s" % command)
                    if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                        self.SendData_textEdit.append("명령 전송 실패: %s" % command.rstrip())
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
            print("명령 전송 실패 - 장치 연결 상태 확인 필요: %s" % e)
            if hasattr(self, 'SendData_textEdit') and self.SendData_textEdit:
                self.SendData_textEdit.append("명령 전송 실패 - 장치 연결 상태 확인 필요: %s" % e)
                # 스크롤을 맨 아래로 이동
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
    
    def _handle_fan_on_callback(self, group_name):
        """FAN이 ON될 때 해당 SPD 버튼을 1로 설정 콜백"""
        if not self.speed_button_manager:
            return
            
        if group_name == 'aircon_fan':
            # AIRCON FAN이 ON될 때 SPD를 1로 설정
            self.speed_button_manager.set_fan_speed_to_one()
        elif group_name == 'aircon_con_fan':
            # AIRCON Con Fan이 ON될 때 SPD를 1로 설정
            self.speed_button_manager.set_con_fan_speed_to_one()
        elif group_name == 'dsct_fan1':
            # DSCT FAN1이 ON될 때 새로운 SPD를 1로 설정
            self.speed_button_manager.set_new_dsct_fan_speed_to_one(1)
        elif group_name == 'dsct_fan2':
            # DSCT FAN2이 ON될 때 새로운 SPD를 1로 설정
            self.speed_button_manager.set_new_dsct_fan_speed_to_one(2)
        elif group_name == 'dsct_fan3':
            # DSCT FAN3이 ON될 때 새로운 SPD를 1로 설정
            self.speed_button_manager.set_new_dsct_fan_speed_to_one(3)
        elif group_name == 'dsct_fan4':
            # DSCT FAN4이 ON될 때 새로운 SPD를 1로 설정
            self.speed_button_manager.set_new_dsct_fan_speed_to_one(4)
        elif group_name == 'pump1':
            # PUMP1이 ON될 때 SPD를 1로 설정
            self.speed_button_manager.set_pump_speed_to_one(1)
        elif group_name == 'pump2':
            # PUMP2이 ON될 때 SPD를 1로 설정
            self.speed_button_manager.set_pump_speed_to_one(2)

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
        elif group_name == 'dsct_fan1':
            # DSCT FAN1이 OFF될 때 새로운 SPD 초기화
            self.speed_button_manager.reset_new_dsct_fan_speed_button(1)
        elif group_name == 'dsct_fan2':
            # DSCT FAN2이 OFF될 때 새로운 SPD 초기화
            self.speed_button_manager.reset_new_dsct_fan_speed_button(2)
        elif group_name == 'dsct_fan3':
            # DSCT FAN3이 OFF될 때 새로운 SPD 초기화
            self.speed_button_manager.reset_new_dsct_fan_speed_button(3)
        elif group_name == 'dsct_fan4':
            # DSCT FAN4이 OFF될 때 새로운 SPD 초기화
            self.speed_button_manager.reset_new_dsct_fan_speed_button(4)
        elif group_name == 'pump1':
            # PUMP1이 OFF될 때 새로운 스피드 버튼 초기화
            if hasattr(self.speed_button_manager.main_window, 'speedButton_pump1'):
                self.speed_button_manager.reset_new_pump_speed_button(1)
            else:
                # 기존 스피드 버튼 초기화 (호환성)
                self.speed_button_manager.reset_pumper_speed_buttons(1)
        elif group_name == 'pump2':
            # PUMP2이 OFF될 때 새로운 스피드 버튼 초기화
            if hasattr(self.speed_button_manager.main_window, 'speedButton_pump2'):
                self.speed_button_manager.reset_new_pump_speed_button(2)
            else:
                # 기존 스피드 버튼 초기화 (호환성)
                self.speed_button_manager.reset_pumper_speed_buttons(2)

    # ==================== RELOAD 기능 ====================
    def handle_dsct_reload(self):
        """DSCT 장비 상태 리로드 요청"""
        if not self.serial_manager.is_connected():
            print("[RELOAD] 시리얼 연결 안됨 - DSCT 리로드 불가")
            return

        # 이미 진행 중이면 무시
        if self.dsct_reload_in_progress:
            print("[RELOAD] DSCT 리로드 이미 진행 중")
            return

        # 버튼 UI 상태 변경: 진행 중
        self._set_reload_button_state(self.dsct_reload_button, "loading")

        # 리로드 진행 중 플래그 설정
        self.dsct_reload_in_progress = True
        self.dsct_reload_data = []  # 응답 데이터 저장용
        self.dsct_reload_start_time = time.time()  # 시작 시간 기록

        # 명령 전송 (Queue를 거치지 않고 직접 전송)
        command = f"{CMD_PREFIX},DSCT,RELOAD"
        self.serial_manager.send_serial_command(command)
        print(f"[RELOAD] ⏱️  DSCT 리로드 요청 전송 (직접 전송): {command} (타임아웃: {self.reload_timeout/1000}초)")

        # 명령 전송 후 큐 일시 중지 (다른 명령 차단)
        if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
            self.serial_manager.command_queue.pause_queue()

        # 타임아웃 타이머 시작 (5초)
        self._start_reload_timeout_timer("dsct")

        # 테스트 모드: 더미 응답 시뮬레이션
        if self.test_mode:
            self._simulate_dsct_reload_response()

    def handle_air_reload(self):
        """AIR 장비 상태 리로드 요청"""
        if not self.serial_manager.is_connected():
            print("[RELOAD] 시리얼 연결 안됨 - AIR 리로드 불가")
            return

        # 이미 진행 중이면 무시
        if self.air_reload_in_progress:
            print("[RELOAD] AIR 리로드 이미 진행 중")
            return

        # 버튼 UI 상태 변경: 진행 중
        self._set_reload_button_state(self.air_reload_button, "loading")

        # 리로드 진행 중 플래그 설정
        self.air_reload_in_progress = True
        self.air_reload_data = []  # 응답 데이터 저장용
        self.air_reload_start_time = time.time()  # 시작 시간 기록

        # 명령 전송 (Queue를 거치지 않고 직접 전송)
        command = f"{CMD_PREFIX},AIR,RELOAD"
        self.serial_manager.send_serial_command(command)
        print(f"[RELOAD] ⏱️  AIR 리로드 요청 전송 (직접 전송): {command} (타임아웃: {self.reload_timeout/1000}초)")

        # 명령 전송 후 큐 일시 중지 (다른 명령 차단)
        if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
            self.serial_manager.command_queue.pause_queue()

        # 타임아웃 타이머 시작 (5초)
        self._start_reload_timeout_timer("air")

        # 테스트 모드: 더미 응답 시뮬레이션
        if self.test_mode:
            self._simulate_air_reload_response()

    def parse_reload_response(self, data: str):
        """RELOAD 및 SOL 응답 파싱 및 처리"""
        # SOL 응답 파싱 (최우선)
        self.parse_sol_response(data)

        # DSCT 리로드 응답 처리
        if self.dsct_reload_in_progress:
            if "EEPROM_ACK,RELOAD,START" in data:
                self.dsct_reload_data = []
                elapsed = time.time() - self.dsct_reload_start_time if self.dsct_reload_start_time else 0
                print(f"[RELOAD] ✅ DSCT 데이터 수집 시작 (응답까지: {elapsed:.2f}초)")
            elif "DSCT_ACK,RELOAD,COMPLETE" in data:
                elapsed = time.time() - self.dsct_reload_start_time if self.dsct_reload_start_time else 0
                print(f"[RELOAD] ✅ DSCT 데이터 수집 완료: {len(self.dsct_reload_data)}개 항목 (총 소요: {elapsed:.2f}초)")
                # 타임아웃 타이머 취소
                self._cancel_reload_timeout_timer("dsct")
                self._apply_dsct_reload_state()
                self.dsct_reload_in_progress = False
                # 명령 큐 재개
                if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
                    self.serial_manager.command_queue.resume_queue()
                # 버튼 UI 상태 변경: 완료 → 정상
                self._set_reload_button_state(self.dsct_reload_button, "complete")
                self._schedule_reload_button_reset(self.dsct_reload_button)
            elif data.startswith("DSCT,"):
                # 예: DSCT,FAN4,ON
                self.dsct_reload_data.append(data.strip())
                print(f"[RELOAD] 📥 DSCT 데이터 수집: {data.strip()}")

        # AIR 리로드 응답 처리
        if self.air_reload_in_progress:
            if "EEPROM_ACK,RELOAD,START" in data:
                self.air_reload_data = []
                elapsed = time.time() - self.air_reload_start_time if self.air_reload_start_time else 0
                print(f"[RELOAD] ✅ AIR 데이터 수집 시작 (응답까지: {elapsed:.2f}초)")
            elif "AIRCON_ACK,RELOAD,COMPLETE" in data:
                elapsed = time.time() - self.air_reload_start_time if self.air_reload_start_time else 0
                print(f"[RELOAD] ✅ AIR 데이터 수집 완료: {len(self.air_reload_data)}개 항목 (총 소요: {elapsed:.2f}초)")
                # 타임아웃 타이머 취소
                self._cancel_reload_timeout_timer("air")
                self._apply_air_reload_state()
                self.air_reload_in_progress = False
                # 명령 큐 재개
                if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
                    self.serial_manager.command_queue.resume_queue()
                # 버튼 UI 상태 변경: 완료 → 정상
                self._set_reload_button_state(self.air_reload_button, "complete")
                self._schedule_reload_button_reset(self.air_reload_button)
            elif data.startswith("AIR,"):
                # 예: AIR,FAN,ON
                self.air_reload_data.append(data.strip())
                print(f"[RELOAD] 📥 AIR 데이터 수집: {data.strip()}")

    def _apply_dsct_reload_state(self):
        """DSCT 리로드 데이터를 UI에 적용"""
        print(f"[RELOAD] DSCT UI 상태 적용 시작")
        for line in self.dsct_reload_data:
            try:
                parts = line.split(',')
                if len(parts) < 3:
                    continue

                device, function, *values = parts

                # FAN_ALL 항목 무시 (전체 설정 정보)
                if function.startswith("FAN_ALL"):
                    print(f"[RELOAD] FAN_ALL 항목 무시: {line}")
                    continue

                # FAN1~4 처리
                if function in ["FAN1", "FAN2", "FAN3", "FAN4"]:
                    # FAN1,ON 또는 FAN1,SPD,값 형식
                    if values[0] == "SPD" and len(values) > 1:
                        # DSCT,FAN1,SPD,1 형식 → 하드웨어 속도 값 그대로 복원
                        speed = int(values[1])
                        fan_num = function[-1]
                        self._update_dsct_fan_speed(fan_num, speed)
                        print(f"[RELOAD] DSCT FAN{fan_num} 속도 복원: {speed}")
                    else:
                        # DSCT,FAN1,ON 형식
                        state = values[0]  # ON/OFF
                        fan_num = function[-1]
                        self._update_dsct_fan_button(fan_num, state)

                # FAN1~4 SPEED 처리 (FSPD1 형식 - 구형 프로토콜)
                elif function in ["FSPD1", "FSPD2", "FSPD3", "FSPD4"]:
                    speed = int(values[0])
                    fan_num = function[-1]
                    self._update_dsct_fan_speed(fan_num, speed)

                # DMP1~4 처리
                elif function.startswith("DMP"):
                    position = values[0]  # OPEN/CLOSE
                    dmp_num = function[-1]
                    self._update_dsct_damper_button(dmp_num, position)

                # PUMP1~2 처리
                elif function.startswith("PUMP"):
                    # PUMP1,ON 또는 PUMP1,SPD,값 형식
                    if values[0] == "SPD" and len(values) > 1:
                        # DSCT,PUMP1,SPD,6 형식 → 무시 (PUMP는 ON/OFF만 존재)
                        pump_num = function[-1]
                        print(f"[RELOAD] PUMP{pump_num},SPD 항목 무시 (ON/OFF만 사용)")
                        continue
                    else:
                        # DSCT,PUMP1,ON 형식
                        state = values[0]  # ON/OFF
                        pump_num = function[-1]
                        self._update_pump_button(pump_num, state)

                # PUMP SPEED 처리 (PSPD1 형식 - 구형 프로토콜)
                # 주의: PUMP는 ON/OFF만 존재하므로 속도 값은 무시함
                elif function in ["PSPD1", "PSPD2"]:
                    pump_num = function[-1]
                    print(f"[RELOAD] PUMP{pump_num},PSPD 항목 무시 (ON/OFF만 사용, 구형 프로토콜)")
                    # speed = int(values[0])
                    # self._update_pump_speed(pump_num, speed)
                    continue

                # SOL 처리 (SOL1만 사용, SOL2~4는 무시)
                elif function.startswith("SOL"):
                    sol_num = function[-1]
                    if sol_num == "1":
                        state = values[0]  # ON/OFF
                        self._update_sol_button(sol_num, state)
                    else:
                        print(f"[RELOAD] SOL{sol_num} 항목 무시 (SOL1만 사용)")

                # SEMIAUTO 처리 (DESICCANT SEMI AUTO 버튼)
                elif function == "SEMIAUTO":
                    state = values[0]  # RUN/STOP
                    self._update_semiauto_button(state)

                # DMPTEST 처리 (DAMP TEST 버튼)
                elif function == "DMPTEST":
                    state = values[0]  # RUN/STOP
                    self._update_dmptest_button(state)

            except Exception as e:
                print(f"[RELOAD] DSCT 데이터 파싱 오류: {line} - {e}")

        print("[RELOAD] DSCT UI 상태 적용 완료")

    def _apply_air_reload_state(self):
        """AIR 리로드 데이터를 UI에 적용"""
        print(f"[RELOAD] AIR UI 상태 적용 시작")
        for line in self.air_reload_data:
            try:
                parts = line.split(',')
                if len(parts) < 3:
                    continue

                device, function, *values = parts

                # EVA FAN 처리
                if function == "FAN":
                    state = values[0]  # ON/OFF
                    self._update_air_fan_button("aircon_fan", state)

                # EVA FAN SPEED 처리
                elif function == "FSPD":
                    speed = int(values[0])
                    self._update_air_fan_speed(speed)

                # CONDENSER FAN 처리
                elif function == "CON_F":
                    state = values[0]  # ON/OFF
                    self._update_air_fan_button("aircon_con_fan", state)

                # CONDENSER FAN SPEED 처리
                elif function == "CON_SPD":
                    speed = int(values[0])
                    self._update_air_con_fan_speed(speed)

                # OA DAMPER LEFT (ALTDMP) 처리
                elif function == "ALTDMP":
                    action = values[0]  # OPEN
                    level = int(values[1]) if len(values) > 1 else 0
                    self._update_oa_damper_level("left", level)

                # OA DAMPER RIGHT (ARTDMP) 처리
                elif function == "ARTDMP":
                    action = values[0]  # OPEN
                    level = int(values[1]) if len(values) > 1 else 0
                    self._update_oa_damper_level("right", level)

                # RA DAMPER LEFT (ALBDMP) 처리
                elif function == "ALBDMP":
                    state = values[0]  # OPEN/CLOSE
                    self._update_ra_damper_button("aircon_left_bottom_DMP", state)

                # RA DAMPER RIGHT (ARBDMP) 처리
                elif function == "ARBDMP":
                    state = values[0]  # OPEN/CLOSE
                    self._update_ra_damper_button("aircon_right_bottom_DMP", state)

                # PUMP 처리
                elif function == "PUMP":
                    state = values[0]  # ON/OFF
                    self._update_air_pump_button(state)

                # CLUCH 처리
                elif function == "CLUCH":
                    state = values[0]  # ON/OFF
                    self._update_air_cluch_button(state)

            except Exception as e:
                print(f"[RELOAD] AIR 데이터 파싱 오류: {line} - {e}")

        print("[RELOAD] AIR UI 상태 적용 완료")

    # ==================== UI 업데이트 헬퍼 메서드 ====================
    def _set_button_state(self, button, is_on: bool, on_text="ON", off_text="OFF"):
        """버튼 상태를 ON/OFF로 설정"""
        if button is None:
            return
        if is_on:
            button.setStyleSheet(BUTTON_ON_STYLE)
            button.setText(on_text)
        else:
            button.setStyleSheet(BUTTON_OFF_STYLE)
            button.setText(off_text)

    def _update_dsct_fan_button(self, fan_num, state):
        """DSCT FAN 버튼 상태 업데이트"""
        group_name = f"dsct_fan{fan_num}"
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")

            # 이전 상태 저장
            was_on = group.get('active', False)

            # 버튼 UI 업데이트
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] DSCT FAN{fan_num} 버튼 상태 업데이트: {state}")

            # OFF로 변경될 때 속도 버튼 초기화
            if was_on and not is_on:
                self._handle_fan_off_callback(group_name)
                print(f"[RELOAD] DSCT FAN{fan_num} OFF → 속도 버튼 초기화")

    def _update_dsct_damper_button(self, dmp_num, position):
        """DSCT DAMPER 버튼 상태 업데이트 (TODO: 구현 필요)"""
        # DAMPER는 현재 숫자 버튼으로 되어 있어 추가 구현 필요
        print(f"[RELOAD] DSCT DMP{dmp_num} 상태: {position} (UI 업데이트 보류)")

    def _update_pump_button(self, pump_num, state):
        """PUMP 버튼 상태 업데이트"""
        group_name = f"pump{pump_num}"
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")

            # 이전 상태 저장
            was_on = group.get('active', False)

            # 버튼 UI 업데이트
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] PUMP{pump_num} 버튼 상태 업데이트: {state}")

            # OFF로 변경될 때 속도 버튼 초기화 (PUMP는 속도 없지만 콜백 일관성 유지)
            if was_on and not is_on:
                self._handle_fan_off_callback(group_name)
                print(f"[RELOAD] PUMP{pump_num} OFF → 상태 초기화")

    def _update_sol_button(self, sol_num, state):
        """SOL 버튼 상태 업데이트"""
        group_name = f"sol{sol_num}"
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] SOL{sol_num} 버튼 상태 업데이트: {state}")

    def _update_semiauto_button(self, state):
        """DESICCANT SEMI AUTO 버튼 상태 업데이트"""
        if hasattr(self.main_window, 'semi_auto_run_button'):
            button = self.main_window.semi_auto_run_button
            is_running = (state == "RUN")

            if is_running:
                button.setText("STOP")
                button.setStyleSheet("background-color: rgb(255, 0, 0); color: white; font-size: 14px; font-weight: bold;")
            else:
                button.setText("RUN")
                button.setStyleSheet("font-size: 14px; font-weight: bold;")

            print(f"[RELOAD] DSCT SEMIAUTO 버튼 상태 업데이트: {state}")
        else:
            print(f"[RELOAD] DSCT SEMIAUTO 상태: {state} (버튼 없음)")

    def _update_dmptest_button(self, state):
        """DAMP TEST 버튼 상태 업데이트"""
        if hasattr(self.main_window, 'damp_test_button'):
            button = self.main_window.damp_test_button
            is_running = (state == "RUN")

            if is_running:
                button.setText("STOP")
                button.setStyleSheet("background-color: rgb(255, 0, 0); color: white; font-size: 14px; font-weight: bold;")
            else:
                button.setText("RUN")
                button.setStyleSheet("font-size: 14px; font-weight: bold;")

            print(f"[RELOAD] DSCT DMPTEST 버튼 상태 업데이트: {state}")
        else:
            print(f"[RELOAD] DSCT DMPTEST 상태: {state} (버튼 없음)")

    def _update_air_fan_button(self, group_name, state):
        """AIR FAN 버튼 상태 업데이트 (EVA FAN, CONDENSER FAN)"""
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] {group_name} 버튼 상태 업데이트: {state}")

    def _update_air_fan_speed(self, speed):
        """EVA FAN 속도 업데이트"""
        if self.speed_button_manager:
            self.speed_button_manager.current_fan_speed = speed
            print(f"[RELOAD] EVA FAN 속도 업데이트: {speed}")
            # UI 업데이트는 SpeedButtonManager가 관리하므로 값만 설정
        else:
            print(f"[RELOAD] EVA FAN 속도: {speed} (SpeedButtonManager 없음)")

    def _update_air_con_fan_speed(self, speed):
        """CONDENSER FAN 속도 업데이트"""
        if self.speed_button_manager:
            self.speed_button_manager.current_con_fan_speed = speed
            print(f"[RELOAD] CON FAN 속도 업데이트: {speed}")
        else:
            print(f"[RELOAD] CON FAN 속도: {speed} (SpeedButtonManager 없음)")

    def _update_dsct_fan_speed(self, fan_num, speed):
        """DSCT FAN 속도 업데이트"""
        if self.speed_button_manager:
            # SpeedButtonManager의 해당 FAN 속도 값 업데이트
            setattr(self.speed_button_manager, f"current_dsct_fan{fan_num}_speed", speed)
            print(f"[RELOAD] DSCT FAN{fan_num} 속도 업데이트: {speed}")

            # 속도 버튼 UI 업데이트 (새로운 순환 버튼 방식)
            if hasattr(self.speed_button_manager.main_window, f"speedButton_dsct_fan{fan_num}"):
                speed_button = getattr(self.speed_button_manager.main_window, f"speedButton_dsct_fan{fan_num}")
                speed_button.setText(str(speed))
        else:
            print(f"[RELOAD] DSCT FAN{fan_num} 속도: {speed} (SpeedButtonManager 없음)")

    def _update_pump_speed(self, pump_num, speed):
        """PUMP 속도 업데이트"""
        if self.speed_button_manager:
            # SpeedButtonManager의 해당 PUMP 속도 값 업데이트
            setattr(self.speed_button_manager, f"current_pump{pump_num}_speed", speed)
            print(f"[RELOAD] PUMP{pump_num} 속도 업데이트: {speed}")

            # 속도 버튼 UI 업데이트 (새로운 순환 버튼 방식)
            if hasattr(self.speed_button_manager.main_window, f"speedButton_pump{pump_num}"):
                speed_button = getattr(self.speed_button_manager.main_window, f"speedButton_pump{pump_num}")
                speed_button.setText(str(speed))
        else:
            print(f"[RELOAD] PUMP{pump_num} 속도: {speed} (SpeedButtonManager 없음)")

    def _update_oa_damper_level(self, side, level):
        """OA DAMPER 레벨 업데이트 (left/right)"""
        # TODO: OA DAMPER 3버튼 구조의 숫자 버튼 업데이트 필요
        print(f"[RELOAD] OA DAMPER ({side}) 레벨: {level} (구현 필요)")

    def _update_ra_damper_button(self, group_name, state):
        """RA DAMPER 버튼 상태 업데이트"""
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "OPEN")
            self._set_button_state(button, is_on, "OPEN", "CLOSE")
            group['active'] = is_on
            print(f"[RELOAD] {group_name} 버튼 상태 업데이트: {state}")

    def _update_air_pump_button(self, state):
        """AIR PUMP 버튼 상태 업데이트"""
        group_name = "pump"
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] AIR PUMP 버튼 상태 업데이트: {state}")

    def _update_air_cluch_button(self, state):
        """AIR CLUCH 버튼 상태 업데이트"""
        group_name = "aircon_cluch"
        if group_name in self.button_groups:
            group = self.button_groups[group_name]
            button = list(group['buttons'].keys())[0]
            is_on = (state == "ON")
            self._set_button_state(button, is_on)
            group['active'] = is_on
            print(f"[RELOAD] AIR CLUCH 버튼 상태 업데이트: {state}")

    # ==================== Reload 버튼 시각적 피드백 ====================
    def _set_reload_button_state(self, button, state):
        """
        Reload 버튼 상태 변경
        state: "normal" (기본), "loading" (진행 중), "complete" (완료), "error" (타임아웃/오류)
        """
        if button is None:
            return

        if state == "loading":
            # 진행 중: 주황색 + 비활성화 + 텍스트 변경
            button.setText("⏳ Loading...")
            button.setEnabled(False)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 2px solid #F57C00;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            print(f"[RELOAD] 버튼 상태: 로딩 중")

        elif state == "complete":
            # 완료: 밝은 초록색 + 체크 마크
            button.setText("✓ Complete!")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #8BC34A;
                    color: white;
                    border: 2px solid #7CB342;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            print(f"[RELOAD] 버튼 상태: 완료")

        elif state == "error":
            # 에러: 빨간색 + X 마크
            button.setText("✗ Timeout!")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: 2px solid #D32F2F;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            print(f"[RELOAD] 버튼 상태: 타임아웃 오류")

        elif state == "normal":
            # 정상: 원래 색상 복원 + 활성화
            # DSCT는 파란색, AIR는 녹색으로 복원
            if button == self.dsct_reload_button:
                button.setText("DSCT Refresh")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: 2px solid #1976D2;
                        border-radius: 5px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                    QPushButton:pressed {
                        background-color: #1565C0;
                    }
                """)
            elif button == self.air_reload_button:
                button.setText("AIR Refresh")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #45a049;
                        border-radius: 5px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                    QPushButton:pressed {
                        background-color: #3d8b40;
                    }
                """)
            button.setEnabled(True)
            print(f"[RELOAD] 버튼 상태: 정상 복원")

    def _schedule_reload_button_reset(self, button, delay=1000):
        """
        완료/에러 표시 후 지정된 시간 뒤에 버튼을 정상 상태로 복원
        delay: 복원까지 대기 시간 (ms), 기본 1000ms (1초)
        """
        if button is None:
            return

        from PyQt5.QtCore import QTimer
        # 지정된 시간 후 정상 상태로 복원
        QTimer.singleShot(delay, lambda: self._set_reload_button_state(button, "normal"))

    # ==================== 테스트 모드 더미 응답 ====================
    def _simulate_dsct_reload_response(self):
        """테스트 모드: DSCT RELOAD 더미 응답 시뮬레이션"""
        from PyQt5.QtCore import QTimer
        print("[TEST] DSCT RELOAD 더미 응답 시뮬레이션 시작")

        # START 신호 (즉시)
        QTimer.singleShot(100, lambda: self.parse_reload_response("EEPROM_ACK,RELOAD,START"))

        # 더미 데이터 (200ms 간격)
        dummy_data = [
            "DSCT,FAN1,ON",
            "DSCT,FSPD1,7",      # FAN1 속도: 7
            "DSCT,FAN2,OFF",
            "DSCT,FSPD2,0",      # FAN2 속도: 0 (OFF 상태)
            "DSCT,FAN3,ON",
            "DSCT,FSPD3,5",      # FAN3 속도: 5
            "DSCT,FAN4,OFF",
            "DSCT,FSPD4,0",      # FAN4 속도: 0 (OFF 상태)
            "DSCT,DMP1,OPEN",
            "DSCT,DMP2,CLOSE",
            "DSCT,DMP3,OPEN",
            "DSCT,DMP4,CLOSE",
            "DSCT,PUMP1,ON",
            "DSCT,PSPD1,6",      # PUMP1 속도: 6
            "DSCT,PUMP2,OFF",
            "DSCT,PSPD2,0",      # PUMP2 속도: 0 (OFF 상태)
            "DSCT,SOL1,OFF",     # SOL1만 사용 (SOL2~4는 무시됨)
            "DSCT,SEMIAUTO,STOP",  # DESICCANT SEMI AUTO: STOP
            "DSCT,DMPTEST,STOP",   # DAMP TEST: STOP
        ]

        delay = 200
        for i, data in enumerate(dummy_data):
            QTimer.singleShot(delay + (i * 100), lambda d=data: self.parse_reload_response(d))

        # COMPLETE 신호 (모든 데이터 후)
        QTimer.singleShot(delay + len(dummy_data) * 100 + 200,
                         lambda: self.parse_reload_response("EEPROM_ACK,RELOAD,END"))
        QTimer.singleShot(delay + len(dummy_data) * 100 + 300,
                         lambda: self.parse_reload_response("DSCT_ACK,RELOAD,COMPLETE"))

    def _simulate_air_reload_response(self):
        """테스트 모드: AIR RELOAD 더미 응답 시뮬레이션"""
        from PyQt5.QtCore import QTimer
        print("[TEST] AIR RELOAD 더미 응답 시뮬레이션 시작")

        # START 신호 (즉시)
        QTimer.singleShot(100, lambda: self.parse_reload_response("EEPROM_ACK,RELOAD,START"))

        # 더미 데이터 (200ms 간격)
        dummy_data = [
            "AIR,FAN,ON",
            "AIR,FSPD,5",
            "AIR,CON_F,ON",
            "AIR,CON_SPD,3",
            "AIR,ALTDMP,OPEN,2",
            "AIR,ALBDMP,OPEN",
            "AIR,ARTDMP,OPEN,1",
            "AIR,ARBDMP,CLOSE",
            "AIR,PUMP,ON",
            "AIR,CLUCH,ON",
        ]

        delay = 200
        for i, data in enumerate(dummy_data):
            QTimer.singleShot(delay + (i * 100), lambda d=data: self.parse_reload_response(d))

        # COMPLETE 신호 (모든 데이터 후)
        QTimer.singleShot(delay + len(dummy_data) * 100 + 200,
                         lambda: self.parse_reload_response("EEPROM_ACK,RELOAD,END"))
        QTimer.singleShot(delay + len(dummy_data) * 100 + 300,
                         lambda: self.parse_reload_response("AIRCON_ACK,RELOAD,COMPLETE"))

    # ==================== 타임아웃 관리 ====================
    def _start_reload_timeout_timer(self, reload_type):
        """
        RELOAD 타임아웃 타이머 시작
        reload_type: "dsct" 또는 "air"
        """
        from PyQt5.QtCore import QTimer

        if reload_type == "dsct":
            # 기존 타이머가 있으면 중지
            if self.dsct_reload_timer is not None:
                self.dsct_reload_timer.stop()
            # 새 타이머 생성
            self.dsct_reload_timer = QTimer()
            self.dsct_reload_timer.setSingleShot(True)
            self.dsct_reload_timer.timeout.connect(lambda: self._handle_reload_timeout("dsct"))
            self.dsct_reload_timer.start(self.reload_timeout)
            print(f"[RELOAD] DSCT 타임아웃 타이머 시작: {self.reload_timeout}ms")

        elif reload_type == "air":
            # 기존 타이머가 있으면 중지
            if self.air_reload_timer is not None:
                self.air_reload_timer.stop()
            # 새 타이머 생성
            self.air_reload_timer = QTimer()
            self.air_reload_timer.setSingleShot(True)
            self.air_reload_timer.timeout.connect(lambda: self._handle_reload_timeout("air"))
            self.air_reload_timer.start(self.reload_timeout)
            print(f"[RELOAD] AIR 타임아웃 타이머 시작: {self.reload_timeout}ms")

    def _cancel_reload_timeout_timer(self, reload_type):
        """
        RELOAD 타임아웃 타이머 취소
        reload_type: "dsct" 또는 "air"
        """
        if reload_type == "dsct":
            if self.dsct_reload_timer is not None:
                self.dsct_reload_timer.stop()
                self.dsct_reload_timer = None
                print(f"[RELOAD] DSCT 타임아웃 타이머 취소")

        elif reload_type == "air":
            if self.air_reload_timer is not None:
                self.air_reload_timer.stop()
                self.air_reload_timer = None
                print(f"[RELOAD] AIR 타임아웃 타이머 취소")

    def _handle_reload_timeout(self, reload_type):
        """
        RELOAD 타임아웃 처리
        reload_type: "dsct" 또는 "air"
        """
        if reload_type == "dsct":
            print(f"[RELOAD] ⚠️ DSCT 리로드 타임아웃! (응답 없음)")
            # 진행 중 플래그 해제
            self.dsct_reload_in_progress = False
            self.dsct_reload_data = []
            # 명령 큐 재개 (타임아웃 발생 시에도 큐 정상화)
            if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
                self.serial_manager.command_queue.resume_queue()
            # 버튼 상태: 에러 표시
            self._set_reload_button_state(self.dsct_reload_button, "error")
            # 2초 후 정상 상태로 복귀 (재시도 가능하도록)
            self._schedule_reload_button_reset(self.dsct_reload_button, delay=2000)

        elif reload_type == "air":
            print(f"[RELOAD] ⚠️ AIR 리로드 타임아웃! (응답 없음)")
            # 진행 중 플래그 해제
            self.air_reload_in_progress = False
            self.air_reload_data = []
            # 명령 큐 재개 (타임아웃 발생 시에도 큐 정상화)
            if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
                self.serial_manager.command_queue.resume_queue()
            # 버튼 상태: 에러 표시
            self._set_reload_button_state(self.air_reload_button, "error")
            # 2초 후 정상 상태로 복귀 (재시도 가능하도록)
            self._schedule_reload_button_reset(self.air_reload_button, delay=2000)

    # ==================== SOL 제어 (15초 딜레이 + Flicker) ====================
    def _start_sol_flicker(self):
        """SOL 버튼 Flicker 시작 (0.5초 간격 초록색 깜빡임)"""
        from PyQt5.QtCore import QTimer

        # 진행 중 플래그 설정
        self.sol_in_progress = True
        self.sol_flicker_state = False

        # SOL1 버튼 가져오기
        sol1_button = self._get_sol1_button()
        if not sol1_button:
            print("[SOL] ⚠️ SOL1 버튼을 찾을 수 없음")
            return

        print("[SOL] Flicker 애니메이션 시작")
        self._sol_flicker_tick()

    def _sol_flicker_tick(self):
        """SOL Flicker 한 틱 실행"""
        from PyQt5.QtCore import QTimer

        if not self.sol_in_progress:
            print("[SOL] Flicker 중지 (진행 중 아님)")
            return

        sol1_button = self._get_sol1_button()
        if not sol1_button:
            return

        # 색상 토글
        if self.sol_flicker_state:
            # 초록색 (ON 상태)
            sol1_button.setStyleSheet(BUTTON_ON_STYLE)
        else:
            # 골드색 (진행 중)
            sol1_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFD700;
                    color: black;
                    border: 2px solid #FFA500;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)

        self.sol_flicker_state = not self.sol_flicker_state

        # 0.5초 후 재호출
        self.sol_flicker_timer = QTimer()
        self.sol_flicker_timer.setSingleShot(True)
        self.sol_flicker_timer.timeout.connect(self._sol_flicker_tick)
        self.sol_flicker_timer.start(500)

    def _stop_sol_flicker(self, final_state):
        """
        SOL Flicker 중지
        final_state: 'ON' 또는 'OFF' (최종 버튼 상태)
        """
        from PyQt5.QtCore import QTimer

        print(f"[SOL] Flicker 중지 - 최종 상태: {final_state}")

        # 진행 중 플래그 해제
        self.sol_in_progress = False

        # 타이머 중지
        if self.sol_flicker_timer is not None:
            self.sol_flicker_timer.stop()
            self.sol_flicker_timer = None

        # 타임아웃 타이머 중지
        self._cancel_sol_timeout_timer()

        # 최종 버튼 상태 설정
        sol1_button = self._get_sol1_button()
        if sol1_button:
            if final_state == 'ON':
                sol1_button.setStyleSheet(BUTTON_ON_STYLE)
                sol1_button.setText("ON")
                # button_groups 상태도 업데이트
                if 'sol1' in self.button_groups:
                    self.button_groups['sol1']['active'] = True
            else:
                sol1_button.setStyleSheet(BUTTON_OFF_STYLE)
                sol1_button.setText("OFF")
                # button_groups 상태도 업데이트
                if 'sol1' in self.button_groups:
                    self.button_groups['sol1']['active'] = False

    def _get_sol1_button(self):
        """SOL1 버튼 객체 반환"""
        if 'sol1' in self.button_groups:
            buttons = list(self.button_groups['sol1']['buttons'].keys())
            if buttons:
                return buttons[0]
        return None

    def _start_sol_timeout_timer(self):
        """SOL 타임아웃 타이머 시작 (20초)"""
        from PyQt5.QtCore import QTimer

        # 기존 타이머가 있으면 중지
        if self.sol_timeout_timer is not None:
            self.sol_timeout_timer.stop()

        # 새 타이머 생성
        self.sol_timeout_timer = QTimer()
        self.sol_timeout_timer.setSingleShot(True)
        self.sol_timeout_timer.timeout.connect(self._handle_sol_timeout)
        self.sol_timeout_timer.start(self.sol_timeout)
        print(f"[SOL] 타임아웃 타이머 시작: {self.sol_timeout}ms")

    def _cancel_sol_timeout_timer(self):
        """SOL 타임아웃 타이머 취소"""
        if self.sol_timeout_timer is not None:
            self.sol_timeout_timer.stop()
            self.sol_timeout_timer = None
            print("[SOL] 타임아웃 타이머 취소")

    def _handle_sol_timeout(self):
        """SOL 타임아웃 처리"""
        print("[SOL] ⚠️ 타임아웃! (20초 경과, 응답 없음)")

        # Flicker 중지 및 에러 상태 표시
        self.sol_in_progress = False
        if self.sol_flicker_timer is not None:
            self.sol_flicker_timer.stop()
            self.sol_flicker_timer = None

        # 버튼 에러 상태로 변경
        sol1_button = self._get_sol1_button()
        if sol1_button:
            sol1_button.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: 2px solid #D32F2F;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            sol1_button.setText("TIMEOUT!")

            # 2초 후 원래 상태로 복귀
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self._reset_sol_button_to_off())

    def _reset_sol_button_to_off(self):
        """SOL 버튼을 OFF 상태로 리셋"""
        sol1_button = self._get_sol1_button()
        if sol1_button:
            sol1_button.setStyleSheet(BUTTON_OFF_STYLE)
            sol1_button.setText("OFF")
            if 'sol1' in self.button_groups:
                self.button_groups['sol1']['active'] = False
            print("[SOL] 버튼 OFF 상태로 리셋 완료")

    def parse_sol_response(self, data: str):
        """
        SOL 응답 메시지 파싱
        - DSCT,SOL,All Opening! → Flicker 계속
        - DSCT,SOL All Open OK! → Flicker 중지, ON 상태
        - DSCT,SOL,All Closing! → Flicker 계속
        - DSCT,SOL All Close OK! → Flicker 중지, OFF 상태
        """
        if not self.sol_in_progress:
            return  # SOL 동작 중이 아니면 무시

        if "DSCT,SOL,All Opening!" in data:
            print("[SOL] 밸브 열림 시작")
            # 이미 Flicker 중이므로 추가 동작 없음

        elif "DSCT,SOL All Open OK!" in data:
            print("[SOL] ✅ 밸브 열림 완료")
            self._stop_sol_flicker(final_state='ON')

        elif "DSCT,SOL,All Closing!" in data:
            print("[SOL] 밸브 닫힘 시작")
            # 이미 Flicker 중이므로 추가 동작 없음

        elif "DSCT,SOL All Close OK!" in data:
            print("[SOL] ✅ 밸브 닫힘 완료")
            self._stop_sol_flicker(final_state='OFF')

    # ==================== 테스트 모드: SOL 더미 응답 ====================
    def _simulate_sol_open_response(self):
        """테스트 모드: SOL OPEN 더미 응답 시뮬레이션 (15초)"""
        from PyQt5.QtCore import QTimer
        print("[TEST] SOL OPEN 더미 응답 시뮬레이션 시작")

        # Opening 메시지 (즉시)
        QTimer.singleShot(100, lambda: self.parse_sol_response("DSCT,SOL,All Opening!"))

        # 15초 후 Open OK 메시지
        QTimer.singleShot(15000, lambda: self.parse_sol_response("DSCT,SOL All Open OK!"))

    def _simulate_sol_close_response(self):
        """테스트 모드: SOL CLOSE 더미 응답 시뮬레이션 (15초)"""
        from PyQt5.QtCore import QTimer
        print("[TEST] SOL CLOSE 더미 응답 시뮬레이션 시작")

        # Closing 메시지 (즉시)
        QTimer.singleShot(100, lambda: self.parse_sol_response("DSCT,SOL,All Closing!"))

        # 15초 후 Close OK 메시지
        QTimer.singleShot(15000, lambda: self.parse_sol_response("DSCT,SOL All Close OK!"))