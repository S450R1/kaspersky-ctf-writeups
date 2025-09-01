FROM python:3.12.9

RUN apt update
RUN apt install -y zlib1g-dev udev libnss3 ca-certificates
RUN apt install -y chromium

RUN rm -rf /tmp/* /var/lib/apt/lists/* /usr/share/man

RUN pip install --break-system-packages --no-cache-dir selenium aiohttp chromedriver-autoinstaller

RUN mkdir -p /home/bot/data/

WORKDIR /app

COPY *.py .
COPY flag.txt .
COPY static static/

RUN python3 install.py

CMD python3 bot.py && python3 server.py