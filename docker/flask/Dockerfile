FROM python:3.7
LABEL maintainer="appsvc-images@microsoft.com"

# Web Site Home
ENV HOME_SITE "/home/site/wwwroot"

#Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-transport-https debconf-utils \
        openssh-server \
        vim \
        nano \
        curl \
        wget \
        tcptraceroute \
        gcc libxml2-dev libxslt1-dev zlib1g-dev g++ unixodbc-dev unixodbc-bin unixodbc \
    && pip install --upgrade pip \
    && pip install subprocess32 \
    && pip install gunicorn \ 
    && pip install virtualenv \
    && pip install flask 

WORKDIR ${HOME_SITE}

# adding custom MS repository for Debian
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list


# install SQL Server drivers and tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

COPY requirements.txt /home/site/wwwroot/
RUN pip install -r requirements.txt

EXPOSE 8000
# setup SSH
RUN mkdir -p /home/LogFiles \
     && echo "root:Docker!" | chpasswd \
     && echo "cd /home" >> /etc/bash.bashrc 

COPY sshd_config /etc/ssh/
RUN mkdir -p /opt/startup
COPY init_container.sh /opt/startup/init_container.sh

# setup default site
RUN mkdir /opt/defaultsite
COPY hostingstart.html /opt/defaultsite
COPY application.py /opt/defaultsite

# configure startup
RUN chmod -R 777 /opt/startup
COPY entrypoint.py /usr/local/bin

ENTRYPOINT ["/opt/startup/init_container.sh"]
