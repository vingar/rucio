=========================================
Setting up a Rucio standalone environment
=========================================

Prerequisites
--------------

Setting up a Rucio standalone environment requires to have `docker` and `docker-compose`
installed. Docker is an application that makes it simple and easy to run
application processes. To install Docker for your platform, please refer to
the `Docker installation guide <https://docs.docker.com/install/>`_.
`Git` should be also `installed <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_.

The containers provided here can be used to easily setup a small demo instance of
Rucio with some mock data to play around with some Rucio commands.

docker-compose
---------------

A YAML file for `docker-compose` has been provided to allow easily setup of the containers: `docker-compose.yml file <https://github.com/vingar/rucio/blob/development/etc/docker/standalone/docker-compose.yml>`_.

To run the multi-container Rucio Docker applications, do::

    $ git clone https://github.com/vingar/rucio
    $ cd rucio
    $ git checkout development
    $ docker-compose --file etc/docker/standalone/docker-compose.yml up -d

The names of the containers should be printed in the terminal for you.

Checking the containers
-----------------------

After you run the docker-compose command you can check the status of the containers::

    > $ docker ps
    CONTAINER ID        IMAGE                                     COMMAND                  CREATED             STATUS                   PORTS                                                      NAMES
    5d361f040b5e        standalone_rucio                          "httpd -D FOREGROUND"    3 minutes ago       Up 3 minutes             0.0.0.0:443->443/tcp                                       standalone_rucio_1
    9e44f49617ee        gitlab-registry.cern.ch/fts/fts3:latest   "/usr/bin/supervisor…"   3 minutes ago       Up 3 minutes             2170/tcp                                                   standalone_fts3_1
    8beb926dbf7e        webcenter/activemq:latest                 "/app/run.sh"            3 minutes ago       Up 3 minutes             1883/tcp, 5672/tcp, 8161/tcp, 61613-61614/tcp, 61616/tcp   standalone_activemq_1
    2174a1dff62a        postgres:10.3                             "docker-entrypoint.s…"   3 minutes ago       Up 3 minutes             5432/tcp                                                   standalone_postgres_1
    6b3c46ac754c        mysql/mysql-server:5.7                    "/entrypoint.sh mysq…"   3 minutes ago       Up 3 minutes (healthy)   3306/tcp, 33060/tcp                                        standalone_mysql_1

Initial setup
-------------

After the first start of the containers you will have to setup Rucio to be able to use the Rucio commands and the WebUI.
To do this you have to simply run the following command::

    $ docker exec -it standalone_rucio_1 /bin/bash
    # To create the table and add the root account
    $  /setup_rucio.py
    # To start the daemons
    $ /usr/bin/python /usr/bin/supervisord -c /etc/supervisord.conf
    # supervisorctl
    # To enable bash completion for the rucio clients
    $  cat /opt/rucio/tools/activate_rucio_global_completion.sh >> /root/.bashrc

To test that Rucio is set up correctly you can do a ping and you should
get the rucio version::
    $ rucio ping
    1.15.0

Using the container
-------------------

When everything is ready you can log into the container
and start playing around with rucio::

    $ sudo docker exec -it standalone_rucio_1 /bin/bash
    [root@ad03d8dc3b4a rucio]# rucio whoami
    status     : ACTIVE
    account    : root
    account_type : SERVICE
    created_at : 2018-02-08T15:37:26
    suspended_at : None
    updated_at : 2018-02-08T15:37:26
    deleted_at : None
    email      : None


Accessing the WebUI
-------------------

In the container is also an instance of the Rucio WebUI started.

To be able to access it you will first have to install the demo client
certificate in your browser. You can find the p12 file containing the
certificate under::

    etc/docker/demo/certs/rucio_demo_cert.p12

The import password is `rucio-demo`.

Then you can access the WebUI using this url: ´https://<hostname>/ui/´

Normally, it's https://localhost/ui/

FTS configuration
-----------------

How to boosttrap FTS db::

    $ docker exec -it standalone_fts3_1  /bin/bash

Then within the container::

    # yum install -y mysql
    # mysql -u fts -h mysql -p
    # use fts
    # source /usr/share/fts-mysql/fts-schema-4.0.0.sql

FTS monitoring: https://127.0.0.1:8449/fts3/ftsmon/#

mini-HOWTOs
-----------

How to add RSE::

    $ rucio-admin rse add MOCK

How to configure the protocol, e.g., for srm::

    $ rse add-protocol --hostname dcache.desy.de --scheme srm\
                                    --prefix /pnfs/desy.de/xxxx/rucio/\
                                    --space-token DATA\
                                    --web-service-path /srm/managerv2?SFN=\
                                    --port 8443 --impl rucio.rse.protocols.gfal.Default\
                                    --domain-json "{'lan': {'read': 1,'write': 1,'delete': 1},'wan': {'read': 1,'write': 1, 'delete': 1}}"\
                                    MOCK

How to configure the connectivity between two RSEs::

    $ rucio-admin rse add-distance --distance 1 --ranking 1 MOCK1 MOCK2

How to upload data::

    $ rucio upload --rse MOCK --scope user.jdoe user.jdoe:MyDatasetName <file1><...>

How to replicate data::

    $ rucio add-rule user.jdoe:MyDatasetName 1 SITE2_DISK

