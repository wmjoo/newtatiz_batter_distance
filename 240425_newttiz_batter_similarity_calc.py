import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests
import lxml

try:
    input_player = st.text_input('Player Name : ', '')
    st.error('This is an error', icon="🚨")
    # st.write('The selected Player : ', player_name)
    
    
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
    df = df[second_elements[:-1]]
    df['yr_team_pos'] = df.Team.copy()
    
    #%%
    yr_lst = []
    team_lst = []
    pos_lst = []
    # NaN 값을 이전 행의 값으로 덮어쓰기
    for i in range(len(df['yr_team_pos'])):
        tmp_str = df['yr_team_pos'][i]
    
        yr_lst = yr_lst + [tmp_str[:2]]
        team_lst = yr_lst + [tmp_str[2:-2]]
        
        # print(i, df['Name'][i], tmp_str[:2], tmp_str[2:-2], tmp_str[-2:])
    df['yr'] = yr_lst    
    #display(df.yr.value_counts())
    ##%%
    baseball_positions = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"]
    for pos in baseball_positions :
        if pos == 'C':
            pos_boollist = df['yr_team_pos'].str.endswith(pos)
        else:
            pos_boollist = df['yr_team_pos'].str.contains(pos)
            
        # print(pos, sum(pos_boollist))
        df_pos = df[pos_boollist]
        df.loc[pos_boollist, ['pos']] = pos
        # print(df_pos.head(2))
    df.pos = df.pos.fillna("")    
    #display(df.pos.value_counts())
    
    teams = ["L", "롯", "두", "한", "키", "넥", "히", "삼", "S", "k", "K", "현", "N" , "O", "해", "쌍"]
    for team in teams :
        team_boollist = df['yr_team_pos'].str.contains(team)
        # print(team, sum(team_boollist ))
        df_team = df[team_boollist]
        df.loc[team_boollist, ['team']] = team
    #display(df.team.value_counts())    
    # 수치형 데이터만 포함하는 열 필터링
    numeric_data = df.select_dtypes(include=['int64', 'float64'])
    numeric_data_cols = ['scaled_' + i for i in numeric_data.columns]
    
    # 표준화
    scaler = StandardScaler()
    scaled_arr = scaler.fit_transform(numeric_data)
    scaled_df = pd.DataFrame(scaled_arr, columns= numeric_data_cols)
    #scaled_df
    input_player_idx = df.index[df.Name == input_player][0]
    #print(input_player_idx)
    
    df_row = df[df.Name == input_player]
    #display(df_row)
    df_exceptrow = df[df.Name != input_player]
    #display(df_exceptrow)
    
    # df.columns
    
    ratio_cols = ['WAR', #'G', 'PA', 'ePA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'TB', 'RBI', 'SB', 'CS', 'BB', 'HP', 'IB', 'SO', 'GDP', 'SH', 'SF', 
           'AVG', 'OBP', 'SLG', 'OPS', #'R/ePA', 
           'wRC+']
    
    scaled_ratio_cols = ['scaled_' + i for i  in ratio_cols]
    
    # 유클리드 거리 계산
    distances = np.sqrt(((scaled_df[scaled_ratio_cols] - np.array(scaled_df.iloc[input_player_idx][scaled_ratio_cols]))**2).sum(axis=1))
    df['dist'] = distances
    df = df.sort_values('dist').reset_index(drop=True)
    
    
    ####################
    st.header('Records')
    st.write(df)

except Exception as e:
    st.error(f"예상치 못한 에러가 발생했습니다: {e}")
