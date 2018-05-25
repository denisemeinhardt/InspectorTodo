# Copyright 2018 TNG Technology Consulting GmbH, Unterföhring, Germany
# Licensed under the Apache License, Version 2.0 - see LICENSE.md in project root directory

import logging
import os

import click

from .config import load_or_create_config, get_config_value, get_multiline_config_value_as_list
from .todo_finder import TodoFinder
from .todo_validation import validate_todos

log = logging.getLogger()


@click.command()
@click.argument('ROOT_DIR', required=True)
@click.argument('ISSUE_PATTERN', required=True)
@click.option('--version-pattern', help='Regular expression for version references in todos.')
@click.option('--version', help='Current version.')
@click.option('--versions', help='List of versions allowed in todos.'
                                 'Versions are separated by comma and increase from left to right.')
@click.option('--configfile', help='Config file to be used. If file does not exist, default config is created.'
                                   'If not set, all config values are treated as None.')
@click.option('--log-level', default='INFO', help="Set the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
def main(root_dir, issue_pattern, version_pattern, version, versions, configfile, log_level):
    """
    ROOT_DIR is the directory to inspect recursively.

    ISSUE_PATTERN is a regular expression for the issue references in todos.
    """

    logging.basicConfig(level=log_level.upper(), format='[%(levelname)s] %(message)s')

    root_dir = os.path.normpath(os.path.abspath(root_dir))
    issue_pattern = issue_pattern.strip()
    versions = versions.split(',') if versions else versions

    if configfile:
        load_or_create_config(configfile)

    paths_whitelist = []
    if get_config_value('files', 'whitelist'):
        paths_whitelist = get_multiline_config_value_as_list('files', 'whitelist')

    todo_finder = TodoFinder(root_dir, paths_whitelist)
    todos = todo_finder.find()
    if not todos:
        log.info('No todos found.')
        return

    validate_todos(todos, issue_pattern, version_pattern, version, versions)
