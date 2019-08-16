"""create_db_qubolebi

Revision ID: 0
Create Date: 2019-08-16 07:57:23.828357

"""

# revision identifiers, used by Bifrost.
from data_app.migrations import Migrations

version = 0
import logging
from qds_sdk.commands import HiveCommand
from mako.template import Template


def upgrade(context):
    logging.debug("Execute upgrade of `%d`" % version)

    template = Template("""
        CREATE DATABASE IF NOT EXISTS qubole_bi_${env}_${account_id};
    """)
    context["revisions.upgraded"].append(version)
    Migrations.upgrade(migration_number=version,
                                command=HiveCommand.run(query=template.render_unicode(env=context["env"],
                                account_id = context['account_id'])))
    print context


def downgrade(context):
    logging.debug("Execute downgrade of `%d`" % version)
    template = Template("""
        DROP DATABASE IF EXISTS qubole_bi_${env}_${account_id};
    """)
    Migrations.downgrade(migration_number=version,
                                command=HiveCommand.run(query=template.render_unicode(env=context["env"],
                                account_id = context['account_id'])))
