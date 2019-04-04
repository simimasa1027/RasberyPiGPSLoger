#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import subprocess
import GPSsettingLoader
import GPSlogWriter
import GPSupsTempMonitor

# define================
# 設定ファイルパス
CONFIG_FILE_PATH = './conf/gpsConfig.conf'
# ======================

# システム終了フラグ
g_systemEndFlag = False

def main() :
    # 設定ファイルの読み込み
    gpsLoader= GPSsettingLoader.GPSsettingLoader()
    gpsLoader.settingLoad(CONFIG_FILE_PATH)
    
    # 各スレッドクラス生成
    upsTempMonitor = GPSupsTempMonitor.GPSupsTempMonitor()    # 電源温度監視スレッド
    gpsWriter = GPSlogWriter.GPSlogWriter()    # gpsログ出力スレッド
    
    # 電源・温度監視スレッド起動
    upsTempMonitor.start(gpsLoader.m_mapGPSConfig["ForcedTerminationTemperatureLimit"])
    # GPSログ出力スレッド起動
    gpsWriter.start(upsTempMonitor, gpsLoader.m_mapGPSConfig["GPXOutputPath"],gpsLoader.m_mapGPSConfig["GetGpsStopTemperatureLimit"])
    
    # メインループ
    bLoop = True
    waitStartTimer = 0.0
    waitEndTimer = 0.0
    while (bLoop):
        if upsTempMonitor.isMonitorError() != False :
            waitEndTimer = time.time()
        else :
            waitStartTimer = time.time()
            waitEndTimer = time.time()
        
        if float(gpsLoader.m_mapGPSConfig["PowerOffTimeOutMin"]) <= \
            float((waitEndTimer - waitStartTimer) / 60):
            bLoop = False
        #print(float(waitEndTimer - waitStartTimer) / 60)
        time.sleep(0.1)
    
    # 終了処理
    upsTempMonitor.stop()
    gpsWriter.stop()
    
    # 電源を落とす
    subprocess.call('poweroff') 
    
main()