import RPi.GPIO as GPIO
import time
import sys
import requests

# GPIOポートの設定
SwGpio = 24
Sw2Gpio = 6
LedGpio = 14
Led2Gpio = 5
lastStatus = 0
ledStatus = 0
last2Status = 0
led2Status = 0

# GPIOの設定
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# １つ目のボタン
GPIO.setup(SwGpio, GPIO.IN)
GPIO.setup(LedGpio, GPIO.OUT)

# 2つ目のボタン
GPIO.setup(Sw2Gpio, GPIO.IN)
GPIO.setup(Led2Gpio, GPIO.OUT)

# API情報
API_URL = "https://wwsx8q4mkd.execute-api.ap-northeast-1.amazonaws.com/prod/counter"
API_KEY = "b8R3f4^Mn37Vez_sAl4xGl4_pEdPcnFr"


def pushCount(name, flag):
    print("start")

    # UNIX時間（秒)で現在時間を取得
    timestamp = int(time.time())
    print(timestamp)

    url = API_URL
    headers = {"x-api-key": API_KEY}
    q = {'username': name, 'timestamp': timestamp, 'flag': flag}
    r = requests.post(url, headers=headers, json=q)
    print(r.json())


while True:
    try:
        btnStatus = not(GPIO.input(SwGpio))
        btn2Status = not(GPIO.input(Sw2Gpio))

        # 1つ目のボタンの動作を制御
        if btnStatus == 0 and lastStatus == 1:
            ledStatus = not ledStatus
            if ledStatus == True:
                GPIO.output(LedGpio, True)
                pushCount('Lucy', 'start')
                print('button 1 ON')
            else:
                GPIO.output(LedGpio, False)
                pushCount('Lucy', 'end')
                print('button 1 OFF')
            # 連続でボタンを誤認識しないように少し待つ
            time.sleep(0.2)

        # ２つ目のボタンの動作を制御
        if btn2Status == 0 and last2Status == 1:
            led2Status = not led2Status
            if led2Status == True:
                GPIO.output(Led2Gpio, True)
                pushCount('Mike', 'start')
                print('button 2 ON')
            else:
                GPIO.output(Led2Gpio, False)
                pushCount('Mike', 'end')
                print('button 2 OFF')
            # 連続でボタンを認識しないように少し待つ
            time.sleep(0.2)

        lastStatus = btnStatus
        last2Status = btn2Status

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()
