import json
import pendulum
import requests
import os

from github_heatmap.loader.base_loader import BaseLoader
from github_heatmap.loader.config import WEREAD_BASE_URL, WEREAD_HISTORY_URL

headers = {
    'User-Agent': "WeRead/8.2.5 WRBrand/xiaomi Dalvik/2.1.0 (Linux; U; Android 12; Redmi Note 7 Pro Build/SQ3A.220705.004)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'baseapi': "32",
    'appver': "8.2.5.10163885",
    'osver': "12",
    'channelId': "11",
    'basever': "8.2.5.10163885",
    'Content-Type': "application/json; charset=UTF-8"
}
class WereadLoader(BaseLoader):
    track_color = "#2EA8F7"
    unit = "mins"

    def __init__(self, from_year, to_year, _type, **kwargs):
        super().__init__(from_year, to_year, _type)

        # self.weread_cookie = kwargs.get("weread_cookie", "")
        self.session = requests.Session()
        self.session.headers = headers
        self.token = os.getenv("REFRESH_TOKEN")
        self.activation_code = os.getenv("ACTIVATION_CODE")
        self.device_id = os.getenv("DEVICE_ID")
        self.refresh_token()
        self._make_years_list()

    @classmethod
    def add_loader_arguments(cls, parser, optional):
        pass
        # parser.add_argument(
        #     "--weread_cookie",
        #     dest="weread_cookie",
        #     type=str,
        #     required=False,
        #     help="",
        # )

    def refresh_token(self):
        body = {"deviceId":self.device_id ,"refreshToken":self.token,"activationCode":self.activation_code}
        r = self.session.post(
            "https://api.notionhub.app/refresh-weread-token", json=body
        )
        if r.ok:
            response_data = r.json()
            vid = response_data.get("vid")
            accessToken = response_data.get("accessToken")
            if vid and accessToken:
                self.session.headers.update({"vid": str(vid), "accessToken": accessToken})
            else:
                print("Failed to refresh token")
        else:
            print("Failed to refresh token")
       
    
    def get_api_data(self):
        r = self.session.get(WEREAD_HISTORY_URL)
        if not r.ok:
            print(r.text)
            # need to refresh cookie
            if r.json()["errcode"] == -2012:
                self.refresh_token()
                r = self.session.get(WEREAD_HISTORY_URL)
            else:
                raise Exception("Can not get weread history data")
        return r.json()

    def make_track_dict(self):
        api_data = self.get_api_data()
        if("readTimes" in api_data):
            readTimes = dict(sorted(api_data["readTimes"].items(), reverse=True))
            for k, v in readTimes.items():
                k = pendulum.from_timestamp(int(k), tz=self.time_zone)
                self.number_by_date_dict[k.to_date_string()] = round(v / 60.0, 2)
            for _, v in self.number_by_date_dict.items():
                self.number_list.append(v)

    def get_all_track_data(self):
        # self.session.cookies = self.parse_cookie_string(self.weread_cookie)
        self.make_track_dict()
        self.make_special_number()
        return self.number_by_date_dict, self.year_list
