FROM python:3.10

WORKDIR /app/

RUN apt-get update && \
    apt-get install -y \
    wget \
    ca-certificates \
    fonts-noto \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    xdg-utils \
    gnupg \
    xvfb

RUN DEBIAN_FRONTEND=noninteractive && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub > /usr/share/keyrings/chrome.pub && \
    echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/chrome.pub] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list && \
    apt update -y && \
    apt install -y google-chrome-stable

COPY ../requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY ../ /app/

EXPOSE 8000

RUN playwright install

RUN Xvfb $DISPLAY -screen $DISPLAY 1280x1024x16 -ac &

CMD xvfb-run python3 manage.py olx_parser