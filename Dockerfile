FROM python:3.7.5-slim
FROM pytorch/pytorch:1.9.0-cuda10.2-cudnn7-devel

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys A4B469963BF863CC
RUN apt-get update && apt-get install -y curl

RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements_movie_api.txt
CMD ["python3","api.py"]