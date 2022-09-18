import re
import requests


class GovForm:
    def __init__(self, instructions: dict) -> None:
        self.instructions = instructions
        self.session = requests.session()
        self.submission_id = ""
        self.cfd_token = ""
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        self.generic_api_request('', 'GET')
        print(self.execute_stages())
        self.generic_api_request(
            'ServiceRequest/Summary', 'POST', {'ID': self.submission_id}, update_token=False)

    def generic_api_request(self, endpoint: str, method: str, body: dict = None, params: dict = {}, update_token=True):
        url = f"https://services.{self.instructions.get('organisation')}.gov.uk/{self.instructions.get('form')}/{endpoint}"
        if self.cfd_token is not "":
            body['__RequestVerificationToken'] = self.cfd_token

        if self.submission_id is not "":
            params['utrn'] = self.submission_id

        response = self.session.request(
            method=method, url=url, verify=False, data=body, params=params)

        if update_token:
            self.update_tokens(response.text)

        return response.text, response.headers

    def update_tokens(self, page: str):
        print(f"Original submission id: {self.submission_id}")
        print(f"Original verification token: {self.cfd_token}")

        self.submission_id = re.findall(r"(?<=/Home/TimeOut\?utrn=)\w\d+",
                                        page)[0]
        self.cfd_token = re.findall(
            r"__RequestVerificationToken.*?value=\"([\w\-]+)", page)[0]

        print(f"New submission id: {self.submission_id}")
        print(f"New verification token: {self.cfd_token}")

    def execute_stages(self):
        stages = self.instructions.get('stages')
        for stage in stages:
            body, headers = self.execute_stage(stage)
        return body

    def execute_stage(self, stage: dict):
        return self.generic_api_request(stage.get('endpoint'),
                                        stage.get('method'),
                                        stage.get('body'),
                                        stage.get('params'))
