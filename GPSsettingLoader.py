#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================================
* Project       : GPSLoger
* FileName      : GPSsettingLoader.py
* Description   : 設定ファイル取得クラス
* CreateDay     : 2019/04/10
*
* History       :
*   2018/04/10  新規作成
*
==========================================================
"""

"""
==========================================================
* ClassName     : 設定ファイル取得クラス
* Description   : GPSLogerの設定ファイルを取得する
==========================================================
"""
class GPSsettingLoader():
    m_mapGPSConfig = {}    # 設定ファイルマップ
    
    """
    ==========================================================
    * Function      : コンストラクタ
    * Description   : -
    ==========================================================
    """
    def __init__(
        self
    ):
       self.m_mapGPSConfig = {
            "SerialPath"     : "/dev/ttyAMA0",          # シリアルポートパス
            "BaudeRate"      : 9600,                    # ボーレート
            "GPXOutputPath"  : "./",                    # GPXファイル出力パス
            "GetGpsStopTemperatureLimit"        : 75,   # GPS取得温度上限
            "ForcedTerminationTemperatureLimit" : 90    # システム強制終了温度上限
        }

    """
    ==========================================================
    * Function      : 設定ファイル読み込み
    * args[in]      : confFilePath  設定ファイルパス
    * args[in]      : strSplit      設定ファイルの分割文字列
    * args[in]      : strComment    設定ファイルのコメント文字列
    * Description   : -
    ==========================================================
    """
    def settingLoad(
        self,
        confFilePath,       # (i)設定ファイルパス
        strSplit="=",       # (i)設定ファイルの分割文字列
        strComment="//"     # (i)設定ファイルのコメント文字列
    ):
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

    """
    ==========================================================
    * Function      : 設定取得
    * args[in]      : name      項目名
    * args[in]      : value     設定値
    * Description   : -
    ==========================================================
    """
    def GPSSettingData(
        self,
        name,   # (i)項目名
        value   # (i)設定名
    ):
        if(name == "SerialPath"        or
           name == "BaudeRate"         or
           name == "GPXOutputPath"     or
           name == "GetGpsStopTemperatureLimit" or
           name == "ForcedTerminationTemperatureLimit" or
           name == "PowerOffTimeOutMin"):
            self.m_mapGPSConfig[name] = value.replace("\n","")