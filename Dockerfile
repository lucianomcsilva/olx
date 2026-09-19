#FROM public.ecr.aws/lambda/python:3.10
#FROM python:3.10
#FROM ubuntu:22.04
FROM 132733789290.dkr.ecr.us-east-1.amazonaws.com/scrapy-playwright:latest
ENV PORT 80
ENV CUSTOM "Variavel de AMBEINTE"
ENV TASKNO "rr"
ENV SESSION "52e7bee7-6673-4f63-9045-7de2e0e9d5ab"
EXPOSE ${PORT}
COPY . ${docke}
# RUN apt-get update 
# RUN apt-get -qq install python3
# RUN apt-get -qq install pip
# RUN apt-get install -y openssh-server
# RUN apt-get -qq install nodejs
# RUN apt-get -qq install npm
# RUN npm install pm2 -g
# RUN export PATH="$PATH:/usr/bin/python3"
# RUN ln -s /usr/bin/python3 /usr/bin/python
# RUN pip install -r requirements.txt
# RUN playwright install
# RUN playwright install-deps
CMD [ "usr/local/bin/scrapy",  "crawl",  "olx_spider" ]
