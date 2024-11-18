import streamlit as st
import pandas as pd
import folium as fo

# cp949 인코딩으로 읽기 (Windows에서 생성된 파일일 가능성 높음)
data = pd.read_csv("강남구_공영주차장.csv", encoding='cp949')

st.title('강남구 공영주차장 안내')


data = data.copy().fillna(0)
data.loc[:,'size'] = (data['주차구획수'])



color = {'노상':'#37eb91',
         '부설':'#ebbb37',
         '노외':'#00FFFF'}
data.loc[:,'color'] = data.copy().loc[:,'주차장유형'].map(color)

data

st.map(data, latitude="위도",
       longitude="경도",
       size="size",
       color="color")


# 주차장 데이터 로드
file_path = '강남구_공영주차장.csv'
parking_data = pd.read_csv(file_path, encoding='cp949')

# 필요한 열만 추출하여 데이터 간소화
columns_needed = ['주차장명', '주차기본시간', '주차기본요금', '추가단위시간', '추가단위요금']
parking_fee_data = parking_data[columns_needed].dropna()

# 데이터 타입 변환
parking_fee_data['주차기본시간'] = parking_fee_data['주차기본시간'].astype(float)
parking_fee_data['주차기본요금'] = parking_fee_data['주차기본요금'].astype(float)
parking_fee_data['추가단위시간'] = parking_fee_data['추가단위시간'].astype(float)
parking_fee_data['추가단위요금'] = parking_fee_data['추가단위요금'].astype(float)

# 주차 요금 계산 함수
def calculate_parking_fee(parking_name, parking_duration):
    parking_info = parking_fee_data[parking_fee_data['주차장명'] == parking_name]
    if parking_info.empty:
        return "주차장 정보를 찾을 수 없습니다."
    
    parking_info = parking_info.iloc[0]
    base_time = parking_info['주차기본시간']
    base_fee = parking_info['주차기본요금']
    additional_time = parking_info['추가단위시간']
    additional_fee = parking_info['추가단위요금']
    
    # 요금 계산
    if parking_duration <= base_time:
        total_fee = base_fee
    else:
        extra_time = parking_duration - base_time
        total_fee = base_fee + (extra_time // additional_time) * additional_fee
        if extra_time % additional_time > 0:
            total_fee += additional_fee  # 남은 시간은 추가 요금 한 번 더 부과
    
    return f"총 주차 요금: {total_fee:.0f}원"

# Streamlit UI
st.title("강남구 공영주차장 요금 계산기")

with st.form("parking_fee_form"):
    parking_name = st.selectbox("주차장명", parking_fee_data['주차장명'].unique())
    parking_duration = st.number_input("주차시간(분)", min_value=0, step=1)
    submitted = st.form_submit_button("요금 계산")
    
    if submitted:
        # 주차 요금 계산 및 결과 출력
        fee = calculate_parking_fee(parking_name, parking_duration)
        st.success(fee)