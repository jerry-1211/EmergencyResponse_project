import time
import cv2
import imutils
import platform
import numpy as np
from threading import Thread
from queue import Queue

class Streamer :
    
    def __init__(self ):

        #(OpenCl 지원 유무 확인)
        if cv2.ocl.haveOpenCL() :  # GPU 가속 활성화 
            cv2.ocl.setUseOpenCL(True) # 지원되면 활성화 
        print( 'OpenCL : ', cv2.ocl.haveOpenCL())
            
        self.capture = None
        self.thread = None
        self.width = 640
        self.height = 360
        self.stat = True
        self.current_time = time.time() # 현재 시간 계산
        self.preview_time = time.time()
        self.sec = 0
        self.Q = Queue(maxsize=128)  # 최대 비디오 프레임 저장 크기 (설정 안하면 무제한 요소 저장)
        self.started = False
        
    def run(self, src = 0 ) :
        
        self.stop()  # 이전 실행 중인 비디오 스트리밍 작업 중단
    
        if platform.system() == 'Windows' :        
            self.capture = cv2.VideoCapture( src , cv2.CAP_DSHOW ) 
            # src는  카메라 장치 번호 (0,1,2)
            # DirectShowAPI 사용(윈도우만 가능)        
        
        else :
            self.capture = cv2.VideoCapture( src )
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)  #가로 값 설정
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height) #세로 값 설정
        
        if self.thread is None :
            self.thread = Thread(target=self.update, args=()) # 스레드 객체 생성
            self.thread.daemon = False # 데몬 스레드 (메인 프로그램 종료되면 자동 종료)
            self.thread.start() # 생성된 스레드 시작
        
        self.started = True
    
    def stop(self):
        
        self.started = False
        
        if self.capture is not None :
            
            self.capture.release()  # 비디오 캡처 중지 및 연결 종료
            self.clear() # self.Q의 내용을 제거
            
    def update(self):
                    
        while True:
            if self.started :  # 비디오 스트리밍 시작될때 
                (grabbed, frame) = self.capture.read()  
                # grabbed는 프레임 캡처 여부(True or False)
                # frame은 실제 프레임 데이터 

                if grabbed :  # 프레임 캡처 성공 시
                    self.Q.put(frame) # frame을 Q에 저장
                          
    def clear(self):
        
        with self.Q.mutex:  # mutex는 여러 스레드 동시 접근 못하도록 보호
            self.Q.queue.clear() # 큐 객체의 내부 리스크 queue 비움
            
    def read(self):

        return self.Q.get()  # 큐에서 가장 오래된 요소를 반환
    
    def blank(self):
        
        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8) # (높이,너비,채널)
    
    def bytescode(self):
        
        if not self.capture.isOpened():  # 카메라가 열려있지 않은 경우
            
            frame = self.blank() # 매서드를 호출하여 빈 이미지 생성 (카메라 작동 않을 때 디폴트 값)

        else :
            # read 함수를 호출하여 큐에서 frame을 가져옴
            # 이후 프레임의 크기를 지정된 너비에 맞게 조정 
            # imutils.resize()는 이미지 크기를 조정하는 함수
            frame = imutils.resize(self.read(), width=int(self.width) )
            if self.stat :  
                # cv2.rectangle( frame, (0,0), (120,30), (0,0,0), -1) # 좌상단 영역
                fps = 'FPS : ' + str(self.fps())

                # cv2.putText  ( frame, fps, (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
                # 생성된 FPS 문자열을 화면 좌상단에 텍스트 추가            
        
        return cv2.imencode('.jpg', frame )[1].tobytes()
        #JPEG 형식으로 인코딩하고, 이미지를 바이트 코드로 반환
        # cv2.imencode('확장자', 이미지 데이터)
        # cv2.imencode()은 튜플로 반환되고 [0]은 성공여부, [1]은 인코딩 데이터 반환
        # .tobytes()를 사용해서 바이트 데이터로 반환

    def fps(self):
        
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        
        if self.sec > 0 :
            fps = round(1/(self.sec),1)
            
        else :
            fps = 1
            
        return fps
                   
    def __exit__(self) :
        print( '* streamer class exit')
        self.capture.release()