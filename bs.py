import streamlit as st

# 목 데이터 정의
mock_data = [
    {"prdlstNm": "일품해물라면", "prdlstReportNo": "123456", "nutrient": "열량 500kcal"},
    {"prdlstNm": "맛있는 라면", "prdlstReportNo": "789012", "nutrient": "열량 600kcal"},
    {"prdlstNm": "해물칼국수", "prdlstReportNo": "345678", "nutrient": "열량 400kcal"}
]

# Streamlit 앱 제목
st.title("테스트: 목 데이터로 제품 정보 조회")

# **2. 상품 이름 입력 및 검색**
st.header("제품 정보 조회")
product_name = st.text_input("상품 이름을 입력하세요:")

if st.button("조회"):
    if not product_name:
        st.error("유효한 상품 이름을 입력해주세요.")
    else:
        # 목 데이터에서 필터링
        filtered_items = [
            item for item in mock_data
            if product_name.lower() in item["prdlstNm"].lower()
        ]

        if filtered_items:
            # 사용자 선택
            selected_product = st.selectbox(
                "조회된 상품 목록",
                filtered_items,
                format_func=lambda x: x.get("prdlstNm", "이름 정보 없음")
            )

            # 선택된 상품 정보 출력
            st.write(f"**제품 이름:** {selected_product.get('prdlstNm', '정보 없음')}")
            st.write(f"**보고 번호:** {selected_product.get('prdlstReportNo', '정보 없음')}")
            st.write(f"**영양 정보:** {selected_product.get('nutrient', '정보 없음')}")
        else:
            st.error(f"'{product_name}'에 대한 관련 상품을 찾을 수 없습니다.")
