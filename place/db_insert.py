import csv
import os
import django
import sys
import ast


# 현재 디렉토리 경로 표시
os.chdir(".")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)

# 프로젝트명.settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ConnectMe.settings")
django.setup()

from place.models import Place, PlaceImage
from user.models import User

# csv 파일 경로
CSV_PATH = '../place.csv'	



# encoding 설정 필요
with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:	
    data_reader = csv.DictReader(csvfile)
    
    try:
        for row in data_reader:
            title = row['name']
            address = row['address']
            
            duple = Place.objects.filter(title=title, address=address).first()
            
            if duple:
                print('중복 데이터')
                continue
            
            category = ''
                        
            if row['category'] == '밥':
                category = '식사'
            elif row['category'] == '술':
                category = '주점'
            else:
                category = row['category']
            
            user = User.objects.filter(is_admin=True).first()
                        
            place = Place.objects.create(
                user_id = user.id,
                title = title,
                category = category,
                sort = row['sort'],
                content = row['content'],
                address = address,
                score = row['score'],
                price = row['price'],
                hour = row['hour'],
                holiday = row['holiday'],
            )
            
            # 데이터가 문자열이라 딕셔너리로 변경
            images = ast.literal_eval(row['images'])
            
            for image in images:
                PlaceImage.objects.create(
                    image = image,
                    place_id = place.id,
                )
            print(place.id)
        print('생성 종료')
    except:
        print('권한이 없습니다.')