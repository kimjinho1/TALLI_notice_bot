import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from tqdm.auto import tqdm
import time
import datetime
import json
import os

"""
TODO: 사람인 크롤링
1. CRA 
2. CRC
3. 연구간호사
4. 보건관리자
5. 보험심사
6. 메디컬라이터

수집 항목
- URL
- 공고명
- 기업명
- 경력
- 학력
- 근무형태
- 급여
- 근무일시
- 근무지역
- 접수 시작일
- 접수 마감일
"""

class Saramin:
    def __init__(self):
        self.save_dir = "result"
        self.origin_url = "https://www.saramin.co.kr"
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40"
        self.search_words = ["CRA", "CRC", "연구간호사", "보건관리자", "보험심사", "메디컬라이터"]
        # self.query_list = ["&searchword=", "&recruitPage="]
        # 헤더에 유저 정보를 안 담으면 중간에 계속 차단되는 이슈가 있음
        # self.headers = [{'User-Agent': UserAgent().ie}]
        self.headers = [{'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}]
        self.today = datetime.datetime.today()
        self.data = {}

    def crawling(self):
        page = 1
        while True:
            url = f"{self.base_url}&searchword={self.search_words[0]}&recruitPage={page}"
            response = requests.get(url, headers=self.headers[0])
            soup = BeautifulSoup(response.content, "lxml")
            finish = soup.select_one(".info_no_result") 

            job_tit_list = soup.select("h2.job_tit a[href]") 
            job_tit_links = []
            for job_tit in job_tit_list:
                job_tit_link = self.origin_url + job_tit["href"]
                job_tit_links.append(job_tit_link)

            if finish is not None:
                break

            page += 1
            break

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
