FROM python:3-slim

WORKDIR /financescraper

ADD . /financescraper

RUN pip install -r requirements.txt

CMD ["python", "main.py", "feed", "-s", "TSLA"]