#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import threading
import time
import subprocess
import os

# 電源温度監視クラス(スレッドになる)
class GPSupsTempMonitor():
    m_nPinNum = 7          # UPSの接続しているGPIOピン番号
    m_cpuTemp = 0          # CPU温度
    m_errorFlag = False    # システム異常フラグ
    m_monitorLoopFlag = True # 監視ループフラグ
    
    # コンストラクタ
    def __init__(self, nPinNum = 7):
        self.m_nPinNum = nPinNum
        
        # ボードの設定(ピン番号指定)
        GPIO.setmode(GPIO.BOARD)
        
        # 指定したピンをインプットモードにする
        GPIO.setup(self.m_nPinNum,GPIO.IN)
    
    # 監視開始関数
    def start(self,maxTemp):
        # gps取得をスレッドでやらせる
        gpsThread = threading.Thread(target=self.startMonitor,args=(maxTemp,))
        gpsThread.start()
        
    # 監視終了関数
    def stop(self):
        self.m_monitorLoopFlag = False
        
    # 監視状態確認関数
    def isMonitorError(self):
        return self.m_errorFlag
        
    # 電源開始スタート
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
                print("し...死んでる！？")
                self.m_errorFlag = True
            # CPU温度が上限に達した場合
            elif float(self.m_cpuTemp) >= float(maxTemp):
                print("し...死んでる！？")
                self.m_errorFlag = True
            else :
                print("大丈夫だ！問題無い！")
            time.sleep(1)
        
        GPIO.cleanup()