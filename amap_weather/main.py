import requests
import os
import logging
import pandas
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget

citydata_path = "./AMap_adcode_citycode_20210406.xlsx"


def load_citycode_xlsx(path: str):
    try:
        xlsx_data = pandas.read_excel(
            path,
            header=None,
            names=["city", "adcode", "citycode"],  # pyright: ignore[reportArgumentType]
            skiprows=2,
        )
    except FileNotFoundError:
        print("AMap_adcode_citycode_20210406.xlsx 不存在")
        exit(1)
    return xlsx_data


def init_log():
    global logger
    logger = logging.getLogger("Logging")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_hander = logging.StreamHandler()
    console_hander.setLevel(logging.DEBUG)
    console_hander.setFormatter(formatter)

    logger.addHandler(console_hander)


class weather_info:
    api_url = "https://restapi.amap.com/v3/weather/weatherInfo"
    url_parms: dict
    raw_data: dict
    weather_data: dict

    def __init__(self, city_code=None) -> None:
        if city_code == None:
            city_code = self.find_city()
        self.url_parms = {"key": key, "city": city_code}
        self.raw_data = self.get_data()
        self.weather_data = self.raw_data["lives"][0]

    def find_city(self) -> int:
        while True:
            try:
                city_name = input("请输入城市：")
                code = city_data[city_data["city"] == city_name]["adcode"].values[0]  # pyright: ignore[reportAttributeAccessIssue]
                break
            except IndexError:
                print("城市错误")
                pass
        return code

    def get_data(self) -> dict:
        response = requests.get(url=self.api_url, params=self.url_parms)
        data = response.json()

        if data.get("status") != "1":
            logger.error("Data status error!")

        return data

    def print_data(self):
        print(self.weather_data["province"], ", ", self.weather_data["city"], sep="")
        print("天气：\t\t", self.weather_data["weather"], sep="")
        print("气温：\t\t", self.weather_data["temperature"], "°C", sep="")
        print("风向：\t\t", self.weather_data["winddirection"], sep="")
        print("风力：\t\t", self.weather_data["windpower"], "级", sep="")
        print("空气湿度：\t", self.weather_data["humidity"], "%", sep="")


class GuiPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("高德开发平台天气API")
    def init_UI(self):
        pass

        

def cli():
    global city_data
    global key
    city_data = load_citycode_xlsx(citydata_path)
    print("""
    API: 高德开发平台 API
    设置系统变量 AMAP_API 为 API
          """)
    try:
        key = os.environ["AMAP_API"]
    except KeyError:
        print("AMAP_API 不存在")
        exit(2)
    init_log()
    w = weather_info()
    w.print_data()

def gui():
    app = QApplication(sys.argv)
    g = GuiPanel()
    g.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    cli()

