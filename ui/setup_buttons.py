from ui.constants import (
    CMD_PREFIX, TERMINATOR, AIR_SYSTEM, DSCT_SYSTEM,
    ON_STATE, OFF_STATE, OPEN_STATE, CLOSE_STATE,
    FAN_CMD, CON_F_CMD, ALTDMP_CMD, ALBDMP_CMD, ARTDMP_CMD, ARBDMP_CMD,
    INVERTER_CMD, CLUCH_CMD, DSCT_FAN_CMD, LDMP_CMD, RDMP_CMD,
    LHOT_CMD, LCOOL_CMD, RHOT_CMD, RCOOL_CMD
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

    #-----------DESICCANT BUTTONS-----------#
    # 제습기 팬 | Desiccant FAN
    window.button_manager.add_group('Desiccant_FAN', {
        window.pushButton_15: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{DSCT_FAN_CMD},{ON_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{DSCT_FAN_CMD},{OFF_STATE}{TERMINATOR}'
        }
    })

    # 제습기 댐퍼 왼쪽 
    window.button_manager.add_group('Desiccant_Damper_LEFT', {
        window.pushButton_16: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{LDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{LDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 제습기 댐퍼 오른쪽 
    window.button_manager.add_group('Desiccant_Damper_RIGHT', {
        window.pushButton_17: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{RDMP_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{RDMP_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 제습기 왼쪽 핫 밸브 
    window.button_manager.add_group('Desiccant_LEFT_HOT_VaLve', {
        window.pushButton_18: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{LHOT_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{LHOT_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 제습기 왼쪽 쿨 밸브 
    window.button_manager.add_group('Desiccant_LEFT_COOL_VaLve', {
        window.pushButton_19: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{LCOOL_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{LCOOL_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 제습기 오른쪽 핫 밸브 
    window.button_manager.add_group('Desiccant_RIGHT_HOT_VaLve', {
        window.pushButton_20: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{RHOT_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{RHOT_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })

    # 제습기 오른쪽 쿨 밸브 
    window.button_manager.add_group('Desiccant_RIGHT_COOL_VaLve', {
        window.pushButton_21: {
            'on': f'{CMD_PREFIX},{DSCT_SYSTEM},{RCOOL_CMD},{OPEN_STATE}{TERMINATOR}',
            'off': f'{CMD_PREFIX},{DSCT_SYSTEM},{RCOOL_CMD},{CLOSE_STATE}{TERMINATOR}'
        }
    })