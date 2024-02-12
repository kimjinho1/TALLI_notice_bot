import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os
import uuid

from bigquery import *
from utils import *


class Saramin:
    def __init__(self, day, save):
        self.day = day
        self.save = save
        self.save_dir = "result"
        self.origin_url = "https://www.saramin.co.kr"
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit?&recruitPageCount=30&recruitSort=relation"
        self.search_words = [
            "CRA",
            "CRC",
            "연구간호사",
            "보건관리자",
            "보험심사",
            "메디컬라이터",
        ]
        # self.search_words = [
        #     "CRC",
        # ]
        self.headers = [
            {
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
            }
        ]
        self.old_data = get_all_positions_df()
        self.data = []
        self.current_date_time = datetime.now()
        self.logger = getLogger("saramin")

    # 사람인 전체 크롤링
    def crawling(self):
        self.logger.info("Crawling positions(saramin) start")
        for search_word in self.search_words:
            page = 1
            idx = 0
            result = pd.DataFrame()

            self.logger.info(f"Crawling {search_word} positions start")
            while True:
                search_url = f"{self.base_url}&searchword={search_word}&recruitPage={page}&except_read=&ai_head_hunting=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7"
                search_response = requests.get(search_url, headers=self.headers[0])
                search_soup = BeautifulSoup(search_response.content, "lxml")

                # 마지막 페이지 확인
                finish = search_soup.select_one("div.info_no_result")
                if finish is not None:
                    self.logger.info(f"Crawling {search_word} position finish")
                    break

                # 채용 공고 링크 리스트 추출[30개]
                job_tit_links = []
                area_jobs = search_soup.select("div.area_job")
                for area_job in area_jobs:
                    job_day = area_job.select_one("span.job_day")
                    job_day_text = text_filter(job_day.text)
                    # 같은 날인지 확인
                    res = check_same_day(job_day_text)
                    if (self.day == "today" and res == False) or (
                        self.day == "all" and res == True
                    ):
                        continue
                    job_tit = area_job.select_one("h2.job_tit a[href]")
                    job_tit_link = self.origin_url + job_tit["href"]
                    job_tit_links.append(job_tit_link)

                self.logger.info(
                    f"Crawling {search_word} position, page: {page}, link_count: {len(job_tit_links)} start"
                )

                # 채용 공고 페이지로 이동
                for link in job_tit_links:
                    url = link.replace("relay/", "")
                    try:
                        data = self.get_parsed_data(url)
                    except Exception as e:
                        self.logger.error(f"Error parsing position data: {url}")
                        self.logger.error(e)
                        continue

                    if not data or self.duplicate_check(data):
                        self.logger.info(f"Skipped duplicate position: {url}")
                        continue

                    data["id"] = uuid.uuid4()
                    data["keyword"] = search_word

                    result = pd.concat([result, pd.DataFrame(data, index=[idx])])
                    idx += 1
                    self.logger.info(
                        f"Success parsing position data(idx: {idx}) | url: {url}"
                    )

                    if (self.day == "today" and idx >= 10) or idx > 100:
                        break
                if (self.day == "today" and (page >= 3 or idx >= 10)) or (
                    page > 10 or idx > 100
                ):
                    break
                page += 1

            if self.save == True:
                self.save_to_csv(result, search_word)

            self.data.append(result)
            self.logger.info(f"{len(result)} {search_word} postions is parsed")

    def get_parsed_data(self, url):
        response = requests.get(url, headers=self.headers[0])
        soup = BeautifulSoup(response.content, "lxml")

        # 회사, 공고명, 스크랩 수
        company = soup.select_one("div.title_inner a.company")
        title = soup.select_one("h1.tit_job")
        # scrap_count = soup.select_one(
        #     "div.jv_header span.txt_scrap")
        # if not company or not title or not scrap_count:
        if not company or not title:
            self.logger.warning("Can't found company or time: {url}")
            return None

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
            dd_first_str = text_filter(str(next(dd_tag.stripped_strings)))
            details = dd_tag.select("ul.toolTipTxt li")
            details_str = ""
            # 상세보기가 있는 경우
            if details:
                for detail in details:
                    detail_key = text_filter(detail.select_one("span").text)
                    detail_key = "".join(detail_key.split())
                    detail_val = text_filter(detail.text[len(detail_key) :])
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
                    details_origin_str = text_filter(
                        li.select_one("dd").select_one("div.toolTipWrap").text
                    )
                    val = val[: -len(details_origin_str) + len(details) + 1]

            summary_dict[key] = val

        # 근무지역이 뒤에 지도 텍스트가 같이 들어와서 자름
        if "근무지역" in summary_dict:
            job_location_split_li = summary_dict["근무지역"].split()
            if job_location_split_li[-1] == "지도":
                job_location = " ".join(job_location_split_li[:-1])
                summary_dict["근무지역"] = job_location_filter(job_location)

        # 더 좋은 근무지 위치 정보가 있다면 업데이트
        job_location = self.get_better_job_location(soup)
        if job_location is not None:
            summary_dict["근무지역"] = job_location_filter(job_location)
        else:
            self.logger.warning(f"Can't found job_location: {url}")

        period_list = soup.select("dl.info_period dd")
        # YYYY.MM.DD HH:MM 형식
        start = text_filter(period_list[0].text)
        # 마감일은 없는 경우 있음
        if len(period_list) == 2:
            end = text_filter(period_list[1].text)
            deadline_date_time = datetime.strptime(end, "%Y.%m.%d %H:%M")
            if self.current_date_time > deadline_date_time:
                print("Already closed Position: {url}")
                self.logger.warning("Already closed Position: {url}")
                return None
        else:
            end = "채용시 마감"

        # 연락처 추출
        contact = self.get_contact_info(soup)
        if contact is not None:
            contact_len = len(contact)
            if contact_len < 9 or contact_len > 20:
                self.logger.warning(
                    f"Contact information that may be an outlier has been detected | url: {url}"
                )
            summary_dict["연락처"] = contact_info_filter(contact)
        else:
            self.logger.warning(f"Can't found contact_info: {url}")

        # 이미지 추출
        # image_list = soup.select("div.jv_cont.jv_detail td img")
        # print(image_list)
        # print(len(image_list))

        # 학력이 박사졸, 석사졸인 채용공고 제외
        education = summary_dict.get("학력", "X")
        if "석사" in education or "박사" in education:
            self.logger.warning(f"PhD or Master's degree is not a target: {url}")
            return None

        data = {
            # "id": uuid.uuid4(),
            # "keyword": search_word,
            "companyName": company_text,
            "title": title_text,
            "experience": experience_filter(summary_dict.get("경력", "X")),
            "education": education_filter(education),
            "jobType": job_type_filter(summary_dict.get("근무형태", "X")),
            "salary": summary_dict.get("급여", "X"),
            "jobLocation": summary_dict.get("근무지역", "X"),
            "requirements": summary_dict.get("필수사항", "X"),
            "preferences": summary_dict.get("우대사항", "X"),
            "contact": summary_dict.get("연락처", "X"),
            "start": start,
            "deadline": end,
            "url": url,
            # "titleImageUrl": ,
            # "companyId": ,
            # "scrapCount": scrap_count_text,
            # "details": ,
            # "detailsImageUrl": ,
        }

        return data

    # 근무지 위치 파싱
    def get_better_job_location(self, soup):
        # 더 자세한 위치 정보가 담긴 근무지 위치가 있을 시 근무지역 수정
        bottom_job_location_span = soup.select_one(
            "div.jv_cont.jv_location span.spr_jview.txt_adr"
        )
        middle_job_location_span = soup.select_one(
            "div.wrap_list_template span#template_job_type_aw_post_address"
        )
        extra_job_location_td_list = soup.select("div.wrap_break_recruit td")

        # Case 1: 하단 근무지역이 존재하는 경우
        if bottom_job_location_span:
            job_location = job_location_filter(bottom_job_location_span.text)
            return job_location
        # Case 2: 중단 근무지역이 존재하는 경우
        elif middle_job_location_span:
            job_location = job_location_filter(middle_job_location_span.text)
            return job_location.split(" - ")[0]
        # Case 3: 공고 본문에서 근무지역 or 회사주소가 있는지 확인
        elif extra_job_location_td_list:
            for td in extra_job_location_td_list:
                td_text = td.text
                # EX) ㆍ근무지역 : (110-850) 서울 종로구 효제동 20 우일빌딩
                # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46512518&location=ts&searchword=CRA&searchType=search&paid_fl=n&search_uuid=9c36f5e9-3b77-40fe-949a-afa4a6ea67b5
                if "근무지역" in td_text:
                    start_idx = td_text.find("근무지역")
                    end_idx = td_text.find("ㆍ", start_idx + 10)
                    if end_idx == -1:
                        job_location = job_location_filter(td_text[start_idx:])
                    # 잘못된 경우 있음, 중간에 공백이 많아서 다음 end_idx가 근무지역을 포함하지 않은 경우
                    # -> 길이가 strip되어 짧아져서 버그가 나옴 -> 일단 데이터 파싱 중에 버그나면 저장안하도록 수정해놓음
                    else:
                        job_location = job_location_filter(td_text[start_idx:end_idx])
                    return job_location[7:]
                # EX) - 회사주소 : 경기 용인시 수지구 손곡로 17
                # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46587286&location=ts&searchword=%EB%A9%94%EB%94%94%EC%BB%AC%EB%9D%BC%EC%9D%B4%ED%84%B0&searchType=search&paid_fl=n&search_uuid=060232a0-7395-47f2-9bd7-12a3ef73425f
                elif "회사주소" in td_text:
                    start_idx = td_text.find("회사주소")
                    end_idx = td_text.find("-", start_idx + 15)
                    if end_idx == -1:
                        job_location = job_location_filter(td_text[start_idx:])
                    else:
                        job_location = job_location_filter(td_text[start_idx:end_idx])
                    return job_location[7:]
        # Case 4: 자세한 근무지역 정보가 아예 존재하지 않는 경우
        else:
            return None

    # 연락처 정보 파싱 -> 근무지 위치 파싱과 비슷함
    def get_contact_info(self, soup):
        contact_info_dd = soup.select_one("div.jv_cont.jv_howto dl.guide dd.info")
        extra_contact_info_list = soup.select("div.wrap_break_recruit td")

        # Case 1: 접수기간 및 방법에 존재하는 경우
        if contact_info_dd:
            # EX) 02-2621-2297
            # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46569782&location=ts&searchword=CRA&searchType=search&paid_fl=n&search_uuid=1ef8ff53-0c68-47e9-8459-3ddd8fae6ca0
            contact_info = text_filter(contact_info_dd.text)
            return contact_info
        # Case 2: 공고 본문에서 연락처 or 전화가 있는지 확인
        elif extra_contact_info_list:
            for td in extra_contact_info_list:
                td_text = td.text
                # EX) ㆍ연락처 : 02-2277-3935
                # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46512518&location=ts&searchword=CRA&searchType=search&paid_fl=n&search_uuid=98bf7c99-311d-4285-bd3f-e6f2370056e6
                if "연락처" in td_text:
                    start_idx = td_text.find("연락처")
                    end_idx = td_text.find("ㆍ", start_idx + 10)
                    if end_idx == -1:
                        contact_info = text_filter(td_text[start_idx:])
                    else:
                        contact_info = text_filter(td_text[start_idx:end_idx])
                    return contact_info[6:]
                # EX) - 전화 : 031-270-5110
                # https://www.saramin.co.kr/zf_user/jobs/view?view_type=search&rec_idx=46587286&location=ts&searchword=%EB%A9%94%EB%94%94%EC%BB%AC%EB%9D%BC%EC%9D%B4%ED%84%B0&searchType=search&paid_fl=n&search_uuid=ea6362ab-030b-4733-9a92-a14bbadccfd2
                elif "전화 : " in td_text:
                    start_idx = td_text.find("전화 : ")
                    end_idx = td_text.find("-", start_idx + 15)
                    if end_idx == -1:
                        contact_info = text_filter(td_text[start_idx:])
                    else:
                        contact_info = text_filter(td_text[start_idx:end_idx])
                    return contact_info[5:]
        # Case 3: 연락처 정보가 아예 존재하지 않는 경우
        else:
            return None

    def duplicate_check(self, data):
        for dt in self.data:
            if len(dt) > 0:
                # duplicate_check = (dt["companyName"] == data["companyName"]) & (
                #     dt["title"] == data["title"]
                # ) & (dt["url"]) == data["url"]
                duplicate_check = (dt["companyName"] == data["companyName"]) & (
                    dt["title"] == data["title"]
                ) | (dt["url"] == data["url"])

                if duplicate_check.any():
                    return True

        if self.old_data is not None and not self.old_data.empty:
            duplicate_check = (self.old_data["companyName"] == data["companyName"]) & (
                self.old_data["title"] == data["title"]
            ) | (self.old_data["url"] == data["url"])

            if duplicate_check.any():
                return True

        return False

    # 마감된 채용 공고인지 확인(회사가 직접 마감 시키는 경우)
    def check_position_closed(self, url):
        response = requests.get(url, headers=self.headers[0])
        soup = BeautifulSoup(response.content, "lxml")

        is_closed = soup.select_one("span.sri_btn_expired_apply")
        if is_closed:
            is_closed_text = text_filter(is_closed.text)
            if is_closed_text == "접수마감":
                return True

        return False

    # 마감된 채용 공고들 목록 반환
    def get_closed_positions(self, positions_without_deadline):
        closed_positions = set()
        for position in positions_without_deadline:
            id = position["id"]
            url = position["url"]

            if self.check_position_closed(url):
                closed_positions.add(id)

        self.logger.info(
            f"Get closed positions from big-query | total: {len(closed_positions)}"
        )
        return closed_positions

    def logUpdatedFieldInfo(self, data, updated_data, updated_fields):
        log = f"position updated | url: {data['url']}"
        for field in updated_fields:
            log += (
                f"\n   {field} field updated '{data[field]}' => '{updated_data[field]}'"
            )
        self.logger.info(log)

    # 업데이트된 채용 공고인지 확인
    def check_position_updated(self, url, position):
        data = self.get_parsed_data(url)
        if not data:
            delete_position(position["id"])
            return False

        updated_fields = []
        for key, val in data.items():
            if val != position[key]:
                # null인 경우 -> big-query에서는 ''로 저장하고, 크롤링은 None으로 저장됨
                if val == "" and position[key] == None:
                    continue

                updated_fields.append(key)

        if len(updated_fields) == 0:
            return None, None

        return data, updated_fields

    # 업데이트된 채용 공고들 목록 반환
    def get_updated_positions(self, positions):
        updated_position_ids = set()
        updated_positions = []

        for position in positions:
            id = position["id"]
            url = position["url"]

            updated_data, updated_fields = self.check_position_updated(url, position)
            if updated_data:
                self.logUpdatedFieldInfo(position, updated_data, updated_fields)
                updated_position_ids.add(id)
                updated_data["id"] = id
                updated_positions.append(updated_data)

        self.logger.info(
            f"Get updated positions from big-query | total: {len(updated_position_ids)}"
        )
        return updated_position_ids, updated_positions

    # 데이터 Getter
    def get_data(self):
        return self.data

    # 데이터 csv로 저장
    def save_to_csv(self, df, keyword):
        file_name = (
            f"{keyword}.csv"
            if self.day == "all"
            else f"{keyword}-{get_current_date().replace('/', '-')}.csv"
        )
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"{file_name} is saved at {file_path}")
        return file_name, file_path

    # 모든 데이터 csv로 저장
    def save_all_data_to_csv(self):
        file_name = (
            f"all-data.csv"
            if self.day == "all"
            else f"사람인-{get_current_date().replace('/', '-')}.csv"
        )
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        result = pd.DataFrame()
        for df in self.data:
            result = pd.concat([result, df])
        if len(result) == 0:
            return ""
        result.to_csv(file_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"{file_name} is saved at {file_path}, len: {len(result)}")
        print(f"{file_name} is saved at {file_path}, len: {len(result)}")
        return file_path

    # 결과 json으로 저장
    def save_to_json(self, keyword):
        file_name = f"{keyword}.json"
        if not os.path.isdir(self.save_dir):
            os.makedirs(self.save_dir)
        file_path = os.path.join(self.save_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(self.data, json_file, ensure_ascii=False, indent="\t")
        self.logger.info(f"{file_name} is saved at {file_path}")
        print(f"{file_name} is saved at {file_path}")
        return file_path
