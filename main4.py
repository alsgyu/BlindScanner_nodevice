import streamlit as st
import os
from dotenv import load_dotenv
from db_utils import get_allergens_risk_levels, get_user_info
from product_info import get_nutrition_info_by_name
from calculate import calculate_daily_nutrients, map_gender

# 환경 변수 로드
load_dotenv()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Brush+Script&display=swap');

    .main {
        background-color: #F9FFFF;
    }
    h1 {
        color: #2B2B52;
        font-size: 40px;
        font-family: 'Nunito', sans-serif;
    }
    h2 {
        color: #2B2B52;
        font-size: 18px;
        font-family: 'Nunito', sans-serif;
    }
    .post-it {
        position: fixed;
        display: inline-block;
        padding: 30px;
        width: 300px;
        border: 1px solid #f8f861;
        border-left: 30px solid #f8f861;
        border-bottom-right-radius: 60px 10px;
        
        font-size: 25px;
        color: #555;
        background: #ffff88;
        transition: all 0.2s;
    }
    .post-it.top-right {
        top: 150px;
        right: 120px;
    }
    .post-it.bottom-right {
        bottom: 150px;
        right: 120px;
    }
    .post-it.bottom-left {
        bottom: 150px;
        left: 120px;
    }
    .message-container {
        display: flex;
        justify-content: flex-end;
        margin: 10px 0;
    }
    .message-container.ai {
        justify-content: flex-start;
    }
    .message {
        background-color: #6AC793;
        border-radius: 10px;
        padding: 10px;
        color: white;
        max-width: 450px;
    }
    .message.ai {
        background-color: #b4b4b4;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# 포스트잇 추가
st.markdown('<div class="post-it top-right">자신만의 성분 비율을 확인하세요!</div>', unsafe_allow_html=True)
st.markdown('<div class="post-it bottom-right">알러지 성분을 꼭 확인하세요!</div>', unsafe_allow_html=True)
st.markdown('<div class="post-it bottom-left">헤리스-베네딕트 방정식을 활용하여 개인화한 비율 정보입니다.</div>', unsafe_allow_html=True)

# Streamlit 앱 제목
st.title("영양성분 조회 및 알러지 탐색")

# **사용자 이름 입력**
st.header("사용자 정보")
user_name = st.text_input("사용자 이름을 입력하세요:", "mingyu")

if st.button("사용자 정보 확인"):
    # 사용자 정보 조회
    user_info = get_user_info(user_name)

    if user_info:
        try:
            # 성별 값 변환
            gender_mapped = map_gender(user_info['gender'])

            # 사용자 정보 출력
            st.write(f"**이름:** {user_name}")
            st.write(f"**체중:** {user_info['weight']} kg")
            st.write(f"**신장:** {user_info['height']} cm")
            st.write(f"**나이:** {user_info['age']} 세")
            st.write(f"**성별:** {gender_mapped}")
            st.write(f"**활동 수준:** {user_info['activity_level']}")

            # 일일 영양소 권장량 계산
            daily_nutrients = calculate_daily_nutrients(
                weight=float(user_info['weight']),
                height=float(user_info['height']),
                age=int(user_info['age']),
                gender=gender_mapped,  # 변환된 성별 값 사용
                activity_level=user_info['activity_level']
            )

            # 영양소 권장량 출력
            st.subheader("일일 영양소 권장량")
            st.write(f"**칼로리:** {daily_nutrients['daily_calories']} kcal")
            st.write(f"**나트륨:** {daily_nutrients['sodium_mg']} mg")
            st.write(f"**첨가당:** {daily_nutrients['added_sugar_g']} g")
            st.write(f"**포화지방:** {daily_nutrients['saturated_fat_g']} g")
            st.write(f"**트랜스지방:** {daily_nutrients['trans_fat_g']} g")
        except ValueError as e:
            st.error(str(e))
    else:
        st.error(f"사용자 '{user_name}' 정보를 찾을 수 없습니다.")

# 상품 정보 입력 및 출력
st.header("제품 정보 조회")
product_name = st.text_input("상품 이름을 입력하세요:")

if product_name and user_info:
    api_data = get_nutrition_info_by_name(product_name, os.getenv("API_KEY_DETAIL"))

    if api_data:
        # 상품 선택
        product_options = {idx: item for idx, item in enumerate(api_data)}
        selected_idx = st.selectbox(
            "조회된 상품 목록",
            options=list(product_options.keys()),
            format_func=lambda x: product_options[x].get("prdlstNm", "이름 정보 없음")
        )

        if selected_idx is not None:
            selected_product = product_options[selected_idx]

            # 선택된 상품 정보 출력
            st.write(f"**제품 이름:** {selected_product.get('prdlstNm', '정보 없음')}")
            st.write(f"**보고 번호:** {selected_product.get('prdlstReportNo', '정보 없음')}")
            st.write(f"**영양 정보:** {selected_product.get('nutrient', '정보 없음')}")

            st.subheader("알레르기 위험도")
            allergy_info = selected_product.get('allergy', "알레르기 정보 없음")

            if allergy_info != "알레르기 정보 없음":
                st.write(f"**제품 알레르기 정보:** {allergy_info}")
                allergens = [a.strip() for a in allergy_info.split(",")]

                risk_levels = get_allergens_risk_levels(user_name, allergens)

                if risk_levels:
                    for allergen, risk_level in risk_levels.items():
                        if risk_level == "Highrisk":
                            st.error(f"⚠️ **{allergen}: 위험군! 이 제품을 피하세요.**")
                        elif risk_level == "Risk":
                            st.warning(f"⚠️ **{allergen}: 주의 필요. 섭취 전 확인하세요.**")
                        else:
                            st.info(f"✅ **{allergen}: 섭취 가능하지만 주의하세요.**")
                else:
                    st.success("등록된 알레르기 성분이 없습니다.")

            # 영양 성분 비율 계산 및 출력
            if "nutrient" in selected_product and selected_product["nutrient"] and user_info:
                nutrient_info = selected_product["nutrient"]  # 제품의 영양소 데이터 가져오기
                st.subheader("제품의 영양소 비율")

                nutrient_map = {
                    "칼로리": "calories",
                    "나트륨": "sodium",
                    "첨가당": "sugar",
                    "포화지방": "saturated_fat",
                    "트랜스지방": "trans_fat",
                }

                for label, nutrient_key in nutrient_map.items():
                    daily_value = daily_nutrients.get(nutrient_key)
                    product_value = nutrient_info.get(label)  # 데이터 매핑 확인

                    if product_value and daily_value:  # 값이 존재할 경우 계산
                        try:
                            product_value = float(product_value)  # 값을 float으로 변환
                            ratio = (product_value / daily_value) * 100
                            st.write(f"**{label}:** {product_value} ({ratio:.1f}% 권장 섭취량)")
                        except (ValueError, TypeError):
                            st.warning(f"**{label}**의 데이터 형식이 올바르지 않습니다.")



