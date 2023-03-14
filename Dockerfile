FROM python:3.11-slim@sha256:7f0ea9ea95d32db6ee8f4973aa76d777923b0cdd83ebec6fd63a20fc7d08f4cf

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
COPY ./favicon.ico /app/favicon.ico
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/HEALTHCHECK

ENTRYPOINT ["streamlit", "run", "./Work-Sheets/WorkSheets/main.py"]