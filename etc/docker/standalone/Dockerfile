# FROM rucio/rucio-systemd-cc7

FROM centos:7

RUN yum install -y epel-release
RUN yum install -y python2-pip


ADD ca.repo /etc/yum.repos.d/ca.repo

# Install Rucio
RUN pip install --upgrade pip
RUN pip install rucio rucio-webui

WORKDIR /opt

RUN mkdir /var/log/rucio
RUN mkdir /var/log/rucio/trace
RUN chmod 777 /var/log/rucio

ADD httpd.conf /etc/httpd/conf/httpd.conf
ADD rucio.conf /etc/httpd/conf.d/rucio.conf

RUN yum install -y supervisor
ADD rucio.ini /etc/supervisord.d/rucio.ini
ADD supervisord.conf /etc/supervisord.conf
# RUN systemctl enable supervisord.service
# CMD ["/usr/sbin/init"]

ADD setup_rucio.py /

WORKDIR /opt/rucio

RUN rm /etc/httpd/conf.d/ssl.conf /etc/httpd/conf.d/autoindex.conf /etc/httpd/conf.d/userdir.conf /etc/httpd/conf.d/welcome.conf

EXPOSE 443

ENV PATH $PATH:/opt/rucio/bin
