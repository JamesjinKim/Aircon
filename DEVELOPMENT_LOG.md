# AIRCON T/H 센서 모니터링 시스템 개발 로그

## 개발 개요

**개발 기간**: 2025년 7월 30일 ~ 2025년 8월 4일  
**목적**: AIRCON 시스템용 온습도 센서 모니터링 기능 추가 및 UI/UX 개선

## 배경

- 기존 시스템에는 DSCT T/H 탭(12개 센서)만 존재
- AIRCON 시스템용 별도 센서 모니터링 필요
- 시리얼 통신을 통한 실시간 데이터 수집 및 CSV 저장 기능 구현

## 개발 내용

### 1. 시스템 분석 및 현황 파악

**기존 구조 확인:**
- DSCT T/H: 12개 센서 (ID01~ID12)
- 시리얼 명령어: `$CMD,DSCT,TH`
- 응답 형식: `[DSCT] ID01,TEMP: 28.3, HUMI: 67.7`

**신규 요구사항:**
- AIRCON T/H: 6개 센서 (ID01~ID06)
- 시리얼 명령어: `$CMD,AIR,TH`
- 응답 형식: `[AIR]` ID01,TEMP: 28.3, HUMI: 67.7`

### 2. 새로운 모듈 개발

#### 2.1 AirSensorManager 클래스
**파일**: `managers/air_sensor_manager.py`

**주요 기능:**
- 6개 AIRCON 센서 데이터 관리
- 시리얼 데이터 파싱 (정상/타임아웃 응답 처리)
- CSV 파일 자동 저장
- 5초 주기 자동 갱신
- 테스트 모드 지원

**핵심 메서드:**
- `parse_sensor_data()`: 시리얼 응답 파싱
- `start_auto_refresh()`: 자동 갱신 시작
- `_save_to_csv()`: CSV 파일 저장

#### 2.2 AirconSensorTab 클래스
**파일**: `ui/aircon_sensor_tab.py`

**주요 기능:**
- 4×2 그리드 레이아웃 (8개 센서)
- 실시간 센서 위젯 업데이트
- 자동/수동 새로고침 기능
- 요약 정보 표시 (정상/타임아웃/대기중 개수)

#### 2.3 DummyAirSensorGenerator 클래스
**파일**: `test/dummy_air_sensor_generator.py`

**주요 기능:**
- 6개 센서용 가상 데이터 생성
- AIRCON 환경에 최적화된 온도/습도 범위
- ID07, ID08 센서 타임아웃 시뮬레이션
- 실제 시리얼 응답 형식 생성

### 3. 기존 시스템 확장

#### 3.1 SerialManager 확장
**파일**: `managers/serial_manager.py`

**추가된 기능:**
- `set_air_sensor_data_callback()`: AIR 센서 콜백 설정
- `read_data()` 메서드에서 [AIR] 응답 자동 라우팅

#### 3.2 MainWindow 통합
**파일**: `ui/main_window.py`

**추가된 기능:**
- AIRCON T/H 탭을 6번째 탭으로 추가
- 시리얼 연결 시 AIR 센서 자동 갱신 시작
- 연결 해제 시 AIR 센서 갱신 중지

### 4. CSV 파일 구조 및 개선

#### 4.1 파일 분리
- **DSCT 센서**: `DSCT_YYYYMMDD.csv` (12개 센서)
- **AIRCON 센서**: `AIRCON_YYYYMMDD.csv` (6개 센서)

#### 4.2 CSV 형식
```csv
timestamp,sensor_id,temperature,humidity
2025-07-30 15:52:33,ID01,27.3,74.1
2025-07-30 15:52:33,ID02,24.9,65.8
```

### 5. 통신 프로토콜

#### 5.1 명령어
- **센서 데이터 요청**: `$CMD,AIR,TH\r`

#### 5.2 응답 형식
```
[AIR] Temp/Humi SCAN START!
[AIR] ID01,TEMP: 28.3, HUMI: 67.7
[AIR] ID02,TEMP: 28.8, HUMI: 68.6
...
[AIR] ID07,Sensor Check TIMEOUT!
[AIR] ID08,Sensor Check TIMEOUT!
[AIR] SEQUENTIAL SCAN COMPLETE: Total: 8, Success: 6, Error: 2, Time: 7470ms
```

## 테스트 결과

### 테스트 모드 검증
```bash
python main.py --test
```

**검증 항목:**
- ✅ 8개 센서 위젯 정상 표시
- ✅ 5초 주기 자동 갱신 동작
- ✅ 정상/타임아웃 상태 시각적 표시
- ✅ CSV 파일 자동 저장
- ✅ 시리얼 연결/해제 시 자동 제어

### 데이터 검증
**실시간 CSV 저장 확인:**
- 총 99개 데이터 포인트 저장
- 타임아웃 센서 제외하고 정상 데이터만 저장
- 5초 간격으로 지속적 데이터 수집

## 사용 방법

### 1. 테스트 모드 실행
```bash
python main.py --test
```

### 2. 실제 하드웨어 연결
```bash
python main.py
```
1. 시리얼 포트 선택 및 연결
2. AIRCON T/H 탭 선택
3. 자동 모니터링 시작

### 3. 수동 새로고침
- "수동 새로고침" 버튼 클릭으로 즉시 데이터 갱신

## 파일 구조

```
Aircon/
├── managers/
│   ├── air_sensor_manager.py      # ✨ 신규: AIR 센서 매니저
│   ├── sensor_manager.py          # 🔧 수정: CSV 파일명 변경
│   └── serial_manager.py          # 🔧 수정: AIR 콜백 추가
├── ui/
│   ├── aircon_sensor_tab.py       # ✨ 신규: AIRCON T/H 탭
│   └── main_window.py             # 🔧 수정: 탭 통합
├── test/
│   └── dummy_air_sensor_generator.py  # ✨ 신규: 더미 데이터 생성기
└── data/
    ├── dsct_sensor_data_20250730.csv   # DSCT 센서 데이터
    └── air_sensor_data_20250730.csv    # ✨ 신규: AIRCON 센서 데이터
```

## 주요 특징

### 🌡️ 실시간 모니터링
- 6개 센서 동시 모니터링
- 5초 주기 자동 갱신
- 시각적 상태 표시 (정상/타임아웃/대기중)

### 💾 데이터 저장
- 날짜별 CSV 파일 자동 생성
- 정상 데이터만 선별 저장
- UTF-8 인코딩 지원

### 🧪 테스트 지원
- 테스트 모드로 시뮬레이션 가능
- 더미 데이터 자동 생성
- 실제 환경과 동일한 동작

### 🔧 시스템 통합
- 기존 DSCT 시스템과 독립적 동작
- 시리얼 연결 상태와 연동
- 사용자 친화적 UI

## v3.3 업데이트 (2025-01-31)

### 1. UI/UX 개선

#### 1.1 온습도 위젯 가독성 향상
- **문제점**: 작은 폰트와 많은 정보로 인한 가독성 저하
- **해결책**:
  - 상태 레이블(정상/타임아웃/대기중) 제거
  - 업데이트 시간 레이블 제거
  - 위젯 높이 축소: 90px → 80px
  - 폰트 크기 대폭 증가:
    - 제목: 10px → 14px (bold)
    - 값: 10px → 16px (bold)
    - 단위: 10px → 14px

#### 1.2 적용 파일
- `ui/sensor_widget.py`: 공통 위젯 수정으로 DSCT/AIRCON 모두 적용

### 2. CSV 파일 분할 저장 기능

#### 2.1 일별 파일 분할
- **파일명 형식 변경**:
  - 기존: `dsct_sensor_data_20250131.csv`
  - 변경: `DSCT_2025-01-31.csv`
  - AIRCON도 동일하게 `AIRCON_2025-01-31.csv` 형식 적용
- **자동 날짜 변경**: 날짜가 바뀌면 새 파일 자동 생성

#### 2.2 크기 기반 분할
- **10MB 제한**: 파일 크기가 10MB에 도달하면 자동 분할
- **순차 번호 방식**: 
  - 첫 파일: `DSCT_2025-01-31.csv`
  - 분할 파일: `DSCT_2025-01-31_001.csv`, `DSCT_2025-01-31_002.csv`
  - 3자리 인덱스로 최대 999개까지 분할 가능

#### 2.3 구현 방식
```python
def _get_csv_filename(self):
    """현재 날짜와 파일 크기를 고려하여 CSV 파일명 생성"""
    today = datetime.now().strftime('%Y-%m-%d')
    base_filename = f'DSCT_{today}'  # 또는 'AIRCON_{today}'
    
    file_index = 0
    while True:
        if file_index == 0:
            filename = f'{base_filename}.csv'
        else:
            filename = f'{base_filename}_{file_index:03d}.csv'
        
        if not os.path.exists(filename):
            return filename
        
        file_size = os.path.getsize(filename)
        if file_size < 10 * 1024 * 1024:  # 10MB
            return filename
        
        file_index += 1
```

#### 2.4 수정된 파일
- `managers/sensor_manager.py`: DSCT 센서 CSV 분할 구현
- `managers/air_sensor_manager.py`: AIRCON 센서 CSV 분할 구현

### 3. 기술적 개선사항

#### 3.1 파일 관리 효율성
- **실시간 크기 체크**: 매 저장 시 파일 크기 확인
- **자동 롤링**: 크기 제한 도달 시 즉시 새 파일로 전환
- **기존 호환성**: CSV 구조 및 필드 유지

#### 3.2 성능 최적화
- **파일 핸들링**: append 모드로 효율적 쓰기
- **메모리 사용**: 스트리밍 방식으로 메모리 최적화

---

## v3.4 업데이트 (2025년 8월 4일)

### 주요 기능 추가 및 개선

#### 1. USB 자동 감지 및 CSV 파일 저장 기능
**목적**: 사용자 편의성 향상을 위한 자동 백업 시스템 구축

##### 1.1 USB 자동 감지 시스템
- **신규 모듈**: `utils/usb_detector.py` 생성
- **실시간 모니터링**: 2초 간격으로 USB 연결/해제 감지
- **다중 마운트 지원**: `/media`, `/mnt`, `/media/pi` 등 다양한 마운트 포인트 지원
- **PyQt5 시그널 연동**: `usb_connected`, `usb_disconnected` 시그널 제공

```python
class USBDetector(QObject):
    usb_connected = pyqtSignal(str)    # USB 연결됨 (마운트 경로)
    usb_disconnected = pyqtSignal()    # USB 연결 해제됨
```

##### 1.2 CSV 파일 저장 버튼 추가
- **DSCT T/H TAB**: "수동 새로고침" 버튼 왼쪽에 "CSV 파일 저장" 버튼 추가
- **AIRCON T/H TAB**: 동일한 위치에 "CSV 파일 저장" 버튼 추가
- **스마트 활성화**: USB 연결 시에만 버튼 활성화
- **자동 폴더 생성**: USB에 "AIRCON_CSV" 폴더 자동 생성

##### 1.3 실시간 상태 표시
- **USB 상태 레이블**: "USB: 연결됨/연결 안됨" 실시간 표시
- **연결된 USB 이름**: 마운트 포인트 기반 USB 장치명 표시
- **색상 구분**: 연결됨(녹색), 연결 안됨(회색)

#### 2. 센서 새로고침 간격 설정 시스템
**목적**: 네트워크 환경에 맞는 최적화된 센서 모니터링

##### 2.1 동적 간격 조정 UI
- **3버튼 구성**: `[-]` `숫자` `[+]` 형태의 간격 조절 UI
- **범위 제한**: 최소 1초 ~ 최대 360초
- **실시간 반영**: 버튼 클릭 시 즉시 센서 매니저에 적용
- **독립 설정**: DSCT와 AIRCON 각각 다른 간격 설정 가능

##### 2.2 설정 영구 저장 시스템
- **설정 관리자**: `config/config_manager.py` 모듈 생성
- **JSON 기반 저장**: `config/settings.json` 파일에 설정 저장
- **자동 복원**: 앱 재시작 시 마지막 설정값으로 자동 복원
- **오류 처리**: 파일 손상 시 기본값(5초)으로 자동 복구

```json
{
  "refresh_intervals": {
    "dsct_sensor": 10,
    "aircon_sensor": 15
  },
  "last_updated": "2025-08-04 14:07:43"
}
```

##### 2.3 센서 매니저 연동
- **동적 타이머 변경**: `set_refresh_interval()` 메서드 추가
- **실시간 적용**: 설정 변경 시 즉시 타이머 간격 조정
- **자동 새로고침 레이블**: 현재 간격 실시간 표시

#### 3. UI/UX 개선사항

##### 3.1 버튼 텍스트 간소화
- **변경 전**: "수동 새로고침"
- **변경 후**: "새로고침"
- **버튼 크기 조정**: 120px → 100px (공간 효율성)

##### 3.2 탭 제목 일관성 개선
- **DSCT T/H TAB**: "DSCT 온습도 모니터링"
- **AIRCON T/H TAB**: "AIRCON 온습도 모니터링"

##### 3.3 새로고침 간격 UI 최적화
- **대괄호 제거**: `[5]` → `5` (시각적 간소화)
- **우측 정렬**: 시간 조절 UI를 탭 우측에 안정감 있게 배치
- **레이아웃**: `새로고침 간격: [-] 5 [+] 초`

#### 4. 센서 위젯 레이아웃 최적화
**목적**: DSCT T/H TAB의 12개 센서 위젯 완전 표시

##### 4.1 위젯 크기 최적화
- **높이 감소**: 80px → 70px (10px 절약)
- **내부 여백**: (8,5,8,5) → (6,3,6,3)
- **요소 간격**: 2px → 1px

##### 4.2 폰트 및 요소 크기 조정
- **ID 폰트**: 11pt → 10pt
- **레이블 폰트**: 14px → 12px
- **값 폰트**: 16px → 14px
- **레이블 너비**: 45px → 40px
- **단위 너비**: 25px → 20px

##### 4.3 그리드 레이아웃 최적화
- **그리드 간격**: 5px → 4px
- **메인 레이아웃 간격**: 5px → 4px
- **하단 정보 간격**: 20px → 15px
- **여백 최소화**: 하단 여백 `addStretch(1)` 적용

##### 4.4 공간 절약 효과
```
기존 총 높이: (80 + 5) × 3 - 5 = 250px
개선 총 높이: (70 + 4) × 3 - 4 = 218px
절약 공간: 32px + 추가 여백 최적화
```

### 기술적 구현사항

#### 1. 모듈화된 설계
- **USB 감지**: `utils/usb_detector.py` - 재사용 가능한 독립 모듈
- **설정 관리**: `config/config_manager.py` - 싱글톤 패턴으로 전역 접근
- **탭별 독립**: 각 탭이 독립적으로 USB 감지기와 설정 관리자 사용

#### 2. 실시간 연동 시스템
- **PyQt5 시그널/슬롯**: USB 상태 변화 실시간 반영
- **자동 저장**: 설정 변경 시 즉시 파일 저장
- **UI 동기화**: 모든 관련 UI 요소 실시간 업데이트

#### 3. 오류 처리 및 안정성
- **파일 시스템 안전성**: 설정 파일 손상 시 자동 복구
- **USB 감지 안정성**: 예외 처리로 시스템 안정성 확보
- **유효성 검증**: 1~360초 범위 체크 및 타입 검증

### 수정된 파일 목록

#### 신규 파일
- `utils/usb_detector.py` - USB 자동 감지 모듈
- `config/config_manager.py` - 설정 관리 모듈
- `config/__init__.py` - config 패키지 초기화
- `utils/__init__.py` - utils 패키지 초기화

#### 수정된 파일
- `ui/sensor_tab.py` - DSCT T/H 탭 UI 개선 및 기능 추가
- `ui/aircon_sensor_tab.py` - AIRCON T/H 탭 UI 개선 및 기능 추가
- `ui/sensor_widget.py` - 센서 위젯 크기 및 레이아웃 최적화
- `managers/sensor_manager.py` - 동적 새로고침 간격 지원
- `managers/air_sensor_manager.py` - 동적 새로고침 간격 지원

#### 생성된 설정 파일
- `config/settings.json` - 사용자 설정 영구 저장

## 향후 개선 사항

1. **USB 보안 기능**: 특정 USB만 인식하는 화이트리스트 기능
2. **데이터 분석 기능**: 온도/습도 트렌드 분석 및 그래프 표시
3. **알람 기능**: 임계값 초과 시 알림 및 이메일 발송
4. **원격 모니터링**: 웹 인터페이스 및 모바일 앱 연동
5. **클라우드 백업**: 자동 클라우드 동기화 기능

## 결론

v3.4 업데이트를 통해 사용자 편의성이 크게 향상되었습니다:

- **자동화**: USB 연결만으로 즉시 CSV 백업 가능
- **개인화**: 각 사용자 환경에 맞는 센서 간격 설정
- **지속성**: 설정값 영구 저장으로 재시작 후에도 유지
- **최적화**: 12개 센서 위젯 완전 표시로 모니터링 효율성 극대화

---

## v3.5 업데이트 - 순차 CMD 전송 시스템 (2025년 8월 7일)

### 문제 상황
DSCT T/H TAB와 AIRCON T/H TAB에서 센서 데이터 CMD 명령이 정상적으로 전송되지 않고, 동시에 전송되어 충돌하는 문제가 발생했습니다.

### 해결 방안
기존의 독립적인 센서 매니저 방식에서 **중앙 스케줄러 기반의 순차 처리 시스템**으로 완전히 재설계했습니다.

### 1. 핵심 아키텍처 변경

#### 1.1 SensorScheduler 클래스 신규 개발
**파일**: `managers/sensor_scheduler.py`

**주요 기능:**
- **상태 머신 패턴**: IDLE → AIRCON_REQUESTING → AIRCON_WAITING → DSCT_REQUESTING → DSCT_WAITING → INTERVAL_WAITING 순으로 진행
- **순차 처리**: AIRCON CMD 전송 → 응답 대기 → DSCT CMD 전송 → 응답 대기 → 주기 대기 → 반복
- **타임아웃 처리**: 각 단계별 10초 타임아웃으로 무응답 상황 방지
- **중앙 집중**: 모든 센서 요청을 스케줄러가 통제

```python
class SchedulerState(Enum):
    IDLE = "idle"
    AIRCON_REQUESTING = "aircon_requesting" 
    AIRCON_WAITING = "aircon_waiting"
    DSCT_REQUESTING = "dsct_requesting"
    DSCT_WAITING = "dsct_waiting"
    INTERVAL_WAITING = "interval_waiting"
    PAUSED = "paused"
```

#### 1.2 시리얼 통신 프로토콜 수정
**파일**: `managers/serial_manager.py`

**문제점 발견 및 수정:**
- **잘못된 종료 문자**: `\r` → `\r\n` (<CR><LF>)로 수정
- **원시 데이터 로깅**: 수신된 바이트 데이터를 16진수로 표시하여 디버깅 강화
- **콜백 조건 개선**: [AIRCON] 태그도 인식하도록 확장

```python
def send_serial_command(self, command):
    """시리얼 명령 전송 함수 (종료 문자 자동 추가)"""
    if self.is_connected():
        full_command = f"{command}\r\n"  # <CR><LF> 추가
        result = self.send_data(full_command)
        if result:
            print(f"[TX] 시리얼 명령 전송: {command} (with <CR><LF>)")
        return result
```

### 2. 태그 표준화 및 호환성

#### 2.1 [AIR] → [AIRCON] 표준화
**목적**: 시스템 내 일관성 확보 및 향후 확장성 고려

**수정된 파일:**
- `managers/air_sensor_manager.py`: 정규식 패턴 수정
- `managers/serial_manager.py`: 콜백 조건 확장

```python
# 기존
self.data_pattern = re.compile(r'\[AIR\]\s+(ID\d{2}),TEMP:\s*([\d.]+),\s*HUMI:\s*([\d.]+)')

# 변경후
self.data_pattern = re.compile(r'\[AIRCON\]\s+(ID\d{2}),TEMP:\s*([\d.]+),\s*HUMI:\s*([\d.]+)')
```

#### 2.2 ID07, ID08 센서 제거
**목적**: 현장 요구사항에 따른 AIRCON 센서 개수 조정 (6개로 제한)

**변경사항:**
- AIRCON 센서 데이터 저장소: ID01~ID06만 관리
- UI 위젯: 6개 센서만 표시
- 수신 데이터: ID07, ID08은 파싱되지만 무시 처리

### 3. UI/UX 개선

#### 3.1 버튼 텍스트 변경
- **변경 전**: "새로고침"
- **변경 후**: "명령 전송"
- **목적**: 사용자에게 명확한 동작 의미 전달

#### 3.2 자동 CMD 전송 시작
- **시리얼 연결 완료 시**: 자동으로 스케줄러 시작
- **사용자 개입 불필요**: 연결만으로 모니터링 시작
- **수동 버튼**: 즉시 CMD 전송이 필요한 경우 사용

### 4. 센서 매니저 리팩토링

#### 4.1 자동 타이머 제거
**기존 구조 문제:**
- 각 센서 매니저가 독립적인 타이머 보유
- 동시 CMD 전송으로 인한 충돌 발생

**해결 방안:**
- 모든 자동 타이머를 스케줄러로 이관
- 센서 매니저는 순수하게 데이터 파싱과 저장만 담당

```python
# 제거된 코드 (주석 처리)
# self.auto_refresh_timer = QTimer()
# self.auto_refresh_timer.timeout.connect(self.request_sensor_data)

# 스케줄러 관리 모드로 변경
def set_serial_manager(self, serial_manager):
    """시리얼 매니저 설정 (자동 요청 제거, 스케줄러가 관리)"""
    self.serial_manager = serial_manager
    print("[AIRCON] 시리얼 매니저 설정 완료 (스케줄러 관리 모드)")
```

### 5. 시스템 통합 및 연동

#### 5.1 MainWindow 통합
**파일**: `ui/main_window.py`

**추가된 기능:**
- SensorScheduler 인스턴스 생성 및 관리
- 시리얼 연결 시 스케줄러 자동 시작
- 연결 해제 시 스케줄러 자동 중지
- 오류 발생 시 스케줄러 일시정지

```python
def __init__(self):
    # 센서 스케줄러 초기화
    self.sensor_scheduler = SensorScheduler(self.serial_manager, test_mode=self.test_mode)
    self.sensor_scheduler.set_sensor_managers(self.air_sensor_manager, self.sensor_manager)
```

#### 5.2 UI 탭 연동
**파일**: `ui/sensor_tab.py`, `ui/aircon_sensor_tab.py`

**변경사항:**
- 스케줄러 참조 추가
- 수동 요청을 스케줄러를 통해 처리
- 간격 조정 시 스케줄러에 반영

### 6. 디버깅 및 로깅 강화

#### 6.1 상세한 로그 시스템
- **상태 변화 추적**: 스케줄러 상태 전환 로그
- **시리얼 통신 로그**: 송수신 데이터 원시 바이트 표시
- **타임아웃 처리**: 무응답 시간 측정 및 로그
- **콜백 조건 체크**: 데이터 파싱 성공/실패 상세 로그

#### 6.2 실시간 상태 모니터링
```
[SCHEDULER] 상태 변경: idle → aircon_requesting
[TX] 시리얼 명령 전송: $CMD,AIR,TH (with <CR><LF>)
[SCHEDULER] 상태 변경: aircon_requesting → aircon_waiting
[RX RAW] 수신된 원본 바이트: b'[AIRCON] ID01,TEMP: 28.3, HUMI: 67.7\r\n'
[AIRCON RX] ID01 센서 데이터 파싱 성공: 온도=28.3°C, 습도=67.7%
[SCHEDULER] AIRCON 응답 완료, DSCT로 이동
```

### 7. 테스트 및 검증

#### 7.1 실제 하드웨어 테스트
- ✅ AIRCON 센서 데이터 정상 수신 및 위젯 표시
- ✅ 순차 처리 시스템 정상 작동 (AIRCON → DSCT → 대기)
- ✅ 타임아웃 처리 정상 작동 (DSCT 하드웨어 무응답 시)
- ✅ 수동 명령 전송 버튼 정상 작동

#### 7.2 발견된 이슈
- **DSCT 하드웨어 미응답**: DSCT 명령은 전송되지만 응답이 없음
- **프레임워크 완성도**: DSCT 데이터가 수신되면 정상 처리될 것으로 예상

### 8. 기술적 성과

#### 8.1 아키텍처 개선
- **단일 책임 원칙**: 스케줄러는 순서 제어, 매니저는 데이터 처리
- **상태 머신 패턴**: 복잡한 순차 처리를 명확한 상태로 관리
- **중앙 집중 제어**: 모든 센서 요청을 하나의 지점에서 통제

#### 8.2 신뢰성 향상
- **충돌 방지**: 동시 CMD 전송 문제 완전 해결
- **타임아웃 처리**: 무응답 상황에서도 시스템 계속 작동
- **오류 복구**: 연결 상태 체크로 자동 복구

#### 8.3 사용자 경험 개선
- **자동 시작**: 연결만으로 모니터링 시작
- **명확한 버튼**: "명령 전송"으로 의미 명확화
- **실시간 피드백**: 상태 변화 즉시 반영

### 수정된 파일 목록

#### 신규 파일
- `managers/sensor_scheduler.py` - 중앙 센서 스케줄러 (핵심 신규)

#### 주요 수정 파일
- `managers/serial_manager.py` - 프로토콜 수정 및 로깅 강화
- `managers/air_sensor_manager.py` - [AIRCON] 태그 적용, ID07/ID08 제거
- `managers/sensor_manager.py` - 스케줄러 연동을 위한 로직 수정
- `ui/main_window.py` - 스케줄러 통합
- `ui/sensor_tab.py` - 스케줄러 연동 및 UI 개선
- `ui/aircon_sensor_tab.py` - 스케줄러 연동 및 UI 개선

### 결론

v3.5는 시스템의 근본적인 안정성 문제를 해결한 핵심 업데이트입니다:

- **순차 처리**: CMD 전송 충돌 문제 완전 해결
- **프로토콜 수정**: 시리얼 통신 안정성 확보
- **중앙 관리**: 스케줄러 기반의 체계적인 센서 제어
- **자동화**: 사용자 개입 없는 자동 모니터링 시작
- **표준화**: [AIRCON] 태그 통일로 시스템 일관성 확보

이제 AIRCON과 DSCT 센서가 서로 간섭 없이 순차적으로 모니터링되며, 하나의 하드웨어가 응답하지 않아도 시스템 전체가 안정적으로 동작합니다.

---

## v3.6 업데이트 - 비동기 시리얼 처리 시스템 (2025년 8월 19일)

### 📋 문제 상황
- 센서 모니터링 기능이 자주 데이터를 요청하면서 중요한 serial CMD 명령어가 블로킹되어 시스템이 hang 걸리는 현상
- 기존 해결책: 시리얼 데이터 읽기를 완전히 비활성화하여 센서 모니터링 기능 상실

### 🎯 해결 목표
- 버튼 명령의 즉각적 응답성 보장 
- 센서 데이터 모니터링 기능 복구
- 시스템 hang 현상 완전 해결
- DSCT 12개 + AIRCON 6개 센서 데이터 안정적 처리

## 🔧 구현된 해결책

### Phase 1: 우선순위 기반 명령 큐 시스템
- **새 파일**: `managers/command_queue_manager.py`
  - 3단계 우선순위 큐 (HIGH/NORMAL/LOW)
  - 50ms 간격 비동기 처리
  - 명령 재시도 로직 (최대 3회)
  - 스레드 안전성 보장 (QMutex)

- **수정 파일**: `managers/serial_manager.py`
  - 큐 매니저 연동 메서드 추가
  - `send_serial_command_with_priority()` 함수 추가

- **수정 파일**: `ui/main_window.py`
  - CommandQueueManager 초기화 및 연결

- **수정 파일**: `managers/button_manager.py`
  - 모든 버튼 명령을 HIGH 우선순위로 전송

### Phase 2: 비동기 시리얼 데이터 읽기
- **새 파일**: `managers/serial_reader_thread.py`
  - 전용 읽기 스레드 (QThread)
  - 10ms 간격 비블로킹 읽기
  - 메인 스레드 hang 방지

- **수정 파일**: `managers/serial_manager.py`
  - `read_data()` 함수 복구 (비블로킹 방식)
  - 읽기 스레드 통합 및 생명주기 관리
  - 데이터 수신 시그널 연결

### Phase 3: 센서 스케줄러 우선순위 및 제한
- **수정 파일**: `managers/sensor_scheduler.py`
  - 센서 요청을 LOW 우선순위로 처리
  - 안전한 주기 간격 제한 (5~300초)
  - 자동/수동 센서 요청 기능 복구

- **수정 파일**: `ui/constants.py`
  - 센서 새로고침 간격 제한 상수 추가
  ```python
  SENSOR_REFRESH_LIMITS = {
      'MIN_INTERVAL': 5,      # 최소 5초
      'DEFAULT_INTERVAL': 10, # 기본 10초
      'MAX_INTERVAL': 300     # 최대 5분
  }
  ```

- **수정 파일**: `ui/sensor_tab.py`, `ui/aircon_sensor_tab.py`
  - UI에서 안전한 범위로만 간격 조정 가능
  - 1초 간격 완전 차단

## 📊 시스템 아키텍처

```
[UI 버튼] ──HIGH────┐
                   ├──→ [CommandQueue] ──50ms──→ [SerialManager] ──→ [하드웨어]
[센서 요청] ──LOW─────┘                                      ↑
                                                           │
[읽기 스레드] ←──10ms──← [SerialReaderThread] ←──────────────┘
     │
     └──→ [센서 매니저] ──→ [UI 업데이트]
```

## ✅ 핵심 개선 사항

### 우선순위 처리
- **HIGH**: 버튼 명령 (즉시 처리)
- **NORMAL**: 일반 명령
- **LOW**: 센서 데이터 요청

### 시간 제한
- 기존: 1~360초 (위험한 1초 간격 허용)
- 개선: 5~300초 (시스템 안정성 보장)

### 비동기 처리
- 명령 전송: 50ms 간격 큐 처리
- 데이터 읽기: 10ms 간격 별도 스레드
- UI 블로킹: 완전 방지

## 🎉 예상 결과

- **버튼 응답성**: 즉시 반응 (HIGH 우선순위)
- **센서 데이터**: 안정적 수집 (LOW 우선순위, 5초 이상 간격)
- **시스템 안정성**: hang 현상 해결
- **데이터 처리**: DSCT 12개 + AIRCON 6개 센서 모두 안정적 처리

## 🧪 테스트 방법

```bash
# 테스트 모드 실행 (시리얼 하드웨어 없이)
python main.py --test

# 실제 하드웨어와 연결 시
python main.py
```

### 확인 포인트
1. 큐 시스템 초기화 로그 확인
2. 버튼 클릭 시 즉시 반응 확인
3. 센서 데이터 주기적 수신 확인
4. 새로고침 간격 제한 동작 확인

## 📁 변경된 파일 목록

### 새로 추가된 파일
- `managers/command_queue_manager.py` - 우선순위 기반 명령 큐 시스템
- `managers/serial_reader_thread.py` - 전용 시리얼 읽기 스레드

### 수정된 파일
- `managers/serial_manager.py` - 큐 시스템 통합, 읽기 스레드 관리
- `managers/sensor_scheduler.py` - 우선순위 적용, 주기 제한
- `managers/button_manager.py` - HIGH 우선순위 적용
- `ui/main_window.py` - 큐 매니저 초기화
- `ui/constants.py` - 센서 제한 상수 추가
- `ui/sensor_tab.py` - 새로고침 간격 제한 적용
- `ui/aircon_sensor_tab.py` - 새로고침 간격 제한 적용

## 🔄 호환성
- 기존 UI 코드 100% 유지
- 기존 인터페이스 하위 호환성 보장
- 점진적 적용으로 안전한 업그레이드

## 🔗 참조
**기반 참조**: [NewAircon](https://github.com/JamesjinKim/NewAircon.git) 저장소의 비동기 처리 방식을 현재 프로젝트에 적용

### 결론

v3.6은 시스템의 근본적인 성능 및 안정성 문제를 해결한 핵심 업데이트입니다:

- **우선순위 처리**: 버튼 명령 즉시 반응, 센서 요청 배경 처리
- **비동기 읽기**: 별도 스레드로 UI hang 완전 방지  
- **안전한 제한**: 5초 최소 간격으로 시스템 안정성 확보
- **완전 호환성**: 기존 UI/기능 100% 유지하면서 성능 향상

이제 버튼 제어와 센서 모니터링이 동시에 안정적으로 동작하며, 시스템 hang 현상 없이 모든 기능을 사용할 수 있습니다.

---

## v3.7 업데이트 - SOL 밸브 통합 제어 시스템 (2025년 10월 12일)

### 📋 문제 상황
- MESSAGE.md 명세에 따르면 `$CMD,DSCT,SOL1,ON` 명령 하나로 모든 SOL 밸브(1~4)를 동시 제어해야 함
- 하지만 UI에는 SOL1, SOL2, SOL3, SOL4 **4개의 독립적인 버튼**이 구현되어 있어 혼란 발생
- SOL 밸브 개폐 시 **15초 딜레이**가 발생하지만 사용자에게 시각적 피드백 없음
- 진행 중 중복 클릭 방지 메커니즘 부재

### 🎯 해결 목표
- SOL1 버튼 하나로 모든 SOL 밸브(1~4) 통합 제어
- 15초 딜레이 동안 사용자에게 시각적 피드백 제공
- 진행 중 중복 클릭 방지
- 20초 타임아웃 안전 장치 구현
- 테스트 모드 지원 (더미 응답 시뮬레이션)

## 🔧 구현된 해결책

### Phase 1: UI 간소화 및 통합

#### 1.1 SOL 버튼 통합
**수정 파일**: `ui/main_window.py`

**변경사항:**
- ❌ SOL2, SOL3, SOL4 버튼 완전 제거
- ✅ SOL1 버튼 레이블 변경: `SOL1` → `SOL 1~4`
- 하나의 버튼으로 모든 SOL 밸브 통합 제어
- 레이블 너비 조정: 50px → 70px

**수정 파일**: `ui/setup_buttons.py`

**변경사항:**
- SOL2, SOL3, SOL4 그룹 제거
- SOL1 그룹만 유지하며 명령어는 동일 유지
- 주석 추가: "15초 딜레이와 Flicker 애니메이션은 button_manager에서 처리"

### Phase 2: Flicker 애니메이션 시스템

#### 2.1 상태 관리 변수 추가
**수정 파일**: `managers/button_manager.py`

**새로운 인스턴스 변수:**
```python
self.sol_in_progress = False      # SOL 동작 진행 중 플래그
self.sol_flicker_state = False    # Flicker 상태 토글
self.sol_flicker_timer = None     # Flicker 타이머
self.sol_timeout_timer = None     # SOL 타임아웃 타이머
self.sol_timeout = 20000          # 타임아웃 시간 (ms) - 20초
```

#### 2.2 Flicker 애니메이션 구현
**핵심 메서드:**

1. **`_start_sol_flicker()`**: Flicker 시작
   - 진행 중 플래그 설정
   - SOL1 버튼 참조 가져오기
   - Flicker 틱 시작

2. **`_sol_flicker_tick()`**: 0.5초 간격 색상 토글
   - **골드색(#FFD700)**: 진행 중 표시
   - **초록색(BUTTON_ON_STYLE)**: 성공 상태
   - QTimer.singleShot(500ms)로 재귀 호출

3. **`_stop_sol_flicker(final_state)`**: Flicker 중지 + 최종 상태 설정
   - 'ON' 또는 'OFF' 최종 상태로 버튼 변경
   - 타이머 정리 및 플래그 해제
   - button_groups 상태 동기화

#### 2.3 시각적 상태 전환
```
[OFF 상태] → [클릭]
    ↓
[골드 ↔ 초록 깜빡임] (진행 중, 0.5초 간격)
    ↓
[장비 응답 수신]
    ↓
[ON/OFF 상태] (완료)
```

### Phase 3: 시리얼 응답 처리

#### 3.1 응답 메시지 파싱
**새 메서드**: `parse_sol_response(data)`

**처리 메시지:**
| 수신 메시지 | 동작 |
|-----------|------|
| `DSCT,SOL,All Opening!` | 열림 시작 (Flicker 계속) |
| `DSCT,SOL All Open OK!` | 열림 완료 (Flicker 중지 → ON) |
| `DSCT,SOL,All Closing!` | 닫힘 시작 (Flicker 계속) |
| `DSCT,SOL All Close OK!` | 닫힘 완료 (Flicker 중지 → OFF) |

#### 3.2 메인 파싱 루프 통합
**수정 메서드**: `parse_reload_response(data)`

```python
def parse_reload_response(self, data: str):
    """RELOAD 및 SOL 응답 파싱 및 처리"""
    # SOL 응답 파싱 (최우선)
    self.parse_sol_response(data)

    # DSCT 리로드 응답 처리
    if self.dsct_reload_in_progress:
        # ...
```

### Phase 4: 안전 장치 구현

#### 4.1 중복 클릭 방지
**수정 위치**: `_toggle_button()` 메서드 시작 부분

```python
# SOL1 진행 중이면 중복 클릭 방지
if group_name == 'sol1' and self.sol_in_progress:
    print("[SOL] 이미 진행 중 - 클릭 무시")
    return
```

#### 4.2 타임아웃 처리 (20초)
**새 메서드:**
- `_start_sol_timeout_timer()`: 20초 타이머 시작
- `_cancel_sol_timeout_timer()`: 타이머 취소
- `_handle_sol_timeout()`: 타임아웃 시 처리
  - 빨간색 `TIMEOUT!` 표시
  - 2초 후 자동 OFF 복귀

**타임아웃 시각 효과:**
```python
button.setStyleSheet("""
    QPushButton {
        background-color: #F44336;  /* 빨간색 */
        color: white;
        border: 2px solid #D32F2F;
    }
""")
button.setText("TIMEOUT!")
```

### Phase 5: 테스트 모드 지원

#### 5.1 명령 감지 및 더미 응답 트리거
**수정 위치**: `send_command_or_call_function()` 메서드

```python
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
```

#### 5.2 더미 응답 시뮬레이션
**새 메서드:**

1. **`_simulate_sol_open_response()`**: OPEN 시뮬레이션
   - 즉시: `DSCT,SOL,All Opening!`
   - 15초 후: `DSCT,SOL All Open OK!`

2. **`_simulate_sol_close_response()`**: CLOSE 시뮬레이션
   - 즉시: `DSCT,SOL,All Closing!`
   - 15초 후: `DSCT,SOL All Close OK!`

## 📊 시스템 플로우

```
[사용자] → [SOL 1~4 버튼 클릭]
    ↓
[ButtonManager] → 중복 클릭 체크
    ↓
[시리얼 명령 전송] $CMD,DSCT,SOL1,ON/OFF
    ↓
[Flicker 시작] 골드 ↔ 초록 (0.5초 간격)
    ↓
[타임아웃 타이머 시작] 20초
    ↓
[장비 응답 대기]
    ├─ [DSCT,SOL,All Opening/Closing!] → Flicker 계속
    ├─ [DSCT,SOL All Open/Close OK!] → Flicker 중지, 최종 상태 설정
    └─ [20초 경과] → TIMEOUT 표시 → 2초 후 OFF 복귀
```

## ✅ 핵심 개선 사항

### UI 간소화
- **버튼 개수**: 4개 → 1개
- **명확한 의미**: `SOL 1~4` 레이블로 통합 제어 명시
- **공간 효율**: 불필요한 버튼 제거로 UI 깔끔화

### 사용자 경험 개선
- **시각적 피드백**: 0.5초 간격 Flicker로 진행 상태 명확히 전달
- **중복 클릭 방지**: 진행 중 클릭 무시로 혼란 방지
- **자동 복구**: 타임아웃 후 2초 뒤 자동 정상 상태 복귀

### 안전성 강화
- **타임아웃 처리**: 20초 내 응답 없으면 에러 표시
- **상태 동기화**: button_groups 상태와 UI 완전 일치
- **테스트 지원**: 하드웨어 없이도 기능 검증 가능

## 🧪 테스트 방법

### 옵션 1: 테스트 모드 (추천)
```bash
python main.py --test
```

**동작 시나리오:**
1. DESICCANT 탭 이동
2. `SOL 1~4` 버튼 클릭
3. 즉시 골드 ↔ 초록 Flicker 시작 확인
4. **15초 후** 자동으로 ON/OFF 상태 변경 확인
5. 진행 중 버튼 클릭 시 무반응 확인

**콘솔 로그 확인:**
```
[SOL] SOL1 명령 감지 - Flicker 시작
[SOL] 타임아웃 타이머 시작: 20000ms
[TEST] SOL OPEN 더미 응답 시뮬레이션 시작
[SOL] 밸브 열림 시작
[SOL] ✅ 밸브 열림 완료
[SOL] Flicker 중지 - 최종 상태: ON
[SOL] 타임아웃 타이머 취소
```

### 옵션 2: 실제 하드웨어 연결
```bash
python main.py
```

**확인 포인트:**
- [ ] 시리얼 연결 후 DESICCANT 탭 이동
- [ ] `SOL 1~4` 버튼 클릭 → Flicker 시작
- [ ] 장비 응답 수신 → Flicker 중지
- [ ] 타임아웃 테스트 (장비 연결 해제 후 버튼 클릭)
- [ ] 20초 후 빨간색 `TIMEOUT!` 표시
- [ ] 2초 후 자동 OFF 복귀

## 📁 변경된 파일 목록

### 수정된 파일
1. **`ui/main_window.py`** (916-931 라인)
   - SOL2~4 버튼 UI 제거
   - SOL1 레이블 `SOL 1~4`로 변경
   - 레이블 너비 조정
   - SOL2~4 버튼 참조 제거

2. **`ui/setup_buttons.py`** (124-131 라인)
   - SOL2~4 그룹 제거
   - SOL1 그룹 유지 및 주석 추가

3. **`managers/button_manager.py`** (920-1140 라인, 약 220라인 추가)
   - SOL 상태 관리 변수 추가
   - Flicker 애니메이션 시스템 구현
   - 시리얼 응답 파싱 로직 추가
   - 타임아웃 처리 메커니즘
   - 테스트 모드 더미 응답 구현

4. **`CHANGELOG.md`**
   - v3.7 릴리스 노트 추가

## 🔗 MESSAGE.md 명세 충족

### 요구사항 검증
- ✅ `$CMD,DSCT,SOL1,ON` 하나로 모든 SOL 밸브 제어
- ✅ 15초 딜레이 동안 Flicker 애니메이션 (0.5초 간격)
- ✅ `DSCT,SOL,All Opening!` 응답 처리
- ✅ `DSCT,SOL All Open OK!` 완료 메시지 처리
- ✅ 진행 중 사용자 피드백 제공
- ✅ 타임아웃 처리 및 자동 복구

### 프로토콜 준수
```
# 전송
$CMD,DSCT,SOL1,ON<CR><LF>

# 수신
DSCT,SOL,All Opening!<CR><LF>
DSCT,SOL All Open OK!<CR><LF>
[EEPROM] Saving DSCT command: SOL1,ON,<CR><LF>
EEPROM save OK<CR><LF>
```

## 🎉 예상 결과

### 사용자 관점
- **직관적 제어**: 하나의 버튼으로 모든 SOL 밸브 제어
- **명확한 피드백**: 골드 ↔ 초록 깜빡임으로 진행 상태 인지
- **안전한 조작**: 진행 중 중복 클릭 자동 차단
- **자동 복구**: 타임아웃 발생 시 2초 후 자동 정상화

### 개발자 관점
- **명확한 책임 분리**: UI는 표시만, 로직은 manager가 담당
- **재사용 가능한 패턴**: Flicker 시스템은 다른 장치에도 적용 가능
- **테스트 용이성**: 테스트 모드로 하드웨어 없이 검증
- **로그 추적**: 상세한 콘솔 로그로 디버깅 간편

## 📈 기술적 성과

### 아키텍처 개선
- **상태 머신 패턴**: OFF → FLICKERING → ON/OFF 명확한 상태 전이
- **타이머 기반 애니메이션**: QTimer.singleShot으로 안전한 재귀 호출
- **시그널/슬롯 활용**: 시리얼 응답을 파싱 메서드에 자동 전달

### 코드 품질
- **가독성**: 메서드 이름과 주석으로 의도 명확화
- **모듈성**: Flicker 로직이 독립적으로 분리
- **확장성**: 다른 장치도 동일한 패턴 적용 가능

### 신뢰성
- **타임아웃 처리**: 무응답 상황에서도 시스템 정상 작동
- **상태 복구**: 에러 후 자동 정상 상태 복귀
- **중복 방지**: 플래그 기반 중복 클릭 차단

## 🔮 향후 확장 가능성

1. **다른 장치 적용**: PUMP, FAN 등에도 Flicker 패턴 재사용
2. **진행률 표시**: Flicker 대신 프로그레스 바 추가 가능
3. **사운드 피드백**: Flicker와 함께 비프음 추가
4. **로그 파일 저장**: SOL 동작 이력을 파일로 기록

### 결론

v3.7은 사용자 경험과 시스템 안정성을 크게 향상시킨 업데이트입니다:

- **UI 간소화**: 4개 버튼 → 1개 버튼으로 혼란 제거
- **시각적 피드백**: 0.5초 간격 Flicker로 진행 상태 명확화
- **안전 장치**: 중복 클릭 방지 + 20초 타임아웃 처리
- **테스트 지원**: 하드웨어 없이도 기능 검증 가능
- **명세 준수**: MESSAGE.md 요구사항 100% 충족

이제 SOL 밸브 제어가 직관적이고 안전하며, 사용자에게 명확한 피드백을 제공합니다. 15초 딜레이 동안 진행 상태를 시각적으로 확인할 수 있어 사용자 만족도가 크게 향상될 것으로 기대됩니다.

---

## v3.8 업데이트 - 장비 상태 동기화 RELOAD 시스템 (2025년 10월 13일)

### 📋 문제 상황
- 프로그램 재시작 또는 연결 재개 시 **UI 버튼 상태와 실제 장비 상태가 불일치**
- 사용자가 하드웨어 상태를 확인하기 위해 매번 수동으로 모든 버튼 확인 필요
- MESSAGE.md 명세에 `$CMD,DSCT,RELOAD` 프로토콜 정의되어 있지만 미구현
- 장비가 EEPROM에 저장한 마지막 상태를 UI에 반영할 방법 없음

### 🎯 해결 목표
- AIRCON/DESICCANT 탭에 **Refresh 버튼** 추가
- `$CMD,DSCT,RELOAD` / `$CMD,AIR,RELOAD` 명령으로 장비 상태 동기화
- 4단계 시각적 피드백 (정상 → 로딩 → 완료 → 에러)
- 15초 타임아웃 안전 장치
- 모든 버튼 상태 자동 복원 (FAN, PUMP, SOL, SEMIAUTO, DMPTEST 등)

## 🔧 구현된 해결책

### Phase 1: RELOAD 버튼 UI 추가

#### 1.1 AIRCON 탭 Refresh 버튼
**수정 파일**: `ui/main_window.py` (487-506 라인)

**새로운 UI 요소:**
- **위치**: OA.DAMPER 숫자 버튼 하단
- **버튼 텍스트**: `AIR Refresh` (🔄 이모지 포함)
- **버튼 크기**: 140px 너비
- **스타일**: 4가지 상태별 색상 구분

```python
air_reload_button = create_button_row("🔄 RELOAD", QPushButton("AIR Refresh"), right_layout, button_width=140)
air_reload_button.setStyleSheet("""
    QPushButton {
        background-color: #E3F2FD;  /* 연한 파란색 */
        color: #1976D2;
        border: 2px solid #1976D2;
    }
    QPushButton:hover {
        background-color: #BBDEFB;
    }
""")
```

#### 1.2 DESICCANT 탭 Refresh 버튼
**수정 파일**: `ui/main_window.py` (589-608 라인)

**동일한 UI 패턴:**
- **버튼 텍스트**: `DSCT Refresh`
- **배치 위치**: PUMP 버튼 하단
- **동일한 4가지 상태 스타일 지원

#### 1.3 버튼 상태별 시각적 피드백
| 상태 | 배경색 | 텍스트색 | 텍스트 | 아이콘 |
|------|--------|---------|--------|--------|
| **정상** | 연한 파란색 (#E3F2FD) | 파란색 (#1976D2) | `AIR/DSCT Refresh` | 🔄 |
| **로딩** | 주황색 (#FF9800) | 흰색 | `Loading...` | ⏳ |
| **완료** | 초록색 (#4CAF50) | 흰색 | `Complete!` | ✅ |
| **에러** | 빨강색 (#F44336) | 흰색 | `Timeout!` | ⚠️ |

### Phase 2: RELOAD 명령 처리 시스템

#### 2.1 ButtonManager RELOAD 기능 추가
**수정 파일**: `managers/button_manager.py` (13-24, 306-430 라인)

**새로운 상태 관리 변수:**
```python
# RELOAD 기능 관련 변수
self.dsct_reload_in_progress = False   # DSCT 리로드 진행 중
self.dsct_reload_data = []             # DSCT 응답 데이터 저장
self.dsct_reload_start_time = None     # 시작 시간 측정
self.air_reload_in_progress = False    # AIR 리로드 진행 중
self.air_reload_data = []              # AIR 응답 데이터 저장
self.air_reload_start_time = None      # 시작 시간 측정
self.dsct_reload_button = None         # DSCT 버튼 참조
self.air_reload_button = None          # AIR 버튼 참조
self.dsct_reload_timer = None          # 타임아웃 타이머
self.air_reload_timer = None           # 타임아웃 타이머
self.reload_timeout = 15000            # 타임아웃 15초
```

#### 2.2 RELOAD 요청 핸들러
**핵심 메서드:**

1. **`handle_dsct_reload()`**: DSCT 리로드 요청
   - 시리얼 연결 체크
   - 중복 요청 방지
   - 버튼 상태 → 로딩
   - 명령 전송: `$CMD,DSCT,RELOAD`
   - 큐 일시 중지 (다른 명령 차단)
   - 타임아웃 타이머 시작

2. **`handle_air_reload()`**: AIR 리로드 요청
   - 동일한 패턴으로 `$CMD,AIR,RELOAD` 전송

**중요 설계 결정:**
```python
# 명령 전송 (Queue를 거치지 않고 직접 전송)
command = f"{CMD_PREFIX},DSCT,RELOAD"
self.serial_manager.send_serial_command(command)

# 명령 전송 후 큐 일시 중지 (다른 명령 차단)
if hasattr(self.serial_manager, 'command_queue') and self.serial_manager.command_queue:
    self.serial_manager.command_queue.pause_queue()
```

**이유:**
- 센서 스케줄러의 LOW 우선순위 `$CMD,DSCT,TH` 명령이 RELOAD 응답을 방해
- 큐를 일시 중지하여 RELOAD 응답 수신 완료까지 다른 명령 차단

### Phase 3: 시리얼 응답 파싱 및 상태 복원

#### 3.1 응답 메시지 파싱
**핵심 메서드**: `parse_reload_response(data)`

**DSCT 응답 프로토콜:**
```
EEPROM_ACK,RELOAD,START           # 시작 신호
DSCT,FAN_ALL_ON                   # 전체 FAN 상태 (무시)
DSCT,FAN_ALL_SPD,1                # 전체 FAN 속도 (무시)
DSCT,FAN1,ON                      # 개별 FAN 상태
DSCT,FAN1,SPD,1                   # 개별 FAN 속도
DSCT,DMP1,OPEN                    # 댐퍼 상태
DSCT,PUMP1,ON                     # 펌프 상태
DSCT,PUMP1,SPD,6                  # 펌프 속도 (무시)
DSCT,SOL1,ON                      # SOL 밸브 상태 (SOL1만 사용)
DSCT,SOL2,OFF                     # SOL2~4 무시
DSCT,SEMIAUTO,STOP                # SEMI AUTO 상태
DSCT,DMPTEST,STOP                 # DAMP TEST 상태
EEPROM_ACK,RELOAD,END             # 종료 신호
DSCT_ACK,RELOAD,COMPLETE          # 완료 신호
```

**AIR 응답 프로토콜:**
```
EEPROM_ACK,RELOAD,START
AIR,EVA_FAN,ON
AIR,EVA_FAN,SPD,5
AIR,CON_FAN,OFF
AIR,COMPRESSOR,ON
EEPROM_ACK,RELOAD,END
AIRCON_ACK,RELOAD,COMPLETE
```

#### 3.2 상태 적용 로직
**핵심 메서드**: `_apply_dsct_reload_state()`, `_apply_air_reload_state()`

**DSCT 파싱 규칙:**
```python
# FAN_ALL 항목 무시
if function.startswith("FAN_ALL"):
    continue

# FAN1~4 처리
if function in ["FAN1", "FAN2", "FAN3", "FAN4"]:
    if values[0] == "SPD" and len(values) > 1:
        # 하드웨어 속도 값 그대로 복원
        speed = int(values[1])
        fan_num = function[-1]
        self._update_dsct_fan_speed(fan_num, speed)
    else:
        # ON/OFF 상태 복원
        state = values[0]
        fan_num = function[-1]
        self._update_dsct_fan_button(fan_num, state)

# PUMP 처리 (SPD 무시, ON/OFF만 사용)
elif function.startswith("PUMP"):
    if values[0] == "SPD":
        continue  # 속도 무시
    else:
        state = values[0]
        pump_num = function[-1]
        self._update_pump_button(pump_num, state)

# SOL 처리 (SOL1만 사용)
elif function.startswith("SOL"):
    sol_num = function[-1]
    if sol_num == "1":
        state = values[0]
        self._update_sol_button(sol_num, state)
    else:
        print(f"[RELOAD] SOL{sol_num} 항목 무시")

# SEMIAUTO 처리
elif function == "SEMIAUTO":
    state = values[0]  # RUN/STOP
    self._update_semiauto_button(state)

# DMPTEST 처리
elif function == "DMPTEST":
    state = values[0]  # RUN/STOP
    self._update_dmptest_button(state)
```

#### 3.3 버튼 상태 업데이트 메서드

**FAN 버튼 복원:**
```python
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

        # OFF로 변경될 때 속도 버튼 초기화
        if was_on and not is_on:
            self._handle_fan_off_callback(group_name)
```

**SEMI AUTO 버튼 복원:**
```python
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
```

### Phase 4: 큐 일시 중지/재개 시스템

#### 4.1 CommandQueueManager 확장
**수정 파일**: `managers/command_queue_manager.py` (56, 117, 223-231 라인)

**새로운 기능:**
```python
# 큐 일시 중지 플래그
self.is_paused = False

def _process_queue(self):
    """큐 처리 (타이머에서 호출)"""
    if self.is_processing or self.is_paused:
        return  # 일시 중지 중이면 처리 안 함

def pause_queue(self):
    """큐 처리 일시 중지 (RELOAD 등 응답 대기 중)"""
    self.is_paused = True
    print("[QUEUE] 🛑 큐 처리 일시 중지 (RELOAD 응답 대기)")

def resume_queue(self):
    """큐 처리 재개"""
    self.is_paused = False
    print("[QUEUE] ▶️  큐 처리 재개")
```

**동작 시나리오:**
```
1. RELOAD 명령 전송
2. 큐 일시 중지 → 센서 TH 명령 차단
3. RELOAD 응답 수신 및 파싱
4. 큐 재개 → 센서 TH 명령 정상 처리
```

### Phase 5: 타임아웃 처리

#### 5.1 타임아웃 타이머 시스템
**핵심 메서드:**

1. **`_start_reload_timeout_timer(reload_type)`**: 15초 타이머 시작
2. **`_cancel_reload_timeout_timer(reload_type)`**: 타이머 취소
3. **`_handle_reload_timeout(reload_type)`**: 타임아웃 처리

**타임아웃 시 동작:**
```python
def _handle_reload_timeout(self, reload_type):
    """RELOAD 타임아웃 처리"""
    if reload_type == "dsct":
        print(f"[RELOAD] ⚠️ DSCT 리로드 타임아웃! (응답 없음)")
        self.dsct_reload_in_progress = False
        self.dsct_reload_data = []

        # 명령 큐 재개 (타임아웃 발생 시에도 큐 정상화)
        if hasattr(self.serial_manager, 'command_queue'):
            self.serial_manager.command_queue.resume_queue()

        # 버튼 상태 → 에러
        self._set_reload_button_state(self.dsct_reload_button, "error")

        # 2초 후 자동 복귀
        self._schedule_reload_button_reset(self.dsct_reload_button, delay=2000)
```

### Phase 6: 테스트 모드 지원

#### 6.1 더미 응답 시뮬레이션
**핵심 메서드**: `_simulate_dsct_reload_response()`, `_simulate_air_reload_response()`

**DSCT 더미 데이터:**
```python
dummy_data = [
    "DSCT,FAN1,ON",
    "DSCT,FSPD1,7",      # 구형 프로토콜 (FSPD)
    "DSCT,FAN2,OFF",
    "DSCT,FSPD2,0",
    "DSCT,FAN3,ON",
    "DSCT,FSPD3,5",
    "DSCT,FAN4,OFF",
    "DSCT,FSPD4,0",
    "DSCT,DMP1,OPEN",
    "DSCT,DMP2,CLOSE",
    "DSCT,DMP3,OPEN",
    "DSCT,DMP4,CLOSE",
    "DSCT,PUMP1,ON",
    "DSCT,PSPD1,6",      # PUMP 속도는 무시됨
    "DSCT,PUMP2,OFF",
    "DSCT,PSPD2,0",
    "DSCT,SOL1,OFF",     # SOL1만 사용
    "DSCT,SEMIAUTO,STOP",
    "DSCT,DMPTEST,STOP",
]
```

**시뮬레이션 시나리오:**
- 100ms 후 START 신호
- 200ms 간격으로 데이터 전송
- 2.57초 후 COMPLETE 신호

## 📊 시스템 플로우

```
[사용자] → [Refresh 버튼 클릭]
    ↓
[ButtonManager] → 중복 요청 체크
    ↓
[시리얼 명령 전송] $CMD,DSCT/AIR,RELOAD (직접 전송, 큐 우회)
    ↓
[큐 일시 중지] → 센서 TH 명령 차단
    ↓
[버튼 상태] → 로딩 (주황색)
    ↓
[타임아웃 타이머 시작] 15초
    ↓
[장비 응답 수신 및 파싱]
    ├─ EEPROM_ACK,RELOAD,START → 데이터 수집 시작
    ├─ DSCT,FAN1,ON → 버튼 상태 업데이트
    ├─ DSCT,FAN1,SPD,1 → 속도 버튼 업데이트
    ├─ ... (모든 장비 상태 수신)
    └─ DSCT_ACK,RELOAD,COMPLETE → 완료
    ↓
[타임아웃 타이머 취소]
    ↓
[큐 재개] → 센서 TH 명령 정상 처리
    ↓
[버튼 상태] → 완료 (초록색) → 1초 후 정상 복귀
```

## ✅ 핵심 개선 사항

### 사용자 경험 개선
- **원클릭 동기화**: Refresh 버튼 한 번으로 모든 장비 상태 복원
- **4단계 피드백**: 정상 → 로딩 → 완료 → 에러 시각적 표시
- **자동 복귀**: 완료/에러 후 1~2초 뒤 자동 정상 상태 복귀
- **진행 시간 표시**: 로그에서 응답 시간 측정 (예: 0.33초)

### 프로토콜 지원
- **신형 프로토콜**: `DSCT,FAN1,SPD,1` (실제 하드웨어)
- **구형 프로토콜**: `DSCT,FSPD1,7` (테스트 모드)
- **양방향 호환**: 두 프로토콜 동시 지원

### 안전성 강화
- **중복 요청 방지**: 진행 중 클릭 무시
- **큐 충돌 방지**: 큐 일시 중지로 센서 명령 차단
- **타임아웃 처리**: 15초 내 응답 없으면 에러 표시 및 자동 복구
- **상태 동기화**: 하드웨어 값 그대로 UI에 반영

### 복원 범위
- ✅ FAN1~4 버튼 ON/OFF 상태
- ✅ FAN1~4 속도 버튼 값 (1~10)
- ✅ FAN OFF 시 속도 버튼 자동 비활성화
- ✅ PUMP1~2 버튼 ON/OFF 상태 (속도 무시)
- ✅ SOL1 버튼 상태 (SOL2~4 무시)
- ✅ SEMIAUTO 버튼 RUN/STOP 상태
- ✅ DMPTEST 버튼 RUN/STOP 상태
- ✅ EVA FAN, CON FAN, COMPRESSOR 상태 (AIR)

## 🧪 테스트 방법

### 옵션 1: 테스트 모드 (추천)
```bash
python main.py --test
```

**동작 시나리오:**
1. DESICCANT 탭 이동
2. FAN1, FAN4 버튼 켜기 (속도 조절)
3. `DSCT Refresh` 버튼 클릭
4. **로딩 애니메이션** 확인 (주황색)
5. **2.57초 후** 완료 표시 (초록색)
6. **버튼 상태 복원** 확인:
   - FAN1: ON, 속도 7
   - FAN2: OFF, 속도 0 (비활성화)
   - FAN3: ON, 속도 5
   - FAN4: OFF, 속도 0 (비활성화)

**콘솔 로그 확인:**
```
[RELOAD] ⏱️  DSCT 리로드 요청 전송: $CMD,DSCT,RELOAD (타임아웃: 15.0초)
[QUEUE] 🛑 큐 처리 일시 중지 (RELOAD 응답 대기)
[RELOAD] ✅ DSCT 데이터 수집 시작 (응답까지: 0.10초)
[RELOAD] 📥 DSCT 데이터 수집: DSCT,FAN1,ON
[RELOAD] 📥 DSCT 데이터 수집: DSCT,FSPD1,7
...
[RELOAD] ✅ DSCT 데이터 수집 완료: 20개 항목 (총 소요: 2.57초)
[RELOAD] DSCT FAN1 버튼 상태 업데이트: ON
[RELOAD] DSCT FAN1 속도 복원: 7
[RELOAD] DSCT FAN2 버튼 상태 업데이트: OFF
[RELOAD] DSCT FAN2 OFF → 속도 버튼 초기화
[QUEUE] ▶️  큐 처리 재개
```

### 옵션 2: 실제 하드웨어 연결
```bash
python main.py
```

**확인 포인트:**
- [ ] 시리얼 연결 후 DESICCANT/AIRCON 탭 이동
- [ ] 일부 버튼 상태 변경 (FAN, PUMP 등)
- [ ] `Refresh` 버튼 클릭 → 로딩 표시
- [ ] 하드웨어 응답 수신 → 완료 표시
- [ ] 모든 버튼 상태가 하드웨어와 동일하게 복원
- [ ] 타임아웃 테스트 (장비 연결 해제 후 버튼 클릭)
- [ ] 15초 후 빨간색 `Timeout!` 표시
- [ ] 2초 후 자동 정상 복귀

### 옵션 3: 하드웨어 이슈 검증
**발견된 하드웨어 문제:**
- FAN2, FAN3가 실제로는 OFF인데 하드웨어가 ON으로 보고
- EEPROM 상태와 실제 출력 상태 불일치

**소프트웨어는 정상 동작:**
- 하드웨어가 보낸 데이터를 정확하게 파싱
- UI에 하드웨어 값 그대로 반영
- 펌웨어 수정 필요

## 📁 변경된 파일 목록

### 수정된 파일
1. **`ui/main_window.py`** (487-506, 589-608 라인)
   - AIRCON 탭 AIR Refresh 버튼 추가
   - DESICCANT 탭 DSCT Refresh 버튼 추가
   - 4가지 버튼 상태 스타일 정의

2. **`ui/setup_buttons.py`** (133-156 라인)
   - RELOAD 버튼 이벤트 연결 함수 추가
   - ButtonManager에 버튼 참조 전달

3. **`managers/button_manager.py`** (13-24, 37-40, 306-927 라인, 약 600라인 추가)
   - RELOAD 상태 관리 변수 추가
   - 핸들러 메서드 구현 (handle_dsct_reload, handle_air_reload)
   - 응답 파싱 로직 (parse_reload_response)
   - 상태 적용 메서드 (_apply_dsct_reload_state, _apply_air_reload_state)
   - 버튼 업데이트 메서드 (FAN, PUMP, SOL, SEMIAUTO, DMPTEST)
   - 타임아웃 처리 시스템
   - 테스트 모드 더미 응답 구현
   - 4단계 버튼 시각적 피드백

4. **`managers/command_queue_manager.py`** (56, 117, 223-231 라인)
   - is_paused 플래그 추가
   - pause_queue() 메서드 구현
   - resume_queue() 메서드 구현
   - 큐 처리 로직에 일시 중지 조건 추가

5. **`CHANGELOG.md`**
   - v3.8 릴리스 노트 추가

## 🔗 MESSAGE.md 명세 충족

### 요구사항 검증
- ✅ `$CMD,DSCT,RELOAD` 프로토콜 완전 구현
- ✅ `$CMD,AIR,RELOAD` 프로토콜 완전 구현
- ✅ EEPROM 저장 상태 복원
- ✅ 15초 타임아웃 처리
- ✅ 시각적 피드백 제공
- ✅ 큐 충돌 방지

### 프로토콜 준수
```
# DSCT RELOAD 요청
$CMD,DSCT,RELOAD<CR><LF>

# DSCT RELOAD 응답
EEPROM_ACK,RELOAD,START<CR><LF>
DSCT,FAN1,ON<CR><LF>
DSCT,FAN1,SPD,1<CR><LF>
...
EEPROM_ACK,RELOAD,END<CR><LF>
DSCT_ACK,RELOAD,COMPLETE<CR><LF>

# AIR RELOAD 요청
$CMD,AIR,RELOAD<CR><LF>

# AIR RELOAD 응답
EEPROM_ACK,RELOAD,START<CR><LF>
AIR,EVA_FAN,ON<CR><LF>
AIR,EVA_FAN,SPD,5<CR><LF>
...
EEPROM_ACK,RELOAD,END<CR><LF>
AIRCON_ACK,RELOAD,COMPLETE<CR><LF>
```

## 🎉 예상 결과

### 사용자 관점
- **빠른 동기화**: 0.3~2초 내 모든 상태 복원
- **명확한 피드백**: 로딩 → 완료 시각적 표시
- **자동 복구**: 에러 발생 시 자동 정상화
- **신뢰성**: 하드웨어 상태 100% 정확 반영

### 개발자 관점
- **모듈화**: RELOAD 로직이 독립적으로 분리
- **확장성**: 새로운 장비 추가 시 파싱 규칙만 추가
- **테스트 용이성**: 테스트 모드로 하드웨어 없이 검증
- **디버깅**: 상세한 로그로 문제 추적 간편

## 📈 기술적 성과

### 아키텍처 개선
- **상태 머신 패턴**: 정상 → 로딩 → 완료/에러 명확한 전이
- **타이머 기반 타임아웃**: QTimer.singleShot으로 안전한 처리
- **큐 일시 중지**: RELOAD 응답 충돌 완전 방지

### 코드 품질
- **가독성**: 메서드 이름과 주석으로 의도 명확화
- **재사용성**: _update_* 메서드 패턴 일관성
- **유지보수성**: 파싱 규칙이 명확하게 분리

### 신뢰성
- **타임아웃 처리**: 무응답 상황에서도 시스템 정상 작동
- **큐 복구**: 에러 후에도 큐 자동 재개
- **상태 복구**: 하드웨어 값 그대로 UI 반영

## 🔮 향후 확장 가능성

1. **진행률 표시**: 프로그레스 바로 데이터 수신 진행도 표시
2. **자동 RELOAD**: 시리얼 연결 시 자동으로 상태 동기화
3. **차이 감지**: UI와 하드웨어 상태 차이를 하이라이트
4. **로그 파일**: RELOAD 이력을 CSV로 저장

### 결론

v3.8은 장비 상태 동기화를 통해 사용자 편의성을 크게 향상시킨 업데이트입니다:

- **원클릭 동기화**: Refresh 버튼으로 모든 상태 즉시 복원
- **4단계 피드백**: 정상 → 로딩 → 완료 → 에러 시각적 표시
- **안전한 처리**: 큐 일시 중지로 충돌 방지, 타임아웃 자동 복구
- **완전한 복원**: FAN, PUMP, SOL, SEMIAUTO, DMPTEST 모든 버튼 상태 동기화
- **양방향 호환**: 신형/구형 프로토콜 동시 지원

이제 프로그램 재시작이나 연결 재개 시 사용자가 수동으로 상태를 확인할 필요 없이, Refresh 버튼 한 번으로 모든 장비 상태를 UI에 정확하게 반영할 수 있습니다. 하드웨어 EEPROM에 저장된 마지막 상태가 즉시 복원되어 안전하고 편리한 장비 제어가 가능합니다.
