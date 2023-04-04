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

- 경력
- 학력
- 근무형태
- 급여
- 근무일시

아주 드믈게 없는 경우 있음
- 근무지역

아래 2개는 없는 경우도 있음
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
        for search_word in self.search_words:
            page = 1
            search_url = f"{self.base_url}&searchword={search_word}&recruitPage={page}"

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
                for link in job_tit_links:
                    # url
                    url = link.replace("relay/", "")
                    response = requests.get(url, headers=self.headers[0])
                    soup = BeautifulSoup(response.content, "lxml")

                    # 회사, 공고명, 스크랩 수
                    company = soup.select_one("div.title_inner a.company").text.strip().replace('\\xa0', ' ')
                    title = soup.select_one("h1.tit_job").text.strip().replace('\\xa0', ' ')
                    scrap_count = soup.select_one("div.jv_header span.txt_scrap").text.strip().replace('\\xa0', ' ')

                    # 경력, 학력, 근무형태, 급여, 근무일시, 근무지역 추출
                    # 필수사항, 우대사항, 직급/직책은 없는 경우 있긴 하지만 일단 추출함
                    # default: dict_keys(['경력', '학력', '근무형태', '급여', '근무일시', '근무지역'])
                    summary_dict = {}
                    summary_list = soup.select("div.jv_summary div.col dl")
                    for li in summary_list:
                        key = li.select_one("dt").text.strip().replace('\\xa0', ' ')
                        dd_tag = li.select_one("dd")
                        dd_first_str = str(next(dd_tag.stripped_strings)).strip().replace('\\xa0', ' ')
                        details = dd_tag.select("ul.toolTipTxt li")
                        details_str = ""
                        # 상세보기가 있는 경우
                        if details:
                            for detail in details:
                                detail_key = detail.select_one("span").text.strip().replace('\\xa0', ' ')
                                detail_key = "".join(detail_key.split())
                                detail_val = detail.text.strip().replace('\\xa0', ' ')[len(detail_key):]
                                if details_str == "":
                                    details_str += f"{detail_key}:{detail_val}"
                                else:
                                    details_str += f"|{detail_key}:{detail_val}"
                        # 기본 텍스트가 없고, 상세보기만 있는 경우
                        if key == dd_first_str:
                            val = details_str
                        else:
                            val = dd_tag.text.strip().replace('\\xa0', ' ')
                            # 기본 텍스트, 상세보기 둘 다 있는 경우
                            if details:
                                details_origin_str = li.select_one("dd").select_one("div.toolTipWrap").text
                                val = val[:-len(details_origin_str) + len(details) + 1]
                        summary_dict[key] = val

                    # 근무지역이 뒤에 지도 텍스트가 같이 들어와서 자름
                    if "근무지역" in summary_dict:
                        summary_dict["근무지역"] = " ".join(summary_dict["근무지역"].split()[:-1])


                    period_list = soup.select("dl.info_period dd") 
                    # YYYY.MM.DD HH:MM 형식
                    start = period_list[0].text.strip().replace('\\xa0', ' ')
                    # 마감일은 없는 경우 있음
                    if len(period_list) == 2:
                        end = period_list[1].text.strip().replace('\\xa0', ' ')
                    else:
                        end = "채용시 마감"

                    print("search_word:", search_word)
                    print("page:", page)
                    print("url:", url)
                    print("company:", company)
                    print("title:", title)
                    print("scrap_count:", scrap_count)
                    for k, v in summary_dict.items():
                        print(f"{k}: {v}")
                    print("start:", start)
                    print("end:", end)
                    print()
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
