import streamlit as st
import pandas as pd
import altair as alt
import os

# 파일 이름 설정
DATA_FILE = "data.csv"

# 데이터 불러오기 함수 (데이터가 없으면 빈 틀 생성)
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=['날짜', '지역', '회', '재적', '인증수'])

# 데이터 저장 함수
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("수,주일 QR인증률")

# 1. 데이터 입력 폼
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
        df = load_data()
        mask = (df['날짜'] == str(date)) & (df['지역'] == region) & (df['회'] == group)
        
        if mask.any():
            df.loc[mask, ['재적', '인증수']] = [rejeok, cert]
            st.success(f"{date} {region} {group} 정보가 수정되었습니다!")
        else:
            new_data = pd.DataFrame({'날짜': [str(date)], '지역': [region], '회': [group], '재적': [rejeok], '인증수': [cert]})
            df = pd.concat([df, new_data], ignore_index=True)
            st.success("데이터가 새로 저장되었습니다!")
        
        save_data(df)

# 2. 실시간 대시보드
st.subheader("수치")
df = load_data()

if not df.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
        all_dates = ["전체"] + sorted(df['날짜'].unique().tolist())
        date_filter = st.selectbox("날짜 선택", all_dates)
    with c2:
        all_regions = ["전체"] + ["본부", "광산", "북구", "담양", "장성"]
        region_filter = st.selectbox("지역 선택", all_regions)
    with c3:
        all_groups = ["전체"] + ["자문회", "장년회", "부녀회", "청년회"]
        group_filter = st.selectbox("회 선택", all_groups)

    is_any_selected = (date_filter != "전체") or (region_filter != "전체") or (group_filter != "전체")

    if is_any_selected:
        df_f = df.copy()
        if date_filter != "전체": df_f = df_f[df_f['날짜'] == date_filter]
        if region_filter != "전체": df_f = df_f[df_f['지역'] == region_filter]
        if group_filter != "전체": df_f = df_f[df_f['회'] == group_filter]
        
        df_f['인증률'] = (df_f['인증수'] / df_f['재적'] * 100).fillna(0).round(2)
        
        df_display = df_f.copy()
        df_display['인증률'] = df_display['인증률'].apply(lambda x: f"{x}%")
        st.dataframe(df_display, use_container_width=True)
        
        for date in df_f['날짜'].unique():
            st.write(f"#### {date}")
            daily_df = df_f[df_f['날짜'] == date].copy()
            # ... (나머지 그래프 코드 동일)
