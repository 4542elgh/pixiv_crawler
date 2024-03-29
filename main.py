from seleniumUtil import SeleniumUtil
from datetime import datetime
import shutil
import os
import schedule
import time
import requests

def main():
    if datetime.today().day == 1:
        # This should match Dockerfile project root
        root_path = "/app/"
        output_path = os.path.join(root_path,"output")

        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path)

        # Init
        se = SeleniumUtil(root_path)
        se.load_cookies()

        # Go to Monthly rank page and go from ID 1 to ID 100
        se.pixiv_monthly_rank()
        
        # 7zip into .zip file (.7z file seem to corrupt for some reason)
        date = str(datetime.now())
        file_name = "Pixiv_"+date.split("-")[1]+"_"+date.split("-")[0]+"_Monthly_Rank.zip"

        if os.path.exists("/run/secrets/zip-pass"):
            passwd = open("/run/secrets/zip-pass").read()
        else:
            passwd = ""

        os.system("7z a "+file_name+" "+root_path+"output/* -p"+passwd)

        # Move to bind mount dir so host system can get zip
        shutil.move(os.path.join(root_path,file_name), "/download/"+file_name)

        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path)

        notify_endpoint = "http://tasks.proxmox-self_notifier:88/send"
        json = {
            "send_method": "discord",
            "payload": "Pixiv monthly crawler finished and stored under "+"\\\\fiber.home.lan\\Photo\\Pixiv\\"+file_name,
            "channel": "manga"
        }
        requests.post(notify_endpoint, json)

def reminder():
    if datetime.today().day == 1:
        notify_endpoint = "http://tasks.proxmox-self_notifier:88/send"
        json = {
            "send_method": "discord",
            "payload": "Pixiv crawler will start in an hour, please have an up to date cookies.pkl in /WDZFS/Docker/self/pixiv_crawler",
            "channel": "manga"
        }
        requests.post(notify_endpoint, json)

def schedule_job():
    schedule.every().day.at("10:00").do(main)
    schedule.every().day.at("09:00").do(reminder)
    while True:
        schedule.run_pending()

        # every half hour check scheduler
        time.sleep(1800)

if __name__ == "__main__":
    schedule_job()
