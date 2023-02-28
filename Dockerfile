FROM python:3.11-slim@sha256:28e5366ce5c423639950d3962b668730535da08cd235bdacef32171e26cd2b5c

WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \ 
    software-properties-common \
    git \ 
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/fregapple/Work-Sheets.git

RUN pip install -r ./Work-Sheets/requirements.txt

COPY ./.streamlit/secrets.toml /app/.streamlit/secrets.toml
COPY ./apple-touch-icon.png /app/apple-touch-icon.png
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/HEALTHCHECK

ENTRYPOINT ["streamlit", "run", "./Work-Sheets/WorkSheets/main.py"]