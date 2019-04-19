#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==========================================================
* Project       : GPSLoger
* FileName      : GPSlogWriter.py
* Description   : ログ取得クラス
* CreateDay     : 2019/04/10
*
* History       :
*   2018/04/10  新規作成
*
==========================================================
"""

import os.path
import serial
import threading
import time
import pytz
from datetime import datetime
import math

"""
==========================================================
* ClassName     : GPSログ取得クラス
* Description   : GPSデータを取得し、GPXデータを出力
==========================================================
"""
class GPSlogWriter():
    m_gpsThread = None
    m_strSerialPath = '/dev/ttyAMA0'    # シリアルポートパス
    m_nBaudeRate = 9600                 # ボーレート
    m_gpsSerial = ""                    # GPSシリアル取得用
    m_bIsStartFlag = False              # スレッド開始・終了フラグ
    
    """
    ==========================================================
    * Function      : コンストラクタ
    * args[in]      : strSerialPath シリアルポートパス
    * args[in]      : nBaudeRate    ボーレート
    * Description   : -
    ==========================================================
    """
    def __init__(
        self,
        strSerialPath = '/dev/ttyAMA0',     # (i)シリアルポートパス
        nBaudeRate = 9600                   # (i)ボーレート
    ):
        self.m_strSerialPath = strSerialPath
        self.m_nBaudeRate = int(nBaudeRate)
        self.m_gpsSerial = serial.Serial(self.m_strSerialPath, self.m_nBaudeRate, timeout=10)

    """
    ==========================================================
    * Function      : GPS取得開始関数
    * args[in]      : upsTempClass  電圧温度監視クラス変数
    * args[in]      : folderPath    GPX出力フォルダパス
    * args[in]      : fileName      GPX出力ファイル名
    * args[in]      : getStopTemp   GPSデータ取得停止温度
    * Description   : -
    ==========================================================
    """
    def start(
        self,
        upsTempClass,       # (i)電圧温度監視クラス変数
        folderPath = './',  # (i)GPX出力フォルダパス
        fileName = '{YMDHMS}.gpx',  # (i)GPX出力ファイル名
        getStopTemp = 75    # (i)GPSデータ取得停止温度
    ):
        # gps取得をスレッドでやらせる
        self.m_gpsThread = threading.Thread(target=self.getGPS,args=(upsTempClass,folderPath,fileName,getStopTemp,))
        self.m_gpsThread.start()
        
    """
    ==========================================================
    * Function      : GPS取得関数
    * args[in]      : upsTempClass  電圧温度監視クラス変数
    * args[in]      : folderPath    GPX出力フォルダパス
    * args[in]      : fileName      GPX出力ファイル名
    * args[in]      : getStopTemp   GPSデータ取得停止温度
    * Description   : -
    ==========================================================
    """
    def getGPS(
        self,
        upsTempClass,   # (i)電圧温度監視クラス変数
        folderPath,     # (i)GPX出力フォルダパス
        fileName,       # (i)GPX出力ファイル名
        getStopTemp     # (i)GPSデータ取得停止温度
    ):
        print("GPSLoger Start")
        self.m_gpsSerial.readline()	#1回目は捨てる
        bGetDataFlag = False
        while(bGetDataFlag == False):
            strGetGPS = ""
            try:
                strGetGPS = self.m_gpsSerial.readline().decode('utf-8')
            except UnicodeDecodeError as e:
                print (e)
                continue
                
            if strGetGPS[0:6] == '$GPRMC': # GPRMC形式でなければ捨てる
                # GPSデータ配列の初期化
                utcDate = strGetGPS.split(",")[9]   # UTC日時
                utcTime = strGetGPS.split(",")[1]   # UTC時刻
                bGetDataFlag = True

        aryNeedGPS = {}
        # 現在日時(YYYYMMDDhhmmss)を取得
        nowDate = datetime(int("20" + utcDate[4:6]),int(utcDate[2:4]),int(utcDate[0:2]),int(utcTime[0:2]),int(utcTime[2:4]),int(utcTime[4:6]),0,tzinfo=pytz.timezone('Asia/Tokyo'))
        formatFileName = dateFormatConverter(nowDate,fileName)

        # ファイルが存在しない場合は新規作成
        if os.path.isfile(folderPath + '/' + formatFileName) == False:
            with open(folderPath + '/' + formatFileName, mode='w') as writeGps:
                # GPXヘッダー文字列
                writeGps.write(self.gpxHeaderWrite(nowDate.strftime("%Y/%m/%d %H:%M:%S"),nowDate.strftime("%Y/%m/%d %H:%M:%S")))
        else :
            fileRead = open(folderPath + '/' + formatFileName,"r")
            fileLines = fileRead.readlines()
            fileRead.close()
            with open(folderPath + '/' + formatFileName, mode='w') as writeGps:
                for i in range(len(fileLines) - 3):
                    writeGps.write(fileLines[i])

        self.m_bIsStartFlag = True
        while(self.m_bIsStartFlag):
            # CPU温度がGPS取得温度上限を超えたら取得を中断する
            if(float(upsTempClass.m_cpuTemp) >= float(getStopTemp)):
                time.sleep(1)
                continue
            
            strGetGPS = ""
            try:
                strGetGPS = self.m_gpsSerial.readline().decode('utf-8')
            except UnicodeDecodeError as e:
                print (e)
                continue
                
            if strGetGPS[0:6] == '$GPRMC': # GPRMC形式でなければ捨てる
                # GPSデータ配列の初期化
                aryNeedGPS = {}
                aryNeedGPS["GPRMC"] = strGetGPS
                continue
            elif strGetGPS[0:6] == '$GPGGA':
                aryNeedGPS["GPGGA"] = strGetGPS
            
            # 必要なGPSデータを取得できたら
            if len(aryNeedGPS) == 2:
                with open(folderPath + '/' + formatFileName, mode='a') as writeGps:    
                    writeGps.write(self.gpsMainWrite(aryNeedGPS))
                # GPSデータ配列の初期化
                aryNeedGPS = {}
                
        with open(folderPath + '/' + formatFileName, mode='a') as writeGps:                       
            writeGps.write(self.gpxFooterWrite())

    """
    ==========================================================
    * Function      : GPS取得停止関数
    * Description   : -
    ==========================================================
    """
    def stop(
        self
    ):
        # 子スレッドのループフラグをFalseにする
        self.m_bIsStartFlag = False
        self.m_gpsThread.join()

    """
    ==========================================================
    * Function      : GPXヘッダー文字列作成
    * args[in]      : strName   GPXデータのタイトル
    * args[in]      : strInfo   GPXデータの説明
    * Return        : GPXヘッダー文字列
    * Description   : -
    ==========================================================
    """
    def gpxHeaderWrite(
        self,
        strName,    # (i)GPXデータのタイトル
        strInfo     # (i)GPXデータの説明
    ):
        strGPXHeader = "";    #GPXのヘッダー文字列(返却用)
        
        strGPXHeader += \
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" \
            "<gpx xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" " \
            "xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" " \
            "xmlns:mytracks=\"http://mytracks.stichling.info/myTracksGPX/1/0\" creator=\"myTracks\" " \
            "version=\"1.1\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 " \
            "http://www.topografix.com/GPX/1/1/gpx.xsd\">\n" 
        
        # トラックヘッダーデータの記述
        strGPXHeader += \
            "    <trk>\n" \
            "        <name>" + strName + "</name>\n" \
            "        <desc>" + strInfo + "</desc>\n" \
            "        <trkseg>\n"
        
        return strGPXHeader

    """
    ==========================================================
    * Function      : GPXデータ文字列作成
    * args[in]      : aryGPS    GPRMC・GPGGA文字列の配列
    * Return        : GPXデータ文字列
    * Description   : -
    ==========================================================
    """
    def gpsMainWrite(
        self,
        aryGPS      # (i)GPRMC・GPGGA文字列の配列
    ):
        strGPXpoint = ""     #GPSのGPSデータ文字列
        
        aryGPRMC = aryGPS["GPRMC"].split(",")    # GPRMCの配列
        aryGPGGA = aryGPS["GPGGA"].split(",")    # GPGGAの配列
        
        # GPSが正常に取得できていない場合は記載しない
        if aryGPRMC[2] == "V" :
            return ""
        
        
        longitude = 0.0    # 経度
        latitude  = 0.0    # 緯度
        speed     = 0.0    # 速度
        altitude  = 0.0    # 海抜高さ
        utcDate   = 0.0    # GPSのUTC日付(フォーマット：ddmmyy)
        utcTime   = 0.0    # GPSのUTC時刻(フォーマット：hhmmss.ss)
        
        # UTC日付取得
        utcDate = aryGPRMC[9]
        
        #UTC時刻取得
        utcTime = aryGPRMC[1]
        
        # 緯度経度をDMM形式からDeg形式に変換
        latitude = math.floor(float(aryGPRMC[3]) / 100) + \
            ((float(aryGPRMC[3]) - (math.floor(float(aryGPRMC[3]) / 100) * 100)) / 60)
        longitude = math.floor(float(aryGPRMC[5]) / 100) + \
            ((float(aryGPRMC[5]) - (math.floor(float(aryGPRMC[5]) / 100) * 100)) / 60)
        
        # 南緯なら負数にする
        if aryGPRMC[4] == "S":
            latitude *= -1
        
        # 西経なら負数にする
        if aryGPRMC[6] == "W":
            latitude *= -1
        
        # gps速度取得
        speed = float(aryGPRMC[7])
        
        # 海抜高さ取得
        altitude = float(aryGPGGA[9])
        
        
        strGPXpoint = \
            "                <trkpt lat=\"" + str(round(latitude,10)) + "\" lon=\"" + str(round(longitude,10)) + "\">\n" \
            "                    <ele>" + str(round(altitude,10)) + "</ele>\n" \
            "                    <time>20" + utcDate[4:6] + "-" + utcDate[2:4] + "-" + utcDate[0:2] + "T" + \
                                 utcTime[0:2] + ":" + utcTime[2:4] + ":" + utcTime[4:6] + "Z</time>\n" + \
            "                    <speed>" + str(round(speed,1)) + "</speed>\n" + \
            "                </trkpt>\n"

        return strGPXpoint   

    """
    ==========================================================
    * Function      : GPXフッター文字列作成
    * Return        : GPXフッター文字列
    * Description   : -
    ==========================================================
    """
    def gpxFooterWrite(
        self
    ):
        strGPXFooter= "";    #GPXのヘッダー文字列(返却用)
        
        strGPXFooter += \
            "        </trkseg>\n" \
            "    </trk>\n" \
            "</gpx>"
        return strGPXFooter

"""
==========================================================
* Function      : 日時→文字列変換
* args[in]      : date      変換日時
* args[in]      : formatStr 変換前文字列
* Return        : 変換後文字列
* Description   : -
==========================================================
"""
def dateFormatConverter(
    date,
    formatStr
):
    dateFormat = ["{YMDHMS}","%Y%m%d%H%M%S"]
    if r"{Y}" in formatStr:
        dateFormat = ["{Y}","%Y"]
    elif r"{YM}" in formatStr:
        dateFormat = ["{YM}","%Y%m"]
    elif r"{YMD}"in formatStr:
        dateFormat = ["{YMD}","%Y%m%d"]
    elif r"{YMDH}" in formatStr:
        dateFormat = ["{YMDH}","%Y%m%d%H"]
    elif r"{YMDHM}" in formatStr:
        dateFormat = ["{YMDHM}","%Y%m%d%H%M"]
    elif r"{YMDHMS}" in formatStr:
        dateFormat = ["{YMDHMS}","%Y%m%d%H%M%S"]
    else :
        return date.strftime("%Y%m%d%H%M%S") + '.gpx'

    return formatStr.replace(dateFormat[0],date.strftime(dateFormat[1]))