============================================
Full data management with dCache, Rucio & Co
============================================

Prerequisites
--------------

- docker
- docker-compose
- Grid credentials (proxy, vo)
- dCache Storage

Quick Start
-----------

A YAML file for `docker-compose` has been provided to allow easily setup of data management
solution: `docker-compose.yml file <https://github.com/vingar/rucio/blob/development/etc/docker/standalone/docker-compose.yml>`_.

To run the multi-container Data management Docker applications, do::

    $ git clone https://github.com/vingar/rucio
    $ cd rucio
    $ git checkout development
    $ export RUCIO_HOME=`pwd`/etc/docker/standalone/files/rucio/
    $ export FTS3_HOME=`pwd`/etc/docker/standalone/files/fts3/
    $ export X509_CERT_DIR=`pwd`/etc/docker/standalone/files/grid-security/
    $ export X509_USER_PROXY=/tmp/x509up_u$(id -u)
    $ docker volume create --name=pg_data
    $ docker volume create --name=mysql_data
    $ docker-compose --file etc/docker/standalone/docker-compose.yml up -d

X509_CERT_DIR should contain the server host certificate and key (hostcert.pem and hostkey.pem)
together with CA certificates. If you dont't have them, this demo provided them in /etc/docker/standalone/files/grid-security/.
A valid proxy, trusted by the storage, should be defined in X509_USER_PROXY.

Provided components
--------------------

After you run the docker-compose command you can check the status of the containers::

    $ docker ps
    CONTAINER ID        IMAGE                                               COMMAND                  CREATED              STATUS                             PORTS                                                                                                       NAMES
    31d66fe03f76        standalone_rucio                                    "httpd -D FOREGROUND"    About a minute ago   Up About a minute                  0.0.0.0:443->443/tcp                                                                                        standalone_rucio_1
    e09e9b50c28d        gitlab-registry.cern.ch/fts/fts-rest:latest         "/usr/sbin/apachectl…"   About a minute ago   Up About a minute                  0.0.0.0:8446->8446/tcp                                                                                      standalone_fts-rest_1
    ade4d8177d9c        gitlab-registry.cern.ch/fts/fts3:latest             "/usr/bin/supervisor…"   About a minute ago   Up 50 seconds                      2170/tcp                                                                                                    standalone_fts3_1
    2bc0b5fb2415        gitlab-registry.cern.ch/fts/fts-monitoring:latest   "/usr/sbin/apachectl…"   About a minute ago   Up About a minute                  0.0.0.0:8449->8449/tcp                                                                                      standalone_fts-monitoring_1
    3dbad44fa6b5        postgres:10.3                                       "docker-entrypoint.s…"   About a minute ago   Up About a minute                  0.0.0.0:5432->5432/tcp                                                                                      standalone_postgres_1
    81481770b54c        webcenter/activemq:latest                           "/app/run.sh"            About a minute ago   Up About a minute                  1883/tcp, 0.0.0.0:8161->8161/tcp, 5672/tcp, 0.0.0.0:61613->61613/tcp, 61614/tcp, 0.0.0.0:61616->61616/tcp   standalone_activemq_1
    5dc115de1b89        mysql/mysql-server:5.7                              "/entrypoint.sh mysq…"   About a minute ago   Up 26 seconds (health: starting)   0.0.0.0:3306->3306/tcp, 33060/tcp                                                                           standalone_mysql_1

To stop the containers::

    $ docker-compose --file etc/docker/standalone/docker-compose.yml down

To summarize:

+------------+-------------+-----------------------------+
| Service    | Port        | Container                   |
+============+=============+=============================+
| **Rucio**                |                             |
+------------+-------------+-----------------------------+
| REST       | 443         | standalone_rucio_1          |
+------------+-------------+-----------------------------+
| Daemons    |             | standalone_rucio_1          |
+------------+-------------+-----------------------------+
| WebUI      | 443         | standalone_rucio_1          |
+------------+-------------+-----------------------------+
| PostgreSQL | 5432        | standalone_postgres_1       |
+------------+-------------+-----------------------------+
| **FTS**                  |                             |
+------------+-------------+-----------------------------+
| REST       | 8446        | standalone_fts-rest_1       |
+------------+-------------+-----------------------------+
| UI         | 8449        | standalone_fts-monitoring_1 |
+------------+-------------+-----------------------------+
| Server     |             | standalone_fts3_1           |
+------------+-------------+-----------------------------+
|  MySQL     | 3306        |  standalone_mysql_1         |
+------------+-------------+-----------------------------+
| **Messaging**            |                             |
+------------+-------------+-----------------------------+
|  ActiveMQ  | 61123,61013 | standalone_activemq_1       |
+------------+-------------+-----------------------------+

.. Mounted volumes


Rucio configuration
-------------------

After the first start of the containers you will have to setup Rucio to be able to use the Rucio commands and the WebUI.
To do this you have to simply run the following command to configure the DB::

    $ docker exec -it standalone_rucio_1 /opt/rucio/tools/setup_rucio.py

To test that Rucio is set up correctly you can do a ping and you should
get the rucio version::

    $ docker exec -it standalone_rucio_1/bin/bash

    $ rucio ping
    1.15.0

Rucio WebUI: https://127.0.0.1/ui/

A demo client p12 certificate is available for your browser in files/grid-security/rucio_demo_cert.p12.
The import password is rucio-demo.

In case the Certificate authorities are not installed::

    $ yum install ca-policy-egi-core

Or for OSG::

    $ yum install osg-ca-certs

you can include the Certificate Revocation List - CLR::

    $ yum install fetch-crl
    $ /usr/sbin/fetch-crl  --verbose

.. systemctl enable fetch-crl-cron.service
.. systemctl start fetch-crl-cron.service

FTS configuration
-----------------

How to bootstrap FTS db::

    $ docker exec -it standalone_fts3_1 /etc/fts3/setup_fts.sh

To apply the change::

    $ docker restart standalone_fts3_1

FTS WebUI: https://127.0.0.1:8449/fts3/ftsmon/#

Demo
----

The demo is self contained in various scripts located in /opt/rucio/tools/.

To configure Rucio&FTS::

    # docker exec -it standalone_rucio_1 /bin/bash

    # cat tools/configure.sh
    #!/usr/bin/env bash

    # Add source site
    rucio-admin rse add NDGF-PIGGY -i

    # Add destination site
    rucio-admin rse add DESY-PROMETHEUS

    # Define the network topology
    rucio-admin rse add-distance --distance 1 --ranking 1 NDGF-PIGGY DESY-PROMETHEUS

    # Add protocol information for source site
    rucio-admin rse add-protocol --hostname srm.ndgf.org --scheme srm\
         --prefix /atlas/disk/atlasdatadisk/\
         --space-token ATLASDATADISK\
         --web-service-path /srm/managerv2?SFN=\
         --port 8443 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         NDGF-PIGGY

     rucio-admin rse add-protocol --hostname dav.ndgf.org --scheme davs\
        --prefix /atlas/disk/atlasdatadisk/\
        --port 443 --impl rucio.rse.protocols.gfal.Default\
        --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
        NDGF-PIGGY

    # Add protocol information for destination
    rucio-admin rse add-protocol --hostname prometheus.desy.de --scheme srm\
         --prefix /VOs/atlas/DATA/rucio/\
         --space-token ATLASDATADISK\
         --web-service-path /srm/managerv2?SFN=\
         --port 8443 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         DESY-PROMETHEUS

    rucio-admin rse add-protocol --hostname prometheus.desy.de --scheme davs\
        --prefix /VOs/atlas/DATA/rucio/\
        --port 443 --impl rucio.rse.protocols.gfal.Default\
        --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
        DESY-PROMETHEUS

    # Define the FTS server
    rucio-admin rse set-attribute --rse  NDGF-PIGGY --key fts  --value https://fts-rest:8446
    rucio-admin rse set-attribute --rse  DESY-PROMETHEUS --key fts  --value https://fts-rest:8446

    # add scope
    rucio-admin scope add --scope MyScope --account root

    # Set infinite quota to root account on DESY-PROMETHEUS
    rucio-admin account set-limits root DESY-PROMETHEUS -1

    # Start the rucio daemons
    /usr/bin/python /usr/bin/supervisord -c /etc/supervisord.conf

    # logs are under /var/log/rucio/


The rest during the session :)
