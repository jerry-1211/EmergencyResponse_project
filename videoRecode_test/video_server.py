# -*- encoding: utf-8 -*-
#-------------------------------------------------#
# Date created          : 2020. 8. 18.
# Date last modified    : 2020. 8. 19.
# Author                : chamadams@gmail.com
# Site                  : http://wandlab.com
# License               : GNU General Public License(GPL) 2.0
# Version               : 0.1.0
# Python Version        : 3.6+
#-------------------------------------------------#

from flask import Flask
from flask import request
from flask import Response
from flask import stream_with_context,render_template
from flask import Flask, jsonify

import time
import cv2
from vider_streamer import Streamer
from firebase_recode import DBModule
import datetime
import os



app = Flask( __name__ )
streamer = Streamer()
firebase_recode = DBModule()

@app.route("/")
def index():    
    return render_template("index.html")
    
#-------------------firebase storage -------------------
@app.route('/video-urls', methods=['GET'])
def video_urls():
    urls = firebase_recode.video_get()
    print(urls)
    return jsonify(urls)


#-------------------video recode -------------------

@app.route('/stream')
def stream():
    src = request.args.get( 'src', default = 0, type = int )
    try : 
        return Response(
            stream_with_context( stream_gen( src ) ),
            mimetype='multipart/x-mixed-replace; boundary=frame' )

    except Exception as e :
        print('[wandlab] ', 'stream error : ',str(e))


def stream_gen( src ):   
    try :
        
        # 비디오 녹화와 종류를 위한 변수
        start_time = time.time()  
        recording = True

        with streamer:  # context manager를 통해 __enter__ / __exit__  구현
            out = streamer.get_filename()
            streamer.run(src)
     
        while True :
           
            frame_byte,frame = streamer.bytescode()

            # if 응급상황 : recording = True / out = streamer.get_filename()

            if recording:  # 비디오 저장 (여기 recording에 조건 걸기)
                out.write(frame)
                if time.time() - start_time > 10:
                    print(f"녹화완료")
                    recording = False
          
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n')
                    
    except GeneratorExit :
        streamer.stop()


if __name__ == "__main__":
    app.run(port=1500,host="0.0.0.0",debug=True)