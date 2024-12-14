import streamlit as st
from dotenv import load_dotenv
import re
from db_utils import insert_allergy_info, delete_allergy_info, get_allergy_info_grouped, insert_user_info

# 사용자 정보 (하드코딩된 예시)
name = "mingyu"

# 환경 변수 로드
load_dotenv()

# 입력값 검증 함수
def validate_allergen(allergen):
    pattern = re.compile(r'^[A-Za-z가-힣\s\-\/]+$')
    return bool(pattern.match(allergen))


def toggle_refresh():
    """refresh 상태를 토글하는 함수"""
    if 'refresh' not in st.session_state:
        st.session_state.refresh = False
    st.session_state.refresh = not st.session_state.refresh


# Streamlit 앱 구성
st.title("알레르기 정보 관리")

# **사이드바에 사용자 정보 입력 섹션**
with st.sidebar:
    st.header("내 정보")
    with st.expander("사용자 정보 입력", expanded=True):
        input_weight = st.text_input("체중 (kg)")
        input_height = st.text_input("신장 (cm)")
        input_age = st.text_input("나이")
        input_gender = st.selectbox("성별", ["male", "female"])
        input_activity_level = st.selectbox("활동 수준", ["비활동적", "저활동적", "활동적", "매우활동적", "극도활동적"])

        if st.button("사용자 정보 저장"):
            if all([input_weight, input_height, input_age, input_gender, input_activity_level]):
                try:
                    insert_user_info(
                        name=name,
                        weight=input_weight,
                        height=input_height,
                        age=input_age,
                        gender=input_gender,
                        activity_level=input_activity_level
                    )
                    st.success("사용자 정보가 저장되었습니다!")
                except Exception as e:
                    st.error(f"저장 중 오류가 발생했습니다: {e}")
            else:
                st.error("모든 필드를 입력해주세요.")

# **알레르기 정보 입력 섹션**
st.subheader("알레르기 정보 입력")
allergen = st.text_input("알레르기 성분을 입력하세요 (예: 땅콩, 우유)")
risk_level = st.selectbox("위험 그룹을 선택하세요", ("High Risk Group", "Risk Group", "Caution Group"))

if st.button("알레르기 정보 추가"):
    if allergen and risk_level:
        if validate_allergen(allergen):
            try:
                insert_allergy_info(name, allergen, risk_level)
                st.success("알레르기 정보가 추가되었습니다!")
                toggle_refresh()  # 데이터 갱신
            except Exception as e:
                st.error(f"알레르기 정보를 추가하는 중 오류가 발생했습니다: {e}")
        else:
            st.error("알레르기 성분에 유효하지 않은 문자가 포함되어 있습니다.")
    else:
        st.error("알레르기 성분과 위험 그룹을 모두 입력해주세요.")

st.markdown("---")

# **저장된 알레르기 정보 표시 및 그룹별 출력**
st.subheader("저장된 알레르기 정보 목록")

try:
    allergy_data_grouped = get_allergy_info_grouped(name)
except Exception as e:
    st.error(f"알레르기 정보를 가져오는 중 오류가 발생했습니다: {e}")
    allergy_data_grouped = {}

# 그룹별로 알레르기 정보 표시
if allergy_data_grouped:
    for group, data in allergy_data_grouped.items():
        st.write(f"### {group}")
        if not data.empty:
            for index, row in data.iterrows():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(row['allergen'])
                with col2:
                    button_key = f"delete_{group}_{index}"
                    if st.button("삭제", key=button_key):
                        try:
                            delete_allergy_info(name, row['allergen'])
                            st.success(f"{row['allergen']} 항목이 삭제되었습니다!")
                            toggle_refresh()  # 데이터 갱신
                        except Exception as e:
                            st.error(f"{row['allergen']} 삭제 중 오류가 발생했습니다: {e}")
        else:
            st.write("해당 그룹에 저장된 알레르기 정보가 없습니다.")
else:
    st.write("알레르기 정보가 없습니다.")
