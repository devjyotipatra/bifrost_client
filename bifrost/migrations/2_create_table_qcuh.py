"""create_table_qcuh

Revision ID: 2
Create Date: 2019-08-16 07:57:23.828357

"""

# revision identifiers, used by Bifrost.
from data_app.migrations import Migrations

version = 2
import logging
from qds_sdk.commands import HiveCommand
from mako.template import Template


def upgrade(context):
    logging.debug("Execute upgrade of `%d`" % version)

    template = Template("""
        CREATE EXTERNAL TABLE IF NOT EXISTS qubole_bi_${env}_${account_id}.`usage`(
                `cluster_id` INT,
                `cluster_inst_id` INT,
                `node_type` STRING,
                `cluster_type` STRING,
                `compute_usage` DECIMAL(30,8))
            PARTITIONED BY (
               `account_id` INT,
               `event_date` STRING)
            STORED AS ORC
            LOCATION '${defloc}/qubole_bi/qcuh/'
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
        DROP TABLE IF EXISTS qubole_bi_${env}_${account_id}.usage;
    """)
    Migrations.downgrade(migration_number=version,
                                command=HiveCommand.run(query=template.render_unicode(env=context["env"],
                                account_id = context['account_id'])))
