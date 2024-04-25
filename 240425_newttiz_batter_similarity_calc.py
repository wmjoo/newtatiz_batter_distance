import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests
import lxml

# 페이지 설정: 탭 제목 변경
st.set_page_config(page_title="타자 유사도 비교", page_icon=":baseball:")

try:
    num_columns = 7
    st.header('Options')
    input_player = st.text_input('Player Name : ', '박용택')
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
    df.columns = second_elements
    df = df[second_elements[:-1]]
    df['yr_team_pos'] = df.Team.copy()
    
    yr_lst = []
    team_lst = []
    pos_lst = []
    # NaN 값을 이전 행의 값으로 덮어쓰기
    for i in range(len(df['yr_team_pos'])):
        tmp_str = df['yr_team_pos'][i]
        yr_lst = yr_lst + [tmp_str[:2]]
        team_lst = yr_lst + [tmp_str[2:-2]]
    df['yr'] = yr_lst    
    baseball_positions = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
    for pos in baseball_positions :
        if pos == 'C':
            pos_boollist = df['yr_team_pos'].str.endswith(pos)
        else:
            pos_boollist = df['yr_team_pos'].str.contains(pos)
        df_pos = df[pos_boollist]
        df.loc[pos_boollist, ['pos']] = pos

    df.pos = df.pos.fillna("")    
    
    teams = ["L", "롯", "두", "한", "키", "넥", "히", "삼", "S", "k", "K", "현", "N" , "O", "해", "쌍"]
    for team in teams :
        team_boollist = df['yr_team_pos'].str.contains(team)
        df_team = df[team_boollist]
        df.loc[team_boollist, ['team']] = team
    # 수치형 데이터만 포함하는 열 필터링
    numeric_data = df.select_dtypes(include=['int64', 'float64'])
    numeric_data_cols = ['scaled_' + i for i in numeric_data.columns]
    
    # 표준화
    scaler = StandardScaler()
    scaled_arr = scaler.fit_transform(numeric_data)
    scaled_df = pd.DataFrame(scaled_arr, columns= numeric_data_cols)
    input_player_idx = df.index[df.Name == input_player][0]
    
    df_row = df[df.Name == input_player]
    df_exceptrow = df[df.Name != input_player]

    default_selections  = ['AVG', 'OBP', 'SLG', 'OPS', 'wRC+']
    # 사용자가 선택할 수 있는 목록
    options = ['WAR', 'G', 'PA', 'ePA', 'AB', 'R', 'H', '2B', '3B', 'HR', 
               'TB', 'RBI', 'SB', 'CS', 'BB', 'HP', 'IB', 'SO', 'GDP', 'SH', 'SF', 
           'AVG', 'OBP', 'SLG', 'OPS', 'R/ePA', 'wRC+']
    
    # 체크박스를 N열로 배열
    columns = st.columns(num_columns)
    selected_options = []
    
    # 각 열에 체크박스 배치
    for index, option in enumerate(options):
        col = columns[index % num_columns]
        with col:
            is_selected = st.checkbox(option, value=option in default_selections, key=option)
            if is_selected:
                selected_options.append(option)
    
    # 선택된 항목 리스트 출력
    # st.write("선택된 항목:", selected_options)

    # 선택된 항목을 거리 계산 기준열로 할당
    ratio_cols = selected_options    
    scaled_ratio_cols = ['scaled_' + i for i  in ratio_cols]
    
    # 유클리드 거리 계산
    distances = np.sqrt(((scaled_df[scaled_ratio_cols] - np.array(scaled_df.iloc[input_player_idx][scaled_ratio_cols]))**2).sum(axis=1))
    df['dist'] = distances
    df = df.sort_values('dist').reset_index(drop=True)
    
    
    ####################
    st.header('Records')
    st.write(df)

except Exception as e:
    st.error(f"예상치 못한 에러가 발생했습니다: {e}", icon="🚨")
