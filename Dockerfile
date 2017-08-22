FROM python:3-slim

WORKDIR /financescraper

ADD . /financescraper

RUN pip install -r requirements.txt

RUN docker run --env-file ./env.list ubuntu env

CMD ["python", "main.py", "feed"]