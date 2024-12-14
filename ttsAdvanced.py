import boto3
import os
from playsound import playsound


aws_access_key: str = os.getenv('AWS_ACCESS_KEY')
aws_secret_key: str = os.getenv('AWS_SECRET_KEY')



def text_to_speak_adv(audio_file_name, text, category):
    # 카테고리별 캐시 디렉토리 설정
    cache_dir = "sound_cache"
    category_dir = os.path.join(cache_dir, category)
    
    # 디렉토리가 없으면 생성
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.exists(category_dir):
        os.makedirs(category_dir)
    
    # 캐시된 파일의 전체 경로
    output = os.path.join(category_dir, audio_file_name)
    
    # 캐시된 파일이 있는지 확인
    if os.path.exists(output):
        print(f"캐시된 파일 {audio_file_name} 사용")
        playsound(output)
        return
    
    # 캐시된 파일이 없는 경우 API 호출
    print(f"새로운 음성 파일 생성: {audio_file_name}")
    polly_client = boto3.Session(
        aws_access_key_id=aws_access_key,                     
        aws_secret_access_key=aws_secret_key,
        region_name='us-east-1').client('polly')

    response = polly_client.synthesize_speech(
        VoiceId='Seoyeon',
        OutputFormat='mp3', 
        Text = text,
        Engine = 'neural',
        LanguageCode='ko-KR'
    )

    # 새로운 파일 저장
    with open(output, 'wb') as file:
        file.write(response['AudioStream'].read())

    playsound(output)



def speak_product_info(barcode, product_name, nutrient):
    # 기본 제품 정보 구성
    product_text = f"제품 이름은 {product_name}이고, "

    # product 디렉토리에 저장하고 재생
    audio_file_name = f"{barcode}_product.mp3"

    # 영양 정보 구성
    sodium = nutrient.get('sodium', None)
    saturated_fat = nutrient.get('saturated_fat', None)
    energy_kcal = nutrient.get('energy_kcal', None)

    if sodium is not None:
        product_text += f"나트륨 {sodium}, "
    if saturated_fat is not None:
        product_text += f"포화지방 {saturated_fat}, "
    if energy_kcal is not None:
        product_text += f"열량 {energy_kcal} 입니다. "

    text_to_speak_adv(audio_file_name, product_text, "product")


def get_allergen_filename(allergen):
    # 알레르겐 한글-영어 매핑
    allergen_mapping = {
        "우유": "milk",
        "대두": "soybean",
        "밀": "wheat",
        "땅콩": "peanut",
        "견과류": "nuts",
        "갑각류": "crustacean",
        "계란": "egg",
        "생선": "fish",
        "조개류": "shellfish",
        # 필요한 매핑 추가
    }
    return allergen_mapping.get(allergen, f"allergen_{hash(allergen)}")



def speak_allergen_info(allergen, risk_level):

    # 알레르겐 파일명을 영어로 변환
    allergen_filename = f"{get_allergen_filename(allergen)}.mp3"
    
    
    # 알레르겐 음성 파일 생성/재생
    text_to_speak_adv(allergen_filename, allergen, "ingredients")
    

    # 위험도 메시지 파일명도 영어로
    risk_filename_mapping = {
        "High Risk Group": "high_risk.mp3",
        "Risk Group": "risk.mp3",
        "Caution Group": "caution.mp3"
    }

    # 위험도 메시지 음성 파일 생성/재생
    risk_message = ""
    if risk_level == "High Risk Group":
        risk_message = "섭취하지 마십시오"
    elif risk_level == "Risk Group":
        risk_message = "주의해 주십시오"
    elif risk_level == "Caution Group":
        risk_message = "참고해 주십시오"
    else:
        risk_message = "알 수 없는 위험 수준."
    
    risk_filename = risk_filename_mapping.get(risk_level, "unknown_risk.mp3")
    category = "warnings"

    text_to_speak_adv(risk_filename, risk_message, category)



def speak_base_warning():
    audio_file_name = "base_warning.mp3"
    text = "알레르기 성분이 포함되어 있습니다"
    category = "warnings" 

    text_to_speak_adv(audio_file_name, text, category)
