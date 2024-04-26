import RPi.GPIO as GPIO
import time

# 以前のGPIOの設定をクリーンアップ
GPIO.cleanup()

# GPIOモード設定
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# センサーのピン設定
#center
TRIG1 = 24
ECHO1 = 27
#right
TRIG2 = 25
ECHO2 = 21
#left
TRIG3 = 23
ECHO3 = 17

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

# 現在の角度を追跡するための変数（初期値は中立位置と仮定）
current_angle1 = 90
current_angle2 = 90

pwm1.start(0)  # 左側のサーボモーターのPWMの開始、デューティサイクル0%で停止
pwm2.start(0)  # 右側のサーボモーターのPWMの開始、デューティサイクル0%で停止

def set_angle(servo1, angle1, servo2, angle2):
    """
    モーターを指定された角度に回転させる関数。
    Parameters:
        servo1 (int): 左側のサーボモーターのGPIOピン番号。
        angle1 (int): 左側のサーボモーターの目標角度。0から180の範囲。
        servo2 (int): 右側のサーボモーターのGPIOピン番号。
        angle2 (int): 右側のサーボモーターの目標角度。0から180の範囲。
    """
    global current_angle1, current_angle2
    new_angle1 = current_angle1 + angle1
    new_angle2 = current_angle2 + angle2
    # 角度の範囲を0から180度に制限
    new_angle1 = max(0, min(180, new_angle1))
    new_angle2 = max(0, min(180, new_angle2))
    duty1 = new_angle1 / 18 + 2
    duty2 = new_angle2 / 18 + 2
    GPIO.output(servo1, True)
    GPIO.output(servo2, True)
    pwm1.ChangeDutyCycle(duty1)
    pwm2.ChangeDutyCycle(duty2)
    # 現在の角度を更新
    current_angle1 = new_angle1
    current_angle2 = new_angle2

def measure_distance(trig, echo):
    """距離を測定する関数"""
    time.sleep(0.1)  # 計測間隔を調整
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    
    timeout_start = time.time()
    while GPIO.input(echo) == 0:
        if time.time() - timeout_start > 0.1:  # タイムアウト時間を設定
            return -1  # タイムアウトした場合は-1を返す
        pulse_start = time.time()
        
    while GPIO.input(echo) == 1:
        if time.time() - pulse_start > 0.1:  # タイムアウト時間を設定
            return -1  # タイムアウトした場合は-1を返す
        pulse_end = time.time()
        
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

def avoid_obstacle():
    """障害物を避ける関数"""
    print("障害物を検知しました。回避します。")
    dist2 = measure_distance(TRIG2, ECHO2)  # 右側センサー
    dist3 = measure_distance(TRIG3, ECHO3)  # 左側センサー
    print(f"distance2 = {dist2} cm")
    print(f"distance3 = {dist3} cm")
    time.sleep(1.0)  # 1秒の遅延を追加

    if dist2 > dist3:  # 右側が広い時
        print("右に回避")
        set_angle(servo_pin1, +45, servo_pin2, +45)  # 右に旋回
        time.sleep(1.3)
    else:
        print("左に回避")
        set_angle(servo_pin1, -45, servo_pin2, -45)  # 左に旋回
        time.sleep(1.3)

    set_angle(servo_pin1, -45, servo_pin2, +45)  # 直進
    print("go")
    time.sleep(0.8)

    if dist2 > dist3:
        print("左に戻る")
        set_angle(servo_pin1, +45, servo_pin2, +45)  # 左に旋回
        time.sleep(1.0)  # 1秒旋回
    else:
        print("右に戻る")
        set_angle(servo_pin1, -45, servo_pin2, -45)  # 右に旋回
        time.sleep(1.0)  # 1秒旋回
    time.sleep(1.0)  # 1秒の遅延を追加

    print("元の道に戻りました。")
    set_angle(servo_pin1, -45, servo_pin2, +45)  # 直進
    time.sleep(1.0)

try:
    while True:
        # 距離が20cm以下の時に左右のセンサー値を取得し広いほうに避ける。20cmより大きい時は直進。
        dist1 = measure_distance(TRIG1, ECHO1)
        print(f"distance1 = {dist1} cm")

        if dist1 <= 20:
            avoid_obstacle()
        else:
            print("前進")
            set_angle(servo_pin1, -45, servo_pin2, +45)  # 直進
            time.sleep(0.1)  # 0.1秒待機

except KeyboardInterrupt:
    print("Measurement stopped by User")
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
