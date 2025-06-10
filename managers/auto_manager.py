# AUTO 모드의 풍량 및 온도 설정을 처리하는 매니저 클래스 manager/auto_manager.py
from PyQt5.QtWidgets import QLabel, QSlider, QPushButton, QLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import random

class AutoSpeedManager:
    """AUTO 모드의 풍량 및 온도 설정을 처리하는 매니저 클래스"""
    
    def __init__(self, serial_manager, SendData_textEdit):
        """초기화"""
        self.serial_manager = serial_manager
        self.SendData_textEdit = SendData_textEdit
        self.current_fan_speed = 0  # 초기값 0으로 설정
        self.current_temperature = 22
        self.auto_mode_active = False
        self.speed_button_manager = None  # MANUAL 매니저 참조 추가
        self.is_updating = False  # 동기화 중 무한 루프 방지용 플래그
        self.fan_speed_slider = None  # 슬라이더 객체 참조 저장
        self.fan_speed_value = None  # 값 레이블 참조 저장
        
        # 타이머
        self.timer = None
        
        # 스피드 인디케이터 레이블 리스트
        self.speed_indicator_labels = []
        self.temp_indicator_labels = []
    
    # MANUAL 탭 매니저 설정 메서드
    def set_speed_button_manager(self, speed_manager):
        """MANUAL 탭 속도 버튼 매니저 참조 설정"""
        self.speed_button_manager = speed_manager
    
    def connect_aircon_fan_speed_slider(self, slider, value_label):
        """에어컨 팬 스피드 슬라이더 연결"""
        if not slider or not value_label:
            print("경고: 슬라이더 또는 값 레이블이 None입니다.")
            return
        
        # 슬라이더와 값 레이블 참조 저장
        self.fan_speed_slider = slider
        self.fan_speed_value = value_label
            
        # 기존 연결 해제
        try:
            slider.valueChanged.disconnect()
        except (TypeError, RuntimeError):
            pass
            
        # 슬라이더 값 변경 시 호출되는 함수
        def update_fan_speed(value):
            # 시리얼 포트 연결 확인
            if not self.serial_manager.is_connected():
                print("시리얼 포트가 연결되지 않음 - AUTO 슬라이더 동작 차단")
                if self.SendData_textEdit:
                    self.SendData_textEdit.append("시리얼 포트가 연결되지 않음 - AUTO 슬라이더 동작 차단")
                    self.SendData_textEdit.verticalScrollBar().setValue(
                        self.SendData_textEdit.verticalScrollBar().maximum()
                    )
                # 슬라이더를 이전 값으로 되돌리기
                slider.blockSignals(True)
                slider.setValue(self.current_fan_speed)
                value_label.setText(str(self.current_fan_speed))
                slider.blockSignals(False)
                return
                
            value_label.setText(str(value))
            self.current_fan_speed = value
            self.set_fan_speed(value)
            
            # 스피드 인디케이터 업데이트
            self.update_speed_indicators(value)
            
            # MANUAL 탭과 동기화 (값 변경 시 호출)
            self.sync_to_manual_tab(value)
        
        # 슬라이더 연결
        slider.valueChanged.connect(update_fan_speed)
        
        # 초기 값 설정
        current_value = slider.value()
        value_label.setText(str(current_value))
        self.current_fan_speed = current_value
        
        # 초기 스피드 인디케이터 업데이트
        self.update_speed_indicators(current_value)
    
    def update_speed_indicators(self, active_value):
        """스피드 인디케이터 레이블 업데이트"""
        if not self.speed_indicator_labels:
            return
            
        for i, label in enumerate(self.speed_indicator_labels):
            if i == active_value:
                label.setStyleSheet("""
                    font-weight: bold;
                    color: #2979ff;
                    background-color: #e3f2fd;
                    border-radius: 4px;
                    padding: 2px;
                """)
            else:
                label.setStyleSheet("")
    
    def update_temp_indicators(self, temp_value):
        """온도 인디케이터 레이블 업데이트"""
        if not self.temp_indicator_labels:
            return
            
        # 가장 가까운 온도 인디케이터 찾기
        min_diff = float('inf')
        closest_idx = -1
        
        for i, label in enumerate(self.temp_indicator_labels):
            try:
                label_temp = int(label.text().replace('°C', ''))
                diff = abs(label_temp - temp_value)
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = i
            except (ValueError, AttributeError):
                continue
        
        # 레이블 스타일 업데이트
        for i, label in enumerate(self.temp_indicator_labels):
            if i == closest_idx:
                label.setStyleSheet("""
                    font-weight: bold;
                    color: #f44336;
                    background-color: #ffebee;
                    border-radius: 4px;
                    padding: 2px;
                """)
            else:
                label.setStyleSheet("")
    
    def connect_temperature_slider(self, slider, value_label):
        """온도 슬라이더 연결"""
        if not slider or not value_label:
            print("경고: 온도 슬라이더 또는 값 레이블이 None입니다.")
            return
            
        # 기존 연결 해제
        try:
            slider.valueChanged.disconnect()
        except (TypeError, RuntimeError):
            pass
            
        # 슬라이더 값 변경 시 호출되는 함수
        def update_temperature(value):
            # 시리얼 포트 연결 확인
            if not self.serial_manager.is_connected():
                print("시리얼 포트가 연결되지 않음 - AUTO 온도 슬라이더 동작 차단")
                if self.SendData_textEdit:
                    self.SendData_textEdit.append("시리얼 포트가 연결되지 않음 - AUTO 온도 슬라이더 동작 차단")
                    self.SendData_textEdit.verticalScrollBar().setValue(
                        self.SendData_textEdit.verticalScrollBar().maximum()
                    )
                # 슬라이더를 이전 값으로 되돌리기
                slider.blockSignals(True)
                slider.setValue(self.current_temperature)
                value_label.setText(f"{self.current_temperature}°C")
                slider.blockSignals(False)
                return
                
            value_label.setText(f"{value}°C")
            self.current_temperature = value
            self.set_temperature(value)
            
            # 온도 인디케이터 업데이트
            self.update_temp_indicators(value)
        
        # 슬라이더 연결
        slider.valueChanged.connect(update_temperature)
        
        # 초기 값 설정
        current_value = slider.value()
        value_label.setText(f"{current_value}°C")
        self.current_temperature = current_value
        
        # 초기 온도 인디케이터 업데이트
        self.update_temp_indicators(current_value)
    
    def set_fan_speed(self, speed_value):
        """팬 스피드 명령어 전송"""
        if speed_value < 0 or speed_value > 10:  # 0도 유효한 값으로 변경 (꺼짐)
            print(f"속도 값 범위 오류: {speed_value}")
            return
            
        # 0인 경우 None으로 전송 (꺼짐)
        if speed_value == 0:
            command = "$CMD,FSPD,None\r"
        else:
            command = f"$CMD,FSPD,{speed_value}\r"
        
        if self.serial_manager.is_connected():
            # 시리얼 전송
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"AUTO 스피드 명령 전송: {command}")
            
            # 로깅
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
        else:
            print("시리얼 포트 연결되지 않음 - AUTO 모드")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("시리얼 포트 연결되지 않음 - AUTO 모드")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
    
    # 값 변경 시 MANUAL 탭과 동기화하는 메서드
    def sync_to_manual_tab(self, fan_speed):
        """AUTO 탭의 팬 속도를 MANUAL 탭과 동기화"""
        if self.is_updating:
            return
            
        if self.speed_button_manager and hasattr(self.speed_button_manager, 'update_from_auto'):
            print(f"Auto -> Manual 동기화: {fan_speed}")
            self.is_updating = True
            self.speed_button_manager.update_from_auto(fan_speed)
            self.is_updating = False
    
    # MANUAL 탭에서 호출될 메서드
    def update_from_manual(self, fan_speed):
        """MANUAL 탭에서의 변경을 AUTO 탭에 반영"""
        if self.is_updating:
            return
            
        self.is_updating = True
        
        # current_fan_speed 업데이트
        self.current_fan_speed = fan_speed
        
        # 슬라이더 값 업데이트 (시그널 차단)
        if self.fan_speed_slider:
            self.fan_speed_slider.blockSignals(True)
            self.fan_speed_slider.setValue(fan_speed)
            self.fan_speed_slider.blockSignals(False)
        
        # 값 레이블 업데이트
        if self.fan_speed_value:
            self.fan_speed_value.setText(str(fan_speed))
        
        # 인디케이터 업데이트
        self.update_speed_indicators(fan_speed)
        
        self.is_updating = False
    
    def connect_auto_controls(self, auto_widget):
        """AUTO 탭의 컨트롤을 한 번에 연결"""
        # 속도 인디케이터 레이블 찾기
        self._find_speed_indicators(auto_widget)
        
        # 온도 인디케이터 레이블 찾기
        self._find_temp_indicators(auto_widget)
        
        # 팬 스피드 슬라이더
        fan_speed_slider = auto_widget.findChild(QSlider, "auto_fan_speed_slider")
        fan_speed_value = auto_widget.findChild(QLabel, "fan_speed_value")
        
        if fan_speed_slider and fan_speed_value:
            self.connect_aircon_fan_speed_slider(
                fan_speed_slider,
                fan_speed_value
            )
        
        # 온도 슬라이더
        temp_slider = auto_widget.findChild(QSlider, "temp_slider")
        temp_value = auto_widget.findChild(QLabel, "temp_value")
        
        if temp_slider and temp_value:
            self.connect_temperature_slider(
                temp_slider,
                temp_value
            )
            
        # AUTO 모드 버튼
        auto_mode_button = getattr(auto_widget, 'auto_mode_button', None)
        if auto_mode_button:
            self.connect_auto_mode_button(auto_mode_button)
        
        # 상태 정보 업데이트를 위한 타이머 설정
        if self.timer:
            self.timer.stop()
        
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.update_status_info(auto_widget))
        self.timer.start(1000)  # 1초마다 업데이트
    
    def update_status_info(self, auto_widget):
        """상태 정보 업데이트"""
        if not auto_widget:
            return
            
        # 모의 온도 및 습도 값 생성 (더미 데이터)
        if hasattr(auto_widget, 'current_temp'):
            current_temp = random.randint(20, 30)
            auto_widget.current_temp.setText(f"{current_temp}°C")
        
        if hasattr(auto_widget, 'humidity_status'):
            current_humidity = random.randint(40, 70)
            auto_widget.humidity_status.setText(f"{current_humidity}%")
        
        # 팬 스피드 상태 갱신
        if hasattr(auto_widget, 'fan_speed_status'):
            fan_speed = self.current_fan_speed
            if fan_speed == 0:
                fan_status = "꺼짐"
            else:
                fan_status = f"{fan_speed}단계"
            auto_widget.fan_speed_status.setText(fan_status)
    
    def _find_speed_indicators(self, auto_widget):
        """스피드 인디케이터 레이블 찾기"""
        self.speed_indicator_labels = []
        
        # 레이아웃 내의 모든 자식 위젯 확인
        def find_labels_in_layout(layout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel):
                    # 레이블의 텍스트가 숫자인지 확인
                    try:
                        int(item.widget().text())
                        # 0-10 사이의 숫자인 경우 속도 인디케이터로 간주
                        if 0 <= int(item.widget().text()) <= 10:
                            self.speed_indicator_labels.append(item.widget())
                    except ValueError:
                        pass
                elif item.layout():
                    find_labels_in_layout(item.layout())
        
        # 위젯의 모든 레이아웃 탐색
        for child in auto_widget.children():
            if isinstance(child, QLayout):
                find_labels_in_layout(child)
    
    def _find_temp_indicators(self, auto_widget):
        """온도 인디케이터 레이블 찾기"""
        self.temp_indicator_labels = []
        
        # 레이아웃 내의 모든 자식 위젯 확인
        def find_labels_in_layout(layout):
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QLabel):
                    # 레이블의 텍스트가 온도 형식인지 확인
                    try:
                        text = item.widget().text()
                        # 숫자이고 16-30 사이의 값인지 확인
                        num_value = int(text)
                        if 16 <= num_value <= 30:
                            self.temp_indicator_labels.append(item.widget())
                    except ValueError:
                        pass
                elif item.layout():
                    find_labels_in_layout(item.layout())
        
        # 위젯의 모든 레이아웃 탐색
        for child in auto_widget.children():
            if isinstance(child, QLayout):
                find_labels_in_layout(child)
    
    def connect_auto_mode_button(self, button):
        """AUTO 모드 버튼 연결"""
        if not button:
            print("경고: AUTO 모드 버튼이 None입니다.")
            return
            
        # 기존 연결 해제
        try:
            button.clicked.disconnect()
        except (TypeError, RuntimeError):
            pass
        
        # 버튼 클릭 시 AUTO 모드 전환
        def toggle_auto_mode():
            self.auto_mode_active = not self.auto_mode_active
            success = self.set_auto_mode_active(self.auto_mode_active)
            
            if success:
                button.setText("AUTO 모드 종료" if self.auto_mode_active else "AUTO 모드 시작")
                button.setStyleSheet("""
                    QPushButton {
                        background-color: """ + ("#ff5722" if self.auto_mode_active else "#2979ff") + """;
                        color: white;
                        font-size: 18px;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: """ + ("#f4511e" if self.auto_mode_active else "#2962ff") + """;
                    }
                    QPushButton:pressed {
                        background-color: """ + ("#e64a19" if self.auto_mode_active else "#1565c0") + """;
                    }
                """)
                
                # AUTO 모드 시작 시 모든 값 초기화
                self.reset_all_values()
        
        # 버튼 연결
        button.clicked.connect(toggle_auto_mode)
    
    def reset_all_values(self):
        """AUTO 모드 시작 시 모든 값 초기화"""
        # 타이머가 있으면 초기화
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer.start(1000)  # 타이머 재시작
        
        # 현재 위젯의 상태 확인
        auto_widget = self._find_parent_auto_widget()
        if not auto_widget:
            print("경고: AUTO 위젯을 찾을 수 없습니다.")
            return
        
        # 팬 스피드 슬라이더 리셋
        fan_speed_slider = auto_widget.findChild(QSlider, "auto_fan_speed_slider")
        fan_speed_value = auto_widget.findChild(QLabel, "fan_speed_value")
        
        if fan_speed_slider and fan_speed_value:
            # 값 변경 전 동기화 중 플래그 설정
            self.is_updating = True
            
            fan_speed_slider.setValue(0)  # 0으로 리셋
            fan_speed_value.setText("0")
            self.current_fan_speed = 0
            self.set_fan_speed(0)
            self.update_speed_indicators(0)
            
            # 수동 탭과도 동기화
            self.sync_to_manual_tab(0)
            self.is_updating = False
        
        # 온도 슬라이더 리셋
        temp_slider = auto_widget.findChild(QSlider, "temp_slider")
        temp_value = auto_widget.findChild(QLabel, "temp_value")
        
        if temp_slider and temp_value:
            reset_temp = 22  # 기본 온도 22도로 리셋
            temp_slider.setValue(reset_temp)
            temp_value.setText(f"{reset_temp}°C")
            self.current_temperature = reset_temp
            self.set_temperature(reset_temp)
            self.update_temp_indicators(reset_temp)
        
        # 상태 정보 업데이트
        if hasattr(auto_widget, 'status_value'):
            if self.auto_mode_active:
                auto_widget.status_value.setText("자동 제어 중")
                auto_widget.status_value.setStyleSheet("font-weight: bold; color: #4CAF50; padding: 6px; font-size: 14px;")
            else:
                auto_widget.status_value.setText("대기 중")
                auto_widget.status_value.setStyleSheet("font-weight: bold; color: #2962ff; padding: 6px; font-size: 14px;")
    
    def _find_parent_auto_widget(self):
        """현재 AUTO 위젯 찾기 - 부모 위젯 찾기"""
        # 속도 인디케이터 레이블 중 하나를 기준으로 부모 위젯 찾기
        if self.speed_indicator_labels and len(self.speed_indicator_labels) > 0:
            parent = self.speed_indicator_labels[0].parent()
            while parent:
                if hasattr(parent, 'auto_mode_button'):
                    return parent
                parent = parent.parent()
        
        return None
    
    def set_auto_mode_active(self, is_active):
        """AUTO 모드 활성화/비활성화"""
        command = "$CMD,AUTO,ON\r" if is_active else "$CMD,AUTO,OFF\r"
        
        if self.serial_manager.is_connected():
            # 시리얼 전송
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"AUTO 모드 명령 전송: {command}")
            
            # 로깅
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            
            # AUTO 모드 시작 시 모든 값 초기화
            self.auto_mode_active = is_active
            
            return True
        else:
            print("시리얼 포트 연결되지 않음 - AUTO 모드 전환 실패")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("시리얼 포트 연결되지 않음 - AUTO 모드 전환 실패")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
            
            return False
    
    def set_temperature(self, temperature):
        """온도 설정"""
        if temperature < 16 or temperature > 30:
            print(f"온도 값 범위 오류: {temperature}")
            return
            
        command = f"$CMD,TEMP,{temperature}\r"
        
        if self.serial_manager.is_connected():
            # 시리얼 전송
            self.serial_manager.shinho_serial_connection.write(command.encode())
            print(f"온도 설정 명령 전송: {command}")
            
            # 로깅
            if self.SendData_textEdit:
                self.SendData_textEdit.append(f"{command}")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )
        else:
            print("시리얼 포트 연결되지 않음 - 온도 설정 실패")
            if self.SendData_textEdit:
                self.SendData_textEdit.append("시리얼 포트 연결되지 않음 - 온도 설정 실패")
                self.SendData_textEdit.verticalScrollBar().setValue(
                    self.SendData_textEdit.verticalScrollBar().maximum()
                )