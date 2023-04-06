import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import time
import datetime
import json
import pandas as pd
import os

from utils import *

"""
사람인 크롤링
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

- 경력
- 학력
- 근무형태
- 급여
- 근무일시

없는 경우 있음
- 근무지역
- 필수사항
- 우대사항

- 접수 시작일
마감일은 없는 경우도 있음 -> 채용시 마감
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
        # columns = ["url", "기업명", "기업명", "스크랩 수", "경력", "학력", "근무형태", "급여", "근무지역", "필수사항", "우대사항", "접수 시작일", "접수 마감일"]

        for search_word in self.search_words:
            page = 1
            search_url = f"{self.base_url}&searchword={search_word}&recruitPage={page}"
            # result = pd.DataFrame(columns=columns)
            result = pd.DataFrame()
            while True:
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

                # 채용 공고 페이지로 이동
                idx = 0
                for link in job_tit_links:
                    # url
                    url = link.replace("relay/", "")
                    response = requests.get(url, headers=self.headers[0])
                    soup = BeautifulSoup(response.content, "lxml")

                    # 회사, 공고명, 스크랩 수
                    company = text_filter(soup.select_one("div.title_inner a.company").text)
                    title = text_filter(soup.select_one("h1.tit_job").text)
                    scrap_count = text_filter(soup.select_one("div.jv_header span.txt_scrap").text)

                    # 경력, 학력, 근무형태, 급여, 근무일시, 근무지역 추출
                    # 필수사항, 우대사항, 직급/직책은 없는 경우 있긴 하지만 일단 추출함
                    # default: dict_keys(['경력', '학력', '근무형태', '급여', '근무일시', '근무지역'])
                    summary_dict = {}
                    summary_list = soup.select("div.jv_summary div.col dl")
                    for li in summary_list:
                        key = text_filter(li.select_one("dt").text)
                        dd_tag = li.select_one("dd")
                        dd_first_str = text_filter(str(next(dd_tag.stripped_strings)))
                        details = dd_tag.select("ul.toolTipTxt li")
                        details_str = ""
                        # 상세보기가 있는 경우
                        if details:
                            for detail in details:
                                detail_key = text_filter(detail.select_one("span").text)
                                detail_key = "".join(detail_key.split())
                                detail_val = text_filter(detail.text[len(detail_key):])
                                if details_str == "":
                                    details_str += f"{detail_key}:{detail_val}"
                                else:
                                    details_str += f"|{detail_key}:{detail_val}"
                        # 기본 텍스트가 없고, 상세보기만 있는 경우
                        if key == dd_first_str:
                            val = details_str
                        else:
                            val = text_filter(dd_tag.text)
                            # 기본 텍스트, 상세보기 둘 다 있는 경우
                            if details:
                                details_origin_str = text_filter(li.select_one("dd").select_one("div.toolTipWrap").text)
                                val = val[:-len(details_origin_str) + len(details) + 1]
                        summary_dict[key] = val

                    # 근무지역이 뒤에 지도 텍스트가 같이 들어와서 자름
                    if "근무지역" in summary_dict:
                        summary_dict["근무지역"] = " ".join(summary_dict["근무지역"].split()[:-1])


                    period_list = soup.select("dl.info_period dd") 
                    # YYYY.MM.DD HH:MM 형식
                    start = text_filter(period_list[0].text)
                    # 마감일은 없는 경우 있음
                    if len(period_list) == 2:
                        end = text_filter(period_list[1].text)
                    else:
                        end = "채용시 마감"

                    data = {"url": url,
                            "기업명": company,
                            "공고명": title,
                            "스크랩 수": scrap_count,
                            "경력": summary_dict.get("경력", "X"),
                            "학력": summary_dict.get("학력", "X"),
                            "근무형태": summary_dict.get("근무형태", "X"),
                            "급여": summary_dict.get("급여", "X"),
                            "근무지역": summary_dict.get("근무지역", "X"),
                            "필수사항": summary_dict.get("필수사항", "X"),
                            "우대사항": summary_dict.get("우대사항", "X"),
                            "접수 시작일": start,
                            "접수 마감일": end,
                    }
                    result = pd.concat([result, pd.DataFrame(data, index=[idx])])
                    idx += 1
                    # print_data(data)
                page += 1
            self.save_to_csv(result, search_word)


    def save_to_csv(self, df, keyword):
        file_name = f"{keyword}.csv"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)                    
        file_path = os.path.join(self.save_dir, file_name)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f'{file_name} is saved at {file_path}')


    def save_to_json(self, keyword):
        file_name = f"{keyword}.json"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)                    
        file_path = os.path.join(self.save_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent='\t')
        print(f'{file_name} is saved at {file_path}')
