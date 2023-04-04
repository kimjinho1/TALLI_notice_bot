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
- 기업명
- 스크랩 수
- 공고명

- 우대사항

TODO:
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
            search_url = f"{self.base_url}&searchword={self.search_words[0]}&recruitPage={page}"
            search_response = requests.get(search_url, headers=self.headers[0])
            search_soup = BeautifulSoup(search_response.content, "lxml")

            # 마지막 페이지 확인
            finish = search_soup.select_one("div.info_no_result") 
            if finish is not None:
                break

            # 채용 공고 링크 리스트 추출[40개]
            job_tit_list = search_soup.select("h2.job_tit a[href]") 
            job_tit_links = []
            for job_tit in job_tit_list:
                job_tit_link = self.origin_url + job_tit["href"]
                job_tit_links.append(job_tit_link)

            for link in job_tit_links:
                # url
                url = link.replace("relay/", "")
                response = requests.get(url, headers=self.headers[0])
                soup = BeautifulSoup(response.content, "lxml")

                # 회사, 공고명, 스크랩 수
                company = soup.select_one("div.title_inner a.company").text.strip()
                title = soup.select_one("h1.tit_job").text.strip()
                scrap_count = soup.select_one("div.jv_header span.txt_scrap").text.strip()

                # 우대사항
                preferred_dict = {}
                preferred_list = soup.select("dd.preferred ul.toolTipTxt li")
                for li in preferred_list:
                    key = li.select_one("span").text.strip()
                    val = li.text[len(key):].strip()
                    preferred_dict[key] = val

                                   

                break

            page += 1
            break


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
