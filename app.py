from flask import Flask,redirect,render_template,url_for
from flask import request,flash,session
from flask import Response, stream_with_context

from DB_handler import DBModule

import warnings

from streamer import Streamer

warnings.filterwarnings("ignore")


app = Flask(__name__)
app.secret_key = "xcvbsdf@sdfvxcv"  # 아무렇게나 생성
streamer = Streamer()
DB = DBModule()


def stream_gen( src ):   
    try :         
        streamer.run( src )
        
        while True :  
            frame = streamer.bytescode()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    
    except GeneratorExit :
        streamer.stop()

@app.route("/")
def index():    
    if "uid" in session : 
        user = session["uid"]
    else :
        user = "Login"
        return redirect(url_for("login"))
    return render_template("index.html",user=user)

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
    user = session["uid"]
    return render_template("detect.html",user=user)


@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == "__main__":
    app.run(port=5500,host="0.0.0.0",debug=True)