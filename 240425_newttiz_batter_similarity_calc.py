import streamlit as st
import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import requests
import lxml

# 페이지 설정: 탭 제목 변경
st.set_page_config(page_title="타자 유사도 비교", page_icon=":baseball:")
selected_options = []
try:
    st.header('RawData table')
    # URL 설정
    url = 'https://statiz.sporki.com/stats/?m=total&m2=batting&m3=default&so=WAR&ob=DESC&sy=1982&ey=2024&te=&po=&lt=10100&reg=A&pe=&ds=&de=&we=&hr=&ha=&ct=&st=&vp=&bo=&pt=&pp=&ii=&vc=&um=&oo=&rr=&sc=&bc=&ba=&li=&as=&ae=&pl=&gc=&lr=&pr=1000&ph=&hs=&us=&na=&ls=0&sf1=G&sk1=&sv1=&sf2=G&sk2=&sv2='
    
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

    st.write(df.drop('Team', axis = 1).reset_index(drop=True))

    #############################################    
    st.subheader('Find Similar Player')

    # 두 열로 레이아웃 분할
    col1, col2, col3 = st.columns(3)
    
    # 첫 번째 열에 텍스트 입력 창 생성
    with col1:
        input_player = st.text_input('Name', '박용택')
    # 2번째 열에 텍스트 입력 창 생성
    with col2:
        topN = st.text_input('Top N', 9) # label_visibility="hidden")    
    # 3번째 열에 버튼 생성
    with col3:
        submit_button = st.button("검색")

    # 버튼 클릭 시 scatter plot 출력
    if submit_button:
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
    
        #############################################
        # 사용자가 선택할 수 있는 목록
        options = ['WAR', 'G', 'PA', 'ePA', 'AB', 'R', 'H', '2B', '3B', 'HR', 
                   'TB', 'RBI', 'SB', 'CS', 'BB', 'HP', 'IB', 'SO', 'GDP', 'SH', 'SF', 
                   'AVG', 'OBP', 'SLG', 'OPS', 'R/ePA', 'wRC+']
        
        # 디폴트로 선택되어야 할 항목들
        default_selections = ['AVG', 'OBP', 'SLG', 'OPS', 'wRC+']
    
        # 체크박스를 N열로 배열
        num_columns = 7
        columns = st.columns(num_columns)
        
        # 각 열에 체크박스 배치
        for index, option in enumerate(options):
            col = columns[index % num_columns]
            with col:
                # 디폴트 선택 항목 또는 전체 선택/해제 상태에 따라 체크박스 초기값 설정
                is_selected = st.checkbox(option, 
                                          value=option in default_selections,
                                          # value=(option in default_selections) or st.session_state.selected_all, 
                                          key=option)
                if is_selected:
                    selected_options.append(option)
    
        # 선택된 항목을 거리 계산 기준열로 할당
        ratio_cols = selected_options    
        scaled_ratio_cols = ['scaled_' + i for i  in ratio_cols]
        
        # 유클리드 거리 계산
        distances = np.sqrt(((scaled_df[scaled_ratio_cols] - np.array(scaled_df.iloc[input_player_idx][scaled_ratio_cols]))**2).sum(axis=1))
        df['dist'] = round(distances, 3)
        df = df.sort_values('dist').reset_index(drop=True)
    
        # 선택된 항목들을 먼저, 나머지를 그 뒤에 배열
        final_options_order = ['dist', 'Rank', 'Name', 'pos'] + selected_options + [option for option in options if option not in selected_options]
    
        df_final = df[final_options_order].reset_index(drop=True)
        df_final = df_final.loc[~df_final[selected_options].isna().any(axis=1)]
        df_final = df_final.head(int(topN)+1)
            #df_final[df_final[selected_options].dropna()].reset_index(drop=True)
        
        ####################
        st.subheader('Similar Players')
        st.write(df_final)
except Exception as e:
    st.error(f"예상치 못한 에러가 발생했습니다: {e}", icon="🚨")

####################
# 그래프 생성
if len(selected_options) >= 2:
    try:
        # 레이아웃 설정
        col1, col2, col3 = st.columns(3)    
        # 첫 번째 열: X축 선택
        with col1:
            x_axis = st.selectbox("X 축을 선택하세요", selected_options)
        
        # 두 번째 열: Y축 선택
        with col2:
            y_axis = st.selectbox("Y 축을 선택하세요", selected_options)
        
        # 세 번째 열: 버튼
        with col3:
            plot_button = st.button("그래프 생성")
    
            # df_final 존재 여부 확인
            if 'df_final' in locals() and not df_final.empty:
                st.subheader('Similar Players Plotting')    
                fig = px.scatter(df_final, x=x_axis, y=y_axis, text="Name",
                                 title=f"Scatter Plot of {x_axis} vs {y_axis}",
                                 hover_data=["Name"])  # Name 컬럼을 호버 데이터로 추가
                fig.update_traces(marker=dict(size=10),
                                  hoverinfo='text+x+y',
                                  hovertemplate="<br>".join([
                                      "Name: %{hovertext}",
                                      f"{x_axis}: %{x}",
                                      f"{y_axis}: %{y}"
                                  ]))
                st.plotly_chart(fig)
            else:
                st.error("df_final 데이터 프레임이 존재하지 않거나 비어 있습니다.")
    except NameError:
        st.error("df_final 데이터 프레임이 정의되지 않았습니다.")
