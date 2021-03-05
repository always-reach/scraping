from dataclasses import dataclass
from icecream import ic
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import time
import requests
import os

from typing import List


@dataclass
class Scraping:
    # 検索する単語
    word: str
    # 探索する画像の枚数
    num: int

    def __post_init__(self):
        if self.num > 400:
            self.num = 400
            print("探索できる最大件数は400までです。")

    def get_image_url(self) -> List[str]:
        """
        クロームを起動。
        指定されたキーワードについて画像検索
        指定された数だけ画像のURLを取得
        :return: URLの配列
        """
        op: Options = Options()
        # seleniumのオプション
        op.add_argument("--disable-gpu")
        op.add_argument("--disable-extensions")
        op.add_argument("--proxy-server='direct://'")
        op.add_argument("--proxy-bypass-list=*")
        op.add_argument("--start-maximized")
        op.add_argument("--headless")

        # Chrome立ち上げ(オプションで画面上に現れないように設定)
        driver: webdriver = webdriver.Chrome(options=op)
        driver.implicitly_wait(2)
        # 検索用URL
        search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
        # URLの設定
        print("launch browser")
        driver.get(search_url.format(q=self.word))
        # ページをスクロールして読み込める画像を増加
        try:
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)
                # サムネイルを取得
                thumbnail_results = driver.find_elements_by_css_selector("img.rg_i")
                print(len(thumbnail_results))
                if len(thumbnail_results) >= self.num:
                    print("Search finished!")
                    break
                else:
                    print("now searching")

            # URLのリスト
            image_urls = []
            # 各サムネイルごとに処理
            count: int = 0
            for img in thumbnail_results:
                try:
                    # サムネイルをクリック
                    print("click image")
                    img.click()
                    time.sleep(2)
                except Exception:
                    continue
                # 一発でurlを取得できないので、候補を出してから絞り込む
                # 'n3VNCb'は変更されることある
                url_candidates = driver.find_elements_by_class_name('n3VNCb')
                # 候補ごとに処理
                for candidate in url_candidates:
                    url = candidate.get_attribute('src')
                    if url and 'https' in url:
                        # jpg画像のURLをリストにセット
                        if os.path.splitext(url)[1] == ".jpg":
                            ic(url)
                            image_urls.append(url)
                            count += 1
                            if count >= self.num:
                                raise Exception
        except Exception:
            pass

        time.sleep(5)
        driver.quit()
        return image_urls

    def download_img(self, url_list: List[str]):
        """
        URLの画像をダウンロード
        :param url_list: URLのリスト
        :return: 無し
        """
        # 警告を無視
        urllib3.disable_warnings(InsecureRequestWarning)
        # リストをループ
        for index, url in enumerate(url_list):
            try:
                with requests.get(url, verify=False, stream=True)as res:
                    with open('./顔_元画像/' + self.word + '/' + format(index, '03') + self.word + '.jpg', 'wb')as image:
                        image.write(res.content)
            except Exception:
                print("Failed download")

    def make_directory(self):
        """
        画像保存用のディレクトリを作成
        :return:無し
        """
        # ディレクトリが存在しない場合
        if not os.path.isdir(self.word):
            # 作成
            os.makedirs(self.word)
            ic("make directory " + self.word)
        else:
            ic("The folder : " + self.word + " already exists.")


if __name__ == '__main__':
    human_name = ['花澤香菜']
    scraping = Scraping('', 400)
    for name in human_name:
        scraping.word = name
        image_url = scraping.get_image_url()
        scraping.make_directory()
        scraping.download_img(image_url)
