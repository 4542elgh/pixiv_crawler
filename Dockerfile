FROM python:3.11.2-bullseye

RUN apt update -y && apt dist-upgrade -y && apt install p7zip-full -y
RUN pip install selenium requests schedule

ARG CHROME_VERSION="110.0.5481.77"
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

WORKDIR ./app

RUN wget --no-verbose -O ./driver.zip https://chromedriver.storage.googleapis.com/${CHROME_VERSION}/chromedriver_linux64.zip \
    && 7z x ./driver.zip \
    && rm driver.zip LICENSE.chromedriver

COPY main.py seleniumUtil.py .

CMD python -u main.py
    # && tail -f /dev/null
