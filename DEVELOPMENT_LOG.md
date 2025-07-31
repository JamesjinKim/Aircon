# AIRCON T/H 센서 모니터링 시스템 개발 로그

## 개발 개요

**개발 기간**: 2025년 7월 30일  
**개발자**: Claude Code Assistant  
**목적**: AIRCON 시스템용 온습도 센서 모니터링 기능 추가

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
- **DSCT 센서**: `dsct_sensor_data_YYYYMMDD.csv` (12개 센서)
- **AIRCON 센서**: `air_sensor_data_YYYYMMDD.csv` (8개 센서)

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

## 향후 개선 사항

1. **데이터 분석 기능**: 온도/습도 트렌드 분석
2. **알람 기능**: 임계값 초과 시 알림
3. **데이터 내보내기**: Excel, JSON 형식 지원
4. **원격 모니터링**: 웹 인터페이스 추가
5. **압축 저장**: 오래된 CSV 파일 자동 압축

## 결론

v3.3 업데이트를 통해 UI 가독성이 크게 향상되었고, CSV 파일 분할 기능으로 장시간 데이터 수집 시 파일 크기 문제가 해결되었습니다. 일별 분할과 크기 기반 분할의 조합으로 효율적인 데이터 관리가 가능해졌습니다.