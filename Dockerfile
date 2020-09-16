# To build it : docker build -t soccer-cli .
# To run it :  docker run -it --rm --name my-soccer-run soccer-cli soccer --standings --league=PL
#
FROM ubuntu:latest

#Copy/Add relevant part of the python project
WORKDIR /soccer-cli
ADD soccer ./soccer
ADD tests ./tests
COPY setup.py ./
COPY requirements.txt ./
COPY .soccer-cli.ini ./

#Install python environment
RUN apt-get update -y
RUN apt-get install software-properties-common apt-utils curl -y
RUN add-apt-repository universe
RUN apt-get install python2 -y
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
RUN python2 get-pip.py
RUN apt-get install python3-pip -y

#Check/Test what works or not
RUN pwd
RUN pip --version
RUN pip3 --version
RUN python2 --version

#Install the python prroject 
RUN pip install --no-cache-dir -r requirements.txt
RUN python2 setup.py install

#Bugfix : It's looking for a file, apparently at the wrong place, let's help it find it
RUN ln /soccer-cli/soccer/teams.json /usr/local/lib/python2.7/dist-packages/soccer_cli-0.1.1.0-py2.7.egg/soccer/teams.json

#Add the football-data.org token provided into a file as the configuration for the user running the command soccer
RUN ln /soccer-cli/.soccer-cli.ini ~/.soccer-cli.ini
