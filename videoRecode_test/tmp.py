import cv2
import numpy as np
# 비디오 파일 이름 설정
file_name = 'test_output'  # 원하는 파일 이름으로 변경

# 코덱과 비디오 파일 생성 객체 설정
fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 또는 'X264', 'H264'
out = cv2.VideoWriter(f"{file_name}.mp4", fourcc, 20.0, (640, 480))

# 흰색 배경의 비디오 프레임 생성
for i in range(100):  # 100 프레임 생성
    frame = 255 * np.ones((480, 640, 3), np.uint8)  # 흰색 배경
    out.write(frame)

# 모든 자원 해제
out.release()
cv2.destroyAllWindows()