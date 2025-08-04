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
- AIRCON T/H: 8개 센서 (ID01~ID08)
- 시리얼 명령어: `$CMD,AIR,TH`
- 응답 형식: `[AIR] ID01,TEMP: 28.3, HUMI: 67.7`

### 2. 새로운 모듈 개발

#### 2.1 AirSensorManager 클래스
**파일**: `managers/air_sensor_manager.py`

**주요 기능:**
- 8개 AIRCON 센서 데이터 관리
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
- 8개 센서용 가상 데이터 생성
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
- **AIRCON 센서**: `AIRCON_YYYYMMDD.csv` (8개 센서)

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
- 8개 센서 동시 모니터링
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

이러한 개선으로 산업용 환경에서의 장기간 안정적인 센서 모니터링이 가능해졌습니다.