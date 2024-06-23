import cv2
import mediapipe as mp
import math
from datetime import datetime, timedelta
from DB_handler import DBModule
from sms import SMS

DB = DBModule()
ms = SMS()

class FallDetection:
    def __init__(self,user):
        self.user = user

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils

        self.falling_time = None
        self.lying_time = None
        self.falling_state = False
        self.lying_state = False

        self.emergency_detected = False
        self.detected_status = "normal" # 상태 초기화

    def calculate_angle(self, a, b, c):
        ang = math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0]))
        return abs(ang)

    def process_frame(self, frame):
        global detected_status
        
        # 메세지 보내는거는 한번만
        emergency_message = True     
        urgent_message = True

        frame = cv2.resize(frame, (640, 480))

        # Mediapipe는 RGB 이미지를 사용하므로 BGR에서 RGB로 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 포즈 추정 수행
        result = self.pose.process(rgb_frame)

        # 랜드마크를 화면에 그리기
        if result.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                result.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2)
            )

            landmarks = result.pose_landmarks.landmark
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]


            # 어깨와 엉덩이의 중심 계산
            shoulder_center = [(left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2]
            hip_center = [(left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2]

            # 어깨-엉덩이 선의 각도 계산
            angle = self.calculate_angle(left_shoulder, hip_center, right_shoulder)
            shoulder_hip_diff = abs(shoulder_center[1] - hip_center[1])

            if not self.emergency_detected :
                # 넘어진 감지
                if angle > 45:
                    cv2.putText(frame, 'Fall Detected', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    self.detected_status = "alert"  # 상태 업데이트
                    if self.falling_time is None:
                        self.falling_time = datetime.now()
                    elif (datetime.now() - self.falling_time).total_seconds() > 0.2:
                        self.falling_state = True

                # 누워 있는 상태 감지
                if shoulder_hip_diff < 0.1:
                    cv2.putText(frame, 'Lying Detected', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    if self.lying_time is None:
                        self.lying_time = datetime.now()
                    elif (datetime.now() - self.lying_time).total_seconds() > 0.4:
                        self.lying_state = True

            # print(shoulder_hip_diff)

            # 응급상황 감지
            if self.falling_state and self.lying_state and not self.emergency_detected:
                print("--------------------------------")
                print("응급상황")
                print(self.user)
                print(emergency_message)
                print("--------------------------------")
                cv2.putText(frame, 'Emergency Detected', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                self.emergency_detected = True
                self.detected_status = "emergency"  # 상태 업데이트
                if emergency_message : 
                    name,g_ph = DB.get_info(self.user)
                    print(name,g_ph)
                    ms.send_emergency(name,g_ph)
                    emergency_message = False 

            if not (self.detected_status == "emergency"):
                # 3초 후 상태 초기화 
                if self.falling_time and (datetime.now() - self.falling_time).total_seconds() > 4:
                    self.falling_state = False
                    self.falling_time = None
                    self.detected_status = "normal"
                    print("falling_state False")

                if self.lying_time and (datetime.now() - self.lying_time).total_seconds() > 4:
                    self.lying_state = False
                    self.lying_time = None
                    print("lying_state False")
                    self.emergency_detected = False

                
            else :
                # emergency 상태에서 바로 일어나지 못하는 경우
                if (datetime.now() - self.lying_time).total_seconds() > 6:
                    if shoulder_hip_diff < 0.4:
                        self.detected_status = "urgent" 
                        name,g_ph = DB.get_info(self.user)
                        ms.send_urgent(name,g_ph)
                    else : 
                        self.detected_status = "normal"
                        emergency_message = True


        return frame
    


