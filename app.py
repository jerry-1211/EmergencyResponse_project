from flask import Flask,redirect,render_template,url_for
from flask import request,flash,session
from DB_handler import DBModule

app = Flask(__name__)
app.secret_key = "xcvbsdf@sdfvxcv"  # 아무렇게나 생성
DB = DBModule()

@app.route("/")
def index():
   
    return render_template("index.html")

@app.route("/signin")
def signin():
   
    return render_template("signin.html")



if __name__ == "__main__":
    app.run(port=5500,host="0.0.0.0",debug=True)