import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os

from utils import *


class Saramin:
    def __init__(self, day, save):
        self.day = day
        self.save = save
        self.save_dir = "result"
        self.origin_url = "https://www.saramin.co.kr"
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=30&recruitSort=relation"
        self.search_words = ["CRA", "CRC", "연구간호사", "보건관리자", "보험심사", "메디컬라이터"]
        self.headers = [
            {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"}]
        self.data = []

    # 사람인 전체 크롤링
    def crawling(self):
        for search_word in self.search_words:
            page = 1
            idx = 0
            result = pd.DataFrame()
            
            while True:
                search_url = f"{self.base_url}&searchword={search_word}&recruitPage={page}&except_read=&ai_head_hunting=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7"
                search_response = requests.get(
                    search_url, headers=self.headers[0])
                search_soup = BeautifulSoup(search_response.content, "lxml")

                # 마지막 페이지 확인
                finish = search_soup.select_one("div.info_no_result")
                if finish is not None:
                    finish
                    break

                # 채용 공고 링크 리스트 추출[30개]
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
                    # scrap_count = soup.select_one(
                    #     "div.jv_header span.txt_scrap")
                    # if not company or not title or not scrap_count:
                    if not company or not title:
                        continue

                    company_text = text_filter(company.text)
                    title_text = text_filter(title.text)
                    # if scrap_count.text == "스크랩":
                    #     scrap_count_text = "0"
                    # else:
                    #     scrap_count_text = text_filter(scrap_count.text)

                    # 경력, 학력, 근무형태, 급여, 근무일시, 근무지역 추출
                    # 필수사항, 우대사항, 직급/직책은 없는 경우 있긴 하지만 일단 추출함
                    # default: dict_keys(['경력', '학력', '근무형태', '급여', '근무일시', '근무지역'])
                    summary_dict = {}
                    summary_list = soup.select("div.jv_summary div.col dl")
                    for li in summary_list:
                        key = text_filter(li.select_one("dt").text)
                        dd_tag = li.select_one("dd")
                        dd_first_str = text_filter(
                            str(next(dd_tag.stripped_strings)))
                        details = dd_tag.select("ul.toolTipTxt li")
                        details_str = ""
                        # 상세보기가 있는 경우
                        if details:
                            for detail in details:
                                detail_key = text_filter(
                                    detail.select_one("span").text)
                                detail_key = "".join(detail_key.split())
                                detail_val = text_filter(
                                    detail.text[len(detail_key):])
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
                                details_origin_str = text_filter(li.select_one(
                                    "dd").select_one("div.toolTipWrap").text)
                                val = val[:-len(details_origin_str) +
                                          len(details) + 1]

                        summary_dict[key] = val

                    # 근무지역이 뒤에 지도 텍스트가 같이 들어와서 자름
                    if "근무지역" in summary_dict:
                        job_location_split_li = summary_dict["근무지역"].split()
                        if job_location_split_li[-1] == "지도":
                            job_location = " ".join(job_location_split_li[:-1])
                            summary_dict["근무지역"] = job_location_filter(job_location)

                    # 더 자세한 위치 정보가 담긴 근무지 위치가 있을 시 근무지역 수정 
                    bottom_job_location_span = soup.select_one("div.jv_cont.jv_location span.spr_jview.txt_adr")
                    middle_job_location_span = soup.select_one("div.wrap_list_template span#template_job_type_aw_post_address")
                    extra_job_location_td_list = soup.select("div.wrap_break_recruit td")

                    # Case 1: 하단 근무지 위치가 존재하는 경우
                    if bottom_job_location_span:
                        job_location = job_location_filter(bottom_job_location_span.text)
                        summary_dict["근무지역"] = job_location
                        # print(f"Case 1: {job_location}")
                    # Case 2: 중단 근무지 위치가 존재하는 경우
                    elif middle_job_location_span:
                        job_location = job_location_filter(middle_job_location_span.text)
                        summary_dict["근무지역"] = job_location.split(' - ')[0]
                        # print(f"Case 2: {summary_dict['근무지역']}")
                    # Case 3: 근무지역이 어딘가에 무조건 들어있긴 해서 텍스트를 다 확인하면 찾을 수는 있다...
                    elif extra_job_location_td_list:
                        for td in extra_job_location_td_list:
                            td_text = td.text
                            # EX) ㆍ근무지역 : (110-850) 서울 종로구 효제동 20 우일빌딩
                            # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46512518&location=ts&searchword=CRA&searchType=search&paid_fl=n&search_uuid=9c36f5e9-3b77-40fe-949a-afa4a6ea67b5
                            if "근무지역" in td_text:
                                # ㆍ근무형태 : 정규직(수습기간 3개월) 
                                start_idx = td_text.find("근무지역")
                                end_idx = td_text.find('ㆍ', start_idx + 15)
                                if end_idx == -1:
                                    job_location = job_location_filter(td_text[start_idx:])
                                else:
                                    job_location = job_location_filter(td_text[start_idx:end_idx])
                                summary_dict["근무지역"] = job_location_filter(job_location[7:])
                                # print(f"case 3-1: {summary_dict['근무지역']}")
                                break
                            # EX) - 회사주소 : 경기 용인시 수지구 손곡로 17
                            # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46587286&location=ts&searchword=%EB%A9%94%EB%94%94%EC%BB%AC%EB%9D%BC%EC%9D%B4%ED%84%B0&searchType=search&paid_fl=n&search_uuid=060232a0-7395-47f2-9bd7-12a3ef73425f
                            elif "회사주소" in td_text:
                                start_idx = td_text.find("회사주소")
                                end_idx = td_text.find('-', start_idx + 15)
                                if end_idx == -1:
                                    job_location = job_location_filter(td_text[start_idx:])
                                else:
                                    job_location = job_location_filter(td_text[start_idx:end_idx])
                                summary_dict["근무지역"] = job_location_filter(job_location[7:])
                                # print(f"case 3-2: {summary_dict['근무지역']}")
                                break
                    # 근무지역 정보가 아예 존재하지 않는 경우
                    else:
                        print(f"case 4: 자세한 근무지역 정보가 존재하지 않습니다")

                    period_list = soup.select("dl.info_period dd")
                    # YYYY.MM.DD HH:MM 형식
                    start = text_filter(period_list[0].text)
                    # 마감일은 없는 경우 있음
                    if len(period_list) == 2:
                        end = text_filter(period_list[1].text)
                    else:
                        end = "채용시 마감"

                    data = {"키워드": search_word,
                            "기업명": company_text,
                            "공고명": title_text,
                            # "스크랩 수": scrap_count_text,
                            "경력": summary_dict.get("경력", "X"),
                            "학력": summary_dict.get("학력", "X"),
                            "근무형태": summary_dict.get("근무형태", "X"),
                            "급여": summary_dict.get("급여", "X"),
                            "근무지역": summary_dict.get("근무지역", "X"),
                            "필수사항": summary_dict.get("필수사항", "X"),
                            "우대사항": summary_dict.get("우대사항", "X"),
                            "접수 시작일": start,
                            "접수 마감일": end,
                            "url": url,
                            }

                    # data = {
                    #         "title": title_text, # 공고명
                    #         # titleImageUrl,
                    #         # companyId,
                    #         "companyName": company_text, # 회사 이름
                    #         "category": search_word, # 직종(검색 단어)
                    #         "start": start, # 시작일
                    #         "deadline": end, # 마감일
                    #         "scrapCount": scrap_count_text, # 스크랩 수
                    #         "experience": summary_dict.get("경력", "X"), # 경력
                    #         "education": summary_dict.get("학력", "X"), # 학력
                    #         "requirements": summary_dict.get("필수사항", "X"), # 필수사항
                    #         "preferences": summary_dict.get("우대사항", "X"), # 우대사항
                    #         "salary": summary_dict.get("급여", "X"), # 급여
                    #         "jobType": summary_dict.get("근무형태", "X"), # 근무형태
                    #         "jobLocation": summary_dict.get("근무지역", "X"), # 근무지역
                    #         # details
                    #         # detailsImageUrl
                    #         "jobWebsite": url, # url(채용 공고 홈페이지)
                    # }

                    # 학력이 박사졸, 석사졸인 채용공고 제외
                    if data['학력'] in ['석사졸업', '박사졸업']:
                        continue

                    result = pd.concat(
                        [result, pd.DataFrame(data, index=[idx])])
                    idx += 1
                    if (idx >= 10):
                        break
                if page >= 3 or idx >= 10:
                    break
                break ##################################################################
                page += 1

            if self.save == True:
                self.save_to_csv(result, search_word)
            self.data.append(result)

    # 데이터 Getter
    def get_data(self):
        return self.data

    # 데이터 csv로 저장
    def save_to_csv(self, df, keyword):
        file_name = f"{keyword}.csv" if self.day == "all" else f"{keyword}-{get_current_date().replace('/', '-')}.csv"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f'{file_name} is saved at {file_path}')
        return file_path

    # 모든 데이터 csv로 저장
    def save_all_data_to_csv(self):
        file_name = f"all-data.csv" if self.day == "all" else f"사람인-{get_current_date().replace('/', '-')}.csv"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        result = pd.DataFrame()
        for df in self.data:
            result = pd.concat(
                [result, df])
        if len(result) == 0:
            return ""
        result.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f'{file_name} is saved at {file_path}')
        return file_path

    # 결과 json으로 저장
    def save_to_json(self, keyword):
        file_name = f"{keyword}.json"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent='\t')
        print(f'{file_name} is saved at {file_path}')
        return file_path
