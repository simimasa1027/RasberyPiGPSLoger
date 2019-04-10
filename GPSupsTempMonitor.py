#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================================
* Project       : GPSLoger
* FileName      : GPSupsTempMonitor.py
* Description   : 電圧温度監視
* CreateDay     : 2019/04/10
*
* History       :
*   2018/04/10  新規作成
*
==========================================================
"""

import RPi.GPIO as GPIO
import threading
import time
import subprocess
import os

"""
==========================================================
* ClassName     : 電圧温度監視クラス
* Description   : ラズパイの入力電圧と温度の管理
==========================================================
"""
class GPSupsTempMonitor():
    m_upsTempThread = None
    m_nPinNum = 7               # UPSの接続しているGPIOピン番号
    m_cpuTemp = 0               # CPU温度
    m_errorFlag = False         # システム異常フラグ
    m_monitorLoopFlag = True    # 監視ループフラグ
    
    """
    ==========================================================
    * Function      : コンストラクタ
    * args[in]      : nPinNum   ミニUPSの接続GPIOピン番号
    * Description   : -
    ==========================================================
    """
    def __init__(
        self,
        nPinNum = 7     # (i)ミニUPSの接続GPIOピン番号
    ):
        self.m_nPinNum = nPinNum
        
        # ボードの設定(ピン番号指定)
        GPIO.setmode(GPIO.BOARD)
        
        # 指定したピンをインプットモードにする
        GPIO.setup(self.m_nPinNum,GPIO.IN)
    
    """
    ==========================================================
    * Function      : 監視開始関数
    * args[in]      : maxTemp   システム停止最大温度
    * Description   : -
    ==========================================================
    """
    def start(
        self,
        maxTemp     # (i)システム停止最大温度
    ):
        # gps取得をスレッドでやらせる
        self.m_upsTempThread = threading.Thread(target=self.startMonitor,args=(maxTemp,))
        self.m_upsTempThread.start()
        
    """
    ==========================================================
    * Function      : 監視終了関数
    * Description   : -
    ==========================================================
    """
    def stop(
        self
    ):
        self.m_monitorLoopFlag = False
        self.m_upsTempThread.join()

    """
    ==========================================================
    * Function      : 監視状態確認関数
    * Return        : True:システム正常 False:システム異常
    * Description   : -
    ==========================================================
    """
    def isMonitorError(
        self
    ):
        return self.m_errorFlag
        

    """
    ==========================================================
    * Function      : 監視関数
    * args[in]      : maxTemp   システム停止最大温度
    * Description   : -
    ==========================================================
    """
    def startMonitor(self, maxTemp):
        while(self.m_monitorLoopFlag):
            # CPU温度取得
            self.m_cpuTemp = subprocess.run(
                    ["vcgencmd","measure_temp"],
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                    ).stdout.decode("utf8").split("=")[1].split("\'")[0]
            
            # 電圧が下がった場合
            if GPIO.input(self.m_nPinNum):
                print("Error : Voltage drop")
                self.m_errorFlag = True
            # CPU温度が上限に達した場合
            elif float(self.m_cpuTemp) >= float(maxTemp):
                print("Error : CPU temperature upper limit")
                self.m_errorFlag = True
            else :
                print("Info : System running...")
            time.sleep(1)
        
        GPIO.cleanup()