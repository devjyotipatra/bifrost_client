import datetime
import glob
import io
import logging
import os
import re
import imp
import string
import tempfile
from mako.template import Template
from mako import exceptions
from revision import Revision
from modulefinder import ModuleFinder
from importlib import import_module
import inspect

from qds_sdk.commands import Command

import migrations


class Migrations(object):
    def __init__(self, **kwargs):
        if kwargs.get('current', None) is None:
            self.current = -1
        else:
            self.current = int(kwargs.get('current'))
        self.context = kwargs


        self.context["revisions.upgraded"] = []
        self.context["revisions.downgraded"] = []


    def get_migrations(self, reverse=False):
        finder = ModuleFinder()
        submodules_names = [name for name in finder.find_all_submodules(migrations) if self._submodule_name_valid(name)]
        submodules = [import_module("migrations.%s" % name) for name in submodules_names]
        submodules = sorted(submodules, key=lambda s: s.version, reverse=reverse)
        return submodules


    def _submodule_name_valid(self, name):
        return len(re.search("[0-9]*", name).group(0)) > 0


    def downgrade(self, migration=0):
        for migration_file in self.get_migrations(reverse=True):
            migration = MigrationWrapper(migration_file)
            if migration.version <= self.current_version:
                yield migration

    def upgrade(self, migration=0):
        for migration_file in self.get_migrations():
            migration =  MigrationWrapper(migration_file)
            if migration.version > self.current_version:
                yield migration



    def __str__(self):
        if self.head is None:
            return "<EMPTY>"
        rev_str = ""

        for rev in range(self.next()):
            rev_str += str(self.map[rev])
            rev_str += "\n"
        return rev_str

    def _generate(self, message, out_stream):
        revision = self.next()
        template = Template(filename="%s/mako_template.py" % self.base_path)

        try:
            output = template.render_unicode(up_revision=revision,
                                             create_date=datetime.datetime.now(),
                                             message=message,
                                             upgrades="""
    context["revisions.upgraded"].append(revision)
    print context""").encode("utf-8")

        except:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as ntf:
                ntf.write(
                    exceptions.text_error_template().
                    render_unicode().encode("utf-8"))
                fname = ntf.name
            raise Exception(
                "Template rendering failed; see %s for a "
                "template-oriented traceback." % fname)
        else:
            out_stream.write(output)

    def generate_str(self, message):
        out_stream = io.StringIO()
        self._generate(message, out_stream)
        return out_stream.getvalue()

    def generate(self, message):
        revision = self.next()

        message_trunc = message[:15] if len(message) > 15 else message
        message_trunc = string.replace(message_trunc, ' ', '_')
        destination_name = "%s_%s.py" % (revision, message_trunc)
        destination_path = "%s/%s" % (self.path, destination_name)

        out_stream = io.FileIO(destination_path, "wb")
        self._generate(message, out_stream)
        out_stream.close()
        logging.info("Created new migration `%s` " % destination_path)

        revision = Revision(self.path, destination_name)
        self.insert(revision)

        return destination_path

    @staticmethod
    def check_for_result(migration_number, command):
        """
        A utility method to check the return status of a migration and fail the migration in case of a failure in the
        query.
        :param migration_number: The migration number that you were trying to run.
        :type migration_number: int
        :param command: The instance type of the migration command.
        :type command: Command
        :return: None
        :raise RuntimeError:
        """
        if not Command.is_success(command.status):
            error_message = "Encountered failure while trying to run migration with id {0}. QDS command id that " \
                            "failed was {1} ".format(migration_number, command.id)
            logging.error(error_message)
            raise RuntimeError(error_message)


class MigrationWrapper(object):
    def __init__(self, migration_file):
        self.migration_file = migration_file

    def __repr__(self):
        return self.filename()

    def __eq__(self, migration):
        return self.migration_file == migration.migration_file


    def header(self):
        if inspect.getdoc(self.migration_file):
            return inspect.getdoc(self.migration_file)
        else:
            return "No docstring founded"

    @property
    def version(self):
        return self.migration_file.version

    def filename(self):
        return os.path.basename(self.migration_file.__file__.replace('.pyc', '.py'))
