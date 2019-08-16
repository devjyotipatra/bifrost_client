"""create_table_tco

Revision ID: 3
Create Date: 2019-08-16 07:57:23.828357

"""

# revision identifiers, used by Bifrost.
from data_app.migrations import Migrations

version = 3
import logging
from qds_sdk.commands import HiveCommand
from mako.template import Template


def upgrade(context):
    logging.debug("Execute upgrade of `%d`" % version)

    template = Template("""
        CREATE TABLE IF NOT EXISTS qubole_bi_${env}_${account_id}.tco_table (
                    node_id BIGINT,
                    cluster_inst_id INT,
                    cluster_id INT,
                    instance_type STRING,
                    availability_zone STRING,
                    region STRING,
                    hour BIGINT,
                    price DOUBLE,
                    node_run_time INT,
                    approx_per_hour_price DOUBLE,
                    ondemand_price DOUBLE,
                    up_time STRING,
                    down_time STRING,
                    node_type STRING
                )
                PARTITIONED BY (account_id INT, event_date STRING)
                STORED AS ORC
                LOCATION '${defloc}/qubole_bi/tco_table/'
    """)
    context["revisions.upgraded"].append(version)
    Migrations.upgrade(migration_number=version,
                                command=HiveCommand.run(query=template.render_unicode(env=context["env"],
                                account_id = context['account_id'],
                                defloc =  context['defloc'])))
    print context


def downgrade(context):
    logging.debug("Execute downgrade of `%d`" % version)
    template = Template("""
        DROP TABLE IF EXISTS qubole_bi_${env}_${account_id}.tco_table;
    """)
    Migrations.downgrade(migration_number=version,
                                command=HiveCommand.run(query=template.render_unicode(env=context["env"],
                                account_id = context['account_id'])))
