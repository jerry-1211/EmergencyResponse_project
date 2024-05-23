import firebase_admin
from firebase_admin import credentials, storage
import pyrebase
import json
import uuid
from datetime import datetime, timedelta

class DBModule : 
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

        self.db = self.firebase.database()
        self.storage = self.firebase.storage()

    def video_save(self) :
        self.storage.child("Video/recode/jerim.avi").put("2024-05-23_19시19분28초~.avi","kcjerim")
        firebase_url = self.storage.child("Video/recode/jerim.avi").get_url("kcjerim")
        print(firebase_url)
        return [firebase_url]
    

    def video_get(self):
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix="Video/recode")         
        urls = []
        for blob in blobs:
            url = blob.generate_signed_url(timedelta(seconds=300))  # URL 생성
            urls.append(url)

        return urls
    



    #----------------------------------------------------------------

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
    
DBModule().video_get()