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

    $ docker exec -it standalone_rucio_1 /bin/bash

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

First, log into the container::

    # docker exec -it standalone_rucio_1 /bin/bash

To configure Rucio&FTS
^^^^^^^^^^^^^^^^^^^^^^

File tools/configure.sh to customize::

    # cat tools/configure.sh
     #!/usr/bin/env bash

    # Add source sites
    rucio-admin rse add NDGF-PIGGY -i
    rucio-admin rse add NDGF-KERMIT

    # Add upload site
    rucio-admin rse add DESY-DISCORDIA -i

    # Add destination site
    rucio-admin rse add DESY-PROMETHEUS

    # Define the topology
    rucio-admin rse add-distance --distance 1 --ranking 1 NDGF-PIGGY DESY-PROMETHEUS
    rucio-admin rse add-distance --distance 1 --ranking 1 NDGF-KERMIT DESY-PROMETHEUS
    rucio-admin rse add-distance --distance 1 --ranking 1 DESY-DISCORDIA DESY-PROMETHEUS

    rucio-admin rse add-protocol --hostname srm.ndgf.org --scheme srm\
         --prefix /atlas/disk/atlasdatadisk/piggy/\
         --space-token ATLASDATADISK\
         --web-service-path /srm/managerv2?SFN=\
         --port 8443 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         NDGF-PIGGY

    # Add protocol information for NDGF-KERMIT
    rucio-admin rse add-protocol --hostname srm.ndgf.org --scheme srm\
         --prefix /atlas/disk/atlasdatadisk/kermit/\
         --space-token ATLASDATADISK\
         --web-service-path /srm/managerv2?SFN=\
         --port 8443 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         NDGF-KERMIT

    rucio-admin rse add-protocol --hostname prometheus.desy.de --scheme srm\
         --prefix /VOs/atlas/DATA/rucio/\
         --space-token ATLASDATADISK\
         --web-service-path /srm/managerv2?SFN=\
         --port 8443 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         DESY-PROMETHEUS

    # Add protocol information for DESY-DISCORDIA
    rucio-admin rse add-protocol --hostname discordia.desy.de --scheme srm\
          --prefix /home/garvin\
          --web-service-path /srm/managerv2?SFN=\
          --port 8443 --impl rucio.rse.protocols.gfal.Default\
          --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
          DESY-DISCORDIA

    rucio-admin rse add-protocol --hostname discordia.desy.de --scheme http\
         --prefix /home/garvin\
         --port 2880 --impl rucio.rse.protocols.gfal.Default\
         --domain-json '{"wan": {"read": 1, "write": 1, "delete": 1, "third_party_copy": 1}, "lan": {"read": 1, "write": 1, "delete": 1}}' \
         DESY-DISCORDIA

    # Define the FTS server for the Site
    rucio-admin rse set-attribute --rse  NDGF-PIGGY --key fts  --value https://fts-rest:8446
    rucio-admin rse set-attribute --rse  NDGF-KERMIT --key fts  --value https://fts-rest:8446
    rucio-admin rse set-attribute --rse  DESY-PROMETHEUS --key fts  --value https://fts-rest:8446
    rucio-admin rse set-attribute --rse  DESY-DISCORDIA --key fts  --value https://fts-rest:8446

    # define deletion
    rucio-admin rse set-attribute --rse  DESY-PROMETHEUS --key reaper  --value 1
    rucio-admin rse set-attribute --rse  NDGF-KERMIT --key reaper  --value 1

    # add scopes
    rucio-admin scope add --scope MyScope --account root
    rucio-admin scope add --scope tests --account root

    # Set infinite quota to root account on NDGF-KERMIT, DESY-PROMETHEUS, DESY-DISCORDIA,
    rucio-admin account set-limits root NDGF-KERMIT -1
    rucio-admin account set-limits root DESY-PROMETHEUS -1
    rucio-admin account set-limits root DESY-DISCORDIA -1

Data upload and replication
^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # cat ./tools/workflow-1.sh
    #!/usr/bin/env bash

    mkdir data

    cd data

    # Generate data, upload it and add replicate it
    ../tools/data_uploader-1.sh

    cd ..

    rm -rf data

Data replication of existing data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    # cat ./tools/workflow-2.sh
    #!/usr/bin/env bash

    # Generate and upload data
    mkdir data
    cd data

    # Generate data, upload it and add replicate it
    ../tools/data_uploader-2.sh

    # Generate the list of files
    ../tools/list-files > ../tools/replicas.csv

    # bulk register replicas on source site
    # Replicas are in ../tools/replicas.csv
    /opt/rucio/tools/bulk_register_replicas

    # Setup the replication
    /opt/rucio/tools/bulk_register_rules

    # Cleanup
    cd ..
    rm -rf data


Data export
^^^^^^^^^^^

::

    # cat ./tools/workflow-4.sh
    #!/usr/bin/env bash

    rucio-admin subscription add \
        --account root\
        'FT data export' \
        '{"datatype": ["AOD"], "scope": ["tests"], "project": ["test"]}'\
        '[{"lifetime": 604800, "rse_expression": "DESY-DISCORDIA", "copies": 1, "grouping": "DATASET", "activity": "Functional Test"}]'\
        'suscription example'

    rucio-automatix --run-once --input-file /opt/rucio/etc/automatix.json
