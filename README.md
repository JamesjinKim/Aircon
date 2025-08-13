# AIRCON 원격 제어 시스템

AIRCON은 PyQt5를 기반으로 한 에어컨 및 제습기 원격 제어 시스템입니다. 시리얼 통신을 통해 다양한 공조 장비를 제어할 수 있는 GUI 애플리케이션을 제공합니다.

## 주요 기능

### 🎛️ 제어 모드
- **AIRCON 탭**: 에어컨 시스템 수동 제어 (EVA FAN, COMPRESSOR 등)
- **PUMP &amp; SOL 탭**: 펌프 및 솔레노이드 밸브 제어
- **DESICCANT 탭**: 제습기 시스템 및 댐퍼 제어 (통합)
- **SEMI AUTO 탭**: 반자동 제어 모드 (DESICCANT SEMI AUTO, DAMP TEST)
- **DSCT T/H 탭**: DSCT 온습도 센서 12개 실시간 모니터링
- **AIRCON T/H 탭**: AIRCON 온습도 센서 6개 실시간 모니터링
- **AUTO 탭**: 온도 및 풍량 자동 제어

### 🌡️ 에어컨 제어 (AIRCON 탭)
- **EVA FAN**: 순환 버튼으로 OFF→1→2→3→4→5→6→7→8→OFF 제어
- **COMPRESSOR**: 압축기 ON/OFF 토글 제어
- **COMP CLUCH**: 압축기 클러치 ON/OFF 토글 제어
- **CONDENSOR FAN**: 순환 버튼으로 OFF→1→2→3→4→5→6→7→8→OFF 제어
- **댐퍼 제어**: OA.DAMP(L/R), RA.DAMP(L/R) OPEN/CLOSE 버튼 및 위치 조절 (0~9)

### 💨 제습기 및 댐퍼 제어 (DESICCANT 탭)
**왼쪽 - DESICCANT CONTROLS:**
- **FAN1~FAN4**: 개별 ON/OFF 토글 + 순환 숫자 버튼 (0→1→...→8→0)
- FAN OFF 시 속도 자동 리셋, ON 시 속도 1부터 시작

**오른쪽 - DAMP CONTROLS:**
- **배기(L), 배기(R), 급기(L), 급기(R)**: CLOSE/OPEN 토글 + 위치 조절 (0→1→...→4→0)
- 위치 0=CLOSE, 위치 1~4=OPEN 상태
- 버튼 순서: 배기(L), 배기(R), 급기(L), 급기(R)

### 🔧 펌프 및 솔레노이드 제어 (PUMP &amp; SOL 탭)
**왼쪽 - PUMP CONTROLS:**
- **PUMP1/PUMP2**: ON/OFF 토글 + 순환 숫자 버튼 (0→1→...→8→0)
- 펌프 OFF 시 속도 자동 리셋, ON 시 속도 1부터 시작

**오른쪽 - SOL CONTROLS:**
- **SOL1, SOL4, SOL2, SOL3**: 솔레노이드 밸브 ON/OFF 토글 (순서 재배치)

### 🔄 반자동 제어 (SEMI AUTO 탭)
**왼쪽 - DESICCANT SEMI AUTO:**
- **DESICCANT RUN**: RUN/STOP 토글 버튼
- **주기(Sec)**: [-] [200] [+] 버튼으로 1~999초 조절 (연속 클릭 지원)
- Serial CMD: `$CMD,DSCT,SEMIAUTO,RUN,(1~999)` / `$CMD,DSCT,SEMIAUTO,STOP`

**오른쪽 - DAMP TEST:**
- **DAMP**: RUN/STOP 토글 버튼  
- Serial CMD: `$CMD,DSCT,DMPTEST,RUN` / `$CMD,DSCT,DMPTEST,STOP`

### 🌡️ 온습도 센서 모니터링
**DSCT T/H 탭:**
- **12개 센서 실시간 모니터링**: ID01~ID12 센서 데이터 표시
- **센서 라벨**: L_HEX1, L_HEX2, L_DCH1, L_DCH2, L_급기, R_급기, R_DCH1, R_DCH2, R_HEX2, R_HEX1, R_외기, L_외기
- **가변 새로고침 간격**: 1~360초 조절 가능 (기본값: 5초)
- **자동 갱신**: 설정된 주기로 자동 데이터 업데이트
- **상태 표시**: 정상(녹색), 타임아웃(빨간색), 대기중(회색)
- **개별 센서 정보**: 온도(°C), 습도(%)
- **요약 정보**: 정상/타임아웃/대기중 센서 개수 실시간 표시
- **CSV 파일 저장**: USB 연결 시 데이터 저장 기능

**AIRCON T/H 탭:**
- **6개 센서 실시간 모니터링**: ID01~ID06 센서 데이터 표시 (ID07, ID08 제거)
- **센서 라벨**: L_RA1, L_RA2, L_실내, R_실내, R_RA2, R_RA1
- **가변 새로고침 간격**: 1~360초 조절 가능 (기본값: 5초)
- **자동 갱신**: 설정된 주기로 자동 데이터 업데이트
- **상태 표시**: 정상(녹색), 타임아웃(빨간색), 대기중(회색)
- **개별 센서 정보**: 온도(°C), 습도(%)
- **요약 정보**: 정상/타임아웃/대기중 센서 개수 실시간 표시
- **CSV 파일 저장**: USB 연결 시 데이터 저장 기능

### 🔄 환기 시스템 (AUTO 탭)
- 외기유입 모드
- 내기순환 모드

### 📊 실시간 모니터링
- 시스템 상태 정보
- 온도 및 습도 표시
- 작동 시간 추적
- 시리얼 통신 로그

## 시스템 요구사항

- Python 3.11 이상
- PyQt5 5.15.0 이상
- pyserial 3.5 이상

## 설치 및 실행

### Raspberry Pi에서 설치 방법

Raspberry Pi OS (Debian 기반)에서는 시스템 Python 환경 보호를 위해 직접 pip 설치가 제한됩니다. 다음 방법으로 설치하세요:

#### 1. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python3 -m venv mvenv

# 가상환경 활성화
source mvenv/bin/activate
```

#### 2. 시스템 PyQt5 패키지 설치
```bash
# 시스템에 PyQt5 설치 (가상환경 밖에서 실행)
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtserialport
```

#### 3. 가상환경에 시스템 PyQt5 연결
```bash
# 가상환경에 시스템 PyQt5 심볼릭 링크 생성
cd mvenv/lib/python3.11/site-packages
ln -sf /usr/lib/python3/dist-packages/PyQt5* .
```

#### 4. pyserial 설치
```bash
# 가상환경 활성화 상태에서
pip install pyserial
```

### 일반 시스템에서 설치 방법
```bash
pip install -r requirements.txt
```

### 애플리케이션 실행
```bash
# 가상환경 활성화 (Raspberry Pi의 경우)
source mvenv/bin/activate

# 프로그램 실행
python main.py
```

## 프로젝트 구조

```
Aircon/
├── main.py                 # 메인 애플리케이션 진입점
├── requirements.txt        # 의존성 패키지 목록
├── images/                 # UI 아이콘 및 이미지
│   ├── fan.png
│   ├── thormo-48.png
│   ├── in-24.png
│   ├── in-50.png
│   ├── out-24.png
│   └── out-30.png
├── ui/                     # UI 관련 모듈
│   ├── main_window.py      # 메인 윈도우 클래스
│   ├── ui_components.py    # UI 컴포넌트 생성 함수
│   ├── constants.py        # UI 상수 정의
│   ├── helpers.py          # UI 도우미 함수
│   ├── setup_buttons.py    # 버튼 설정
│   ├── sensor_widget.py    # 개별 센서 위젯
│   ├── sensor_tab.py       # DSCT T/H 탭 레이아웃
│   └── aircon_sensor_tab.py # AIRCON T/H 탭 레이아웃
├── data/                   # 센서 데이터 저장 폴더
│   ├── DSCT_2025-08-*.csv  # DSCT 센서 데이터
│   └── AIRCON_2025-08-*.csv # AIRCON 센서 데이터
├── config/                 # 설정 관리
│   ├── config_manager.py   # 설정 저장/로드
│   └── settings.json       # 새로고침 간격 등 저장
├── utils/                  # 유틸리티 모듈
│   └── usb_detector.py     # USB 감지기
└── managers/               # 비즈니스 로직 매니저
    ├── serial_manager.py   # 시리얼 통신 관리
    ├── button_manager.py   # 버튼 동작 관리
    ├── speed_manager.py    # 속도 버튼 관리
    ├── auto_manager.py     # AUTO 모드 관리
    ├── sensor_manager.py   # DSCT 센서 데이터 관리
    ├── air_sensor_manager.py # AIRCON 센서 데이터 관리
    └── sensor_scheduler.py # 센서 스케줄러 관리
```

## 사용 방법

### 1. 시리얼 포트 연결
1. 상단의 Port 드롭다운에서 연결할 포트 선택
2. Baudrate 설정 (기본값: 115200)
3. "연결" 버튼 클릭
4. 연결 상태가 "Connected"로 변경되면 제어 가능

### 2. 탭별 사용법

#### DSCT T/H 탭 및 AIRCON T/H 탭
- **자동 모니터링**: 시리얼 연결 시 설정된 간격으로 자동 센서 데이터 갱신
- **새로고침 간격 조절**: [-] [숫자] [+] 버튼으로 1~360초 조절 가능
- **센서 상태 확인**:
  - 녹색 표시: 센서 정상 작동
  - 빨간색 표시: 센서 응답 없음 (타임아웃)
  - 회색 표시: 데이터 대기중
- **요약 정보**: 하단에 전체 센서 상태 요약 표시
- **CSV 파일 저장**: USB 연결 시 데이터 폴더의 모든 CSV 파일을 USB로 복사

#### AIRCON 탭
- **FAN CONTROLS 그룹**:
  - Fan: 메인 팬 온/오프
  - Fan SPD: 팬 속도 조절 (&lt;, 현재값, &gt; 버튼)
  - Con Fan: 콘덴서 팬 온/오프
  - Con Fan SPD: 콘덴서 팬 속도 조절
- **DMP CONTROLS 그룹**:
  - Left/Right Top/Bottom DMP: 댐퍼 열기/닫기
  - INVERTER/CLUCH: 인버터 및 클러치 제어

#### DESICCANT 탭
- **FAN1~FAN4 제어**:
  - 각 팬별 개별 온/오프 토글
  - 속도 조절 버튼 (&lt;, 현재값, &gt;)
  - 팬 OFF 시 속도 자동 리셋

#### DAMPER 탭
- **DMP1~DMP4 위치 제어**:
  - CLOSE/OPEN 라벨 표시
  - 위치값 조절 버튼 (&lt;, 현재값, &gt;)
  - 0-10 범위 위치 설정

#### PUMP & SOL 탭
- **PUMP CONTROLS 그룹**:
  - PUMP1/PUMP2: 펌프 온/오프
  - 속도 조절 버튼 (&lt;, 현재값, &gt;)
  - 펌프 OFF 시 속도 자동 리셋
- **SOL CONTROLS 그룹**:
  - SOL1~SOL4: 솔레노이드 밸브 온/오프

### 3. AUTO 모드 사용
1. AUTO 탭으로 전환
2. 풍량 슬라이더로 원하는 속도 설정 (0-10)
3. 온도 슬라이더로 목표 온도 설정 (16-30°C)
4. 환기 모드 선택 (외기유입/내기순환)
5. "AUTO 모드 시작" 버튼 클릭

### 4. 메시지 로그 확인
- **Send Data**: 전송된 명령어 로그
- **Receive Data**: 수신된 응답 로그
- Clear 버튼으로 로그 초기화 가능

## 시리얼 통신 프로토콜

### 명령어 형식
```
$CMD,<DEVICE>,<VALUE>\r
```

### 주요 명령어 예시

#### AIRCON 시스템
- 팬 제어: `$CMD,AIR,FAN,ON` / `$CMD,AIR,FAN,OFF`
- 속도 제어: `$CMD,AIR,FSPD,5` (0-10 범위)
- 콘덴서 팬: `$CMD,AIR,CON_F,ON` / `$CMD,AIR,CON_F,OFF`
- 댐퍼 제어: `$CMD,AIR,ALTDMP,OPEN` / `$CMD,AIR,ALTDMP,CLOSE`

#### DESICCANT 시스템
- 팬 제어: `$CMD,DSCT,FAN1,ON` / `$CMD,DSCT,FAN1,OFF`
- 팬 속도: `$CMD,DSCT,FAN1,SPD,5` (1-10 범위)
- 댐퍼 위치: `$CMD,DSCT,DMP1_CLOSE,3` (1-10 범위)

#### PUMP & SOL 시스템
- 펌프 제어: `$CMD,DSCT,PUMP1,ON` / `$CMD,DSCT,PUMP1,OFF`
- 펌프 속도: `$CMD,DSCT,PUMP1,SPD,7` (1-10 범위)
- 솔레노이드: `$CMD,DSCT,SOL1,ON` / `$CMD,DSCT,SOL1,OFF`

#### SEMI AUTO 시스템
- DESICCANT SEMI AUTO: `$CMD,DSCT,SEMIAUTO,RUN,300` / `$CMD,DSCT,SEMIAUTO,STOP`
- DAMP TEST: `$CMD,DSCT,DMPTEST,RUN` / `$CMD,DSCT,DMPTEST,STOP`

#### DSCT T/H 시스템  
- 센서 데이터 요청: `$CMD,DSCT,TH`
- 응답 형식:
  - 정상: `[DSCT] ID01,TEMP: 28.3, HUMI: 67.7`
  - 에러: `[DSCT] ID07,Sensor Check TIMEOUT!`

#### AIRCON T/H 시스템
- 센서 데이터 요청: `$CMD,AIR,TH`
- 응답 형식:
  - 정상: `[AIRCON] ID01,TEMP: 28.3, HUMI: 67.7`
  - 에러: `[AIRCON] ID07,Sensor Check TIMEOUT!`

#### AUTO 모드
- AUTO 모드: `$CMD,AUTO,ON` / `$CMD,AUTO,OFF`
- 온도 제어: `$CMD,TEMP,22`

## 화면 해상도 최적화

- 800x480 해상도에 최적화된 UI 설계
- 라즈베리파이 터치 디스플레이 지원
- 고해상도 디스플레이 자동 스케일링

## 특징

### 🔒 안전 기능
- 시리얼 포트 연결 상태 실시간 모니터링
- 연결 해제 시 모든 버튼 자동 리셋
- 팬/펌프 OFF 시 속도 버튼 자동 초기화
- 시리얼 연결 없이는 제어 버튼 동작 차단
- 명령 전송 실패 시 에러 로깅

### 🎨 사용자 친화적 UI
- 탭 기반 인터페이스 (AIRCON | PUMP & SOL | DESICCANT | DSCT T/H | AIRCON T/H | SEMI AUTO | AUTO)
- 직관적인 2컬럼 레이아웃 설계 (모든 탭 통일)
- 실시간 상태 표시 및 버튼 색상 피드백
- 통일된 버튼 스타일 (COMPRESSOR 버튼 기준)
- 터치 친화적인 순환 버튼 방식
- 시각적 그룹화로 기능별 구분

### ⚡ 고성능
- 비동기 시리얼 통신
- 실시간 데이터 로깅
- 효율적인 메모리 관리

## 개발 정보

- **언어**: Python 3.x
- **GUI 프레임워크**: PyQt5
- **통신**: 시리얼 통신 (RS232/USB)
- **아키텍처**: MVC 패턴 기반 모듈화 설계

## 라이선스

이 프로젝트는 공조 시스템 제어를 위한 전용 소프트웨어입니다.

## 문제 해결

### 일반적인 문제
1. **포트 연결 실패**: 올바른 포트와 보레이트 확인
2. **명령어 전송 안됨**: 시리얼 포트 연결 상태 확인
3. **UI 반응 없음**: 애플리케이션 재시작

### 로그 파일
- 수신 데이터는 `serial_data_log.txt`에 자동 저장됩니다.

## 업데이트 내역

### v3.6 (2025년 8월 13일) 🌡️
- **NEW**: 듀얼 센서 모니터링 시스템
  - DSCT T/H 탭: 12개 센서 모니터링 (L_HEX1~L_외기)
  - AIRCON T/H 탭: 6개 센서 모니터링 (L_RA1~R_RA1, ID07/08 제거)
- **NEW**: 가변 새로고침 간격 시스템
  - [-] [숫자] [+] 버튼으로 1~360초 조절 가능
  - 설정 자동 저장 및 복원 기능
- **NEW**: CSV 데이터 저장 및 USB 백업
  - 센서 데이터 자동 CSV 저장 (파일 크기 10MB 단위 분할)
  - USB 연결 감지 및 원클릭 백업 기능
- **NEW**: AIRCON 댐퍼 제어 개선
  - OPEN/CLOSE 별도 버튼 + 위치 표시 (0~9)
  - CLOSE 시 위치 0에서 멈춤 기능
- **NEW**: SEMI AUTO 탭 DMPTEST 명령어 수정
  - $CMD,DSCT,DAMPTEST,RUN → $CMD,DSCT,DMPTEST,RUN
- **IMPROVED**: 펌프 모드 변경
  - PUMP 명령을 sequential → toggle 모드로 변경
- **ENHANCED**: 센서 스케줄러 중앙 관리
  - 통합된 센서 요청 스케줄링 시스템
  - 에어컨/DSCT 센서 독립적 관리

### v3.0 (2025년 7월) 🎉
- **NEW**: SEMI AUTO 탭 추가
  - DESICCANT SEMI AUTO 기능 (RUN/STOP + 주기 조절 1~999초)
  - DAMP TEST 기능 (RUN/STOP)
  - 연속 클릭 지원하는 주기 조절 버튼 ([-] [값] [+])
- **MAJOR**: 탭 구조 개편
  - 탭 순서 변경: AIRCON → PUMP & SOL → DESICCANT → SEMI AUTO → AUTO
  - DESICCANT 탭에 DAMPER 제어 통합 (기존 DAMPER 탭 제거)
- **IMPROVED**: 버튼 스타일 통일
  - 모든 TAB 버튼을 COMPRESSOR 버튼 스타일로 통일 (font-size: 14px, font-weight: bold)
  - SEMI AUTO, AUTO TAB은 예외로 기존 스타일 유지
- **ENHANCED**: 터치 친화적 UI 디자인
  - 모든 제어 버튼이 순환 방식으로 동작 (토글 + 숫자 순환)
  - 직관적인 2컬럼 레이아웃으로 모든 탭 통일
- **FIXED**: 시리얼 통신 안정성 개선
  - 연결 끊김 감지 로직 강화 (5회 연속 에러 시 자동 해제)
  - 무한 에러 메시지 루프 방지

### v2.1 (2025년 1월)
- **MAJOR**: FAN 속도 버튼 로직 대폭 개선
  - 모든 FAN (AIRCON FAN, Con Fan, DESICCANT FAN1~4) 동일한 동작 로직 적용
  - FAN OFF 시: SPD 버튼 0으로 초기화
  - FAN ON 시: SPD 버튼 자동으로 1로 설정 및 Serial CMD 전송
  - SPD 범위: 1~10 (감소 버튼 클릭 시 1에서 멈춤, 0은 OFF 상태에서만)
  - 중앙 버튼: FAN ON 상태에서는 1로 리셋
- **ENHANCED**: FAN 토글 버튼과 SPD 버튼 간 완벽한 동기화
- **IMPROVED**: 모든 FAN 타입에 대한 일관성 있는 사용자 경험

### v2.0 (2024년)
- **NEW**: DESICCANT 탭 추가 - FAN1~FAN4 개별 제어
- **NEW**: DAMPER 탭 추가 - DMP1~DMP4 위치값 제어
- **NEW**: PUMP & SOL 탭 추가 - 펌프 및 솔레노이드 밸브 제어
- **IMPROVED**: 탭 기반 UI 재설계로 사용성 향상
- **IMPROVED**: 2컬럼 레이아웃으로 화면 공간 효율성 증대
- **ENHANCED**: 시리얼 연결 상태 기반 안전 제어 강화
- **ENHANCED**: 팬/펌프 OFF 시 자동 속도 리셋 기능

### v1.0 (초기 버전)
- 기본 AIRCON 시스템 제어
- AUTO 모드 구현
- 시리얼 통신 기본 기능

---

**개발자 노트**: 이 시스템은 산업용 공조 장비 제어를 위해 설계되었으며, 모듈화된 탭 인터페이스와 강력한 안전 기능을 통해 안정성과 사용 편의성을 최우선으로 고려하여 개발되었습니다.