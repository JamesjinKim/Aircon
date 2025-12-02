# CHANGELOG

## v3.11 (2025-12-02) 🔧

### 🐛 **버그 수정**

#### **시리얼 연결 안정성 개선**
- **문제**: 시리얼 장비 없이도 내장 UART 포트(ttyAMA*)로 연결되는 문제
- **해결**: USB 시리얼 포트만 표시하도록 필터링 추가

#### **연결 해제 예외 처리 개선**
- **문제**: 연결 안된 상태에서 해제 버튼 클릭 시 에러 발생
- **해결**: 안전한 예외 처리 및 사용자 알림 메시지 추가

### 🔧 **변경 사항**

#### **serial_manager.py**
- `get_available_ports(usb_only=True)`: USB 포트 필터링 파라미터 추가
- USB 시리얼 포트만 표시: `ttyUSB*`, `ttyACM*`, `COM*`
- 내장 UART 포트 제외: `ttyAMA*` (라즈베리파이 내장)
- `connect_serial()`: USB 포트 검증 강화
- `disconnect_serial()`: 단계별 예외 처리 개선

#### **main_window.py**
- `disconnect_serial()`: 연결 안된 상태 체크 추가
- 센서 탭 업데이트 개별 try-except 처리
- 디버깅용 traceback 출력 추가

### 📁 **수정된 파일**
- `managers/serial_manager.py`
- `ui/main_window.py`

---

## v3.10 (2025-12-02) 📊

### ✨ **새로운 기능**

#### **PT02 센서 CSV 저장 시스템**
- **PT02 센서 전용 매니저 추가**: 1분 주기 온도/CO2/PM2.5 데이터 관리
- **일일 CSV 파일 자동 생성**: `PT02_YYYY-MM-DD.csv` 형식
- **10MB 초과 시 자동 분할**: `_001`, `_002` 인덱스 추가
- **30일치 파일 유지**: 오래된 파일 자동 정리

#### **CSV 구조**
```csv
timestamp,temperature,co2,pm25
2025-12-02 11:30:55,25.3,850,35
```

#### **테스트 모드 지원**
- `DummyPT02Generator`: 더미 데이터 생성기 추가
- 트렌드 시뮬레이션으로 자연스러운 데이터 변화

### 🛠️ **기술적 세부사항**

#### **새로운 클래스: PT02SensorManager**
**파일**: `managers/pt02_sensor_manager.py`

**주요 메서드**:
- `save_sensor_data(temp, co2, pm25)`: 데이터 저장 및 CSV 기록
- `parse_pt02_response(data)`: 시리얼 응답 파싱
- `_get_csv_filename()`: 날짜/크기 기반 파일명 생성
- `_save_to_csv()`: CSV append 저장
- `_cleanup_pt02_files()`: 오래된 파일 정리

#### **AutoModeManager 연동**
- `set_pt02_sensor_manager()`: PT02 매니저 연결
- `parse_pt02_response()`: 파싱 후 CSV 저장 호출

### 📁 **추가된 파일**
- `managers/pt02_sensor_manager.py` (신규)
- `test/dummy_pt02_generator.py` (신규)

### 📁 **수정된 파일**
- `managers/auto_manager.py`: PT02 매니저 연동 추가
- `ui/main_window.py`: PT02SensorManager 초기화

---

## v3.9 (2025-11-26) 🎛️

### ✨ **새로운 기능**

#### **AUTO 탭 전면 개편 - AUTOMODE 시스템**
- **2컬럼 컴팩트 레이아웃**: 800×480 터치스크린에 최적화
- **왼쪽 컬럼 (AUTO MODE CONTROL)**:
  - AUTO START/STOP 토글 버튼 (180×60)
  - 모드 상태 인디케이터 (자동/환기/순환)
  - PT02 센서 실시간 표시 (온도, CO2, PM2.5)
- **오른쪽 컬럼 (설정값 입력)**:
  - 온도 설정: 목표값 ± 히스테리시스 (°C)
  - CO2 설정: 목표값 ± 히스테리시스 (ppm)
  - PM2.5 설정: 목표값 ± 히스테리시스 (µg/m³)
  - SEMI 동작시간 설정 (초)
  - Refresh / SAVE 버튼

#### **새로운 시리얼 명령어 (AUTOMODE)**
- `$CMD,AIR,AUTOMODE,ON` / `OFF`: 자동 모드 시작/중지
- `$CMD,AIR,TEMPSET,XXXX,nnnn`: 온도 설정 (값×10, 히스테리시스×10)
- `$CMD,AIR,CO2SET,XXXX,nnnn`: CO2 설정 (ppm)
- `$CMD,AIR,PM25SET,XX,nn`: PM2.5 설정 (µg/m³)
- `$CMD,AIR,SEMITIME,XXXX`: SEMI 동작시간 (초)
- `$CMD,AIR,GETSET`: 현재 설정값 조회

#### **히스테리시스 제어 시스템**
- **온도 제어**: 목표 온도 ± 허용 범위로 냉방 ON/OFF 결정
- **CO2 제어**: 기준 농도 ± 허용 범위로 환기 ON/OFF 결정
- **PM2.5 제어**: 기준 농도 ± 허용 범위로 순환 ON/OFF 결정
- **잦은 ON/OFF 방지**: 히스테리시스 값으로 안정적 제어

### 🔧 **UI 개선**

#### **탭 순서 재배치**
- **새로운 순서**: AUTO → SEMI AUTO → AIRCON → PUMP & SOL → DESICCANT → DSCT T/H → AIRCON T/H
- AUTO 탭을 맨 앞으로 이동하여 접근성 향상

#### **설정값 입력 버튼 최적화**
- **버튼 크기 조정**: 겹침 방지를 위해 컴팩트하게 재설계
  - -/+ 버튼: 36×36
  - 값 표시: 60×36
  - 히스테리시스 -/+: 32×36
  - 히스테리시스 값: 48×36
- **간격 최적화**: spacing 2px로 조밀하게 배치

### 🛠️ **기술적 세부사항**

#### **새로운 클래스: AutoModeManager**
**파일**: `managers/auto_manager.py`

**주요 메서드**:
- `connect_auto_controls()`: UI 위젯 연결
- `handle_auto_mode_toggle()`: AUTO START/STOP 토글
- `handle_save()`: 모든 설정값 전송
- `handle_refresh()`: 현재 설정값 조회
- `parse_pt02_response()`: PT02 센서 응답 파싱
- `parse_getset_response()`: GETSET 응답 파싱
- `log_message()`: 전송 메시지 로깅

#### **설정값 범위**
| 항목 | 최소 | 최대 | 단계 | 기본값 |
|------|------|------|------|--------|
| 온도 | 15.0 | 35.0 | 0.5 | 25.0°C |
| 온도 히스테리시스 | 0.5 | 5.0 | 0.5 | 2.0°C |
| CO2 | 400 | 2000 | 50 | 1000ppm |
| CO2 히스테리시스 | 50 | 500 | 50 | 100ppm |
| PM2.5 | 10 | 100 | 5 | 35µg/m³ |
| PM2.5 히스테리시스 | 5 | 50 | 5 | 5µg/m³ |
| SEMI 시간 | 60 | 3600 | 30 | 300초 |

### 📁 **수정된 파일**

#### **UI 관련**
- `ui/ui_components.py`: `create_auto_control_tab()` 함수 전면 재작성
- `ui/main_window.py`: 탭 순서 변경, `connect_auto_controls()` 업데이트

#### **비즈니스 로직**
- `managers/auto_manager.py`: `AutoModeManager` 클래스 전면 재작성

---

## v3.5 (2025-10-12) 🎯

### ✨ **새로운 기능**

#### **SOL 밸브 통합 제어 시스템 (15초 딜레이 + Flicker)**
- **UI 간소화**: SOL2, SOL3, SOL4 버튼 제거
- **SOL1 버튼으로 1~4 전체 제어**:
  - 레이블: `SOL 1~4`
  - 명령어: `$CMD,DSCT,SOL1,ON/OFF`
  - 하나의 명령으로 모든 SOL 밸브 동시 개폐

#### **Flicker 애니메이션 (0.5초 간격)**
- **골드색 ↔ 초록색 반복**: 사용자에게 진행 상태 시각적 피드백
- **진행 중 클릭 방지**: `sol_in_progress` 플래그로 중복 클릭 차단
- **자동 종료**: 장비 응답 수신 시 Flicker 중지

#### **시리얼 응답 메시지 처리**
- `DSCT,SOL,All Opening!` → Flicker 계속
- `DSCT,SOL All Open OK!` → Flicker 중지, ON 상태
- `DSCT,SOL,All Closing!` → Flicker 계속
- `DSCT,SOL All Close OK!` → Flicker 중지, OFF 상태

#### **타임아웃 안전 장치 (20초)**
- **20초 내 응답 없으면**: 빨간색 `TIMEOUT!` 표시
- **2초 후 자동 복구**: OFF 상태로 리셋, 재시도 가능

### 🧪 **테스트 모드 지원**

#### **더미 응답 시뮬레이션**
- **OPEN 시뮬레이션**:
  - 즉시 `DSCT,SOL,All Opening!`
  - 15초 후 `DSCT,SOL All Open OK!`
- **CLOSE 시뮬레이션**:
  - 즉시 `DSCT,SOL,All Closing!`
  - 15초 후 `DSCT,SOL All Close OK!`

### 🛠️ **기술적 세부사항**

#### **새로운 메서드 (button_manager.py)**
- `_start_sol_flicker()`: Flicker 시작
- `_sol_flicker_tick()`: 0.5초 간격 색상 토글
- `_stop_sol_flicker(final_state)`: Flicker 중지 + 최종 상태 설정
- `_get_sol1_button()`: SOL1 버튼 객체 반환
- `_start_sol_timeout_timer()`: 20초 타임아웃 타이머
- `_handle_sol_timeout()`: 타임아웃 처리
- `parse_sol_response(data)`: SOL 응답 메시지 파싱
- `_simulate_sol_open_response()`: 테스트 모드 OPEN 시뮬레이션
- `_simulate_sol_close_response()`: 테스트 모드 CLOSE 시뮬레이션

#### **수정된 파일**
- `ui/main_window.py`: SOL2~4 버튼 UI 제거, SOL1 레이블 변경
- `ui/setup_buttons.py`: SOL2~4 그룹 제거
- `managers/button_manager.py`: SOL 제어 로직 추가 (~220 라인)

#### **버튼 상태 변화**
```
[OFF 상태] → [클릭]
    ↓
[골드 ↔ 초록 Flicker] (진행 중, 0.5초 간격)
    ↓
[DSCT,SOL All Open/Close OK!]
    ↓
[ON/OFF 상태] (완료)
```

#### **에러 처리**
- **타임아웃**: 20초 내 응답 없음 → 빨간색 `TIMEOUT!` → 2초 후 OFF
- **중복 클릭**: 진행 중 클릭 무시
- **시리얼 연결 끊김**: 버튼 동작 차단

---

## v3.4 (2025-10-11) 🔄

### ✨ **새로운 기능**

#### **장비 상태 동기화 (RELOAD) 시스템**
- **2개의 Refresh 버튼 추가**:
  - **AIRCON 탭**: `AIR Refresh` 버튼 (녹색)
  - **DESICCANT 탭**: `DSCT Refresh` 버튼 (파란색)
- **장비 상태 자동 동기화**:
  - UI 버튼 상태 ↔ 실제 장비 상태 일치화
  - 수동 조작, 재연결 시 발생하는 불일치 해결
- **시리얼 명령어**:
  - DSCT: `$CMD,DSCT,RELOAD`
  - AIR: `$CMD,AIR,RELOAD`

#### **시각적 피드백 시스템**
- **4단계 버튼 상태 표시**:
  1. **정상 (Normal)**: 원래 색상 (녹색/파란색)
  2. **로딩 (Loading)**: 주황색 `⏳ Loading...` + 버튼 비활성화
  3. **완료 (Complete)**: 밝은 초록색 `✓ Complete!` (1초 지속)
  4. **에러 (Error)**: 빨간색 `✗ Timeout!` (2초 지속)
- **자동 상태 복귀**: 완료/에러 후 자동으로 정상 상태로 복원

#### **타임아웃 안전 장치**
- **5초 타임아웃 타이머**: 응답 없으면 자동 에러 처리
- **중복 클릭 방지**: 진행 중에는 버튼 비활성화
- **재시도 가능**: 타임아웃 후 2초 뒤 자동 복귀로 재시도 가능

#### **SPEED 값 동기화**
- **DSCT 장비**:
  - FAN1~4 속도: `FSPD1`, `FSPD2`, `FSPD3`, `FSPD4`
  - PUMP1~2 속도: `PSPD1`, `PSPD2`
- **AIR 장비**:
  - EVA FAN 속도: `FSPD`
  - CONDENSER FAN 속도: `CON_SPD`
- **UI 자동 업데이트**: SpeedButtonManager 연동으로 속도 버튼 텍스트 자동 변경

### 🔧 **시스템 구조**

#### **RELOAD 프로토콜**
```
[버튼 클릭]
    ↓
[명령 전송: $CMD,DSCT/AIR,RELOAD]
    ↓
[EEPROM_ACK,RELOAD,START]
    ↓
[데이터 수집: DSCT,FAN1,ON / DSCT,FSPD1,7 ...]
    ↓
[DSCT_ACK,RELOAD,COMPLETE]
    ↓
[UI 상태 동기화 완료]
```

#### **동기화 대상 항목**

**DSCT (데시칸트)**:
- ✅ FAN1~4 ON/OFF 상태
- ✅ FAN1~4 속도 (0-10)
- ⏳ DMP1~4 OPEN/CLOSE 위치 (로그만, UI 업데이트 보류)
- ✅ PUMP1~2 ON/OFF 상태
- ✅ PUMP1~2 속도 (0-10)
- ✅ SOL1~4 ON/OFF 상태

**AIR (에어컨)**:
- ✅ EVA FAN ON/OFF 상태
- ✅ EVA FAN 속도 (0-10)
- ✅ CONDENSER FAN ON/OFF 상태
- ✅ CONDENSER FAN 속도 (0-10)
- ⏳ OA DAMPER LEFT/RIGHT 레벨 (로그만, UI 업데이트 보류)
- ✅ RA DAMPER LEFT/RIGHT OPEN/CLOSE 상태
- ✅ PUMP ON/OFF 상태
- ✅ CLUCH ON/OFF 상태

### 🧪 **테스트 모드 지원**

#### **더미 응답 시뮬레이션**
- **테스트 모드 활성화**: `python main.py --test`
- **자동 더미 데이터 생성**: 실제 하드웨어 없이 기능 테스트 가능
- **타이밍 시뮬레이션**:
  - DSCT: 2초 소요 (20개 항목)
  - AIR: 1.6초 소요 (10개 항목)

#### **테스트 시나리오**
1. **정상 완료**: 모든 데이터 수신 → `✓ Complete!`
2. **타임아웃**: 5초 내 응답 없음 → `✗ Timeout!`
3. **재시도**: 에러 후 2초 뒤 재시도 가능

### 🛠️ **기술적 세부사항**

#### **새로운 모듈 및 메서드**

**managers/button_manager.py**:
- `handle_dsct_reload()`: DSCT 리로드 요청
- `handle_air_reload()`: AIR 리로드 요청
- `parse_reload_response()`: 응답 데이터 파싱
- `_apply_dsct_reload_state()`: DSCT UI 적용
- `_apply_air_reload_state()`: AIR UI 적용
- `_update_dsct_fan_speed()`: DSCT FAN 속도 업데이트
- `_update_pump_speed()`: PUMP 속도 업데이트
- `_set_reload_button_state()`: 버튼 시각적 상태 변경
- `_start_reload_timeout_timer()`: 타임아웃 타이머 시작
- `_cancel_reload_timeout_timer()`: 타임아웃 타이머 취소
- `_handle_reload_timeout()`: 타임아웃 처리
- `_simulate_dsct_reload_response()`: 테스트 모드 더미 응답
- `_simulate_air_reload_response()`: 테스트 모드 더미 응답

**ui/setup_buttons.py**:
- `setup_reload_buttons()`: Refresh 버튼 이벤트 연결

#### **상태 관리 변수**
```python
# RELOAD 진행 상태
self.dsct_reload_in_progress = False
self.air_reload_in_progress = False

# 수집된 데이터
self.dsct_reload_data = []
self.air_reload_data = []

# 타임아웃 타이머
self.dsct_reload_timer = None
self.air_reload_timer = None
self.reload_timeout = 5000  # 5초
```

### 📁 **수정된 파일**

#### **UI 관련**
- `ui/main_window.py`: Refresh 버튼 추가 (AIRCON 탭, DESICCANT 탭)
- `ui/setup_buttons.py`: 이벤트 핸들러 연결 및 버튼 참조 전달
- `ui/constants.py`: (기존 스타일 활용)

#### **비즈니스 로직**
- `managers/button_manager.py`: RELOAD 기능 전체 구현 (~380 라인 추가)

#### **시그널/슬롯 연결**
- `ui/main_window.py`: `serial_manager.data_received` → `button_manager.parse_reload_response` 연결

### 🎯 **사용자 경험 개선**

#### **명확한 상태 피드백**
- **진행 중**: 주황색 로딩 표시로 동작 중임을 명확히 표시
- **완료**: 체크 마크로 성공 확인
- **에러**: X 마크로 실패 알림
- **타이밍**: 자동 복귀로 사용자 개입 불필요

#### **안전성 강화**
- **타임아웃 보호**: 무한 대기 방지
- **중복 방지**: 진행 중 재클릭 차단
- **자동 복구**: 에러 발생 시 자동으로 재시도 가능 상태로 복원

#### **실시간 동기화**
- **버튼 상태**: ON/OFF 즉시 반영
- **속도 값**: 1-10 범위 숫자 즉시 업데이트
- **시각적 확인**: 로그와 UI 양쪽에서 확인 가능

### 📊 **응답 데이터 예시**

#### **DSCT RELOAD 응답**
```
EEPROM_ACK,RELOAD,START
DSCT,FAN1,ON
DSCT,FSPD1,7
DSCT,FAN2,OFF
DSCT,FSPD2,0
DSCT,PUMP1,ON
DSCT,PSPD1,6
...
EEPROM_ACK,RELOAD,END
DSCT_ACK,RELOAD,COMPLETE
```

#### **AIR RELOAD 응답**
```
EEPROM_ACK,RELOAD,START
AIR,FAN,ON
AIR,FSPD,5
AIR,CON_F,ON
AIR,CON_SPD,3
AIR,PUMP,ON
AIR,CLUCH,ON
...
EEPROM_ACK,RELOAD,END
AIRCON_ACK,RELOAD,COMPLETE
```

### 🔍 **버그 수정**

#### **테스트 모드 동작 문제**
- **문제**: 테스트 모드에서 RELOAD 시 응답 없어 무한 로딩
- **해결**: `test_mode` 파라미터 추가 및 더미 응답 시뮬레이션 구현

#### **무한 로딩 문제**
- **문제**: 하드웨어 응답 없을 시 버튼이 로딩 상태로 고정
- **해결**: 5초 타임아웃 타이머 및 자동 에러 처리 구현

---

## v3.3 (2025-01-31) 📊

### ✨ **새로운 기능**

#### **CSV 파일 분할 저장 기능**
- **일별 파일 분할**: 
  - DSCT 센서: `DSCT_2025-01-31.csv` 형식
  - AIRCON 센서: `AIRCON_2025-01-31.csv` 형식
  - 날짜 변경 시 자동으로 새 파일 생성
- **크기 기반 분할**:
  - 10MB 도달 시 자동으로 새 파일 생성
  - 순차 번호 추가: `DSCT_2025-01-31_001.csv`, `DSCT_2025-01-31_002.csv`
  - 최대 999개까지 분할 가능 (3자리 인덱스)

### 🎨 **UI/UX 개선**

#### **온습도 위젯 가독성 향상**
- **불필요한 레이블 제거**:
  - 상태 레이블 (정상/타임아웃/대기중) 삭제
  - 업데이트 시간 레이블 삭제
  - 위젯 높이 90px → 80px로 조정
- **폰트 크기 증가**:
  - 온도/습도 제목: 10px → 14px (bold 추가)
  - 온도/습도 값: 10px → 16px (bold 추가)  
  - 단위 표시: 10px → 14px
- **적용 대상**: DSCT T/H TAB, AIRCON T/H TAB 모두 적용

### 🔧 **기술적 개선**

#### **파일 관리 시스템**
- **새로운 메서드**: `_get_csv_filename()` - 지능적 파일명 생성
- **파일 크기 체크**: `os.path.getsize()`로 실시간 모니터링
- **자동 롤링**: 크기 제한 도달 시 자동으로 다음 파일로 전환
- **기존 데이터 호환성**: CSV 구조 및 필드 형식 유지

### 📁 **수정된 파일**

#### **UI 관련**
- `ui/sensor_widget.py`: 레이블 제거 및 폰트 크기 조정

#### **데이터 저장 관련**  
- `managers/sensor_manager.py`: DSCT 센서 CSV 분할 저장 구현
- `managers/air_sensor_manager.py`: AIRCON 센서 CSV 분할 저장 구현

---

## v3.2 (2025-01-29) 🌡️

### ✨ **새로운 기능**

#### **온습도 센서 모니터링 시스템 추가**
- **SENSORS 탭 신규 추가**: 5번째 탭으로 배치 (SEMI AUTO와 AUTO 사이)
- **12개 센서 실시간 모니터링**: ID01~ID12 센서 데이터 표시
- **자동 갱신 기능**: 5초 주기로 자동 데이터 갱신
- **시각적 상태 표시**: 
  - 정상: 녹색 테두리 및 배경
  - 타임아웃: 빨간색 테두리 및 배경
  - 대기중: 회색 테두리 및 배경

#### **센서 데이터 표시 정보**
- **개별 센서당 표시 항목**:
  - 센서 ID (ID01~ID12)
  - 온도값 (°C)
  - 습도값 (%)
  - 연결 상태 (정상/타임아웃/대기중)
  - 마지막 업데이트 시간
- **요약 정보 표시**: 정상/타임아웃/대기중 센서 개수 실시간 집계

### 🔧 **시스템 구조 개선**

#### **새로운 모듈 추가**
- `managers/sensor_manager.py`: 센서 데이터 관리 및 파싱
- `ui/sensor_widget.py`: 개별 센서 표시 위젯
- `ui/sensor_tab.py`: SENSORS 탭 전체 레이아웃

#### **기존 모듈 확장**
- `managers/serial_manager.py`: 센서 데이터 콜백 메커니즘 추가
- `ui/main_window.py`: SENSORS 탭 통합 및 연결/해제 시 처리 로직

### 📡 **통신 프로토콜**

#### **센서 데이터 요청/응답**
- **요청 명령어**: `$CMD,DSCT,TH`
- **응답 형식**:
  - 정상: `[DSCT] ID01,TEMP: 28.3, HUMI: 67.7`
  - 타임아웃: `[DSCT] ID07,Sensor Check TIMEOUT!`
  - 완료: `[DSCT] SEQUENTIAL SCAN COMPLETE: Total: 12, Success: 6, Error: 6, Time: 7470ms`

### 🎯 **사용자 경험 개선**

#### **직관적인 인터페이스**
- **4×3 그리드 레이아웃**: 12개 센서를 한눈에 확인
- **실시간 상태 업데이트**: 색상과 텍스트로 즉각적인 피드백
- **수동 새로고침 버튼**: 필요시 즉시 데이터 갱신 가능

#### **안정성 강화**
- **연결 상태 연동**: 시리얼 연결/해제 시 자동으로 센서 모니터링 시작/중지
- **에러 처리**: 타임아웃 센서 명확히 표시
- **기존 기능 보존**: 다른 탭 기능에 영향 없이 독립적으로 동작

### 🛠️ **기술적 세부사항**

#### **데이터 구조**
```python
sensor_data = {
    'ID01': {
        'temp': 28.3,
        'humi': 67.7,
        'status': 'active',
        'last_update': datetime.now()
    },
    # ... ID02 ~ ID12
}
```

#### **시그널/슬롯 구조**
- `sensor_data_updated`: 개별 센서 업데이트 시그널
- `all_sensors_updated`: 전체 스캔 완료 시그널

### 📁 **파일 변경 사항**

#### **신규 파일**
- `managers/sensor_manager.py` (133 lines)
- `ui/sensor_widget.py` (125 lines)
- `ui/sensor_tab.py` (157 lines)

#### **수정된 파일**
- `ui/main_window.py`: import 문 추가, SENSORS 탭 통합
- `managers/serial_manager.py`: 콜백 메커니즘 추가

---

## v3.1 (2025-07-03) 🎯

### ✨ **새로운 기능**

#### **OA.DAMP 버튼 구조 개선**
- **3버튼 구조 도입**: OPEN + 숫자 + CLOSE 형태로 변경
- **균일한 버튼 크기**: OPEN과 CLOSE 버튼 모두 65×45px로 통일
- **새로운 함수**: `create_oa_damper_three_button_row()` 추가

#### **OA.DAMP 버튼 동작 로직 변경**
- **OPEN 버튼**: 
  - 클릭 시 숫자 +1 증가 (0~9 순환)
  - Green 색상으로 시각적 피드백
  - Serial 명령어: `$CMD,AIR,ALTDMP,OPEN,1` (고정값)
- **CLOSE 버튼**:
  - 클릭 시 숫자 -1 감소 (0에서 멈춤)
  - Green 색상으로 시각적 피드백
  - Serial 명령어: `$CMD,AIR,ALTDMP,CLOSE,1` (1 이상일 때만 전송)
- **숫자 버튼**: 이벤트 없음, 표시 전용

### 🔧 **개선 사항**

#### **UI/UX 개선**
- **그룹 명칭 변경**: "DAMPER CONTROLS" → "DAMP CONTROLS"
- **크기 일관성 보장**: `ensure_uniform_button_sizes()` 메서드에서 OA.DAMP 버튼 크기 재설정

#### **Serial 명령어 최적화**
- **SEMI AUTO TAB**: DAMP TEST 명령어 `DAMPTEST` → `DMPTEST`로 변경
- **조건부 전송**: CLOSE 버튼에서 숫자가 0일 때 명령어 전송 중단

### 🛠️ **기술적 개선**

#### **코드 구조**
- **새로운 이벤트 핸들러**: `create_new_oa_damper_controls()` 메서드 추가
- **기존 호환성 유지**: 기존 코드에 영향 없이 새 기능 구현
- **모듈화**: 기능별로 분리된 함수 구조

#### **상태 관리**
- **색상 피드백**: OPEN/CLOSE 버튼 간 상호 배타적 색상 변경
- **초기화 기능**: 연결 해제 시 버튼 상태 및 색상 초기화

### 📁 **수정된 파일**

#### **핵심 파일**
- `ui/ui_components.py`: 새로운 3버튼 함수 추가
- `managers/speed_manager.py`: 새로운 이벤트 핸들러 구현
- `ui/main_window.py`: 새 함수 연결 및 그룹 명칭 변경

#### **설정 파일**
- `ui/setup_buttons.py`: 토글 기능 제거 관련 수정
- `ref/aircon_dsct_cmd.txt`: 요구사항 문서 업데이트

### 🎯 **사용자 경험**

#### **직관적인 조작**
- **시각적 피드백**: 클릭한 버튼이 Green으로 변경되어 현재 선택 상태 표시
- **숫자 표시**: 클릭 횟수를 숫자로 시각적 확인 가능
- **안전한 조작**: 0에서 멈춤으로 예상치 못한 동작 방지

#### **하드웨어 제어 단순화**
- **고정값 전송**: 복잡한 숫자 값 대신 항상 1로 고정하여 하드웨어 제어 단순화
- **조건부 전송**: 불필요한 명령어 전송 방지

### 🔍 **버그 수정**

#### **버튼 크기 문제 해결**
- **원인**: `ensure_uniform_button_sizes()` 메서드가 OA.DAMP 버튼을 140px로 덮어쓰는 문제
- **해결**: OA.DAMP 버튼들을 65px로 재설정하는 코드 추가

#### **토글 기능 충돌 해결**
- **문제**: 기존 토글 기능과 새로운 이벤트 핸들러 충돌
- **해결**: 새로운 이벤트 핸들러가 기존 기능을 덮어쓰도록 구현

---

## v3.0 (2025년 7월 이전) 🎉
- **NEW**: SEMI AUTO 탭 추가
- **MAJOR**: 탭 구조 개편
- **IMPROVED**: 버튼 스타일 통일
- **ENHANCED**: 터치 친화적 UI 디자인
- **FIXED**: 시리얼 통신 안정성 개선


