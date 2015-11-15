FROM python:2.7

RUN mkdir -p usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python-pip \
    python-dev \
    libmysqlclient-dev \
    libatlas-dev \
    liblapack-dev \
    gfortran \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libtidy-dev \
    libncurses5-dev \
    locales

RUN echo "America/Sao_Paulo" > /etc/timezone; dpkg-reconfigure -f noninteractive tzdata
RUN echo 'pt_BR.UTF-8 UTF-8' >> /etc/locale.gen && locale-gen && DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales

COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 5003
