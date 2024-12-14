from product_info import get_nutrition_info_by_report_no  # 필요한 함수만 import
import os
from dotenv import load_dotenv
import re
from db_utils import get_allergens_risk_levels, get_user_info  # 사용자 정보 가져오는 함수 추가
import sys
from ttsAdvanced import speak_allergen_info, speak_product_info

def map_gender(gender):
    """성별 값을 '남성' 또는 '여성'으로 변환"""
    if gender.lower() in ['male', '남성']:
        return '남성'
    elif gender.lower() in ['female', '여성']:
        return '여성'
    else:
        raise ValueError("올바르지 않은 성별 값입니다. '남성' 또는 '여성'이어야 합니다.")
    
def calculate_bmr(weight, height, age, gender):
    """기초대사량(BMR) 계산 - 입력값 유효성 검사 추가"""
    if not isinstance(weight, (int, float)) or not isinstance(height, (int, float)) or not isinstance(age, (int, float)):
        raise ValueError("체중, 신장, 나이는 숫자여야 합니다.")
    if gender.lower() not in ['남성', '여성']:
        raise ValueError("성별은 '남성' 또는 '여성'이어야 합니다.")
    
    if gender.lower() == '남성':
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:  # 여성
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

def get_activity_multiplier(activity_level):
    """활동 수준에 따른 곱수 반환"""
    multipliers = {
        '비활동적': 1.2,    # 운동 안함
        '저활동적': 1.375,  # 주 1-3회 운동
        '활동적': 1.55,     # 주 3-5회 운동
        '매우활동적': 1.725,# 주 6-7회 운동
        '극도활동적': 1.9   # 매우 힘든 운동 또는 육체노동
    }
    return multipliers.get(activity_level, 1.2)


def calculate_daily_nutrients(weight, height, age, gender, activity_level):
    """일일 영양소 권장량 계산"""
    
    # 1. 기초대사량 계산
    bmr = calculate_bmr(weight, height, age, gender)
    
    # 2. 활동량 곱수 적용하여 일일 필요 칼로리 계산
    activity_multiplier = get_activity_multiplier(activity_level)
    daily_calories = bmr * activity_multiplier
    
    # 3. 나트륨 계산 (나이와 활동량 고려)
    if age >= 65:
        sodium = 1500  # mg
    else:
        base_sodium = 2000
        if activity_level in ['매우활동적', '극도활동적']:
            sodium = base_sodium * 1.2
        else:
            sodium = base_sodium
    
    # 4. 당류 계산 (칼로리의 10% 기준)
    added_sugar = (daily_calories * 0.10) / 4  # 탄수화물 1g = 4kcal
    
    # 5. 포화지방 계산 (칼로리의 10% 기준)
    saturated_fat = (daily_calories * 0.10) / 9  # 지방 1g = 9kcal
    
    # 6. 트랜스지방 계산 (칼로리의 1% 미만)
    trans_fat = (daily_calories * 0.01) / 9
    
    return {
        'daily_calories': round(daily_calories, 0),
        'sodium_mg': round(sodium, 0),
        'added_sugar_g': round(added_sugar, 1),
        'saturated_fat_g': round(saturated_fat, 1),
        'trans_fat_g': round(trans_fat, 1)
    }