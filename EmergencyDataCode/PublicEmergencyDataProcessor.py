import requests
import pandas as pd 
import xmltodict
import json
import re
import warnings

"""
# 공공데이터 전처리 클래스
- get_integratedCitiesData  : 시도통합 데이터를 가져옴
- get_hospitalInfo : 응급실 데이터 (필요한 것들만) 가져옴
- preprocess_hospitalInfo : 응급실 데이터 전처리

# 클래스 사용
preprocess_hospitalInfo 함수 쓰면 전처리된 응급실 데이터 csv로 변환

"""

class processor :
    def __init__(self):
        # 공공데이터 api key 
        self.encoding = "ZGFbPK5eJt31IzIyZNSEm0qEg6%2Bmxn2%2FOGy%2FttBMNZORzNLmuH%2F2s%2BpLZvTsyvv4A4q%2Bt%2BOitipn%2BtzK3gjqdg%3D%3D"
        self.decoding = "ZGFbPK5eJt31IzIyZNSEm0qEg6+mxn2/OGy/ttBMNZORzNLmuH/2s+pLZvTsyvv4A4q+t+Oitipn+tzK3gjqdg=="

        # 데이터 request url
        self.url = 'http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire'  

        # 필요한 데이터 컬럼
        self.essential_columns = ["hvec","hvoc","hvgc","hvmriayn","hvventiayn","hvamyn","dutyName","dutyTel3"]

        warnings.filterwarnings("ignore")


    # 시도통합 데이터 호출
    def get_integratedCitiesData(self): 
        integratedCitiesData = pd.read_csv("EmergencyData/시도통합_수정본.csv")
        return integratedCitiesData
    

    # 응급실 데이터 호출
    def get_hospitalInfo(self):
        integratedCitiesData = self.get_integratedCitiesData()

        # df에서 응급실 데이터 저장
        df = pd.DataFrame(columns= ["city","district"] + self.essential_columns)
        index = 0

        for i in range(len(integratedCitiesData)) :
            params ={'serviceKey' : self.decoding,
                    'STAGE1' : integratedCitiesData.iloc[i,0],
                    'STAGE2' : integratedCitiesData.iloc[i,1],
                    'pageNo' : '1',
                    'numOfRows' : '10' }

            response = requests.get(self.url, params=params)
            dic = xmltodict.parse(response.content)
            
            city = integratedCitiesData.iloc[i,0]
            district = integratedCitiesData.iloc[i,1]

            try :
                # item의 개수가 1개 이상인 경우 
                items = dic["response"]["body"]["items"]["item"]
            
                # 2개 이상인 경우 (딕셔너리 형태)
                if type(items) == list : 
                    for i in range(len(items)):         
                        hostpital_info = [city,district]
                        for essential_column in self.essential_columns :
                            if essential_column in items[i]:
                                hostpital_info.append(items[i][essential_column])
                            else:
                                hostpital_info.append(None)
                        df.loc[index] = hostpital_info  # df에 추가
                        index += 1
                    
                # 1개인 경우는 리스트 형태
                else:  
                    hostpital_info = [city,district]
                    for essential_column in self.essential_columns :
                        if essential_column in items:
                            hostpital_info.append(items[essential_column])
                        else:
                            hostpital_info.append(None)
                    df.loc[index] = hostpital_info  # df에 추가
                    index += 1
                        
            except :
                pass

        return df
    
    
    def preprocess_hospitalInfo(self):
        hospitalInfo = self.get_hospitalInfo()

        # 네이버 검색 API에서 검색에 방해되는 단어 제거 
        remove_lst = ["학교법인","의료법인","재단법인","을지학원","세종","가톨릭학원가톨릭대학교대전",
              "(재)미리내천주성삼성직수도회","한국보훈복지의료공단","고려중앙학원",
              "( 천주교부산교구유지재단)","(의)","()",")"]

        for i in range(len(hospitalInfo["dutyName"])):        
            modified_hospital = hospitalInfo["dutyName"][i]
            for word in remove_lst : 
                modified_hospital = hospitalInfo["dutyName"][i].replace(word,"")
                hospitalInfo["dutyName"][i] =  modified_hospital

        # 재단이 들어가는 부분 나누기  ex) [**재단 ,**병원]
        for i in range(len(hospitalInfo["dutyName"])):    
            length = len(hospitalInfo["dutyName"][i].split("재단"))  # 길이 1이면 재단 단어가 없고, 길이가 2이면 재단 단어 있음
            if length == 2 : 
                modified_hospital = hospitalInfo["dutyName"][i].split("재단")[1]
            else : 
                modified_hospital = hospitalInfo["dutyName"][i].split("재단")[0]
            hospitalInfo["dutyName"][i] =  modified_hospital

        hospitalInfo.to_csv("EmergencyData/hospital_data.csv",index=False)
        return 0


# processor_c  = processor ()
# processor_c.get_integratedCitiesData()