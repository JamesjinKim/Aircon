# AIRCON 원격 제어 시스템

AIRCON은 PyQt5를 기반으로 한 에어컨 및 제습기 원격 제어 시스템입니다. 시리얼 통신을 통해 다양한 공조 장비를 제어할 수 있는 GUI 애플리케이션을 제공합니다.

## 주요 기능

### 🎛️ 제어 모드
- **AIRCON 탭**: 에어컨 시스템 수동 제어
- **DESICCANT 탭**: 제습기 시스템 제어
- **DAMPER 탭**: 댐퍼 위치 제어
- **PUMPER & SOL 탭**: 펌프 및 솔레노이드 밸브 제어
- **AUTO 탭**: 온도 및 풍량 자동 제어

### 🌡️ 에어컨 제어
- 팬 온/오프 및 속도 조절 (0-10단계)
- 콘덴서 팬 온/오프 및 속도 조절
- 댐퍼 제어 (Left/Right Top/Bottom)
- 인버터 및 클러치 제어
- 온도 설정 (16-30°C)

### 💨 제습기(DESICCANT) 제어
- FAN1~FAN4 개별 온/오프 및 속도 조절 (0-10단계)
- 각 팬별 독립적인 속도 제어
- 팬 OFF 시 자동 속도 리셋

### 🌬️ 댐퍼(DAMPER) 제어
- DMP1~DMP4 위치값 제어 (0-10 범위)
- CLOSE 명령 기반 위치 설정
- 시리얼 연결 상태 검증

### 🔧 펌프 및 솔레노이드(PUMPER & SOL) 제어
- PUMP1/PUMP2 온/오프 및 속도 조절 (0-10단계)
- SOL1~SOL4 솔레노이드 밸브 온/오프
- 펌프 OFF 시 자동 속도 리셋

### 🔄 환기 시스템
- 외기유입 모드
- 내기순환 모드

### 📊 실시간 모니터링
- 시스템 상태 정보
- 온도 및 습도 표시
- 작동 시간 추적
- 시리얼 통신 로그

## 시스템 요구사항

- Python 3.6 이상
- PyQt5 5.15.0 이상
- pyserial 3.5 이상

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 애플리케이션 실행
```bash
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
│   └── setup_buttons.py    # 버튼 설정
└── managers/               # 비즈니스 로직 매니저
    ├── serial_manager.py   # 시리얼 통신 관리
    ├── button_manager.py   # 버튼 동작 관리
    ├── speed_manager.py    # 속도 버튼 관리
    └── auto_manager.py     # AUTO 모드 관리
```

## 사용 방법

### 1. 시리얼 포트 연결
1. 상단의 Port 드롭다운에서 연결할 포트 선택
2. Baudrate 설정 (기본값: 115200)
3. "연결" 버튼 클릭
4. 연결 상태가 "Connected"로 변경되면 제어 가능

### 2. 탭별 사용법

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

#### PUMPER & SOL 탭
- **PUMPER CONTROLS 그룹**:
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

#### PUMPER & SOL 시스템
- 펌프 제어: `$CMD,DSCT,PUMP1,ON` / `$CMD,DSCT,PUMP1,OFF`
- 펌프 속도: `$CMD,DSCT,PUMP1,SPD,7` (1-10 범위)
- 솔레노이드: `$CMD,DSCT,SOL1,ON` / `$CMD,DSCT,SOL1,OFF`

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
- 탭 기반 인터페이스 (AIRCON | DESICCANT | DAMPER | PUMPER & SOL | AUTO)
- 직관적인 2컬럼 레이아웃 설계
- 실시간 상태 표시 및 버튼 색상 피드백
- 균일한 버튼 크기와 간격으로 터치 친화적
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

### v2.0 (2024년 최신)
- **NEW**: DESICCANT 탭 추가 - FAN1~FAN4 개별 제어
- **NEW**: DAMPER 탭 추가 - DMP1~DMP4 위치값 제어
- **NEW**: PUMPER & SOL 탭 추가 - 펌프 및 솔레노이드 밸브 제어
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