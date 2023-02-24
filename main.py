from seleniumUtil import SeleniumUtil
from datetime import datetime
import shutil
import os
import schedule
import time

def main():
    if datetime.today().day == 1:
        # This should match Dockerfile project root
        root_path = "/app/"

        os.makedirs(os.path.join(root_path,"output"))

        # Init
        se = SeleniumUtil(root_path)
        se.load_cookies()

        # Go to Monthly rank page and go from ID 1 to ID 100
        se.pixiv_monthly_rank()
        
        # 7zip into .zip file (.7z file seem to corrupt for some reason)
        date = str(datetime.now())
        file_name = "Pixiv_"+date.split("-")[1]+"_"+date.split("-")[0]+"_Monthly_Rank.zip"
        os.system("7z a "+file_name+" "+root_path+"output/* -p"+os.getenv("ZIP_PASSWORD"))

        # Move to bind mount dir so host system can get zip
        shutil.move(os.path.join(root_path,file_name), "/download/"+file_name)

def schedule_job():
    schedule.every().day.at("10:00").do(main)
    while True:
        schedule.run_pending()

        # every half hour check scheduler
        time.sleep(1800)

if __name__ == "__main__":
    schedule_job()
