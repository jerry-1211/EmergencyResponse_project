import firebase_admin
from firebase_admin import credentials, storage
import pyrebase
import json
from datetime import datetime, timedelta
import os
import shutil

class DBModule : 
    def __init__(self):
        with open("./auth/firebaseAuth.json") as f :
            config = json.load(f)     
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def signin(self,name,_id_,pwd,phoneNumber):
        informations = {
            "uname" : name,
            "pwd" : pwd,
            "phoneNumber" : phoneNumber
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
            

    # 드롭다운에서 전달 받은 값들 호출
    def region(self,city,district):
        regions = self.db.child("region").get().val()
        address = []
        hospital = []
        
        for reg in regions:
            if reg["city"] == city and reg["town"] == district : 
                address.append(reg["address"])
                hospital.append(reg["hospital"])
        return address,hospital
                

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