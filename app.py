import streamlit as st
import pandas as pd
import altair as alt

# 1. 초기 데이터 설정
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=['날짜', '지역', '회', '재적', '인증수'])

st.title("수,주일 QR인증률")

# 2. 데이터 입력 폼
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("날짜")
        region = st.selectbox("지역", ["본부", "광산", "북구", "담양", "장성"])
        group = st.selectbox("회", ["자문회", "장년회", "부녀회", "청년회"])
    with col2:
        rejeok = st.number_input("재적", min_value=0)
        cert = st.number_input("인증수", min_value=0)
    
    submitted = st.form_submit_button("데이터 저장/수정")
    
    if submitted:
        mask = (st.session_state.data['날짜'] == date) & \
               (st.session_state.data['지역'] == region) & \
               (st.session_state.data['회'] == group)
        
        if mask.any():
            st.session_state.data.loc[mask, ['재적', '인증수']] = [rejeok, cert]
            st.success(f"{date} {region} {group} 정보가 수정되었습니다!")
        else:
            new_data = pd.DataFrame({'날짜': [date], '지역': [region], '회': [group], '재적': [rejeok], '인증수': [cert]})
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            st.success("데이터가 새로 저장되었습니다!")

# 3. 실시간 대시보드
st.subheader("수치")

if not st.session_state.data.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
        all_dates = ["전체"] + sorted(st.session_state.data['날짜'].astype(str).unique().tolist())
        date_filter = st.selectbox("날짜 선택", all_dates)
    with c2:
        all_regions = ["전체"] + ["본부", "광산", "북구", "담양", "장성"]
        region_filter = st.selectbox("지역 선택", all_regions)
    with c3:
        all_groups = ["전체"] + ["자문회", "장년회", "부녀회", "청년회"]
        group_filter = st.selectbox("회 선택", all_groups)

    is_any_selected = (date_filter != "전체") or (region_filter != "전체") or (group_filter != "전체")

    if is_any_selected:
        df_f = st.session_state.data.copy()
        if date_filter != "전체": df_f = df_f[df_f['날짜'].astype(str) == date_filter]
        if region_filter != "전체": df_f = df_f[df_f['지역'] == region_filter]
        if group_filter != "전체": df_f = df_f[df_f['회'] == group_filter]
        
        # 인증률 계산
        df_f['인증률'] = (df_f['인증수'] / df_f['재적'] * 100).fillna(0).round(2)
        
        # 표 출력을 위해 % 추가
        df_display = df_f.copy()
        df_display['인증률'] = df_display['인증률'].apply(lambda x: f"{x}%")
        st.dataframe(df_display, use_container_width=True)
        
        for date in df_f['날짜'].astype(str).unique():
            st.write(f"#### {date}")
            daily_df = df_f[df_f['날짜'].astype(str) == date].copy()
            
            region_order = ["본부", "광산", "북구", "담양", "장성"]
            group_order = ["자문회", "장년회", "부녀회", "청년회"]
            
            daily_df['지역'] = pd.Categorical(daily_df['지역'], categories=region_order, ordered=True)
            daily_df['회'] = pd.Categorical(daily_df['회'], categories=group_order, ordered=True)
            daily_df = daily_df.sort_values(['지역', '회'])
            
            # y축을 '인증률'로 변경
            # Altair 차트 생성 (x축 라벨과 y축 제목을 가로로 강제 설정)
            # Altair 차트 생성 (y축 최대값 100 설정 및 제목 간격 조정)
            chart = alt.Chart(daily_df).mark_bar().encode(
                x=alt.X('회', sort=group_order, title='회', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('인증률', 
                title='인증률 (%)', 
                scale=alt.Scale(domain=[0, 100]), # y축 최대값 100으로 고정
                axis=alt.Axis(titleAngle=0, titlePadding=50)), # 20에서 50으로 변경
                color='회', 
                column=alt.Column('지역', sort=region_order, header=alt.Header(titleOrient='top', labelOrient='top'))
            ).properties(width=100) 
            
            st.altair_chart(chart)
    else:
        st.info("날짜, 지역, 또는 회를 선택하면 상세 통계와 그래프가 나타납니다.")
else:
    st.write("입력된 데이터가 없습니다.")