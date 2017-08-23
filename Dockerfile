FROM python:3-slim

WORKDIR /financescraper

ADD . /financescraper

RUN pip install -r requirements.txt

ENV AWS_DEFAULT_REGION us-east-1

CMD ["python", "application.py"]