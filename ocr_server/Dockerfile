FROM 10.12.0.78:5000/k8s/python:3.9.0

RUN mkdir -p /data/
COPY . /data/
WORKDIR /data/
RUN mkdir -p /root/.pip/ && \
  cp ./repo/pip.conf /root/.pip/pip.conf

RUN sed -i 's/deb.debian.org/mirrors.cloud.aliyuncs.com/g' /etc/apt/sources.list
RUN sed -i 's/security.debian.org/mirrors.cloud.aliyuncs.com/g' /etc/apt/sources.list

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 poppler-utils -y

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN pip cache purge
RUN apt-get clean

CMD ["python", "main.py"]
