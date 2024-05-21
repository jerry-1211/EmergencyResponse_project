import pyrebase
import json
import uuid

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
                