import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests
import lxml
import plotly.express as px
import requests

# 페이지 설정: 탭 제목 변경
st.set_page_config(page_title="타자 유사도 비교", page_icon=":baseball:")

# 포지션 목록
positions = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", ""]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

# Main Tab 
tab1, tab2, tab3 = st.tabs(["Raw", "Find Player", "Plot"])
with tab1:
   st.subheader('Raw Data') 
   if 'raw_data' not in st.session_state:
      try:
           # URL 설정
           url = 'https://statiz.sporki.com/stats/?m=total&m2=batting&m3=default&so=WAR&ob=DESC&sy=1982&ey=2024&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=0&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='
           st.write(url)
           # 웹페이지에서 데이터를 가져옴
           response = requests.get(url, headers=headers)
           st.write(response)
           # HTML 내의 모든 테이블을 DataFrame으로 읽어옴
           tables = pd.read_html(response.text)
           st.write(tables)
           # 첫 번째 테이블을 출력
           df = tables[0]
           
           # 두 번째 요소만 추출
           second_elements = [element[1] for element in df.columns]
           df.columns = second_elements
           df = df[second_elements[:-1]].copy()
       
           df.rename(columns = {'2B':'2BH', '3B':'3BH', 'Team': 'yr_team_pos'}, inplace = True)
         
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
       
           st.dataframe(df.drop(['yr_team_pos'], axis = 1).reset_index(drop=True))
   
      except Exception as e:
         st.error(f"예상치 못한 에러가 발생했습니다: {e}", icon="🚨")

with tab2:
      # 재실행을 위해 다시 필요한 데이터를 설정하고 함수를 정의합니다.
   import pandas as pd
   
   # 포지션 목록
   positions = ["P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH", ""]
   
   # 유사도 데이터
   similarity_data = [
       [1.0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # P
       [0.1, 1.0, 0.2, 0.2, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],  # C
       [0.1, 0.2, 1.0, 0.4, 0.5, 0.3, 0.2, 0.2, 0.2, 0.1, 0.1],  # 1B
       [0.1, 0.2, 0.4, 1.0, 0.6, 0.7, 0.3, 0.3, 0.3, 0.1, 0.1],  # 2B
       [0.1, 0.2, 0.5, 0.6, 1.0, 0.6, 0.3, 0.3, 0.3, 0.1, 0.1],  # 3B
       [0.1, 0.2, 0.3, 0.7, 0.6, 1.0, 0.3, 0.3, 0.3, 0.1, 0.1],  # SS
       [0.1, 0.1, 0.2, 0.3, 0.3, 0.3, 1.0, 0.6, 0.6, 0.1, 0.1],  # LF
       [0.1, 0.1, 0.2, 0.3, 0.3, 0.3, 0.6, 1.0, 0.6, 0.1, 0.1],  # CF
       [0.1, 0.1, 0.2, 0.3, 0.3, 0.3, 0.6, 0.6, 1.0, 0.1, 0.1],  # RF
       [0.1, 0.1, 0.6, 0.3, 0.3, 0.3, 0.6, 0.6, 0.6, 1.0, 0.1],  # DH
       [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],  # "" - void
   ]
   
   # DataFrame 생성
   similarity_matrix = pd.DataFrame(similarity_data, index=positions, columns=positions)
   
   def get_similarity(position1, position2, matrix = similarity_matrix):
       """
       이 함수는 주어진 두 포지션의 유사도 값을 반환합니다.
       
       Args:
       position1 (str): 첫 번째 포지션
       position2 (str): 두 번째 포지션
       matrix (pd.DataFrame): 포지션 유사도 매트릭스
       
       Returns:
       float: 두 포지션 간의 유사도 값
       """
       return matrix.loc[position1, position2]
   
   # 예시로 2루수(2B)와 유격수(SS) 간의 유사도를 확인
   #get_similarity("2B", "SS", similarity_matrix)

   selected_options = []
   try:
       # 두 열로 레이아웃 분할
       col1, col2 = st.columns(2)
       with col1:    
           st.subheader('Find Similar Player')
       with col2:
           submit_button = st.button("검색")
   
       # 두 열로 레이아웃 분할
       col1, col2 = st.columns(2)
       with col1:
           input_player = st.text_input('Name', '홍창기')
       with col2:
           topN = st.text_input('Top N', 10) # label_visibility="hidden")    
           
       # 사용자가 선택할 수 있는 목록
       options = baseball_positions + ['']
       # 체크박스를 N열로 배열
       st.write('Positions')
       position_option_on = st.toggle('Similar Position')
      
       num_columns = 6
       columns = st.columns(num_columns)
       selected_positions = []
       # 각 열에 체크박스 배치
       for index, option in enumerate(options):
           col = columns[index % num_columns]
           with col:
               # 디폴트 선택 항목 또는 전체 선택/해제 상태에 따라 체크박스 초기값 설정
               is_selected = st.checkbox(option, value=options,
                                           # value=(option in default_selections) or st.session_state.selected_all, 
                                           key=option)
               if is_selected:
                   selected_positions.append(option)
   
       # 사용자가 선택할 수 있는 목록
       st.write('Stats')        
       options = ['WAR', 'G', 'PA', 'ePA', 'AB', 'R', 'H', '2BH', '3BH', 'HR',  'TB', 'RBI', 'SB', 'CS', 'BB', 'HP', 'IB', 'SO', 'GDP', 'SH', 'SF',  'AVG', 'OBP', 'SLG', 'OPS', 'R/ePA', 'wRC+']
       
       # 디폴트로 선택되어야 할 항목들
       default_selections = ['AB', 'AVG', 'OBP', 'SLG', 'OPS', 'wRC+']
   
       # 체크박스를 N열로 배열
       num_columns = 7
       columns = st.columns(num_columns)
       with st.expander("접을 수 있는 섹션"):
          # 각 열에 체크박스 배치
          for index, option in enumerate(options):
              col = columns[index % num_columns]
              with col:
                  # 디폴트 선택 항목 또는 전체 선택/해제 상태에 따라 체크박스 초기값 설정
                  is_selected = st.checkbox(option, 
                                              value=option in default_selections, key=option)
                  if is_selected:
                      selected_options.append(option)
   
       # 선택된 항목을 거리 계산 기준열로 할당
       ratio_cols = selected_options    
       scaled_ratio_cols = ['scaled_' + i for i  in ratio_cols]
       
       if submit_button:
           # 수치형 데이터만 포함하는 열 필터링
           numeric_data = df.select_dtypes(include=['int64', 'float64'])
           numeric_date_cols_orig = numeric_data.columns.tolist()
           numeric_data_cols = ['scaled_' + i for i in numeric_data.columns]
           
           # 표준화
           scaler = StandardScaler()
           scaled_arr = scaler.fit_transform(numeric_data)
           scaled_df = pd.DataFrame(scaled_arr, columns= numeric_data_cols)
           input_player_idx = df.index[df.Name == input_player][0]
           
           df_row = df[df.Name == input_player]
           df_exceptrow = df[df.Name != input_player]
       
           #############################################
           # 체크박스 생성
           # samepos_check = st.checkbox('Same Position')
           # st.write(samepos_check)
           # if samepos_check:
           #     st.write(df_row.pos[0])
           
           # 유클리드 거리 계산
           distances = np.sqrt(((scaled_df[scaled_ratio_cols] - np.array(scaled_df.iloc[input_player_idx][scaled_ratio_cols]))**2).sum(axis=1))
           df['dist'] = round(distances, 3)
           df = df.sort_values('dist').reset_index(drop=True)
       
           # 선택된 항목들을 먼저, 나머지를 그 뒤에 배열
           final_options_order = ['dist', 'Rank', 'Name', 'pos'] + selected_options + [option for option in options if option not in selected_options]
       
           df_final = df[final_options_order].reset_index(drop=True)
           df_final = df_final.loc[df_final.pos.isin(pd.Series(selected_positions))] # 최종 검색 결과에서 선택된 포지션만 반영 되도록
           df_final = df_final.loc[~df_final[selected_options].isna().any(axis=1)]
           df_final = df_final.head(int(topN)+1)
               #df_final[df_final[selected_options].dropna()].reset_index(drop=True)
           
           ####################
           st.subheader('Similar Players')
           st.write(df_final)
           st.session_state.df_final = df_final
           st.session_state.numeric_date_cols_orig = numeric_date_cols_orig

   except Exception as e:
       st.error(f"예상치 못한 에러가 발생했습니다: {e}", icon="🚨")
with tab3:
    # 'df_final'이 세션 상태에 있는지 확인
    if 'df_final' in st.session_state and 'numeric_date_cols_orig' in st.session_state:
        st.write(st.session_state.df_final.head(1))  # 예시로 첫 번째 행을 보여줌
        try:
            # 그래프 생성
            st.subheader('Plotting Graph')
            # 두 열로 레이아웃 분할
            col1, col2 = st.columns(2)
            with col1:
                # 세션 상태에서 변수 목록 가져오기
                x_axis = st.selectbox('Select the X-axis', options=st.session_state.numeric_date_cols_orig, index=1)
            with col2:
                y_axis = st.selectbox('Select the Y-axis', options=st.session_state.numeric_date_cols_orig, index=2)
            
            # 스케터 플롯 생성
            fig = px.scatter(st.session_state.df_final, x=x_axis, y=y_axis, text="Name",
                             title=f'Scatter Plot of {x_axis} vs {y_axis}',
                             hover_data=['Name'])
            
            # 텍스트 위치 조정
            fig.update_traces(textposition='top right', marker=dict(size=12),
                              hoverinfo='text+x+y',
                              hovertemplate="<br>".join([
                                  "Name: %{text}",
                                  "{}: %{{x}}".format(x_axis),
                                  "{}: %{{y}}".format(y_axis)
                              ])
            )
            
            # 그래프 크기 조정
            fig.update_layout(width=800, height=600)  # 원하는 크기로 설정 가능

            # 스트림릿에 플롯 출력
            st.plotly_chart(fig, use_container_width=True)  # 화면 너비에 맞추려면 이 옵션을 사용
        except Exception as e:
            st.error(f"예상치 못한 에러가 발생했습니다: {e}", icon="🚨")
    else:
        st.error("데이터를 먼저 찾아야 그래프를 그릴 수 있습니다.", icon="🚨")
      
