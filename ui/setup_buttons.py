def setup_button_groups(window):
    """버튼 그룹 설정 - 일반 버튼만 (SPD 버튼 제외)"""
    # 에어컨 팬 | AIRCON FAN
    window.button_manager.add_group('aircon_fan', {
        window.pushButton_1: {'on': '$CMD,FAN,ON\n', 'off': '$CMD,FAN,OFF\n'}
    })

    # 에어컨 콘 팬 | Aircoen Con Fan 
    window.button_manager.add_group('aircon_con_fan', {
        window.pushButton_5: {'on': '$CMD,CON_F,ON\n', 'off': '$CMD,CON_F,OFF\n'}
    })

    # 에어컨 왼쪽 위 DMP | Aircon LEFT TOP DMP
    window.button_manager.add_group('aircon_left_top_DMP', {
        window.pushButton_9: {'on': '$CMD,ALTDMP,OPEN\n', 'off': '$CMD,ALTDMP,CLOSE\n'}
    })

    # 에어컨 왼쪽 바닥 DMP | Aircon LEFT BOTTOM DMP
    window.button_manager.add_group('aircon_left_bottom_DMP', {
        window.pushButton_10: {'on': '$CMD,ALBDMP,OPEN\n', 'off': '$CMD,ALBDMP,CLOSE\n'}
    })

    # 에어컨 오른쪽 위 DMP | Aircon RIGHT TOP DMP
    window.button_manager.add_group('aircon_right_top_DMP', {
        window.pushButton_11: {'on': '$CMD,ARTDMP,OPEN\n', 'off': '$CMD,ARTDMP,CLOSE\n'}
    })

    # 에어컨 오른쪽 바닥 DMP | Aircon RIGHT BOTTOM DMP
    window.button_manager.add_group('aircon_right_bottom_DMP', {
        window.pushButton_12: {'on': '$CMD,ARBDMP,OPEN\n', 'off': '$CMD,ARBDMP,CLOSE\n'}
    })

    # inverter 
    window.button_manager.add_group('inverter', {
        window.pushButton_13: {'on': '$CMD,INVERTER,ON\n', 'off': '$CMD,INVERTER,OFF\n'}
    })

    # CLUCH 
    window.button_manager.add_group('aircon_cluch', {
        window.pushButton_14: {'on': '$CMD,CLUCH,ON\n', 'off': '$CMD,CLUCH,OFF\n'}
    })

    #-----------Dehumidifier
    # 제습기 팬 | Dehumidifier FAN
    window.button_manager.add_group('Desiccant_FAN', {
        window.pushButton_15: {'on': '$CMD,DSCT,FAN,ON\n', 'off': '$CMD,DSCT,FAN,OFF\n'}
    })

    # 제습기 댐퍼 왼쪽 
    window.button_manager.add_group('Desiccant_Damper_LEFT', {
        window.pushButton_16: {'on': '$CMD,DSCT,LDMP,OPEN\n', 'off': '$CMD,DSCT,LDMP,CLOSE\n'}
    })

    # 제습기 댐퍼 오른쪽 
    window.button_manager.add_group('Desiccant_Damper_RIGHT', {
        window.pushButton_17: {'on': '$CMD,DSCT,RDMP,OPEN\n', 'off': '$CMD,DSCT,RDMP,CLOSE\n'}
    })

    # 제습기 왼쪽 핫 밸브 
    window.button_manager.add_group('Desiccant_LEFT_HOT_VaLve', {
        window.pushButton_18: {'on': '$CMD,DSCT,LHOT,OPEN\n', 'off': '$CMD,DSCT,LHOT,CLOSE\n'}
    })

    # 제습기 왼쪽 쿨 밸브 
    window.button_manager.add_group('Desiccant_LEFT_COOL_VaLve', {
        window.pushButton_19: {'on': '$CMD,DSCT,LCOOL,OPEN\n', 'off': '$CMD,DSCT,LCOOL,CLOSE\n'}
    })

    # 제습기 오른쪽 핫 밸브 
    window.button_manager.add_group('Desiccant_RIGHT_HOT_VaLve', {
        window.pushButton_20: {'on': '$CMD,DSCT,RHOT,OPEN\n', 'off': '$CMD,DSCT,RHOT,CLOSE\n'}
    })

    # 제습기 오른쪽 쿨 밸브 
    window.button_manager.add_group('Desiccant_RIGHT_COOL_VaLve', {
        window.pushButton_21: {'on': '$CMD,DSCT,RCOOL,OPEN\n', 'off': '$CMD,DSCT,RCOOL,CLOSE\n'}
    })