from selenium import webdriver
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
import csv
import re


base_url = 'https://www.menupan.com'

# csv 파일 쓰기
filename = "place.csv"
f = open(filename,"w",encoding="utf-8-sig",newline="")
writer = csv.writer(f)
# 제목 행 추가
row = "name category sort content address images score price hour holiday".split()
writer.writerow(row)

# 페이지 수 확인후 반복
url = 'https://www.menupan.com/restaurant/bestrest/bestrest.asp?page=1&trec=8684&pt=wk'
driver = webdriver.Chrome()
driver.get(url)
# 페이지 로딩 대기
driver.implicitly_wait(2)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
pages_elements = soup.select('div.paging > a:nth-child(14)')[0]['href']
pages = re.sub(r'[^0-9]', '', pages_elements)
driver.close()

# 페이지 반복
for page in range(1, int(pages)):
    url = 'https://www.menupan.com/restaurant/bestrest/bestrest.asp?page='
    # 주간랭킹
    week_url = url+str(page)+'&trec=8684&pt=wk'

    driver = webdriver.Chrome()
    driver.get(week_url)
    # 페이지 로딩 대기
    driver.implicitly_wait(2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    li_tag = driver.find_elements(By.XPATH,'/html/body/div/div[1]/div[1]/div[4]/div[4]/ul/li')
    # 게시글 반복
    for li in range(1, len(li_tag)+1):
        select_title = driver.find_element(By.XPATH,f'/html/body/div/div[1]/div[1]/div[4]/div[4]/ul/li[{li}]/p[2]/span/a')
        select_title.click()

        # 새 페이지 전환
        driver.switch_to.window(driver.window_handles[1])

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            title = soup.select('div.areaBasic > dl.restName > dd')[0].text.strip()
            sort = soup.select('dl.restType > dd')[0].text.strip()
            content = soup.select('#info_ps_f')[0].text.strip()
            address = soup.select('dl.restAdd > dd.add2')[0].text.strip()
            image_elements = soup.select('#id_restphoto_list_ul > div > li')
            score = soup.select('span.total')[0].text.strip()
            price = soup.select('div.restPrice > p.price')[0].text.strip()
            hour = soup.select('ul.tableTopA > li:nth-child(1) > dl > dd')[0].text.strip()
            holiday = soup.select('ul.tableTopA > li:nth-child(3) > dl > dd')[0].text.strip()
            image_list = []
            category = ''
            
            if address:
                address = address[6:]
            else:
                address = soup.select('dl.restAdd > dd.add1')[0].text.strip()
                
                
            if '[' in title:
                title = title.split('[')[0]
            else:
                title
                
                
            if '카페' in sort:
                if sort[-2:] == '카페':
                    category = '카페'
                else:
                    category = '주점'
            else:
                category = '식사'
                
            
            for image in image_elements:
                image_src = image.find('img')['src']
                img = base_url+image_src
                image_list.append(img)
                
            writer.writerow([
                title, 
                category,
                sort, 
                content,
                address,
                image_list, 
                score, 
                price, 
                hour, 
                holiday
                ])
        except:
            pass
        # 페이지 닫기
        driver.close()
        # 페이지 뒤로가기
        driver.switch_to.window(driver.window_handles[0])
    driver.close()
# 종료
driver.quit() 
# 파일 쓰기 종료
f.close()

