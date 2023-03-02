from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
from datetime import datetime, timedelta
import os
import random

import requests # to get image from the web
import shutil # to save it locally

class SeleniumUtil:
    def __init__(self, root_path):
        options = Options()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        chrome_options.add_argument("window-size=1920,1080")

        self.root_path = root_path
        self.driver = webdriver.Chrome(executable_path=r"chromedriver", options=chrome_options)
        self.output = os.path.join(self.root_path,"output")

    def load_cookies(self):
        self.driver.get("https://www.pixiv.net/ranking.php")

        print("Getting cookies from ./cookies.pkl")
        selenium_cookies = pickle.load(open(os.path.join(self.root_path, "cookies.pkl"), "rb"))
        for cookie in selenium_cookies:
            self.driver.add_cookie(cookie)

        print("Parsing cookies for requests lib")
        self.cookies = ''
        for cookie in selenium_cookies:
            self.cookies += '%s=%s;' % (cookie['name'], cookie['value'])
        self.driver.refresh()

    def pixiv_monthly_rank(self):
        # Get first day of the month and fetch from there
        print("Going to Pixiv Monthly Ranking")

        # Need to be T-1 day so it doenst error out
        month = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
        self.driver.get("https://www.pixiv.net/ranking.php?mode=monthly&date="+month)

        for i in range(100):
            # Scroll down 1 page when finish download 10 images
            if i == 10 or i == 20 or i == 30 or i == 40 or i == 50 or i == 60 or i == 70 or i == 80 or i == 90:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)
            # Catch exception if an image is a comic series, skip to next id
            try:
                self.driver.find_element(By.XPATH, '//*[@id="'+str(i+1)+'"]/div[2]/a[1]').click()
            except e:
                print(e)
                continue

            print("Page",i+1)
            # Switch tab
            parent = self.driver.window_handles[0]
            chld = self.driver.window_handles[1]
            self.driver.switch_to.window(chld)

            # Wait for page to load
            print("Wait for image frame to load")
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main')))

            nsfw_button = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main/section/div[1]/div/figure/div/div[1]/div/div/button')

            if len(nsfw_button)>0:
                print("Click on NSFW button")
                nsfw_button[0].click()

            # Get load more and read more button, if they have such button then it contain more than one image
            load_more = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main/section/div[1]/div/div[4]/div/div[2]/button')

            # Read more is comic series
            read_more = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main/section/div[1]/div/div[5]/div/div[2]/button')

            # If load more presents, loop multiple img tags
            if len(load_more)>0 :
                print("Click Load/Read More")
                load_more[0].click()

                time.sleep(1)
                imgs = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main/section/div[1]/div/figure/div[1]')
                for idx,j in enumerate(imgs.find_elements(By.CSS_SELECTOR, "img")):
                    self.download_with_cookies(j.get_attribute("src"), self.output, str(i+1)+"_img_"+str(idx+1)+".jpg")

            # Skip comic and go next
            elif len(read_more)>0:
                print("Skip comic")
                pass

            # Just get single image
            else:
                img = self.driver.find_elements(By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/div/div[1]/main/section/div[1]/div/figure/div[2]')
                if len(img) == 0:
                    continue
                else:
                    self.download_with_cookies(img[0].find_element(By.CSS_SELECTOR, "img").get_attribute("src"), self.output, str(i+1)+"_img_"+str(1)+".jpg")

            # Switch back to parent tab
            self.driver.close()
            self.driver.switch_to.window(parent)

    def download_with_cookies(self, url, folder, filename):
        # Modify url so its getting source image rather than a shrink down preview
        url = url.replace("img-master", "img-original")
        url = "_".join(url.split("_")[0:2])+".jpg"
        print("Downloading with url:", url)

        # Try .jpg extension first, if this link doesnt work, we will try .png
        r = requests.get(
                url, 
                headers={
                     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 
                    'referer' : url,
                    'scheme' : 'https',
                    'accept' : 'image/webp,image/apng,image/*,*/*;q=0.8',
                    "cookies": self.cookies,
                    },
                stream=True
            )
        if r.status_code == 200:
            with open(os.path.join(self.root_path, "output", filename),'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)    
        else:
            url = url.replace("jpg", "png")
            r = requests.get(
                    url, 
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36', 
                        'referer' : url,
                        'scheme' : 'https',
                        'accept' : 'image/webp,image/apng,image/*,*/*;q=0.8',
                        "cookies": self.cookies,
                    },
                    stream=True
                )
            if r.status_code == 200:
                # Filename will need a change too
                filename.replace("jpg","png")
                with open(os.path.join(self.root_path, "output", filename),'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        print("Save image as file:", filename)
