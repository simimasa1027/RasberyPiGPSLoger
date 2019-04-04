#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import threading
import time
from datetime import datetime
import math

class GPSlogWriter():
    m_strSerialPath = '/dev/ttyAMA0'    # シリアルポートパス
    m_nBaudeRate = 9600                 # ボーレート
    m_gpsSerial = ""           # GPSシリアル取得用
    m_bIsStartFlag = False     # スレッド開始・終了フラグ
    
    # コンストラクタ
    def __init__(self, strSerialPath = '/dev/ttyAMA0', nBaudeRate = 9600):
        self.m_strSerialPath = strSerialPath
        self.m_nBaudeRate = nBaudeRate
        self.m_gpsSerial = serial.Serial(self.m_strSerialPath, self.m_nBaudeRate, timeout=10)
    
    # gps取得開始関数
    def start(self, upsTempClass, filePath = './', getStopTemp = 75):
        # gps取得をスレッドでやらせる
        gpsThread = threading.Thread(target=self.getGPS,args=(upsTempClass,filePath,getStopTemp,))
        gpsThread.start()
        
    # gps取得関数(スレッド)
    def getGPS(self, upsTempClass, filePath,getStopTemp):
        self.m_gpsSerial.readline()	#1回目は捨てる
        aryNeedGPS = {}
        
        # 現在日時(YYYYMMDDhhmmss)を取得
        nowDate = datetime.now()
        
        with open(filePath + '/' + nowDate.strftime("%Y%m%d%H%M%S") + '.gpx', mode='w') as writeGps:
        
            # GPXヘッダー文字列
            writeGps.write(self.gpxHeaderWrite(nowDate.strftime("%Y/%m/%d %H:%M:%S"),"だめ"))
            
            self.m_bIsStartFlag = True
            while(self.m_bIsStartFlag):
                
                # CPU温度がGPS取得温度上限を超えたら取得を中断する
                #print(upsTempClass.m_cpuTemp)
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
                    writeGps.write(self.gpsMainWrite(aryNeedGPS))
                    # GPSデータ配列の初期化
                    aryNeedGPS = {}
                    
            writeGps.write(self.gpxFooterWrite())

    # gps取得停止関数
    def stop(self):
        # 子スレッドのループフラグをFalseにする
        self.m_bIsStartFlag = False
    
    # GPXヘッダー文字列作成
    def gpxHeaderWrite(self,strName,strInfo):
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
    
    # GPXデータ文字列作成
    def gpsMainWrite(self,aryGPS):
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
    
    # GPXフッター文字列作成
    def gpxFooterWrite(self):
        strGPXFooter= "";    #GPXのヘッダー文字列(返却用)
        
        strGPXFooter += \
            "        </trkseg>\n" \
            "    </trk>\n" \
            "</gpx>"
        return strGPXFooter