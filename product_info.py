import requests
import json
import re


def get_nutrition_info_by_name(product_name, api_key):
    """
    상품 이름을 기반으로 성분 정보를 조회하는 함수
    """
    url = "http://apis.data.go.kr/B553748/CertImgListServiceV3/getCertImgListServiceV3"
    params = {
        'ServiceKey': api_key,
        'returnType': 'json',
        'prdlstNm': product_name,  # 상품 이름
        'numOfRows': '100'  # 최대 100개의 결과 반환
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("\n요청 URL:", response.url)

        if response.status_code == 200:
            data = response.json()
            print("API 응답 데이터:", json.dumps(data, indent=2, ensure_ascii=False))

            if 'body' in data and 'items' in data['body']:
                # API에서 반환된 상품 정보 리스트
                return [item['item'] for item in data['body']['items']]
            else:
                print(f"'{product_name}'에 대한 정보가 없습니다.")
                return []
        else:
            print("성분 정보 API 요청 실패:", response.status_code)
            return []
    except requests.RequestException as e:
        print(f"성분 정보 API 요청 중 오류 발생: {e}")
        return []


def parse_nutrient_string(nutrient_str):
    """
    'nutrient' 문자열을 파싱하여 딕셔너리로 변환하는 함수
    """
    nutrient_dict = {}
    key_mapping = {
        "열량": "energy_kcal",
        "탄수화물": "carbohydrates",
        "단백질": "proteins",
        "지방": "fat",
        "나트륨": "sodium",
        "포화지방": "saturated_fat"
    }

    for korean, english in key_mapping.items():
        pattern = rf"{korean}\s+([\d,]+(?:\.\d+)?)\s*([kK][cC][aA][lL]|[gG]|[mM][gG])"
        match = re.search(pattern, nutrient_str)
        if match:
            number = match.group(1).replace(',', '')
            unit = match.group(2)
            nutrient_dict[english] = f"{number}{unit}"
        else:
            nutrient_dict[english] = "정보 없음"

    return nutrient_dict

def get_nutrition_info_by_report_no(report_no, api_key):
    """
    보고 번호를 기반으로 성분 정보를 조회하는 함수
    """
    url = "http://apis.data.go.kr/B553748/CertImgListServiceV3/getCertImgListServiceV3"
    params = {
        'ServiceKey': api_key,
        'prdlstReportNo': report_no,
        'returnType': 'json',
        'numOfRows': '1'
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'body' in data and 'items' in data['body'] and len(data['body']['items']) > 0:
                item = data['body']['items'][0]['item']
                nutrient_str = item.get('nutrient', "알레르기 정보 없음")
                allergy = item.get('allergy', "알레르기 정보 없음")

                if isinstance(nutrient_str, str):
                    nutrient = parse_nutrient_string(nutrient_str)
                else:
                    nutrient = nutrient_str

                return {"nutrient": nutrient, "allergy": allergy}
            else:
                print(f"'{report_no}'에 대한 정보가 없습니다.")
                return None
        else:
            print("성분 정보 API 요청 실패:", response.status_code)
            return None
    except requests.RequestException as e:
        print(f"성분 정보 API 요청 중 오류 발생: {e}")
        return None