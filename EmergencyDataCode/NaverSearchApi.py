import requests
import pandas as pd 
import xmltodict
import json
import re
import warnings
from PublicEmergencyDataProcessor import processor 

processor_class  = processor()

"""
# 네이버 검색 api 클래스 
- set_param : 파라미터 값들 수정 
- get_location : 주소,위도,경도 리스트 출력


"""

class NaverSearchApi:
    def __init__(self):

        # 응급상황 데이터 호출
        # PublicEmergencyDataProcessor.preprocess_hospitalInfo()

        self.headers = {
            'X-Naver-Client-Id': '6Q9w3YC8r3qfKhf11tTY',
            'X-Naver-Client-Secret': 'gVhmq760LU',
        }
        
        self.hostpital_info = pd.read_csv("EmergencyData/hospital_data.csv")
    

    # 파라미터 설정
    def set_param(self,hospital) : 
        params = {
            'query': hospital,
            'display': '10',
            'start': '1',
            'sort': 'random',
        }
        response = requests.get('https://openapi.naver.com/v1/search/local.json', params=params, headers= self.headers)
        search = response.json()
        return search
    

    # 위치 데이터 호출
    def get_location(self):
        road_address = []
        road_mapx = []
        road_mapy = []

        for idx,hospital in enumerate(self.hostpital_info["dutyName"]):
            hospital = self.hostpital_info["city"][idx]  +" "+ hospital
            search = self.set_param(hospital)
            
            try :
                address = search["items"][0]["roadAddress"]
                mapx = float(search["items"][0]["mapx"][:3] +"." +  search["items"][0]["mapx"][3:]) # 경도
                mapy = float(search["items"][0]["mapy"][:2] +"." +  search["items"][0]["mapy"][2:]) # 위도
                
                road_address.append(address)
                road_mapy.append(mapy)
                road_mapx.append(mapx)
            
            except : 
                    road_address.append(None)
                    road_mapy.append(None)
                    road_mapx.append(None)

        return road_address,road_mapx,road_mapy
    

    # 기존 응급상황 병원 데이터에  위치데이터 추가
    def save_location(self):
        road_address,road_mapx,road_mapy = self.get_location()

        tmp = pd.DataFrame([road_address,road_mapx,road_mapy],index=["address","mapx","mapy"]).transpose()
        df = pd.concat([self.hostpital_info,tmp],axis=1)


        df.dropna(subset=['address'], inplace=True) # address의 결측치만 제거
        df.to_csv("EmergencyData/emergency_data.csv",index=False)  # 병원별 위치 저장 


    
NaverSearchApi = NaverSearchApi()
NaverSearchApi.save_location()