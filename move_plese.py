import RPi.GPIO as GPIO
import time

# 以前のGPIOの設定をクリーンアップ
GPIO.cleanup()

# GPIOモード設定
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# センサーのピン設定
TRIG1 = 24
ECHO1 = 27
TRIG2 = 22
ECHO2 = 23
TRIG3 = 20
ECHO3 = 21

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)
GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)
GPIO.setup(TRIG3, GPIO.OUT)
GPIO.setup(ECHO3, GPIO.IN)

# サーボモーターのピン設定
servo_pin1 = 18  # 左側のサーボモーターのGPIOピン番号
servo_pin2 = 19  # 右側のサーボモーターのGPIOピン番号

GPIO.setup(servo_pin1, GPIO.OUT)
GPIO.setup(servo_pin2, GPIO.OUT)

# PWMインスタンスの作成
pwm1 = GPIO.PWM(servo_pin1, 50)  # 左側のサーボモーターのPWM周波数を50Hzに設定
pwm2 = GPIO.PWM(servo_pin2, 50)  # 右側のサーボモーターのPWM周波数を50Hzに設定

pwm1.start(0)  # 左側のサーボモーターのPWMの開始、デューティサイクル0%で停止
pwm2.start(0)  # 右側のサーボモーターのPWMの開始、デューティサイクル0%で停止
# --------------------------------------------------------------------
def set_angle(servo1, angle1, servo2, angle2):
    """
    モーターを指定された角度に回転させる関数。
    Parameters:
        servo1 (int): 左側のサーボモーターのGPIOピン番号。
        angle1 (int): 左側のサーボモーターの目標角度。0から180の範囲。
        servo2 (int): 右側のサーボモーターのGPIOピン番号。
        angle2 (int): 右側のサーボモーターの目標角度。0から180の範囲。
    """
    duty1 = angle1 / 18 + 2
    duty2 = angle2 / 18 + 2
    GPIO.output(servo1, True)
    GPIO.output(servo2, True)
    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
# --------------------------------------------------------------------
def measure_distance(trig, echo):
    """距離を測定する関数"""
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    start_time = time.time()
    stop_time = time.time()
    while GPIO.input(echo) == 0:
        start_time = time.time()
    while GPIO.input(echo) == 1:
        stop_time = time.time()
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance
# --------------------------------------------------------------------
def avoid_obstacle():
    """障害物を避ける関数"""
    print("障害物を検知しました。回避します。")
    dist2 = measure_distance(TRIG2, ECHO2)#右側センサー
    dist3 = measure_distance(TRIG3, ECHO3)#左側センサー
    #距離の遠いほうに旋回→直進→距離の遠いほうに旋回→直進。
    #if文を２回行っていて冗長な気もする
    #適宜モーターの値を調整する。
    if dist2 > dist3:#右側が広い時
        print("右に回避")
        set_angle(servo_pin1, 0, servo_pin2, 180)  # 右に旋回
        time.sleep(1.0)  # 1秒旋回
    else:
        print("左に回避")
        set_angle(servo_pin1, 180, servo_pin2, 0)  # 左に旋回
        time.sleep(1.0)  # 1秒旋回

    set_angle(servo_pin1, 90, servo_pin2, 90)  # 直進
    time.sleep(1.0)  # 1秒直進

    if dist2 > dist3:
        print("左に戻る")
        set_angle(servo_pin1, 180, servo_pin2, 0)  # 左に旋回
        time.sleep(1.0)  # 1秒旋回
    else:
        print("右に戻る")
        set_angle(servo_pin1, 0, servo_pin2, 180)  # 右に旋回
        time.sleep(1.0)  # 1秒旋回

    print("元の道に戻りました。")
    set_angle(servo_pin1, 90, servo_pin2, 90)  # 直進
# --------------------------------------------------------------------
try:
    while True:
        #距離が20cm以下の時に左右のセンサー値を取得し広いほうに避ける。20cmより大きい時は直進。
        dist1 = measure_distance(TRIG1, ECHO1)
        print(f"distance1 = {dist1} cm")

        if dist1 <= 20:
            avoid_obstacle()
        else:
            print("前進")
            set_angle(servo_pin1, 90, servo_pin2, 90)  # 直進
            time.sleep(0.1)  # 0.1秒待機

except KeyboardInterrupt:
    print("Measurement stopped by User")
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
