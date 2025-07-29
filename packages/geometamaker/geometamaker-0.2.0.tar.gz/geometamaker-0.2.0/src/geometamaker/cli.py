import logging
import os
import sys

import click
import fsspec
import numpy
from pydantic import ValidationError

import geometamaker

LOGGER = logging.getLogger('geometamaker')
LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.StreamHandler(sys.stdout)
FORMATTER = logging.Formatter(
    fmt='%(asctime)s %(name)-18s %(levelname)-8s %(message)s',
    datefmt='%m/%d/%Y %H:%M:%S ')
HANDLER.setFormatter(FORMATTER)
LOGGER.addFilter(
    lambda record: not record.__dict__.get(
        geometamaker.geometamaker._NOT_FOR_CLI, False))


# The recommended approach to allowing multiple ParamTypes
# https://github.com/pallets/click/issues/1729
class _ParamUnion(click.ParamType):
    def __init__(self, types, report_all_errors=True):
        """Union of click.ParamTypes.

        Args:
            types (list): List of click.ParamTypes to try to convert the value.
            report_all_errors (bool): If True, all errors will be reported.
                If False, only the last error will be reported.

        """
        self.types = types
        self.report_all_errors = report_all_errors

    def convert(self, value, param, ctx):
        errors = []
        for type_ in self.types:
            try:
                return type_.convert(value, param, ctx)
            except click.BadParameter as e:
                errors.append(e)
                continue

        if self.report_all_errors:
            self.fail(errors)
        else:
            # If errors from different types are expected to
            # be very similar, just report the last one.
            self.fail(errors.pop())


# https://click.palletsprojects.com/en/stable/parameters/#how-to-implement-custom-types
class _URL(click.ParamType):
    """A type that asserts a URL exists."""

    name = "url"

    def convert(self, value, param, ctx):
        of = fsspec.open(value)
        if not of.fs.exists(value):
            self.fail(f'{value} does not exist', param, ctx)

        return value


@click.command(
    help='''Describe properties of a dataset given by FILEPATH and write this
    metadata to a .yml sidecar file. Or if FILEPATH is a directory, describe
    all datasets within.''',
    short_help='Generate metadata for geospatial or tabular data, compressed'
               ' archives, or collections of files in a directory.')
@click.argument('filepath',
                type=_ParamUnion([click.Path(exists=True), _URL()],
                                 report_all_errors=False))
@click.option('-nw', '--no-write',
              is_flag=True,
              default=False,
              help='Dump metadata to stdout instead of to a .yml file.'
                   ' This option is ignored when describing all files'
                   ' in a directory.')
@click.option('-st', '--stats',
              is_flag=True,
              default=False,
              help='Compute raster band statistics.')
@click.option('-d', '--depth',
              default=numpy.iinfo(numpy.int16).max,
              help='if FILEPATH is a directory, describe files in'
                   ' subdirectories up to depth. Defaults to describing'
                   ' all files.')
@click.option('-x', '--exclude',
              default=None,
              help='Regular expression used to exclude files from being'
                   ' described. Only used if FILEPATH is a directory.')
@click.option('-a', '--all', 'all_files',
              is_flag=True,
              default=False,
              help='Do not ignore files starting with .'
                   ' Only used if FILEPATH is a directory.')
@click.option('-co', '--collection-only',
              is_flag=True,
              default=False,
              help='If FILEPATH is a directory, do not write metadata documents'
                   ' for all files in the directory. Only create a single'
                   ' *-metadata.yml document for the collection')
def describe(filepath, depth, exclude, all_files, no_write, stats,
             collection_only):
    describing_single = True  # if filepath is a file, or collection_only=True
    if os.path.isdir(filepath):
        resource = geometamaker.describe_collection(
            filepath,
            depth=depth,
            exclude_regex=exclude,
            exclude_hidden=(not all_files),
            describe_files=(not collection_only),
            compute_stats=stats)
        describing_single = collection_only
    else:
        resource = geometamaker.describe(filepath, compute_stats=stats)

    if no_write and describing_single:
        click.echo(geometamaker.utils.yaml_dump(
            resource._dump_for_write()))
        return

    if no_write and not describing_single:
        click.echo('the -nw, or --no-write, flag is ignored when '
                   'describing all files in a directory.')
    if resource._would_overwrite:
        click.confirm(
            f'\n{resource.metadata_path} is about to be overwritten'
            ' because it is not a valid metadata document.\n'
            'Are you sure want to continue?',
            abort=True)
    try:
        # Users can abort at the confirm and manage their own backups.
        resource.write(backup=False)
    except OSError:
        click.echo(
            f'geometamaker could not write to {resource.metadata_path}\n'
            'Try using the --no-write flag to print metadata to '
            'stdout instead:')
        click.echo(f'    geometamaker describe --no-write {filepath}')


def echo_validation_error(error, filepath):
    summary = u'\u2715' + f' {filepath}: {error.error_count()} validation errors'
    click.secho(summary, fg='bright_red')
    for e in error.errors():
        location = '.'.join([str(loc) for loc in e['loc']])
        msg_string = (f"    {e['msg']}. [input_value={e['input']}, "
                      f"input_type={type(e['input']).__name__}]")
        click.secho(location, bold=True)
        click.secho(msg_string)


@click.command(
    help='''Validate a .yml metadata document given by FILEPATH.
    Or if FILEPATH is a directory, validate all documents within.''',
    short_help='Validate metadata documents for syntax or type errors.')
@click.argument('filepath',
                type=click.Path(exists=True))
@click.option('-d', '--depth',
              default=numpy.iinfo(numpy.int16).max,
              help='if FILEPATH is a directory, validate files in'
                   ' subdirectories up to depth. Defaults to validating'
                   ' all files.')
def validate(filepath, depth):
    if os.path.isdir(filepath):
        file_list, message_list = geometamaker.validate_dir(
            filepath, depth=depth)
        for filepath, msg in zip(file_list, message_list):
            if isinstance(msg, ValidationError):
                echo_validation_error(msg, filepath)
            else:
                color = 'yellow'
                icon = u'\u25CB'
                if not msg:
                    color = 'bright_green'
                    icon = u'\u2713'
                click.secho(f'{icon} {filepath} {msg}', fg=color)
    else:
        error = geometamaker.validate(filepath)
        if error:
            echo_validation_error(error, filepath)


def print_config(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    config = geometamaker.Config()
    click.echo(config)
    ctx.exit()


def delete_config(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    config = geometamaker.Config()
    click.confirm(
        f'\nAre you sure you want to delete {config.config_path}?',
        abort=True)
    config.delete()
    ctx.exit()


@click.command(
    short_help='''Configure GeoMetaMaker with information to apply to all
    metadata descriptions''',
    help='''When prompted, enter contact and data-license information
    that will be stored in a user profile. This information will automatically
    populate contact and license sections of any metadata described on your
    system. Press enter to leave any field blank.''')
@click.option('--individual-name', prompt=True, default='')
@click.option('--email', prompt=True, default='')
@click.option('--organization', prompt=True, default='')
@click.option('--position-name', prompt=True, default='')
@click.option('--license-title', prompt=True, default='',
              help='the name of a data license, e.g. "CC-BY-4.0"')
@click.option('--license-url', prompt=True, default='',
              help='a url for a data license')
@click.option('-p', '--print', is_flag=True, is_eager=True,
              callback=print_config, expose_value=False,
              help='Print your current GeoMetaMaker configuration.')
@click.option('--delete', is_flag=True, is_eager=True,
              callback=delete_config, expose_value=False,
              help='Delete your configuration file.')
def config(individual_name, email, organization, position_name,
           license_url, license_title):
    contact = geometamaker.models.ContactSchema()
    contact.individual_name = individual_name
    contact.email = email
    contact.organization = organization
    contact.position_name = position_name

    license = geometamaker.models.LicenseSchema()
    license.path = license_url
    license.title = license_title

    profile = geometamaker.models.Profile(contact=contact, license=license)
    config = geometamaker.Config()
    config.save(profile)
    click.echo(f'saved profile information to {config.config_path}')


@click.group(
    epilog='https://geometamaker.readthedocs.io/en/latest/ for more details')
@click.option('-v', 'verbosity', count=True, default=2, required=False,
              help='''Override the default verbosity of logging. Use "-vvv" for
              debug-level logging. Omit this flag for default,
              info-level logging.''')
@click.version_option(message="%(version)s")
def cli(verbosity):
    log_level = logging.ERROR - verbosity*10
    HANDLER.setLevel(log_level)
    LOGGER.addHandler(HANDLER)


cli.add_command(describe)
cli.add_command(validate)
cli.add_command(config)
