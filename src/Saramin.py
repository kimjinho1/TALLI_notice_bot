import requests
from bs4 import BeautifulSoup
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
    def __init__(self, day, save):
        self.day = day
        self.save = save
        self.save_dir = "result"
        self.origin_url = "https://www.saramin.co.kr"
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=40&recruitSort=reg_dt"
        self.search_words = ["CRA", "CRC", "연구간호사", "보건관리자", "보험심사", "메디컬라이터"]
        # 헤더에 유저 정보를 안 담으면 중간에 계속 차단되는 이슈가 있음
        self.headers = [{'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}]
        self.data = []

    def crawling(self):
        for search_word in self.search_words:
            page = 1
            idx = 0
            # columns = ["url", "기업명", "기업명", "스크랩 수", "경력", "학력", "근무형태", "급여", "근무지역", "필수사항", "우대사항", "접수 시작일", "접수 마감일"]
            result = pd.DataFrame()
            while True:
                search_url = f"{self.base_url}&searchword={search_word}&recruitPage={page}"
                search_response = requests.get(search_url, headers=self.headers[0])
                search_soup = BeautifulSoup(search_response.content, "lxml")

                # 마지막 페이지 확인
                finish = search_soup.select_one("div.info_no_result") 
                if finish is not None:
                    finish
                    break

                # 채용 공고 링크 리스트 추출[40개]
                job_tit_links = []
                area_jobs = search_soup.select("div.area_job") 
                for area_job in area_jobs:
                    job_day = area_job.select_one("span.job_day")
                    job_day_text = text_filter(job_day.text)
                    # 같은 날인지 확인
                    res = check_same_day(job_day_text)
                    if (self.day == "today" and res == False) or (self.day == "all" and res == True):
                        continue
                    job_tit = area_job.select_one("h2.job_tit a[href]")
                    job_tit_link = self.origin_url + job_tit["href"]
                    job_tit_links.append(job_tit_link)
                    

                # 채용 공고 페이지로 이동
                for link in job_tit_links:
                    # url
                    url = link.replace("relay/", "")
                    response = requests.get(url, headers=self.headers[0])
                    soup = BeautifulSoup(response.content, "lxml")

                    # 회사, 공고명, 스크랩 수
                    company = soup.select_one("div.title_inner a.company")
                    title = soup.select_one("h1.tit_job")
                    scrap_count = soup.select_one("div.jv_header span.txt_scrap")
                    if not company or not title or not scrap_count:
                        continue

                    company_text = text_filter(company.text)
                    title_text = text_filter(title.text)
                    scrap_count_text = text_filter(scrap_count.text)

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

                    # data = {"키워드": search_word,
                    #         "기업명": company_text,
                    #         "공고명": title_text,
                    #         "스크랩 수": scrap_count_text,
                    #         "경력": summary_dict.get("경력", "X"),
                    #         "학력": summary_dict.get("학력", "X"),
                    #         "근무형태": summary_dict.get("근무형태", "X"),
                    #         "급여": summary_dict.get("급여", "X"),
                    #         "근무지역": summary_dict.get("근무지역", "X"),
                    #         "필수사항": summary_dict.get("필수사항", "X"),
                    #         "우대사항": summary_dict.get("우대사항", "X"),
                    #         "접수 시작일": start,
                    #         "접수 마감일": end,
                    #         "url": url,
                    # }
                    data = {
                            "title": title_text, # 공고명
                            # titleImageUrl, 
                            # companyId, 
                            "companyName": company_text, # 회사 이름
                            "category": search_word, # 직종(검색 단어)
                            "start": start, # 시작일
                            "deadline": end, # 마감일
                            "scrapCount": scrap_count_text, # 스크랩 수
                            "experience": summary_dict.get("경력", "X"), # 경력
                            "education": summary_dict.get("학력", "X"), # 학력
                            "requirements": summary_dict.get("필수사항", "X"), # 필수사항
                            "preferences": summary_dict.get("우대사항", "X"), # 우대사항
                            "salary": summary_dict.get("급여", "X"), # 급여
                            "jobType": summary_dict.get("근무형태", "X"), # 근무형태
                            "jobLocation": summary_dict.get("근무지역", "X"), # 근무지역
                            # details
                            # detailsImageUrl
                            "jobWebsite": url, # url(채용 공고 홈페이지)
                    }
                    result = pd.concat([result, pd.DataFrame(data, index=[idx])])
                    idx += 1
                    if (idx >= 20):
                        break                       
                if idx >= 20:
                    break
                page += 1

            if self.save == True:
                self.save_to_csv(result, search_word)
            self.data.append(result)

    def get_data(self):
        return self.data

    def save_to_csv(self, df, keyword):
        file_name = f"{keyword}.csv"  if self.day == "all" else f"{keyword}-{get_current_date().replace('/', '-')}.csv" 
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
