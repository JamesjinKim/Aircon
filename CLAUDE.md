# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AIRCON is a PyQt5-based remote control system for air conditioning and dehumidifier equipment via serial communication. The application provides a GUI with multiple tabs for manual and automatic control of HVAC systems, with real-time sensor monitoring and data logging capabilities.

**Key Technologies:**
- Python 3.11+
- PyQt5 5.15.0+ (GUI framework)
- pyserial 3.5+ (serial communication)
- MVC architecture pattern

## Development Commands

### Environment Setup (Raspberry Pi)
```bash
# Create and activate virtual environment
python3 -m venv mvenv
source mvenv/bin/activate

# Install system PyQt5 packages (outside venv)
sudo apt update
sudo apt install -y python3-pyqt5 python3-pyqt5.qtserialport

# Link system PyQt5 to venv
cd mvenv/lib/python3.11/site-packages
ln -sf /usr/lib/python3/dist-packages/PyQt5* .

# Install Python dependencies
pip install pyserial
```

### Running the Application
```bash
# Normal mode
python main.py

# Test mode (with dummy sensor data, no serial connection required)
python main.py --test
```

### Development Workflow
```bash
# Check git status
git status

# View recent changes
git diff

# Check serial ports (useful for debugging)
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

## Architecture Overview

### Module Organization

**managers/** - Business logic and state management
- `serial_manager.py` - Serial communication with hardware (pyserial wrapper, USB port filtering)
- `command_queue_manager.py` - Async command queue system to prevent UI blocking
- `button_manager.py` - Button state and toggle logic
- `speed_manager.py` - Fan/pump speed control logic (large file: ~1800 lines)
- `auto_manager.py` - Automatic temperature/airflow control, PT02 sensor integration
- `sensor_scheduler.py` - Central scheduler for AIRCON and DSCT sensor polling
- `sensor_manager.py` - DSCT sensor data parsing and CSV logging
- `air_sensor_manager.py` - AIRCON sensor data parsing and CSV logging
- `pt02_sensor_manager.py` - PT02 sensor (temp/CO2/PM2.5) data management and CSV logging

**ui/** - User interface components
- `main_window.py` - Main application window with tab structure (large file: ~2400 lines)
- `ui_components.py` - Reusable UI component factory functions
- `setup_buttons.py` - Button initialization and event wiring
- `sensor_tab.py` - DSCT T/H tab layout (12 sensors)
- `aircon_sensor_tab.py` - AIRCON T/H tab layout (6 sensors)
- `sensor_widget.py` - Individual sensor display widget
- `constants.py` - UI constants (button styles, colors)
- `helpers.py` - UI utility functions

**config/** - Configuration management
- `config_manager.py` - Persistent settings storage (JSON)
- `settings.json` - Refresh intervals and UI preferences

**utils/** - Utility modules
- `usb_detector.py` - USB drive detection for CSV backup
- `csv_cleaner.py` - CSV file maintenance utilities

**test/** - Test mode utilities
- `dummy_sensor_generator.py` - DSCT sensor dummy data generation
- `dummy_air_sensor_generator.py` - AIRCON sensor dummy data generation
- `dummy_pt02_generator.py` - PT02 sensor (temp/CO2/PM2.5) dummy data generation

### Key Design Patterns

**Manager Pattern**: Business logic separated into manager classes that handle specific domains (serial, buttons, sensors, speed control). Main window delegates to managers rather than handling logic directly.

**Signal/Slot Architecture**: PyQt5 signals connect managers to UI updates. Important signals:
- `SerialManager.data_received` - Raw serial data from hardware
- `SensorScheduler.aircon_sensor_updated` / `dsct_sensor_updated` - Parsed sensor data
- `CommandQueueManager.command_sent` / `command_failed` - Command status

**Command Queue System**: `CommandQueueManager` implements priority-based async command queue to prevent UI freezing during serial operations. Three priority levels: HIGH (emergency stop), NORMAL (button commands), LOW (sensor requests).

**Sensor Scheduling**: `SensorScheduler` centrally manages alternating AIRCON and DSCT sensor polling with configurable intervals. Uses state machine pattern with states: IDLE, AIRCON_REQUESTING, AIRCON_WAITING, DSCT_REQUESTING, DSCT_WAITING, INTERVAL_WAITING, PAUSED.

**Test Mode**: When launched with `--test` flag, dummy sensor generators provide realistic data without serial connection. Scheduler skips connection checks in test mode.

### Serial Communication Protocol

Commands follow format: `$CMD,<DEVICE>,<FUNCTION>,<VALUE>\r`

**Devices:** AIR (aircon), DSCT (desiccant), AUTO
**Examples:**
- Fan control: `$CMD,AIR,FAN,ON`, `$CMD,AIR,FAN,OFF`
- Speed control: `$CMD,AIR,FSPD,5` (0-10 range)
- Damper: `$CMD,AIR,ALTDMP,OPEN,1`, `$CMD,AIR,ALTDMP,CLOSE,1`
- Sensor request: `$CMD,DSCT,TH`, `$CMD,AIR,TH`

**AUTOMODE Commands (v3.9+):**
- Auto mode: `$CMD,AIR,AUTOMODE,ON`, `$CMD,AIR,AUTOMODE,OFF`
- Temperature: `$CMD,AIR,TEMPSET,XXXX,nnnn` (value×10, hysteresis×10)
- CO2: `$CMD,AIR,CO2SET,XXXX,nnnn` (ppm)
- PM2.5: `$CMD,AIR,PM25SET,XX,nn` (µg/m³)
- SEMI time: `$CMD,AIR,SEMITIME,XXXX` (seconds)
- Get settings: `$CMD,AIR,GETSET`

**Sensor Response Format:**
- Success: `[DSCT] ID01,TEMP: 28.3, HUMI: 67.7`
- Timeout: `[DSCT] ID07,Sensor Check TIMEOUT!`
- Completion: `[DSCT] SEQUENTIAL SCAN COMPLETE: Total: 12, Success: 6, Error: 6, Time: 7470ms`

### CSV Data Logging

Sensor data automatically saved to `data/` directory:
- DSCT sensors: `DSCT_2025-01-31.csv`
- AIRCON sensors: `AIRCON_2025-01-31.csv`
- PT02 sensors: `PT02_2025-12-02.csv` (1분 주기 온도/CO2/PM2.5)
- Auto-split at 10MB with sequence numbers: `DSCT_2025-01-31_001.csv`
- New file created daily at midnight
- CSV headers:
  - DSCT/AIRCON: Timestamp, ID, Temperature (°C), Humidity (%), Status
  - PT02: Timestamp, Temperature (°C), CO2 (ppm), PM2.5 (µg/m³)

## UI Tab Structure

Application uses tabbed interface optimized for 800x480 touchscreen:

1. **AUTO** - Automatic temperature/CO2/PM2.5 control with AUTOMODE system
2. **SEMI AUTO** - Semi-automatic modes (DESICCANT cycle, DAMP test)
3. **AIRCON** - Manual air conditioner control (EVA FAN, COMPRESSOR, dampers)
4. **PUMP & SOL** - Pump and solenoid valve control
5. **DESICCANT** - Dehumidifier fans and damper positions
6. **DSCT T/H** - 12-sensor temperature/humidity monitoring with CSV export
7. **AIRCON T/H** - 6-sensor temperature/humidity monitoring with CSV export

## Button Naming Convention

The codebase uses a structured naming convention documented in [BUTTON_NAMING_GUIDE.md](BUTTON_NAMING_GUIDE.md):

**Format:** `{tab}_{group}_{function}_{type}`

**Examples:**
- `self.aircon_eva_fan_button` - AIRCON tab EVA FAN cycle button
- `self.desiccant_fan1_toggle_button` - DESICCANT tab FAN1 ON/OFF
- `self.desiccant_fan1_speed_button` - DESICCANT tab FAN1 speed cycle
- `self.pumper_pump1_new_toggle_button` - PUMP tab PUMP1 ON/OFF

**Legacy Compatibility:** Old names (e.g., `pushButton_1`, `evaFanButton_1`) coexist with new names. Prefer new naming for new code.

## Important Implementation Notes

### Serial Connection Safety
- All button handlers must check `serial_manager.is_connected()` before sending commands
- Connection loss automatically resets all buttons via `reset_all_buttons()` in managers
- 5 consecutive serial errors trigger automatic disconnection to prevent infinite error loops
- **USB 포트 필터링**: `get_available_ports(usb_only=True)`로 내장 UART 제외
  - 허용 포트: `ttyUSB*`, `ttyACM*`, `COM*`
  - 제외 포트: `ttyAMA*` (라즈베리파이 내장 UART)

### Speed Button Logic (Fans/Pumps)
- OFF state: speed shows 0, speed buttons disabled
- ON state: speed auto-sets to 1, sends serial command
- Speed range: 1-10 (cannot go below 1 when ON)
- Clicking speed button cycles through values

### Damper Controls
- OA.DAMP uses 3-button layout: OPEN + number + CLOSE
- OPEN increments position (0-9 cycle), sends `$CMD,AIR,ALTDMP,OPEN,1`
- CLOSE decrements position (stops at 0), sends `$CMD,AIR,ALTDMP,CLOSE,1` only if > 0
- Number button is display-only, no event handler

### Sensor Refresh Intervals
- Configurable via UI: 1-360 seconds (default: 5 seconds)
- Settings persist in `config/settings.json`
- Separate intervals for AIRCON and DSCT sensors
- Scheduler coordinates requests to avoid collision

### Display Settings
- Default resolution: 800x480 (Raspberry Pi touchscreen)
- High DPI support enabled via Qt attributes
- Fusion style enforced for consistency across platforms

## Common Pitfall Prevention

1. **Don't send commands without serial connection check** - Always verify connection first to avoid hanging UI
2. **Don't modify button sizes in `setup_buttons.py`** - Use `ensure_uniform_button_sizes()` in main_window.py instead
3. **Don't parse sensor data outside managers** - Use SensorManager/AirSensorManager parsing methods
4. **Don't add todos to UI files** - Business logic belongs in managers, not UI code
5. **Don't skip command queue** - Use `CommandQueueManager.send_command()` instead of direct serial writes for better reliability
6. **Test mode is for development only** - Never ship with `--test` flag in production scripts

## File Locations for Common Tasks

- Add new serial command: `managers/button_manager.py` or `managers/speed_manager.py`
- Modify sensor parsing: `managers/sensor_manager.py` or `managers/air_sensor_manager.py`
- Change UI layout: `ui/main_window.py` or respective tab files
- Update button styles: `ui/constants.py`
- Add new sensor widget: `ui/sensor_widget.py`
- Modify scheduler behavior: `managers/sensor_scheduler.py`
- Change CSV format: `managers/sensor_manager.py::_get_csv_filename()` or `_save_to_csv()`

## Recent Changes

See [CHANGELOG.md](CHANGELOG.md) for full version history. Most recent version is v3.12 (2025-12-03) with:

### v3.12 (2025-12-03)
- AUTO 설정 저장 시 PM25SET 응답 누락 버그 수정
- 명령어 간 200ms 딜레이 적용 (응답 잼 방지)
- **시리얼 통신 주의**: 여러 명령어 연속 전송 시 최소 200ms 간격 유지 필요

### v3.11 (2025-12-02)
- 시리얼 연결 안정성 개선 (USB 포트 필터링)
- 연결 해제 예외 처리 개선

### v3.10 (2025-12-02)
- PT02 센서 CSV 저장 시스템 추가
- 1분 주기 온도/CO2/PM2.5 데이터 로깅
- PT02SensorManager 클래스 추가

### v3.9 (2025-11-26)
- AUTO 탭 전면 개편 (AUTOMODE 시스템)
- 2컬럼 컴팩트 레이아웃 (800×480 최적화)
- 히스테리시스 제어 (온도/CO2/PM2.5)
- 탭 순서 재배치 (AUTO 맨 앞)
- 새로운 시리얼 명령어 (AUTOMODE, TEMPSET, CO2SET, PM25SET, SEMITIME, GETSET)


# 중요: 응답은 반드시 한글로 할것!
1.수정 요청 사항을 받으면 기존 코드를 참고하여 알고리즘의 일관성을 유지 할것.
2.이미 작성된 UI를 수정할 때는 반드시 승인을 받고 수정 할것.
