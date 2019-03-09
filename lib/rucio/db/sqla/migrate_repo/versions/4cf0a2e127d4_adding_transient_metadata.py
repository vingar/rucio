# Copyright 2013-2019 CERN for the benefit of the ATLAS collaboration.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors:
# - Vincent Garonne <vincent.garonne@cern.ch>, 2014-2017
# - Cedric Serfon <cedric.serfon@cern.ch>, 2015
# - Mario Lassnig <mario.lassnig@cern.ch>, 2019

''' adding transient metadata '''

import sqlalchemy as sa

from alembic import context
from alembic.op import add_column, drop_column


# Alembic revision identifiers
revision = '4cf0a2e127d4'
down_revision = '271a46ea6244'


def upgrade():
    '''
    Upgrade the database to this revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'postgresql']:
        schema = context.get_context().version_table_schema
        add_column('dids', sa.Column('transient', sa.Boolean(name='DID_TRANSIENT_CHK'), server_default='0'), schema=schema)


def downgrade():
    '''
    Downgrade the database to the previous revision
    '''

    if context.get_context().dialect.name in ['oracle', 'mysql', 'postgresql']:
        schema = context.get_context().version_table_schema
        drop_column('dids', 'transient', schema=schema)
