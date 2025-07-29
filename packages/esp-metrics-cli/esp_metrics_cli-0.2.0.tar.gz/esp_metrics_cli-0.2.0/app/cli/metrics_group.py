import logging
import sys
import time

import click

from app.models.config import BucketType
from app.models.config import MetricsSettings

from ..uploaders.metrics_uploader import MetricsUploader
from ..validators.metrics_validator import MetricsValidator
from ._options import option_bucket_type
from ._options import option_custom_bucket
from ._options import option_definitions_file
from ._options import option_input_file
from ._options import option_verbose

logger = logging.getLogger(__name__)


def print_errors(errors):
    click.echo('Errors:')
    for error in errors:
        click.echo(f'  - {error}')


def handle_exception(msg, e):
    click.secho(f'{msg}: {e}', fg='red')
    logger.exception(msg)
    sys.exit(1)


def _validate_upload_options(bucket_type: str, custom_bucket: str) -> None:
    """Validate upload command options."""
    if bucket_type == BucketType.CUSTOM.value and not custom_bucket:
        raise click.UsageError('--custom-bucket is required when --bucket-type=custom')


def _print_upload_info(
    input_file: str, definitions_file: str, bucket_type: str, custom_bucket: str, verbose: bool
) -> None:
    """Print upload information if verbose mode is enabled."""
    if not verbose:
        return

    click.echo(f'Uploading metrics file: {input_file}')
    click.echo(f'Using definitions file: {definitions_file}')
    if bucket_type:
        click.echo(f'Bucket type override: {bucket_type}')
        if bucket_type == BucketType.CUSTOM.value and custom_bucket:
            click.echo(f'Custom bucket: {custom_bucket}')


def _handle_upload_result(result, validation_result, verbose, start_time):
    """Handle and print upload result."""
    if result.upload_successful:
        click.secho('✓ Upload successful!', fg='green')
        if verbose:
            upload_time = time.time() - start_time
            click.echo(f'Uploaded {validation_result.metrics_count} metrics in {upload_time:.2f} seconds')
            if result.upload_url:
                click.echo(f'Upload URL: {result.upload_url}')
    else:
        click.secho('✗ Upload failed!', fg='red')
        if result.upload_error:
            click.echo(f'Upload error: {result.upload_error}')
        return False
    return True


@click.command()
@option_definitions_file
@option_input_file
@option_verbose
@click.pass_context
def validate(ctx, definitions_file, input_file, verbose):
    """Validate a metrics file against schema definitions."""
    start_time = time.time()
    settings = MetricsSettings()
    validator = MetricsValidator(settings, verbose)
    if verbose:
        click.echo(f'Validating metrics file: {input_file}')
        click.echo(f'Using definitions file: {definitions_file}')
    try:
        result = validator.validate(input_file, definitions_file)
    except Exception as e:
        handle_exception('✗ Validation error', e)

    if not result.is_valid:
        click.secho('✗ Validation failed!', fg='red')
        print_errors(result.errors)
        ctx.exit(1)

    click.secho('✓ Validation successful!', fg='green')
    if verbose:
        validation_time = time.time() - start_time
        click.echo(f'Validated {result.metrics_count} metrics in {validation_time:.2f} seconds')


@click.command()
@option_definitions_file
@option_input_file
@option_verbose
@option_bucket_type
@option_custom_bucket
@click.pass_context
def upload(ctx, definitions_file, input_file, verbose, bucket_type, custom_bucket):
    """Upload validated metrics to the service."""
    start_time = time.time()
    settings = MetricsSettings()
    validator = MetricsValidator(settings, verbose)
    uploader = MetricsUploader(settings, verbose)
    _validate_upload_options(bucket_type, custom_bucket)
    _print_upload_info(input_file, definitions_file, bucket_type, custom_bucket, verbose)

    validation_result = validator.validate(input_file, definitions_file)
    if not validation_result.is_valid:
        click.secho('✗ Validation failed! Cannot upload invalid metrics.', fg='red')
        print_errors(validation_result.errors)
        ctx.exit(1)

    try:
        result = uploader.upload(validation_result.data, bucket_type, custom_bucket)
    except Exception as e:
        handle_exception('✗ Upload error', e)

    success = _handle_upload_result(result, validation_result, verbose, start_time)
    if not success:
        ctx.exit(1)
