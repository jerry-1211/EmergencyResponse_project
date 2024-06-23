import firebase_admin
from firebase_admin import credentials, storage,db
import pyrebase
import json
from datetime import datetime, timedelta
import os
import shutil
import pandas as pd

class DBModule : 
    def __init__(self):
        with open("./auth/firebaseAuth.json") as f :
            config = json.load(f)     
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

#----------------------------- 로그인 ------------------------------

    def signin(self,name,_id_,pwd,phoneNumber,guardian_phoneNumber):
        informations = {
            "uname" : name,
            "pwd" : pwd,
            "phoneNumber" : phoneNumber,
            "guardian_phoneNumber" : guardian_phoneNumber
        } 
        if self.signin_verification(_id_):
            self.db.child("users").child(_id_).set(informations)
            return True
        else :
            return False
        
    def signin_verification(self,uid):
        users = self.db.child("users").get().val()
        for i in users:
            if uid == i :
                return False
        return True

    def login(self,uid,pwd):
            users = self.db.child("users").get().val()
            try : 
                userinfo = users[uid]
                if userinfo["pwd"] == pwd :
                    return True
                else :
                    return False 
            except :
                return False
#-----------------------------------------------------------------------
    def get_info(self,user):
        users_info = self.db.child("users").child(user).get().val()
        name = users_info["uname"]
        g_ph = users_info["guardian_phoneNumber"]
        return name,g_ph

#----------------------- emergency 데이터 관리 --------------------------

    # 생성한  emergency 데이터들 firebase에 저장
    def put_emergencyData(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("./auth/serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://emergencyresponse-b8c54-default-rtdb.firebaseio.com/'  # Firebase Realtime Database URL
                })
            
        # CSV 파일을 읽어 데이터프레임으로 변환
        csv_file_path = "EmergencyData/emergency_data.csv"
        data = pd.read_csv(csv_file_path)

        # 데이터를 딕셔너리로 변환
        data_dict = data.to_dict(orient="records")  # 각 행이 하나의 딕셔너리가 되도록 변환

        # emergency_data 참조 후 저장 
        ref = db.reference("/emergency_data")
        ref.set(data_dict)

        print("Firebase 업로드 완료")
        return 0


    # 드롭다운에서 전달 받은 값들 호출    
    def emergencyData(self,city,district):

        list_names = [
            'address', 'hospital', 'tel', 'hospital_link', 'hvamyn',
            'hvec', 'hvgc', 'hvmriayn', 'hvoc', 'hvventiayn'
        ]

        # 사전(dictionary)을 사용하여 빈 리스트를 생성
        lists = {name: [] for name in list_names}

        # 개별 리스트에 접근할 때는 다음과 같이 사용
        address = lists['address']
        hospital = lists['hospital']
        tel = lists['tel']
        hospital_link = lists['hospital_link']
        hvamyn = lists['hvamyn']
        hvec = lists['hvec']
        hvgc = lists['hvgc']
        hvmriayn = lists['hvmriayn']
        hvoc = lists['hvoc']
        hvventiayn = lists['hvventiayn']

        emergency_data = self.db.child("emergency_data").get().val()
        for data in emergency_data:
            if data["city"] == city and data["district"] == district:
                address.append(data["address"])
                hospital.append(data["dutyName"])
                tel.append(data["dutyTel3"])
                hospital_link.append(data["hospital_link"])
                hvamyn.append(data["hvamyn"])
                hvec.append(data["hvec"])
                hvgc.append(data["hvgc"])
                hvmriayn.append(data["hvmriayn"])
                hvoc.append(data["hvoc"])
                hvventiayn.append(data["hvventiayn"])
        return lists             

class Storage :
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("./auth/serviceAccountKey.json")
            firebase_admin.initialize_app(cred, {
              'storageBucket': 'emergencyresponse-b8c54.appspot.com',
              'databaseURL': 'https://emergencyresponse-b8c54-default-rtdb.firebaseio.com/'  # Firebase Realtime Database URL
            })
        
        with open("./auth/firebaseAuth.json") as f:
            config = json.load(f)
        self.firebase = pyrebase.initialize_app(config)
        self.storage = self.firebase.storage()

    def video_save(self,user,filename) :
        self.storage.child(f"Video/recode/{user}/{filename}.mp4").put(f"videoRecode_tmp/{filename}.mp4",f"{user}")
        print(f"{filename} {user}님 DB 저장")
        return 0

    # 로컬 녹화본 삭제    
    def delete_all_files_in_directory(self,directory="./videoRecode_tmp"):
        if os.path.exists(directory) and os.path.isdir(directory):
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f"{file_path} 파일이 삭제되었습니다.")
                except Exception:
                    pass
        return 0


    def video_getUrl(self,uid):
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=f"Video/recode/{uid}/")         
        urls = []
        filenames = []
        for blob in blobs:
            filename = os.path.basename(blob.name)
            if filename and '.' in filename:  # 파일 이름이 의미 있는 경우에만 처리
                url = blob.generate_signed_url(timedelta(seconds=300))  # URL 생성
                urls.append(url)
                filenames.append(filename)
        return urls,filenames

# db = DBModule()
# db.get_info("jihyun")

