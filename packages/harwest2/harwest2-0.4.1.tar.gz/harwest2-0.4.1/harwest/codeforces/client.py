import base64
import hashlib
import random
import string
import time
from datetime import datetime
from urllib.parse import urlencode

import requests

requests.packages.urllib3.disable_warnings()


class CodeforcesClient:
    API = "https://codeforces.com/api/"
    CONTEST_URL = "https://codeforces.com/contest/{contest_id}/problem/{problem_index}"
    SUBMISSION_URL = "https://codeforces.com/contest/{contest_id}/submission/{submission_id}"

    CODE_ENCODING = "utf-8"

    # count of submissions per requests to the api
    PAGE_SIZE_LIMIT = 50

    def __init__(self, codeforces_data):
        self.user = codeforces_data["handle"]
        self.api_key = codeforces_data["api_key"]
        self.api_scret = codeforces_data["api_secret"]

        self.session = requests.Session()

    def __get_api_request(self, endpoint, params):
        params["apiKey"] = self.api_key
        params["time"] = str(int(time.time()))

        sorted_params = sorted(params.items(), key=lambda item: (item[0], item[1]))
        salt = "".join(random.choices(string.ascii_letters, k=6))
        to_hash = "{salt}/{endpoint}?{params}#{secret}".format(
            salt=salt,
            endpoint=endpoint,
            params=urlencode(sorted_params),
            secret=self.api_scret,
        )
        params["apiSig"] = salt + hashlib.sha512(to_hash.encode()).hexdigest()

        url = CodeforcesClient.API + endpoint + "?" + urlencode(params)
        response = self.session.get(url, verify=False).json()
        if not response["status"] == "OK":
            raise ValueError("Error while fetching submissions: " + response["comment"])
        return response

    def __get_user_submissions(self, page_index, count, include_sources=False):
        return self.__get_api_request(
            "user.status",
            {
                "handle": self.user,
                "from": (page_index - 1) * CodeforcesClient.PAGE_SIZE_LIMIT + 1,
                "count": count,
                "includeSources": "true" if include_sources else "false",
            },
        )

    def __get_url_content(self, url):
        return self.session.get(url, verify=False).content

    @staticmethod
    def get_platform_name():
        return "Codeforces", "CF"

    def get_submissions_page_count(self):
        pages = 0

        while True:
            pages += 1

            submissions = len(
                self.__get_user_submissions(pages, CodeforcesClient.PAGE_SIZE_LIMIT)["result"]
            )
            if submissions < CodeforcesClient.PAGE_SIZE_LIMIT:
                if submissions == 0:
                    pages -= 1
                break

        return pages

    def get_submission_code(self, submission):
        response = self.__get_user_submissions(submission["page"], 1, include_sources=True)
        code_base64 = response["result"][0]["sourceBase64"]
        return base64.b64decode(code_base64).decode(CodeforcesClient.CODE_ENCODING)

    def get_user_submissions(self, page_index):
        response = self.__get_user_submissions(page_index, CodeforcesClient.PAGE_SIZE_LIMIT)

        submissions = []
        for row in response["result"]:
            if "verdict" not in row.keys():
                continue
            if "contestId" not in row.keys():
                continue
            if row["testset"] != "TESTS":
                continue

            contest_id = row["contestId"]
            if contest_id > 100000:
                continue  # Ignore gym submissions

            status = row["verdict"]
            if status != "OK":
                continue  # Only process accepted solutions

            submission_id = int(row["id"])

            problem = row["problem"]
            problem_index = problem["index"]
            problem_name = problem["name"]
            tags_list = problem["tags"]
            if "rating" in problem:
                tags_list.append("*" + str(problem["rating"]))

            contest_url = CodeforcesClient.CONTEST_URL.format(
                contest_id=contest_id, problem_index=problem_index
            )
            lang_name = row["programmingLanguage"]

            # print(submission_id, contest_id, problem_name, lang_name, contest_url)

            timestamp = row["creationTimeSeconds"]
            date_time_str = datetime.fromtimestamp(timestamp).strftime("%b/%d/%Y %H:%M")

            sub_url = CodeforcesClient.SUBMISSION_URL.format(
                contest_id=contest_id, submission_id=submission_id
            )
            submission = {
                "contest_id": contest_id,
                "problem_index": problem_index,
                "problem_url": contest_url,
                "problem_name": problem_name,
                "language": lang_name,
                "timestamp": date_time_str,
                "tags": tags_list,
                "submission_id": submission_id,
                "submission_url": sub_url,
                "platform": self.get_platform_name()[0],
                "page": page_index,
            }
            submissions.append(submission)
        return submissions
