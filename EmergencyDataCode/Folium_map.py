import requests
import pandas as pd 
import numpy as np
import xmltodict
import json
import re
import warnings
import folium
from NaverSearchApi import searchApi


search  = searchApi()

class folium_map:
    def __init__(self):        
        search.save_location()
        self.hospital_info = pd.read_csv("EmergencyData/emergency_data.csv")
    
    

    def process_data(self):
        hospital_info = self.hospital_info
        
        for col in ["hvoc","hvgc"]:
            if col in hospital_info.columns:
                # 문자열을 NaN으로 변환하고, NaN을 0으로 대체
                hospital_info[col] = pd.to_numeric(hospital_info[col], errors='coerce').fillna(99999999).astype(int)

        hospital_info.fillna(99999999, inplace=True)
        for col in hospital_info.columns:
            hospital_info[col] = hospital_info[col].replace(99999999,"Unknown")

        hospital_info = hospital_info.astype(str).replace('99999999', 'Unknown')
        
        hospital_info.to_csv("EmergencyData/emergency_data.csv",index=False)  # 병원별 위치 저장 
        return hospital_info



    def make_map(self):
        emergency = self.process_data()

        m = folium.Map(location=[ 36.321655, 127.378953],zoom_start=7)
       
        for idx,hospital in enumerate(emergency["dutyName"]) : 
            popup_html = f'''
            <div style="font-style:italic; font-size: 11pt;">
                <b>병원명:</b> {hospital}<br>
                <b>주소:</b> {emergency["address"][idx]}<br>
                <b>응급 상황판:</b><br>
                - 응급실: {emergency["hvec"][idx]}<br>
                - 수술실: {emergency["hvoc"][idx]}<br>
                - 입원실: {emergency["hvgc"][idx]}<br>
                - MRI가용: {emergency["hvmriayn"][idx]}<br>
                - 인공호흡기가용: {emergency["hvventiayn"][idx]}<br>
                - 구급차가용: {emergency["hvamyn"][idx]}<br>
                <b>응급실전화:</b> {emergency["dutyTel3"][idx]}<br>
                <b>홈페이지:</b> {emergency["hospital_link"][idx]}
            </div>
            '''
            popup = folium.Popup(popup_html, max_width=600, max_height=600)
            
            icon = folium.Icon(
                color = "red",
                icon_color='white',
                icon='a-solid fa-star',
                prefix='fa'
            )
            
            folium.Marker(
                [emergency["mapy"][idx],emergency["mapx"][idx]],
                popup=popup,
                tooltip=f"<b>{hospital}</b>",
                icon=icon
            ).add_to(m)
        
        m.save("map.html")
    


# 클래스의 인스턴스를 생성
map_instance = folium_map()


# 인스턴스에서 메서드 호출
map_instance.make_map()