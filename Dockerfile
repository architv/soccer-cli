# To build it : docker build -t soccer-cli .
# To run it :  docker run -it --rm --name my-soccer-run my-soccer soccer --standings --league=PL --apikey=693f58c36d5b4bc48b1f8d110d92a5a9
#
# Now we need to do that in a workflow
# And publish the built image as a package with the proper docker action
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
RUN pip --version
RUN pip3 --version
RUN whoami
RUN pwd
RUN python2 -V
RUN pip -V
#RUN tree .

RUN pip install --no-cache-dir -r requirements.txt
RUN python2 setup.py install
RUN ln /soccer-cli/soccer/teams.json /usr/local/lib/python2.7/dist-packages/soccer_cli-0.1.1.0-py2.7.egg/soccer/teams.json
RUN ln /soccer-cli/.soccer-cli.ini ~/.soccer-cli.ini

#COPY . .

#CMD [ "python", "./your-daemon-or-script.py" ]
