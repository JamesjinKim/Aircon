# Button Naming Convention Guide

## 개요
이 문서는 Aircon 프로젝트의 새로운 버튼 네이밍 컨벤션을 설명합니다. 기존 코드와의 호환성을 유지하면서 직관적이고 일관성 있는 네이밍을 제공합니다.

## 네이밍 원칙
1. **기능 우선**: 버튼의 실제 기능을 이름에 반영
2. **계층 구조**: `탭_그룹_기능_타입` 형태
3. **일관성**: 모든 버튼에 동일한 패턴 적용
4. **가독성**: 약어보다는 명확한 단어 사용

## 새로운 네이밍 구조

### AIRCON 탭
```python
# EVA FAN CONTROLS
self.aircon_eva_fan_button           # EVA FAN 순환 버튼
self.aircon_condensor_fan_button     # CONDENSOR FAN 순환 버튼
self.aircon_compresure_button        # COMPRESURE 토글 버튼
self.aircon_comp_cluch_button        # COMP CLUCH 토글 버튼

# DMP CONTROLS
self.aircon_oa_damper_left_button    # OA.DAMPER(L) 댐퍼 버튼
self.aircon_oa_damper_right_button   # OA.DAMPER(R) 댐퍼 버튼
self.aircon_ra_damper_left_button    # RA.DAMPER(L) 댐퍼 버튼
self.aircon_ra_damper_right_button   # RA.DAMPER(R) 댐퍼 버튼
```

### DESICCANT 탭
```python
# DESICCANT FAN CONTROLS (기존 방식)
self.desiccant_fan1_toggle_button       # FAN1 ON/OFF 토글 버튼
self.desiccant_fan1_speed_dec_button    # FAN1 스피드 감소 버튼
self.desiccant_fan1_speed_val_button    # FAN1 스피드 값 버튼
self.desiccant_fan1_speed_inc_button    # FAN1 스피드 증가 버튼

# DESICCANT FAN CONTROLS (터치 친화적 방식)
self.desiccant_fan1_new_toggle_button   # FAN1 ON/OFF 토글 버튼
self.desiccant_fan1_new_speed_button    # FAN1 순환 스피드 버튼

# DAMPER CONTROLS
self.desiccant_damper1_toggle_button    # DMP1 CLOSE/OPEN 토글 버튼
self.desiccant_damper1_position_button  # DMP1 위치 버튼
```

### PUMPER & SOL 탭
```python
# PUMPER CONTROLS (기존 방식)
self.pumper_pump1_toggle_button         # PUMP1 ON/OFF 토글 버튼
self.pumper_pump1_speed_dec_button      # PUMP1 스피드 감소 버튼
self.pumper_pump1_speed_val_button      # PUMP1 스피드 값 버튼
self.pumper_pump1_speed_inc_button      # PUMP1 스피드 증가 버튼

# PUMPER CONTROLS (터치 친화적 방식)
self.pumper_pump1_new_toggle_button     # PUMP1 ON/OFF 토글 버튼
self.pumper_pump1_new_speed_button      # PUMP1 순환 스피드 버튼

# SOL CONTROLS
self.sol_sol1_button                    # SOL1 토글 버튼
self.sol_sol2_button                    # SOL2 토글 버튼
self.sol_sol3_button                    # SOL3 토글 버튼
self.sol_sol4_button                    # SOL4 토글 버튼
```

## 기존 호환성
모든 새로운 네이밍은 기존 네이밍과 병행하여 사용됩니다:

```python
# 새로운 네이밍 (권장)
self.aircon_eva_fan_button = cycle_button

# 기존 네이밍 (호환성 유지)
self.pushButton_1 = cycle_button
self.evaFanButton_1 = cycle_button
```

## 사용 방법

### 새로운 코드 작성 시
```python
# 권장: 새로운 네이밍 사용
if hasattr(self, 'aircon_eva_fan_button'):
    self.aircon_eva_fan_button.clicked.connect(self.handle_eva_fan)

# 기존 코드와의 호환성을 위한 fallback
elif hasattr(self, 'evaFanButton_1'):
    self.evaFanButton_1.clicked.connect(self.handle_eva_fan)
```

### 디버깅 및 로깅
```python
# 직관적인 버튼 식별
print(f"EVA FAN 버튼 상태: {self.aircon_eva_fan_button.text()}")
print(f"PUMP1 스피드: {self.pumper_pump1_new_speed_button.text()}")
```

## 장점

1. **직관성**: 이름만 봐도 어떤 기능인지 즉시 파악 가능
2. **유지보수성**: 코드 수정 시 해당 버튼을 쉽게 찾을 수 있음
3. **확장성**: 새로운 버튼 추가 시 네이밍 규칙을 쉽게 적용
4. **디버깅**: 로그나 에러 메시지에서 버튼 식별이 용이
5. **문서화**: 코드 자체가 문서 역할을 함

## 마이그레이션 계획

1. ✅ **1단계**: 새로운 네이밍 컨벤션 정의
2. ✅ **2단계**: 모든 버튼에 새로운 네이밍 적용 (기존 호환성 유지)
3. ✅ **3단계**: 주요 참조 부분에서 새로운 네이밍 우선 사용
4. 🔄 **4단계**: 점진적으로 매니저 클래스들의 참조 업데이트
5. 📅 **5단계**: 완전 마이그레이션 후 기존 네이밍 제거 (향후)

## 주의사항

- 기존 코드의 안정성을 위해 급격한 변경은 피함
- 새로운 네이밍을 우선 사용하되, 기존 네이밍도 병행 유지
- 모든 변경사항은 단계적으로 적용
- 철저한 테스트를 통해 호환성 확인