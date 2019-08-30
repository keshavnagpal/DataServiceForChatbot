FROM python:3.7

#Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl apt-transport-https debconf-utils \
        openssh-server \
        vim \
        nano \
        wget \
        tcptraceroute \
        gcc python3-dev python3-pip libxml2-dev libxslt1-dev zlib1g-dev g++ unixodbc-dev unixodbc-bin unixodbc 


# adding custom MS repository for Debian
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list


# install SQL Server drivers and tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"


RUN pip install --upgrade pip
RUN pip install uvicorn gunicorn

RUN mkdir -p /home/site/wwwroot
COPY app/requirements.txt /home/site/wwwroot
RUN pip install -r /home/site/wwwroot/requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

COPY ./app /home/site/wwwroot
WORKDIR /home/site/wwwroot
ENV PYTHONPATH=/home/site/wwwroot


# setup SSH
RUN mkdir -p /home/LogFiles \
     && echo "root:Docker!" | chpasswd \
     && echo "cd /home" >> /etc/bash.bashrc 

COPY sshd_config /etc/ssh/
RUN mkdir -p /opt/startup

RUN chmod -R 777 /opt/startup

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]

# Run the start script, it will check for an /app/prestart.sh script (e.g. for migrations)
# And then will start Gunicorn with Meinheld
CMD ["/start.sh"]
