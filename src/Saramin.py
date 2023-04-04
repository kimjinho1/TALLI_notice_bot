import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import time
import datetime
import json
import os

"""
사람인(https://www.saramin.co.kr/zf_user/) 크롤링
TODO: 1. CRA 
TODO: 2. CRC
TODO: 3. 연구간호사
TODO: 4. 보건관리자
TODO: 5. 보험심사
TODO: 6. 메디컬라이터

## URL 파악
처음에 채용 페이지가 [1, 2, 3] 같은 식이 아니라 "더보기"로 되어 있어서 더보기를 한 주소 기준으로 진행함
기본 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1&recruitSort=relation
zf_user: 로그인 안한 상태를 의미하는 것 같음
search: 검색 쿼리
 * searchword: 검색할 단어 -> searchword=CRA
 * recruitPage: 검색 결과 페이지 번호 -> 
 * recruitSort: 검색 결과 정렬 -> recruitSort=relation
   수집이 목표니까 필요 없어 보임
 * recruitPageCount: 한 페이지에 보여줄 채용 공고 개수 -> recruitPageCount=40

기준 URL: https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword={키워드}&recruitPage={페이지}
EX) https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&searchword=CRA&recruitPage=1

검색하고 나면 552건 완료 같은 방식으로 총 개수가 나와서 총 페이지 수를 알 수 있음
첫 페이지는 무조건 있으니 첫 페이지 크롤링 할 때 전체 페이지 수를 저장함
EX) max_page = 552 // 40 = 14
"""

class Saramin:
    def __init__(self):
        self.save_dir = "result"
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40"
        self.query_list = ["searchword", "recruitPage"]
        self.headers = [{'User-Agent': UserAgent().ie}]
        self.today = datetime.datetime.today()
        self.data = {}

    def crawling(self):
        a = 1
        # go = 1
        # page = 1
        # while go:
        #     data = {}
        #     params = {'id': 'stockus', 'page': page}
            
        #     response = requests.get(self.base_url, params=params, headers=self.headers[0])    
        #     soup = BeautifulSoup(response.content, 'html.parser')
            
        #     article_list = soup.find('tbody').select('tr')
                
        #     cnt = 0
        #     for tr_item in article_list:
        #         title_subject = tr_item.select('.gall_subject')[0].text
        #         if title_subject != "일반":
        #             continue
                
        #         date = tr_item.select('.gall_date')[0].text
        #         if '.' not in date:
        #             continue
        #         elif date == month_day_format(self.two_days_ago):
        #             go = 0
        #             break
                
        #         title_tag = tr_item.find('a', href=True)
        #         title = title_tag.text

        #         article_response = requests.get(self.article_base_url + title_tag['href'], headers=self.headers[0])
        #         article_url = article_response.url
                
        #         article_id = (title_tag['href'].split('no=')[1]).split('&')[0]

        #         article_soup = BeautifulSoup(article_response.content, 'html.parser')

        #         writer_nickname = article_soup.find('span', class_='nickname').text
                
        #         reporting_date, reporting_time = article_soup.find('span', class_='gall_date').text.split()

        #         up_num = article_soup.find('p', class_='up_num').text
                
        #         down_num = article_soup.find('p', class_='down_num').text

        #         article_contents = article_soup.find('div', class_='write_div').text.strip()
                        
        #         data = {
        #             "title" : title,
        #             "article_url": article_url,
        #             "writer_nickname": writer_nickname,
        #             "reporting_date": reporting_date,
        #             "reporting_time": reporting_time,
        #             "up_num": up_num,
        #             "down_num": down_num,
        #             "article_contents": article_contents,
        #         }                

        #         self.article_data[article_id] = data
        #         time.sleep(0.5)


    def save_result(self, keyword):
        filename = f"{keyword}.json"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)                    
        with open(os.path.join(self.save_dir, filename), 'w', encoding='utf-8') as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent='\t')
        print(f"===== Save {filename}  =====\n")


    def check_result(self):
        for value in self.data.values():
            print(value)
