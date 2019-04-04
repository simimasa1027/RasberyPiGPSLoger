#!/usr/bin/env python
# -*- coding: utf-8 -*-

class GPSsettingLoader():
    m_mapGPSConfig = {}    # 設定ファイルマップ
    
    # コンストラクタ
    def __init__(self):
       self.m_mapGPSConfig = {
            "SerialPath"     : "/dev/ttyAMA0",    # シリアルポートパス
            "BaudeRate"      : 9600,               # ボーレート
            "GPXOutputPath"  : "./",           # GPXファイル出力パス
            "GetGpsStopTemperatureLimit"        : 75,          # GPS取得温度上限
            "ForcedTerminationTemperatureLimit" : 90           # システム強制終了温度上限
        }
    
    def settingLoad(self,confFilePath ,strSplit="=" , strComment="//"):
        # 設定ファイル読み込み
        gpsConf = open(confFilePath, "r")
        
        # 1行ずつ読み込み
        for line in gpsConf:
            settingLine = line
            
            # コメントの検索
            commentFindNum = settingLine.find(strComment)
            if commentFindNum != -1 :
                settingLine = settingLine[0:commentFindNum]
            
            settingArray = settingLine.split(strSplit)
            if len(settingArray) == 2:
                self.GPSSettingData(settingArray[0],settingArray[1])
    
    def GPSSettingData(self,name,value):
        if(name == "SerialPath"        or
           name == "BaudeRate"         or
           name == "GPXOutputPath"     or
           name == "GetGpsStopTemperatureLimit" or
           name == "ForcedTerminationTemperatureLimit" or
           name == "PowerOffTimeOutMin"):
            self.m_mapGPSConfig[name] = value.replace("\n","")