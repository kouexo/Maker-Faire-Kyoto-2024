import RPi.GPIO as GPIO
import time

# 以前のGPIOの設定をクリーンアップ
GPIO.cleanup()

# GPIOモード設定
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# センサーのピン設定
TRIG = 24
ECHO = 27
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

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

# モーターを指定された角度に回転する関数
def set_angle(servo1, angle1, servo2, angle2):
   duty1 = angle1 / 18 + 2
   duty2 = angle2 / 18 + 2
   GPIO.output(servo1, True)
   GPIO.output(servo2, True)
   pwm1.ChangeDutyCycle(duty1)
   pwm2.ChangeDutyCycle(duty2)

def measure_distance():
   """距離を測定する関数"""
   GPIO.output(TRIG, True)
   time.sleep(0.00001)
   GPIO.output(TRIG, False)
   start_time = time.time()
   stop_time = time.time()
   while GPIO.input(ECHO) == 0:
       start_time = time.time()
   while GPIO.input(ECHO) == 1:
       stop_time = time.time()
   time_elapsed = stop_time - start_time
   distance = (time_elapsed * 34300) / 2
   return distance

try:
   while True:
       dist = measure_distance()
       print(f"distance = {dist} cm")
       if dist <= 20:
         print("right")
         set_angle(servo_pin1, 90, servo_pin2, 180)  
         # 左側のサーボモーターを左折、右側のサーボモーターを左折
         time.sleep(1.8)  # 1秒待機
         set_angle(servo_pin1, 0, servo_pin2, 180)  # 例: 両方のモーターを90度に設定
         time.sleep(0.3)
          
         # 左側のサーボモーターを停止、右側のサーボモーターを左折
         set_angle(servo_pin1, 0, servo_pin2, 90) 
         time.sleep(0.8)  # 1秒待機
         #set_angle(servo_pin1, 90, servo_pin2, 90)   
       else:
           set_angle(servo_pin1, 0, servo_pin2, 180)  # 例: 両方のモーターを90度に設定
           time.sleep(0.3)
           print("forward.")
       time.sleep(1)
except KeyboardInterrupt:
   print("Measurement stopped by User")
   pwm1.stop()
   pwm2.stop()
   GPIO.cleanup()
