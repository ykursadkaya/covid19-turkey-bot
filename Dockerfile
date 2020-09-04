FROM python:3.8.5-alpine

WORKDIR /src

COPY requirements.txt ./

RUN pip --no-cache-dir install -r requirements.txt

ENV TELEGRAM_API_TOKEN api_token
ENV TELEGRAM_CHAT_ID chat_id
ENV COVIDAPI_URL api_url

COPY main.py ./

ENTRYPOINT ["python", "main.py"]
