#FROM python:2
FROM ubuntu:latest

#Copy/Add relevant part of the python project
ADD soccer ./soccer
ADD tests ./tests
COPY setup.py ./
COPY requirements.txt ./
RUN apt-get update -y
RUN add-apt-repository universe
RUN apt-get install python2 -y
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
RUN python2 get-pip.py
RUN sudo apt install python3-pip



#Check/Test what works or not
RUN whoami
RUN pwd
RUN python -V
RUN pip -V
#RUN tree .

RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

#CMD [ "python", "./your-daemon-or-script.py" ]
