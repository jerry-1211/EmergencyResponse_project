import pandas as pd
import time
import datetime
import os
import cv2
import numpy as np


from flask import Flask,redirect,render_template,url_for,jsonify
from flask import request,flash,session,abort
from flask import Response, stream_with_context

from DB_handler import DBModule,Storage

import warnings
from ultralytics import YOLO

from streamer import Streamer

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.secret_key = "xcvbsdf@sdfvxcv"  # 아무렇게나 생성
model = YOLO('best.pt') # yolo model 
streamer = Streamer()
DB = DBModule()
Storage = Storage()

page_move = False  # detect에서 board로 이동
detected_status = False # 상태 감지
#------------------------------ 함수  ------------------------------
def stream_gen( src ):   
    global page_move,detected_status
    page_move = False
    detected_status = False
    
    try :
        user = get_user()

       # 비디오 녹화와 종류를 위한 변수
        initial_start_time = time.time()  
        last_prediction_time = 0
        fall_down_cnt = 0

        out,filename = streamer.get_filename()
        streamer.run(src)
    
        while True :
            current_time = time.time()
            frame_byte,frame = streamer.bytescode()
            
            # 3초마다 이미지를 처리
            if current_time - last_prediction_time >= 3:
                last_prediction_time = current_time

                # YOLO 모델에 넣기 전에 이미지를 resize
                resized_image = cv2.resize(frame, (640, 640))
                results = model(resized_image)

                # 예측 결과에 대한 처리
                detected = False
                for result in results:
                    for box in result.boxes:
                        cls_id = int(box.cls)
                        cls_name = model.names[cls_id]
                        confidence = box.conf  # 객체의 확률 (신뢰도 점수)
                        if cls_name == 'fall_down':  # 관심 객체 클래스 이름
                            detected = True
                            detected_status = True
                            print(f'Class: {cls_name}, Confidence: {confidence}')
                            
                if not detected:
                    detected_status = False

            # 비디오 저장
            if detected: 
                out.write(frame)
                fall_down_cnt += 1
                print(fall_down_cnt)
                if fall_down_cnt  > 1000:
                    print(f"{filename} {user}님 녹화완료")
                    out.release()
                    Storage.video_save(user=user,filename=filename)  # 녹화본 DB에 저장
                    Storage.delete_all_files_in_directory() # 로컬 녹화본에 삭제
                    page_move = True
                    streamer.stop()
                    break  # Stop streaming after setting page_move

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n') 
                    
    except GeneratorExit :
        streamer.stop()


# 로그인이 되지 않았을 경우 로그인 창으로 전환
def get_user():
    if "uid" in session:
        return session["uid"]
    else:
        return redirect(url_for("login"))
    
    
# 하루 최대 한번 Board판 업데이트    
def should_run_folium_map():
    if not os.path.exists("last_run_date.txt"):
        return True

    with open("last_run_date.txt", "r") as file:
        last_run_date = file.read().strip()

    last_run_date = datetime.datetime.strptime(last_run_date, "%Y-%m-%d").date()
    current_date = datetime.datetime.now().date()

    return current_date > last_run_date

#-----------------------------------------------------------------------

@app.route("/")
def index():

    user = get_user()
    if isinstance(user, str): 
        return render_template("index.html", user=user)
    return user  

#------------------------------회원 가입 ------------------------------
@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/signin_done",methods=["GET"])
def signin_done():
    name = request.args.get("signin_name")
    uid = request.args.get("signin_id")
    pwd = request.args.get("signin_pwd")
    phoneNumber = request.args.get("signin_phoneNumber")
    if DB.signin(name=name,_id_=uid,pwd=pwd,phoneNumber=phoneNumber):
         return redirect(url_for("index"))
    else :
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for("signin"))
    
@app.route("/login")
def login():
    if "uid" in session : 
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/login_done",methods=["GET"])
def login_done():
    uid = request.args.get("signin_id")
    pwd = request.args.get("signin_pwd")
    if DB.login(uid,pwd) :
        session["uid"] = uid 
        return redirect(url_for("index"))
    else : 
        flash("아이디가 없거나 비밀번호가 틀립니다.")
        return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
   if "uid" in session :
        session.pop("uid")
        return redirect(url_for("index"))
   else :
       return redirect(url_for("login"))

#-----------------------------------------------------------------------

#------------------------------비디오 녹화 ------------------------------
@app.route("/stream")
def stream():
    global page_move
    page_move = False 
    src = request.args.get( 'src', default = 0, type = int )
    try :    
        return Response(
            stream_with_context( stream_gen( src ) ),
            mimetype='multipart/x-mixed-replace; boundary=frame' )
    except Exception as e :
        pass

@app.route("/detect")
def detect():
    user = get_user()
    if isinstance(user, str): 
        return render_template("detect.html",user=user)
    return user  

# board로 페이지 이동
@app.route("/check_page_move")
def check_page_move():
    global page_move
    return jsonify({"page_move": page_move})

# 상태 전달
@app.route("/check_detected_status")
def check_detected_status():
    global detected_status
    return jsonify({"detected": detected_status})

#-----------------------------------------------------------------------
#------------------------------응급 상황판 ------------------------------

@app.route("/board", methods=['GET', 'POST'])
def board():
    
    if should_run_folium_map():
        os.system("python EmergencyDataCode/Folium_map.py")
        DB.put_emergencyData()  # emergency 데이터 저장
    else:
        print("Folium map 업데이트 이미 완료하였습니다.")

    user = get_user()
    city = ''
    if isinstance(user, str):
        if request.method == 'POST':
            city = request.form.get('city')
            district = request.form.get('district')
            emergency_data = DB.emergencyData(city, district)
            print(emergency_data)
            return jsonify({
                "user": user,
                "city": city,
                "district": district,
                "info_address": emergency_data["address"],
                "info_hospital": emergency_data["hospital"],
                "info_tel": emergency_data["tel"],
                "info_hospital_link": emergency_data["hospital_link"],                
                "info_hvamyn": emergency_data["hvamyn"],
                "info_hvec": emergency_data["hvec"],
                "info_hvgc": emergency_data["hvgc"],
                "info_hvmriayn": emergency_data["hvmriayn"],
                "info_hvoc": emergency_data["hvoc"],
                "info_hvventiayn": emergency_data["hvventiayn"],
            })
        else:
            return render_template("board.html", user=user, city=None, district=None,
                info_address=None, info_hospital=None,info_tel=None, info_hospital_link=None, 
                info_hvamyn=None ,info_hvec=None ,info_hvgc=None , info_hvmriayn=None ,info_hvoc=None , info_hvventiayn=None)
    return user

        
@app.route("/Emergencymap")
def Emergencymap():
    return render_template("map.html")

#-----------------------------------------------------------------------
#----------------------------- 비디오 기록 ------------------------------

@app.route('/video-urls/<string:uid>', methods=['GET'])
def video_urls(uid):
    urls,filenames = Storage.video_getUrl(uid)
    return jsonify(urls,filenames)


@app.route('/user_uid', methods=['GET'])
def user_uid():
    user = get_user()
    if isinstance(user, str) and "uid" in session:
        return jsonify(session["uid"])
    return jsonify({"error": "Unauthorized"}), 403


# uid까지 가져옴
@app.route("/videolist/<string:uid>")
def video_list(uid):
    # 세션의 uid와 요청된 uid를 비교하여 일치하지 않으면 403 오류 반환
    if "uid" not in session or session["uid"] != uid:
        abort(403, description="Unauthorized access")

    return render_template("videorecode.html", uid=uid)
#-----------------------------------------------------------------------

if __name__ == "__main__":
    app.run(port=5501,host="0.0.0.0",debug=True)