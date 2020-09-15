#FROM python:2
FROM ubuntu:latest

#Copy/Add relevant part of the python project
ADD soccer ./soccer
ADD tests ./tests
COPY setup.py ./
COPY requirements.txt ./

#Install python environment
RUN apt-get update -y
RUN apt-get install software-properties-common apt-utils curl -y
RUN add-apt-repository universe
RUN apt-get install python2 -y
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
RUN python2 get-pip.py
RUN apt-get install python3-pip -y

#Check/Test what works or not
RUN pip --version
RUN pip3 --version
RUN whoami
RUN pwd
RUN python2 -V
RUN pip -V
#RUN tree .

RUN pip install --no-cache-dir -r requirements.txt
RUN python2 setup.py install

#COPY . .

#CMD [ "python", "./your-daemon-or-script.py" ]
