FROM python:3-slim

WORKDIR /financescraper

ADD . /financescraper

RUN mkdir -p ~/.aws/

# COPY ./credentials ~/.aws/credentials

RUN pip install -r requirements.txt

ENV AWS_DEFAULT_REGION us-east-1

EXPOSE 5000

CMD ["python", "financescraper"]