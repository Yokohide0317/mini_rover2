# -*- coding: utf-8 -*-
import  sys
from time import sleep, time
import paho.mqtt.client as mqtt
import threading
import subprocess
import wiringpi

# --------------------------------------------------
# 変数定義
# --------------------------------------------------
# ブローカー情報
Host = "ホスト名"
Port = 1883
User = "ユーザー名"
Password = "パスワード"
Pull = "controller/minirover/test"
#Push = "rover/cafe01/rover021"

# その他
Continue = True
Msg = "" # 現在のメッセージ
Arrive = False # メッセージ状態
Dev = 22
Pin = [19, 26, 16, 20]
Trig = 27
Echo = 17
Danger = [0, 0, 0, 0, 0]
Stop = 0
Pubmsg = ["FR", "FL", "BR", "BL"] # Pinと対応
Gear = 1
Speed = [0.2, 0.4, 0.6, 0.8]

# --------------------------------------------------
# MQTT通信動作定義
# --------------------------------------------------
def on_connect(client, userdata, flags, respons_code):
    print("status {0}".format(respons_code))
    Client.subscribe(Pull)

def on_message(client, userdata, msg):
    global Msg, Arrive
    Msg = str(msg.payload,"utf-8")
    print("Msg:", Msg)
    
    Arrive = True

# --------------------------------------------------
# セットアップ
# ------------------------------------------------

# MQTTのセットアップ
Client = mqtt.Client(protocol=mqtt.MQTTv311)
Client.on_connect = on_connect
Client.on_message = on_message
Client.username_pw_set(User, Password)


# ラズベリーパイのピンのセットアップ
# GPIO端子の設定
motor1_pin = 23
motor2_pin = 24
motor3_pin = 27
motor4_pin = 22

# GPIO出力モードを1に設定する
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(motor1_pin, 1)
wiringpi.pinMode(motor2_pin, 1)
wiringpi.pinMode(motor3_pin, 1)
wiringpi.pinMode(motor4_pin, 1)

# --------------------------------------------------
# タイヤ制御
# --------------------------------------------------
def forward():
        global Msg
        wiringpi.digitalWrite(motor1_pin, 1)
        wiringpi.digitalWrite(motor2_pin, 0)
        wiringpi.digitalWrite(motor3_pin, 1)
        wiringpi.digitalWrite(motor4_pin, 0)
        Msg = "n"

def back():
        global Msg
        wiringpi.digitalWrite(motor1_pin, 0)
        wiringpi.digitalWrite(motor2_pin, 1)
        wiringpi.digitalWrite(motor3_pin, 0)
        wiringpi.digitalWrite(motor4_pin, 1)    
        Msg = "n"

def stop():
        global Msg
        wiringpi.digitalWrite(motor1_pin, 1)
        wiringpi.digitalWrite(motor2_pin, 1)
        wiringpi.digitalWrite(motor3_pin, 1)
        wiringpi.digitalWrite(motor4_pin, 1)
        Msg = "n"

# --------------------------------------------------
# メインスレッド
# --------------------------------------------------
def start():
    global Host, Port, Continue, Arrive, Stop, Msg

    sys.stderr.write("*** 通信開始 ***\n")
    Client.connect(Host, port=Port, keepalive=60)
    Client.loop_start()


    msg = ["forward", "back", "turn_right", "turn_left", "forward_right", "forward_left", "stop"]
    num = 0

    while Continue:
        if Msg == "F":
            num = 0
            forward()
            print("Forward")
        elif Msg == "B":
            back()
            print("Back")
        elif Msg == "R":
            pass
        elif Msg == "L":
            pass
        elif Msg == "":
            print("Stop")
            stop()
        else:
            stop()
        sleep(0.1)
#        Msg = "n"

# --------------------------------------------------
# 終了
# --------------------------------------------------
def finish():
    global Continue
    try:
        stop()
        Client.disconnect()
        sys.exit()
    except SystemExit:
        sys.stderr.write("*** 終了 ***\n")
    except:
        sys.stderr.write("*** 終了 ***\n")
        sys.exit()


# --------------------------------------------------
# 動作開始（動作管理）
# --------------------------------------------------
if __name__ == '__main__':
    try:
        start()
        finish()
    except KeyboardInterrupt:
        finish()
    except SyntaxError as e:
        print(e)
        finish()
