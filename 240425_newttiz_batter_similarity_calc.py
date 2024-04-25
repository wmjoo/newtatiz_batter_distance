import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests

title = st.text_input('Player Name : ', '')
st.write('The selected Player : ', title)

# URL 설정
url = 'https://statiz.sporki.com/stats/?m=total&m2=batting&m3=default&so=&ob=&sy=1982&ey=2024&te=&po=&lt=10100&reg=C3000&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=10000&ph=&hs=&us=&na=&ls=1&sf1=PA&sk1=100&sv1=&sf2=G&sk2=&sv2='

# 웹페이지에서 데이터를 가져옴
response = requests.get(url)

# HTML 내의 모든 테이블을 DataFrame으로 읽어옴
tables = pd.read_html(response.text)

# 첫 번째 테이블을 출력
df = tables[0]

# 두 번째 요소만 추출
second_elements = [element[1] for element in df.columns]
# print(second_elements)
df.columns = second_elements

st.header('Records')
st.write(df)

