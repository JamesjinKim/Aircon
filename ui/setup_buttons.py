from ui.constants import (
    CMD_PREFIX, TERMINATOR, AIR_SYSTEM, DSCT_SYSTEM,
    ON_STATE, OFF_STATE, OPEN_STATE, CLOSE_STATE,
    FAN_CMD, CON_F_CMD, ALTDMP_CMD, ALBDMP_CMD, ARTDMP_CMD, ARBDMP_CMD,
    INVERTER_CMD, CLUCH_CMD, DSCT_FAN_CMD, LDMP_CMD, RDMP_CMD,
    LHOT_CMD, LCOOL_CMD, RHOT_CMD, RCOOL_CMD,
    FAN1_CMD, FAN2_CMD, FAN3_CMD, FAN4_CMD, SPD_CMD,
    PUMP1_CMD, PUMP2_CMD, SOL1_CMD, SOL2_CMD, SOL3_CMD, SOL4_CMD
)

def setup_button_groups(window):
    """버튼 그룹 설정 - 일반 버튼만 (SPD 버튼 제외)"""
    # 에어컨 팬 | AIRCON FAN
    window.button_manager.add_group('aircon_fan', {
        window.pushButton_1: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{FAN_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{FAN_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # 에어컨 콘 팬 | Aircoen Con Fan 
    window.button_manager.add_group('aircon_con_fan', {
        window.pushButton_5: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{CON_F_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{CON_F_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # 에어컨 왼쪽 위 DMP | Aircon LEFT TOP DMP
    window.button_manager.add_group('aircon_left_top_DMP', {
        window.pushButton_9: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{ALTDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{ALTDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 에어컨 왼쪽 바닥 DMP | Aircon LEFT BOTTOM DMP
    window.button_manager.add_group('aircon_left_bottom_DMP', {
        window.pushButton_10: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{ALBDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{ALBDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 에어컨 오른쪽 위 DMP | Aircon RIGHT TOP DMP
    window.button_manager.add_group('aircon_right_top_DMP', {
        window.pushButton_11: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{ARTDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{ARTDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 에어컨 오른쪽 바닥 DMP | Aircon RIGHT BOTTOM DMP
    window.button_manager.add_group('aircon_right_bottom_DMP', {
        window.pushButton_12: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{ARBDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{ARBDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # inverter 
    window.button_manager.add_group('inverter', {
        window.pushButton_13: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{INVERTER_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{INVERTER_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # CLUCH 
    window.button_manager.add_group('aircon_cluch', {
        window.pushButton_14: {
            'on': f'{CMD_PREFIX},{AIR_SYSTEM},{CLUCH_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{AIR_SYSTEM},{CLUCH_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })


    #-----------NEW DESICCANT FAN BUTTONS-----------#
    # DSCT FAN1 토글 버튼
    window.button_manager.add_group('dsct_fan1', {
        window.pushButton_dsct_fan1: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN1_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN1_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # DSCT FAN2 토글 버튼
    window.button_manager.add_group('dsct_fan2', {
        window.pushButton_dsct_fan2: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN2_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN2_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # DSCT FAN3 토글 버튼
    window.button_manager.add_group('dsct_fan3', {
        window.pushButton_dsct_fan3: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN3_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN3_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # DSCT FAN4 토글 버튼
    window.button_manager.add_group('dsct_fan4', {
        window.pushButton_dsct_fan4: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN4_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{FAN4_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    #-----------DAMPER는 라벨만 있고 토글 버튼 없음-----------#
    # DAMPER 위치값 버튼만 동작하며, 항상 CLOSE 명령 전송

    #-----------NEW PUMPER & SOL BUTTONS-----------#
    # PUMP1 토글 버튼
    window.button_manager.add_group('pump1', {
        window.pushButton_pump1: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{PUMP1_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{PUMP1_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # PUMP2 토글 버튼
    window.button_manager.add_group('pump2', {
        window.pushButton_pump2: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{PUMP2_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{PUMP2_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # SOL1 토글 버튼
    window.button_manager.add_group('sol1', {
        window.pushButton_sol1: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL1_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL1_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # SOL2 토글 버튼
    window.button_manager.add_group('sol2', {
        window.pushButton_sol2: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL2_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL2_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # SOL3 토글 버튼
    window.button_manager.add_group('sol3', {
        window.pushButton_sol3: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL3_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL3_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # SOL4 토글 버튼
    window.button_manager.add_group('sol4', {
        window.pushButton_sol4: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL4_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{SOL4_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })