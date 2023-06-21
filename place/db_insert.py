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

from place.models import *

# csv 파일 경로
CSV_PATH = 'place.csv'	



# encoding 설정 필요
with open(CSV_PATH, newline='', encoding='utf-8-sig') as csvfile:	
    data_reader = csv.DictReader(csvfile)

    for row in data_reader:
        title = row['name']
        address = row['address']
        
        duple = Place.objects.filter(title=title, address=address).first()
        
        if duple:
            print('중복 데이터')
            continue
                    
        place = Place.objects.create(
            user_id = 1,
            title = title,
            category = row['category'],
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
                place_id = place.pk,
            )
        print(place.pk)
    print('생성 종료')