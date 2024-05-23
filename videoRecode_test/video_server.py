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
from flask import stream_with_context

import time
import cv2
from vider_streamer import Streamer
import datetime
import os



app = Flask( __name__ )
streamer = Streamer()

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

        # 비디오 녹화 컨트롤
        start_time = time.time() 
        recording = True

        def create_new_video_writer():
            dt_now = datetime.datetime.now()
            dt_str = dt_now.strftime("%Y-%m-%d_%H시%M분%S초~")
            file_name = str(dt_str)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(f"{file_name}.avi", fourcc, 20.0, (640, 480))
            return out
        out = create_new_video_writer()

        streamer.run( src )
     
        while True :
           
            frame_byte,frame = streamer.bytescode()

            # if 응급상황 : recording = True / fourcc = cv2.VideoWriter_fourcc(*'XVID') / out = create_new_video_writer()

            if recording:  # 비디오 저장 (여기 recording에 조건 걸기)
                out.write(frame)
                if time.time() - start_time > 10:
                    print(f"녹화완료")
                    recording = False
          
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_byte + b'\r\n')
                    
    except GeneratorExit :
        #print( '[wandlab]', 'disconnected stream' )
        streamer.stop()


if __name__ == "__main__":
    app.run(port=1500,host="0.0.0.0",debug=True)