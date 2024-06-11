import pandas as pd
import time
import datetime
import os

from flask import Flask,redirect,render_template,url_for,jsonify
from flask import request,flash,session,abort
from flask import Response, stream_with_context

from DB_handler import DBModule,Storage

import warnings

from streamer import Streamer

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.secret_key = "xcvbsdf@sdfvxcv"  # 아무렇게나 생성
streamer = Streamer()
DB = DBModule()
Storage = Storage()

#------------------------------ 함수  ------------------------------
def stream_gen( src ):   
    try :
        user = get_user()
        # 비디오 녹화와 종류를 위한 변수
        start_time = time.time()  
        recording = True

        out,filename = streamer.get_filename()
        streamer.run(src)
    
        while True :
            frame_byte,frame = streamer.bytescode()
            # if 응급상황 : recording = True / out = streamer.get_filename()

            if recording:  # 비디오 저장 (여기 recording에 조건 걸기)
                out.write(frame)
                if time.time() - start_time > 10:
                    print(f"{filename} {user}님 녹화완료")
                    recording = False
                    out.release()
                    Storage.video_save(user=user,filename=filename)  # 녹화본 DB에 저장
                    Storage.delete_all_files_in_directory() # 로컬 녹화본에 삭제

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n')
                    
    except GeneratorExit :
        streamer.stop()
        if recording:
            out.release()


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
            info_address, info_hospital = DB.emergencyData(city, district)
            return jsonify({
                "user": user,
                "city": city,
                "district": district,
                "info_address": info_address,
                "info_hospital": info_hospital
            })
        else:
            return render_template("board.html", user=user, city=None, district=None,
                            info_address=None, info_hospital=None)
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