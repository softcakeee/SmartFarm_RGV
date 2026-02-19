from multiprocessing.resource_sharer import stop
from re import M
import cv2
import numpy as np
import serial
import time
import pytesseract
from PIL import Image
from enum import Enum
import RPi.GPIO as GPIO  

cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
ser = serial.Serial('/dev/ttyUSB0', 9600)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO_TRIGGER_01 = 2
GPIO_ECHO_01 = 3

GPIO_TRIGGER_02 = 4
GPIO_ECHO_02 = 14

GPIO_TRIGGER_03 = 17
GPIO_ECHO_03 = 18

GPIO.setup(GPIO_TRIGGER_01, GPIO.OUT)
GPIO.setup(GPIO_ECHO_01 , GPIO.IN)


GPIO.setup(GPIO_TRIGGER_02, GPIO.OUT)
GPIO.setup(GPIO_ECHO_02 , GPIO.IN)

GPIO.setup(GPIO_TRIGGER_03, GPIO.OUT)
GPIO.setup(GPIO_ECHO_03 , GPIO.IN)

state = 1
current_state = 0
next_state = 0
last_state = 0
GUTTER = 0

class stopwatch (Enum) :
    TIME_1sec = 0
    TIME_3sec = 1
    TIME_200msec = 2
    TIME_9sec = 3
    TIME_12sec = 4
    TIME_100msec = 5
    
class statement (Enum) :
    START = 0
    CAMERA_CAPTURE = 1
    OCR = 2
    FIRST_START = 3
    MOVE_FIRST_STOP = 4  
    MOVE_FIRST_UP = 5 
    MOVE_SECOND_UP = 6 
    MOVE_FIRST_BACK = 7
    MOVE_SECOND_BACK = 8
    ON_ULTRA_SONIC_01 = 9
    MOVE_FAST_BACK = 10
    MOVE_SLOW_BACK = 11
    MOVE_SECOND_STOP = 12
    MOVE_DOWN = 13
    MOVE_FAST_FRONT = 14
    MOVE_SLOW_FRONT = 15
    ON_ULTRA_SONIC_02_01 = 16
    ON_ULTRA_SONIC_02_02 = 17
    
def ULTRA_SONIC_01():
    global StartTime_01
    global StopTime_01
    global TimeElapsed_01
    global distance_01
    
    GPIO.output(GPIO_TRIGGER_01, True)
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_01, False)
        
    while GPIO.input(GPIO_ECHO_01) == 0 :
        StartTime_01 = time.time()
        
    while GPIO.input(GPIO_ECHO_01) == 1 :
        StopTime_01 = time.time()
            
        
    TimeElapsed_01 = StopTime_01 - StartTime_01
    distance_01 = TimeElapsed_01 * 17000 
    # 음파의 속력은 340m/s 우리가 측정하는것은 cm -> 34000 의 속력이며
    # 거리는 시간 * 속력으로 계산한다. 여기서 속력은 초음파 센서가 왕복하기 때문에 나누기 2 를 해준다.
    
    #distance_01 = round(distance_01, 2) # 거리에서 소수점 2번째 자리에서 반올림 해라 라는 문장이다.
    
    #print ("Measured Distance = %d cm" % distance_01)
    return distance_01

def ULTRA_SONIC_02():
    global StartTime_02
    global StopTime_02
    global TimeElapsed_02
    global distance_02
    
    
    GPIO.output(GPIO_TRIGGER_02, True)
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_02, False)
        
    while GPIO.input(GPIO_ECHO_02) == 0 :
        StartTime_02 = time.time()
        
    while GPIO.input(GPIO_ECHO_02) == 1 :
        StopTime_02 = time.time()
            
        
    TimeElapsed_02 = StopTime_02 - StartTime_02
    distance_02 = TimeElapsed_02 * 17000 
    # 음파의 속력은 340m/s 우리가 측정하는것은 cm -> 34000 의 속력이며
    # 거리는 시간 * 속력으로 계산한다. 여기서 속력은 초음파 센서가 왕복하기 때문에 나누기 2 를 해준다.
    
    #distance_01 = round(distance_01, 2) # 거리에서 소수점 2번째 자리에서 반올림 해라 라는 문장이다.
    
    #print ("Measured Distance = %d cm" % distance_01)
    return distance_02

def ULTRA_SONIC_03():
    
    global StartTime_03
    global StopTime_03
    global TimeElapsed_03
    global distance_03
    
    GPIO.output(GPIO_TRIGGER_03, True)
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER_03, False)
        
    while GPIO.input(GPIO_ECHO_03) == 0 :
        StartTime_03 = time.time()
        
    while GPIO.input(GPIO_ECHO_03) == 1 :
        StopTime_03 = time.time()
            
        
    TimeElapsed_03 = StopTime_03 - StartTime_03
    distance_03 = TimeElapsed_03 * 17000 
    # 음파의 속력은 340m/s 우리가 측정하는것은 cm -> 34000 의 속력이며
    # 거리는 시간 * 속력으로 계산한다. 여기서 속력은 초음파 센서가 왕복하기 때문에 나누기 2 를 해준다.
    
    #distance_01 = round(distance_01, 2) # 거리에서 소수점 2번째 자리에서 반올림 해라 라는 문장이다.
    
    #print ("Measured Distance = %d cm" % distance_01)
    return distance_03

    def camera_BLUE_cap() : 
        ret, frame = cap.read()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_blue = np.array([90,90,100])
        upper_blue = np.array([150,255,255])
        mask1 = cv2.inRange(hsv,lower_blue,upper_blue)
        res_2 = cv2.bitwise_and(frame, frame , mask=mask1)    
        kernel = np.ones((5,5) , np.uint8)
        
        closing = cv2.morphologyEx(res_2, cv2.MORPH_CLOSE, kernel)
        cv2.imwrite("capture.jpg", closing)
        
    def camera_OCR() :
        a = Image.open('capture.jpg')
        result = pytesseract.image_to_string(a , lang = 'kor')
        #print(result)
        #print("OCR 중입니다.")
        return result

def MOVE_SLOW_BACK() :
    data = "A".encode()
    ser.write(data)

def MOVE_SLOW_FRONT() :
    data = "B".encode()
    ser.write(data)  
    
def MOVE_FAST_BACK() :
    data = "C".encode()
    ser.write(data)       

def MOVE_FAST_FRONT() :            
    data = "D".encode()
    ser.write(data) 
    
def MOVE_STOP() :
    data = "Z".encode()
    ser.write(data) 
        
def MOVE_UP() :
    data = "E".encode()
    ser.write(data) 
    
def MOVE_DOWN() :
    data = "F".encode()
    ser.write(data)     
    

current_state = statement.START

######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################

if __name__ == "__main__" :
 try:  
    while True:
     if current_state == statement.START :
        ZONE = int(input("몇번째 존을 거터로 채우실 것입니까? : [1],[2],[3],[4],[5] 중에 선택해주세요 : "))
        if ZONE < 6 and ZONE > 0 :
            print("확인 되었습니다.")
            MAX_GUTTER = int(input("몇 개의 거터를 채우시겠습니까? : "))
            GUTTER = 0
            #next_state = statement.MOVE_FAST_BACK
            next_state = statement.CAMERA_CAPTURE            
            last_state = next_state
            current_state = next_state

        else : 
            print("오류 입니다. 다시 입력해 주십시오.")
            
            
######################################################################################################################
######################################################################################################################
######################################################################################################################

     if ZONE == 1 :
      while GUTTER <= MAX_GUTTER :
       while GUTTER == 0 :
        current_state = next_state            
        
        if current_state == statement.CAMERA_CAPTURE :
            #print("글자 캡처")
            camera_BLUE_cap()
            last_state = current_state
            next_state = statement.OCR
        
        elif current_state == statement.OCR :
            OCR_DATA = camera_OCR()
            OCR =""
            for i in range(0, len(OCR_DATA)):
                if OCR_DATA[i] == '가' or OCR_DATA[i] == '바' or OCR_DATA[i] == '그' or OCR_DATA[i] == '라' or OCR_DATA[i] =='마' :
                    OCR += OCR_DATA[i]     
            #print(OCR)                 

            if state == 1 : 
             try :         
                if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[3] == '가' :
                    next_state = statement.FIRST_START
                    state = 2
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 2 :
             try :         
                if OCR[0] == '바' or OCR[1] == '바' or OCR[2] == '바' or OCR[4] == '바':
                    next_state = statement.MOVE_FIRST_STOP
                    state = 3
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 3 :
             try :         
                if OCR[0] == '그' or OCR[1] == '그' or OCR[2] == '그' or OCR[3] == '그' :
                    next_state = statement.MOVE_SLOW_BACK
                    state = 4
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass   

            elif state == 4 :
             try :         
                if OCR[0] == '라' or OCR[1] == '라' or OCR[2] == '라' or OCR[3] == '라':
                    next_state = statement.MOVE_SECOND_STOP
                    state = 5

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass

            elif state == 5 :
             try :         
                if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[3] == '마' :
                    next_state = statement.MOVE_SLOW_FRONT
                    state = 6

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass

            elif state == 6 :
             try :         
                if OCR[0] == '바' or OCR[1] == '바' or OCR[2] == '바' or OCR[4] == '바' :
                    next_state = statement.MOVE_FIRST_STOP
                    state = 7

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE        
                pass     
            
        elif current_state == statement.FIRST_START :
            print("시작합니다.")
            MOVE_SLOW_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_FIRST_STOP :
            print("첫번째 스탑")
            MOVE_STOP()
            last_state = current_state
            next_state = statement.MOVE_FIRST_UP
            
        elif current_state == statement.MOVE_FIRST_UP :
            print("5.5초 올리기 시작")
            MOVE_UP()
            last_state = current_state
            next_state = stopwatch.TIME_3sec
        
        elif current_state == stopwatch.TIME_3sec :
            time.sleep(5.5)
            MOVE_STOP()
            print("5.5초 올리기 종료")
            last_state = current_state
            next_state = statement.ON_ULTRA_SONIC_01
            
        elif current_state == statement.ON_ULTRA_SONIC_01 :
            dis = ULTRA_SONIC_01()
            #print(dis)
            if dis <= 4 :
                MOVE_STOP()
                print("거터 인식 완료")
                next_state = statement.MOVE_FIRST_BACK
            elif dis > 4 and dis < 60 :
                MOVE_SLOW_FRONT()
                print("거터 인식 뒤로 가는중")
            elif dis > 60 and dis < 100 :
                MOVE_STOP()
                print("거터 인식 실패")
                
        elif current_state == statement.MOVE_FIRST_BACK :
            MOVE_SLOW_FRONT()
            last_state = current_state 
            next_state = stopwatch.TIME_200msec
            
        elif current_state == stopwatch.TIME_200msec :
            time.sleep(0.1)
            MOVE_STOP()
            next_state = statement.MOVE_SECOND_UP 
                
        elif current_state == statement.MOVE_SECOND_UP :
            print("두번째 올리기 시작")
            MOVE_UP()
            last_state = current_state
            next_state = stopwatch.TIME_9sec
                                   
        elif current_state == stopwatch.TIME_9sec :
            time.sleep(9)
            MOVE_STOP()
            print("올리기 끝")
            next_state = statement.MOVE_FAST_BACK
            
            if state == 7 :
                state = 1
                GUTTER += 1                
        
        elif current_state == statement.MOVE_FAST_BACK :
            print("두번째 출발 시작")
            MOVE_FAST_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SLOW_BACK :
            MOVE_SLOW_BACK()
            print("슬~로~우")
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SECOND_STOP :
            MOVE_STOP()
            print("스탑!")
            last_state = current_state
            next_state = statement.MOVE_DOWN
            
        elif current_state == statement.MOVE_DOWN :
            print("내리기 시작!")
            MOVE_DOWN()
            last_state = current_state
            next_state = stopwatch.TIME_12sec
            
        elif current_state == stopwatch.TIME_12sec :
            time.sleep(15)
            MOVE_STOP()
            print("내리기 종료")
            next_state = statement.MOVE_FAST_FRONT
            
        elif current_state == statement.MOVE_FAST_FRONT :        
            print("뒤로가기 시작")
            MOVE_FAST_FRONT()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
        
        elif current_state == statement.MOVE_SLOW_FRONT :
            MOVE_SLOW_FRONT()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE

######################################################################################################################
######################################################################################################################
######################################################################################################################
            
       while GUTTER > 0 and GUTTER < MAX_GUTTER :
            current_state = next_state   
            
            if current_state == statement.MOVE_FAST_BACK :
                print("다시 시작!")
                MOVE_FAST_BACK()     
                last_state = current_state 
                next_state = statement.ON_ULTRA_SONIC_02_01
                
            elif current_state == statement.ON_ULTRA_SONIC_02_01 :
                dis = ULTRA_SONIC_02()
                if dis <= 40 :
                    print("패스트 인식")
                    next_state = statement.MOVE_SLOW_BACK 
                else :
                    print(dis)
                    
            elif current_state == statement.MOVE_SLOW_BACK :
                MOVE_SLOW_BACK()
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_02_02
            
            elif current_state == statement.ON_ULTRA_SONIC_02_02 :
                dis = ULTRA_SONIC_02()
                if dis <= 4 :
                    print("슬로우 인식 완료")
                    next_state = statement.MOVE_FIRST_STOP
            
            elif current_state == statement.MOVE_FIRST_STOP :
                MOVE_STOP()
                print("멈춰랏!")
                last_state = current_state
                next_state = stopwatch.TIME_100msec
                #next_state = statement.MOVE_DOWN
                
            elif current_state == stopwatch.TIME_100msec :
                MOVE_SLOW_BACK()
                time.sleep(0.2)
                next_state = statement.MOVE_DOWN 
                 
                
            elif current_state == statement.MOVE_DOWN :
                MOVE_STOP()
                print("내려라 내려라")
                MOVE_DOWN()
                last_state = current_state
                next_state = stopwatch.TIME_12sec
                
            elif current_state == stopwatch.TIME_12sec :
                time.sleep(15)
                MOVE_STOP()
                print("내리기 끝")
                next_state = statement.MOVE_FAST_FRONT
                
            elif current_state == statement.MOVE_FAST_FRONT :
                MOVE_FAST_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE 
                
            elif current_state == statement.CAMERA_CAPTURE :
                #print("글자 캡처")
                camera_BLUE_cap()
                last_state = next_state
                next_state = statement.OCR    
                                
            elif current_state == statement.OCR :
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '마' or OCR_DATA[i] == '바' :
                        OCR += OCR_DATA[i]     
                #print(OCR) 

                if state == 1 : 
                    try :         
                        if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[3] == '마' :
                            next_state = statement.MOVE_SLOW_FRONT
                            state = 2
                    except IndexError :
                        print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE                
                elif state == 2 :
                    try :         
                        if OCR[0] == '바' or OCR[1] == '바' or OCR[2] == '바' or OCR[3] == '바' :
                            next_state = statement.MOVE_SECOND_STOP
                            state = 1
                    except IndexError :
                        print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE     
                        
            elif current_state == statement.MOVE_SLOW_FRONT :
                MOVE_SLOW_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE
                
            elif current_state == statement.MOVE_SECOND_STOP :
                MOVE_STOP()
                print("멈춰랏!")
                GUTTER += 1
                print("현 거터 개수 : " , GUTTER)  
                last_state = current_state
                next_state = statement.MOVE_FIRST_UP
                
            elif current_state == statement.MOVE_FIRST_UP :
                print("5.5초 올리기 시작")
                MOVE_UP()
                last_state = current_state
                next_state = stopwatch.TIME_3sec
            
            elif current_state == stopwatch.TIME_3sec :
                time.sleep(5.5)
                MOVE_STOP()
                print("5.5초 올리기 종료")
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_01
                
            elif current_state == statement.ON_ULTRA_SONIC_01 :
                dis = ULTRA_SONIC_01()
                #print(dis)
                if dis <= 4 :
                    MOVE_STOP()
                    #print("거터 인식 완료")
                    next_state = statement.MOVE_FIRST_BACK
                elif dis > 4 and dis < 60 :
                    MOVE_SLOW_FRONT()
                    #print("거터 인식 뒤로 가는중")
                elif dis > 60 and dis < 100 :
                    MOVE_STOP()
                    #print("거터 인식 실패")
                    
            elif current_state == statement.MOVE_FIRST_BACK :
                MOVE_SLOW_FRONT()
                last_state = current_state 
                next_state = stopwatch.TIME_200msec
                
            elif current_state == stopwatch.TIME_200msec :
                time.sleep(0.1)
                MOVE_STOP()
                next_state = statement.MOVE_SECOND_UP 
                    
            elif current_state == statement.MOVE_SECOND_UP :
                print("두번째 올리기 시작")
                MOVE_UP()
                last_state = current_state
                next_state = stopwatch.TIME_9sec
                                    
            elif current_state == stopwatch.TIME_9sec :
                time.sleep(9)
                MOVE_STOP()
                print("올리기 끝")
                next_state = statement.MOVE_FAST_BACK                    

            if GUTTER == MAX_GUTTER :
                next_state = statement.MOVE_SLOW_FRONT  
                print("거터 맥스 같음")

######################################################################################################################
######################################################################################################################
######################################################################################################################

       while GUTTER == MAX_GUTTER :
            current_state = next_state            
            if current_state == statement.MOVE_SLOW_FRONT:
                MOVE_SLOW_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE 
            
           
            elif current_state == statement.CAMERA_CAPTURE :
                print("글자 캡처")
                camera_BLUE_cap()
                last_state = next_state
                next_state = statement.OCR
                
                
            elif current_state == statement.OCR :
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '가' :
                        OCR += OCR_DATA[i]     
                print(OCR) 

                if state == 1 : 
                    try :         
                        if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[3] == '가':
                            next_state = statement.MOVE_FIRST_STOP
                            state = 1
                    except IndexError :
                        print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE 
                        pass
                    
            elif current_state == statement.MOVE_FIRST_STOP :                                     
                MOVE_STOP()
                print("끝났습니다.")
                last_state = current_state
                next_state = statement.START  
                current_state = next_state    
                ZONE = 0
                GUTTER += 1
                state = 1                  
######################################################################################################################
######################################################################################################################
############################################################################################################################################################################################################################################
######################################################################################################################
######################################################################################################################


     if ZONE == 2 :
      while GUTTER <= MAX_GUTTER :
       while GUTTER == 0 :
        current_state = next_state            
        
        if current_state == statement.CAMERA_CAPTURE :
            #print("글자 캡처")
            camera_BLUE_cap()
            last_state = current_state
            next_state = statement.OCR
        
        elif current_state == statement.OCR :
            OCR_DATA = camera_OCR()
            OCR =""
            for i in range(0, len(OCR_DATA)):
                if OCR_DATA[i] == '가' or OCR_DATA[i] == '리' or OCR_DATA[i] == '라' or OCR_DATA[i] =='마' or OCR_DATA[i] =='그':
                    OCR += OCR_DATA[i]     
            #print(OCR)                 

            if state == 1 : 
             try :         
                if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[3] == '가' :
                    next_state = statement.FIRST_START
                    state = 2
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 2 :
             try :         
                if OCR[0] == '그' or OCR[1] == '그' or OCR[2] == '그' or OCR[4] == '그':
                    next_state = statement.MOVE_SLOW_BACK
                    state = 3
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 3 :
             try :         
                if OCR[0] == '라' or OCR[1] == '라' or OCR[2] == '라' or OCR[3] == '라' :
                    time.sleep(1)
                    next_state = statement.MOVE_FIRST_STOP
                    state = 4
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass   

            elif state == 4 :
             try :         
                if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[3] == '마':
                    next_state = statement.MOVE_SLOW_BACK
                    state = 5

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass

            elif state == 5 :
             try :         
                if OCR[0] == '리' or OCR[1] == '리' or OCR[2] == '리' or OCR[3] == '리' :
                    next_state = statement.MOVE_SECOND_STOP
                    state = 6

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass
    
            
        elif current_state == statement.FIRST_START :
            print("2존 시작합니다.")
            MOVE_FAST_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
        
        elif current_state == statement.MOVE_SLOW_BACK :
            MOVE_SLOW_BACK()
            print("슬~로~우")
            last_state = current_state 
            next_state = statement.CAMERA_CAPTURE
                
        elif current_state == statement.MOVE_FIRST_STOP :
            time.sleep(0.2)
            print("첫번째 스탑")
            MOVE_STOP()
            last_state = current_state
            next_state = statement.MOVE_FIRST_UP
            
        elif current_state == statement.MOVE_FIRST_UP :
            print("6초 올리기 시작")
            MOVE_UP()
            last_state = current_state 
            next_state = stopwatch.TIME_3sec

        elif current_state == stopwatch.TIME_3sec :
            time.sleep(6.5)
            MOVE_STOP()
            print("6초 올리기 종료")
            last_state = current_state
            next_state = statement.ON_ULTRA_SONIC_01
            
        elif current_state == statement.ON_ULTRA_SONIC_01 :
            dis = ULTRA_SONIC_01()
            #print(dis)
            if dis <= 4 and dis > 3 :
                MOVE_STOP()
                print("거터 인식 완료")
                next_state = statement.MOVE_FIRST_BACK
            elif dis > 4 :
                MOVE_SLOW_FRONT()
                print("거터 인식 뒤로 가는중")

                                        
        elif current_state == statement.MOVE_FIRST_BACK :
            MOVE_SLOW_FRONT()
            last_state = current_state 
            next_state = stopwatch.TIME_200msec
            
        elif current_state == stopwatch.TIME_200msec :
            time.sleep(0.2)
            MOVE_STOP()
            next_state = statement.MOVE_SECOND_UP 
                
        elif current_state == statement.MOVE_SECOND_UP :
            print("두번째 올리기 시작")
            MOVE_UP()
            last_state = current_state
            next_state = stopwatch.TIME_9sec
                                   
        elif current_state == stopwatch.TIME_9sec :
            time.sleep(9)
            MOVE_STOP()
            print("올리기 끝")
            next_state = statement.MOVE_FAST_BACK
                          
        
        elif current_state == statement.MOVE_FAST_BACK :
            print("두번째 출발 시작")
            MOVE_FAST_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SLOW_BACK :
            MOVE_SLOW_BACK()
            print("슬~로~우")
            last_state = current_state 
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SECOND_STOP :
            MOVE_STOP()
            print("멈춰랏!")
            last_state = current_state
            next_state = statement.MOVE_DOWN

        elif current_state == statement.MOVE_DOWN :
            print("내리기 시작!")
            MOVE_DOWN()
            last_state = current_state
            next_state = stopwatch.TIME_12sec
            
        elif current_state == stopwatch.TIME_12sec :
            time.sleep(16)
            MOVE_STOP()
            print("내리기 종료")
            state = 1
            GUTTER += 1 
            next_state = statement.MOVE_FAST_FRONT
            
######################################################################################################################
######################################################################################################################
######################################################################################################################


       while GUTTER > 0 and GUTTER < MAX_GUTTER :
            current_state = next_state   
            
            if current_state == statement.MOVE_FAST_FRONT :
                print("자자 또 거터 들러 갑니다!")
                MOVE_FAST_FRONT()     
                last_state = current_state 
                next_state = statement.CAMERA_CAPTURE
                
            elif current_state == statement.CAMERA_CAPTURE :
                #print("글자 캡처")
                camera_BLUE_cap()
                last_state = current_state
                next_state = statement.OCR
            
            elif current_state == statement.OCR :   
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '라' or OCR_DATA[i] == '너'  :
                        OCR += OCR_DATA[i]     
                #print(OCR)                 

                if state == 1 : 
                    try :         
                        if OCR[0] == '너' or OCR[1] == '너' or OCR[2] == '너' or OCR[3] == '너' :
                            next_state = statement.MOVE_SLOW_FRONT
                            state = 2
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass

                elif state == 2 :
                    try :         
                        if OCR[0] == '라' or OCR[1] == '라' or OCR[2] == '라' or OCR[4] == '라':
                            next_state = statement.ssttoopp
                            state = 1
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass
            elif current_state == statement.ssttoopp :
                MOVE_STOP()
                print("멈춰랏!")
                last_state = current_state
                next_state = statement.MOVE_FIRST_UP
                    
            elif current_state == statement.MOVE_FIRST_UP :
                print("6초 올리기 시작")
                MOVE_UP()
                last_state = current_state 
                next_state = stopwatch.TIME_3sec

            elif current_state == stopwatch.TIME_3sec :
                time.sleep(6.5)
                MOVE_STOP()
                print("6초 올리기 종료")
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_01            
                    
            elif current_state == statement.MOVE_SLOW_FRONT :
                MOVE_SLOW_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE
                            
            elif current_state == statement.ON_ULTRA_SONIC_01 :
                dis = ULTRA_SONIC_01()
                #print(dis)
                if dis <= 40 :
                    MOVE_STOP()
                    print("거터 인식 1 완료")
                    next_state = statement.ON_ULTRA_SONIC_01_02
                elif dis > 40 :
                    MOVE_FAST_FRONT()
                    print("거터 인식 뒤로 가는중") 
                            
            elif current_state == statement.ON_ULTRA_SONIC_01_02 :
                dis = ULTRA_SONIC_01()
                #print(dis)
                if dis <= 4 and dis > 3 :
                    MOVE_STOP()
                    print("거터 인식 2 완료")
                    next_state = statement.MOVE_FIRST_BACK
                elif dis > 4 and dis < 60 :
                    MOVE_SLOW_FRONT()
                    print("거터 인식 뒤로 가는중")
                elif dis > 60 and dis < 100 :
                    MOVE_STOP()
                    print("거터 인식 실패")  
                    
            elif current_state == statement.MOVE_FIRST_BACK :
                MOVE_SLOW_FRONT()
                last_state = current_state 
                next_state = stopwatch.TIME_200msec
                
            elif current_state == stopwatch.TIME_200msec :
                time.sleep(0.2)
                MOVE_STOP()
                next_state = statement.MOVE_SECOND_UP 
                    
            elif current_state == statement.MOVE_SECOND_UP :
                print("두번째 올리기 시작")
                MOVE_UP()
                last_state = current_state
                next_state = stopwatch.TIME_9sec
                                    
            elif current_state == stopwatch.TIME_9sec :
                time.sleep(9)
                MOVE_STOP()
                print("올리기 끝")
                next_state = statement.MOVE_FAST_BACK
                            
            
            elif current_state == statement.MOVE_FAST_BACK :
                print("두번째 출발 시작")
                MOVE_FAST_BACK()
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_02_01
                
            elif current_state == statement.ON_ULTRA_SONIC_02_01 :
                dis = ULTRA_SONIC_02()
                if dis <= 40 :
                    print("패스트 인식")
                    next_state = statement.MOVE_SLOW_BACK 
                        
            elif current_state == statement.MOVE_SLOW_BACK :
                MOVE_SLOW_BACK()
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_02_02
            
            elif current_state == statement.ON_ULTRA_SONIC_02_02 :
                dis = ULTRA_SONIC_02()
                if dis <= 4 :
                    print("슬로우 인식 완료")
                    next_state = statement.MOVE_FIRST_STOP
                    
            elif current_state == statement.MOVE_FIRST_STOP :
                MOVE_STOP()
                print("멈춰랏!")
                last_state = current_state
                next_state = statement.MOVE_DOWN 
                
            elif current_state == statement.MOVE_DOWN :
                print("내려라 내려라")
                MOVE_DOWN()
                last_state = current_state
                next_state = stopwatch.TIME_12sec

            elif current_state == stopwatch.TIME_12sec :
                time.sleep(16)
                MOVE_STOP()
                print("내리기 종료")
                GUTTER += 1 
                next_state = statement.MOVE_FAST_FRONT          
                
            if GUTTER == MAX_GUTTER :
                print("거터 맥스 같음")

######################################################################################################################
######################################################################################################################
######################################################################################################################

       while GUTTER == MAX_GUTTER :
            current_state = next_state          

            if current_state == statement.MOVE_FAST_FRONT:
                MOVE_FAST_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE 
            
           
            elif current_state == statement.CAMERA_CAPTURE :
                print("글자 캡처")
                camera_BLUE_cap()
                last_state = next_state
                next_state = statement.OCR
    
            elif current_state == statement.OCR :
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '가' or OCR_DATA[i] == '마' :
                        OCR += OCR_DATA[i]     
                #print(OCR)                 

                if state == 1 : 
                    try :         
                        if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[3] == '마' :
                            next_state = statement.MOVE_SLOW_FRONT
                            state = 2
                    except IndexError :
                        print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass

                elif state == 2 :
                    try :         
                        if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[4] == '가':
                            next_state = statement.MOVE_FIRST_STOP
                            state = 3
                    except IndexError :
                        print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass
                    
            elif current_state == statement.MOVE_SLOW_FRONT :
                MOVE_SLOW_FRONT()
                print("슬~로~우")
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE
                
            elif current_state == statement.MOVE_FIRST_STOP :                                     
                MOVE_STOP()
                print("끝났습니다.")
                last_state = current_state
                next_state = statement.START  
                current_state = next_state    
                ZONE = 0
                GUTTER += 1
                state = 1   

######################################################################################################################
######################################################################################################################
######################################################################################################################

     if ZONE == 3 :
      while GUTTER <= MAX_GUTTER :
       while GUTTER == 0 :
        current_state = next_state            
        if current_state == statement.CAMERA_CAPTURE :
            #print("글자 캡처")
            camera_BLUE_cap()
            last_state = current_state
            next_state = statement.OCR
        
        elif current_state == statement.OCR :
            OCR_DATA = camera_OCR()
            OCR =""
            for i in range(0, len(OCR_DATA)):
                if OCR_DATA[i] == '가' or OCR_DATA[i] == '리' or OCR_DATA[i] == '바' or OCR_DATA[i] =='마' :
                    OCR += OCR_DATA[i]     
            #print(OCR)                 

            if state == 1 : 
             try :         
                if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[3] == '가' :
                    next_state = statement.FIRST_START
                    state = 2
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 2 :
             try :         
                if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[4] == '마':
                    next_state = statement.MOVE_SLOW_BACK
                    state = 3
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass

            elif state == 3 :
             try :         
                if OCR[0] == '리' or OCR[1] == '리' or OCR[2] == '리' or OCR[3] == '리' :
                    time.sleep(0.2)
                    next_state = statement.MOVE_FIRST_STOP
                    state = 4
             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE
                pass   

            elif state == 4 :
             try :         
                if OCR[0] == '바' or OCR[1] == '바' or OCR[2] == '바' or OCR[3] == '바':
                    next_state = statement.MOVE_SLOW_BACK
                    state = 5

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass

            elif state == 5 :
             try :         
                if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[3] == '가' :
                    next_state = statement.MOVE_SECOND_STOP
                    state = 6

             except IndexError :
                #print("문자 인식 실패")
                next_state = statement.CAMERA_CAPTURE 
                pass
    
            
        elif current_state == statement.FIRST_START :
            print("3존 시작합니다.")
            MOVE_FAST_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
        
        elif current_state == statement.MOVE_SLOW_BACK :
            MOVE_SLOW_BACK()
            print("슬~로~우")
            last_state = current_state 
            next_state = statement.CAMERA_CAPTURE
                
        elif current_state == statement.MOVE_FIRST_STOP :
            print("첫번째 스탑")
            MOVE_STOP()
            last_state = current_state
            next_state = statement.MOVE_FIRST_UP
            
        elif current_state == statement.MOVE_FIRST_UP :
            print("6초 올리기 시작")
            MOVE_UP()
            last_state = current_state 
            next_state = stopwatch.TIME_3sec

        elif current_state == stopwatch.TIME_3sec :
            time.sleep(6.5)
            MOVE_STOP()
            print("6초 올리기 종료")
            last_state = current_state
            next_state = statement.ON_ULTRA_SONIC_01
            
        elif current_state == statement.ON_ULTRA_SONIC_01 :
            dis = ULTRA_SONIC_01()
            #print(dis)
            if dis <= 4 and dis > 3 :
                MOVE_STOP()
                print("거터 인식 완료")
                next_state = statement.MOVE_FIRST_BACK
            elif dis > 4 :
                MOVE_SLOW_FRONT()
                print("거터 인식 뒤로 가는중")

                                        
        elif current_state == statement.MOVE_FIRST_BACK :
            MOVE_SLOW_FRONT()
            last_state = current_state 
            next_state = stopwatch.TIME_200msec
            
        elif current_state == stopwatch.TIME_200msec :
            time.sleep(0.2)
            MOVE_STOP()
            next_state = statement.MOVE_SECOND_UP 
                
        elif current_state == statement.MOVE_SECOND_UP :
            print("두번째 올리기 시작")
            MOVE_UP()
            last_state = current_state
            next_state = stopwatch.TIME_9sec
                                   
        elif current_state == stopwatch.TIME_9sec :
            time.sleep(9)
            MOVE_STOP()
            print("올리기 끝")
            next_state = statement.MOVE_FAST_BACK
                          
        
        elif current_state == statement.MOVE_FAST_BACK :
            print("두번째 출발 시작")
            MOVE_FAST_BACK()
            last_state = current_state
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SLOW_BACK :
            MOVE_SLOW_BACK()
            print("슬~로~우")
            last_state = current_state 
            next_state = statement.CAMERA_CAPTURE
            
        elif current_state == statement.MOVE_SECOND_STOP :
            MOVE_STOP()
            print("멈춰랏!")
            last_state = current_state
            next_state = statement.MOVE_DOWN

        elif current_state == statement.MOVE_DOWN :
            print("내리기 시작!")
            MOVE_DOWN()
            last_state = current_state
            next_state = stopwatch.TIME_12sec
            
        elif current_state == stopwatch.TIME_12sec :
            time.sleep(16)
            MOVE_STOP()
            print("내리기 종료")
            state = 1
            GUTTER += 1 
            next_state = statement.MOVE_FAST_FRONT
            
######################################################################################################################
######################################################################################################################
######################################################################################################################


       while GUTTER > 0 and GUTTER < MAX_GUTTER :
            current_state = next_state   
            
            if current_state == statement.MOVE_FAST_FRONT :
                print("자자 또 거터 들러 갑니다!")
                MOVE_FAST_FRONT()     
                last_state = current_state 
                next_state = statement.CAMERA_CAPTURE
                
            elif current_state == statement.CAMERA_CAPTURE :
                #print("글자 캡처")
                camera_BLUE_cap()
                last_state = current_state
                next_state = statement.OCR
            
            elif current_state == statement.OCR :
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '라' or OCR_DATA[i] == '리'  :
                        OCR += OCR_DATA[i]     
                #print(OCR)                 

                if state == 1 : 
                    try :         
                        if OCR[0] == '라' or OCR[1] == '라' or OCR[2] == '라' or OCR[3] == '라' :
                            next_state = statement.MOVE_SLOW_FRONT
                            state = 2
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass

                elif state == 2 :
                    try :         
                        if OCR[0] == '리' or OCR[1] == '리' or OCR[2] == '리' or OCR[4] == '리':
                            next_state = statement.ssttoopp
                            state = 1
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass
            elif current_state == statement.ssttoopp :
                MOVE_STOP()
                print("멈춰랏!")
                last_state = current_state
                next_state = statement.MOVE_FIRST_UP
                    
            elif current_state == statement.MOVE_FIRST_UP :
                print("6초 올리기 시작")
                MOVE_UP()
                last_state = current_state 
                next_state = stopwatch.TIME_3sec

            elif current_state == stopwatch.TIME_3sec :
                time.sleep(6.5)
                MOVE_STOP()
                print("6초 올리기 종료")
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_01            
                    
            elif current_state == statement.MOVE_SLOW_FRONT :
                MOVE_SLOW_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE
                            
            elif current_state == statement.ON_ULTRA_SONIC_01 :
                dis = ULTRA_SONIC_01()
                #print(dis)
                if dis <= 40 :
                    MOVE_STOP()
                    print("거터 인식 1 완료")
                    next_state = statement.ON_ULTRA_SONIC_01_02

            elif current_state == statement.ON_ULTRA_SONIC_01_02 :
                dis = ULTRA_SONIC_01()
                #print(dis)
                if dis <= 4 and dis > 3 :
                    MOVE_STOP()
                    print("거터 인식 2 완료")
                    next_state = statement.MOVE_FIRST_BACK
                elif dis > 4 and dis < 60 :
                    MOVE_SLOW_FRONT()
                    print("거터 인식 뒤로 가는중")
                elif dis > 60 and dis < 100 :
                    MOVE_STOP()
                    print("거터 인식 실패")  
                    
            elif current_state == statement.MOVE_FIRST_BACK :
                MOVE_SLOW_FRONT()
                last_state = current_state 
                next_state = stopwatch.TIME_200msec
                
            elif current_state == stopwatch.TIME_200msec :
                time.sleep(0.2)
                MOVE_STOP()
                next_state = statement.MOVE_SECOND_UP 
                    
            elif current_state == statement.MOVE_SECOND_UP :
                print("두번째 올리기 시작")
                MOVE_UP()
                last_state = current_state
                next_state = stopwatch.TIME_9sec
                                    
            elif current_state == stopwatch.TIME_9sec :
                time.sleep(9)
                MOVE_STOP()
                print("올리기 끝")
                next_state = statement.MOVE_FAST_BACK
                            
            
            elif current_state == statement.MOVE_FAST_BACK :
                print("두번째 출발 시작")
                MOVE_FAST_BACK()
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_02_01
                
            elif current_state == statement.ON_ULTRA_SONIC_02_01 :
                dis = ULTRA_SONIC_02()
                if dis <= 45 :
                    print("패스트 인식")
                    next_state = statement.MOVE_SLOW_BACK 
                elif dis > 35 :
                    print("인식 중")
                    
            elif current_state == statement.MOVE_SLOW_BACK :
                MOVE_SLOW_BACK()
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_02_02
            
            elif current_state == statement.ON_ULTRA_SONIC_02_02 :
                dis = ULTRA_SONIC_02()
                if dis <= 7.1 :
                    print("슬로우 인식 완료")
                    next_state = statement.MOVE_FIRST_STOP
                elif dis > 7.1 :
                    print("인식 중")

            elif current_state == statement.MOVE_FIRST_STOP :
                MOVE_STOP()
                print("멈춰랏!")
                last_state = current_state
                next_state = statement.ON_ULTRA_SONIC_03_01
                
            elif current_state == statement.ON_ULTRA_SONIC_03_01 :
                dis = ULTRA_SONIC_03()
                if dis <= 10 :
                    MOVE_STOP()
                    print("슬로우 인식 완료")
                    next_state = statement.MOVE_DOWN
                elif dis > 10 :
                    #print("인식 중")            
                    MOVE_SLOW_BACK()
                    
            elif current_state == statement.MOVE_DOWN :
                print("내려라 내려라")
                MOVE_DOWN()
                last_state = current_state
                next_state = stopwatch.TIME_12sec

            elif current_state == stopwatch.TIME_12sec :
                time.sleep(16)
                MOVE_STOP()
                print("내리기 종료")
                GUTTER += 1 
                next_state = statement.MOVE_FAST_FRONT          
                
            if GUTTER == MAX_GUTTER :
                print("거터 맥스 같음")

######################################################################################################################
######################################################################################################################
######################################################################################################################

       while GUTTER == MAX_GUTTER :
            current_state = next_state          

            if current_state == statement.MOVE_FAST_FRONT:
                MOVE_FAST_FRONT()
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE 
            
           
            elif current_state == statement.CAMERA_CAPTURE :
                print("글자 캡처")
                camera_BLUE_cap()
                last_state = next_state
                next_state = statement.OCR
    
            elif current_state == statement.OCR :
                OCR_DATA = camera_OCR()
                OCR =""
                for i in range(0, len(OCR_DATA)):
                    if OCR_DATA[i] == '가' or OCR_DATA[i] == '마' or OCR_DATA[i] == '라'  :
                        OCR += OCR_DATA[i]     
                #print(OCR)                 
                if state == 1 :
                    try :         
                        if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[3] == '마' :
                            next_state = statement.CAMERA_CAPTURE
                            state = 2
                            time.sleep(5)
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass
                                        
                elif state == 2 : 
                    try :         
                        if OCR[0] == '라' or OCR[1] == '라' or OCR[2] == '라' or OCR[3] == '라' :
                            next_state = statement.CAMERA_CAPTURE
                            state = 3
                            time.sleep(5)
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass

                elif state == 3 :
                    try :         
                        if OCR[0] == '마' or OCR[1] == '마' or OCR[2] == '마' or OCR[4] == '마':
                            next_state = statement.MOVE_SLOW_FRONT
                            state = 4
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass

                elif state == 4 :
                    try :         
                        if OCR[0] == '가' or OCR[1] == '가' or OCR[2] == '가' or OCR[4] == '가':
                            next_state = statement.MOVE_FIRST_STOP
                            state = 4
                    except IndexError :
                        #print("문자 인식 실패")
                        next_state = statement.CAMERA_CAPTURE
                        pass
                
            elif current_state == statement.MOVE_SLOW_FRONT :
                MOVE_SLOW_FRONT()
                print("슬~로~우")
                last_state = current_state
                next_state = statement.CAMERA_CAPTURE
                
            elif current_state == statement.MOVE_FIRST_STOP :                                     
                MOVE_STOP()
                print("끝났습니다.")
                last_state = current_state
                next_state = statement.START  
                current_state = next_state    
                ZONE = 0
                GUTTER += 1
                state = 1   
                                                            
 except KeyboardInterrupt :
        print("강제 종료")
        MOVE_STOP()
        GPIO.cleanup()        
        
 except UnboundLocalError :
        print("현 거터 개수 : " , GUTTER)  
        MOVE_STOP()
        GPIO.cleanup()
        