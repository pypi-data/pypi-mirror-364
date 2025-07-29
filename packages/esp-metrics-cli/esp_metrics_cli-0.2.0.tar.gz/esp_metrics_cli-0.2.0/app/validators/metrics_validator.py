import logging
import time
import typing as t

from datetime import datetime

import jsonschema

from pydantic import ValidationError

from app.models import MetricsData
from app.models.config import MetricsSettings
from app.models.result import ValidationResult
from app.utils import format_bytes
from app.utils import get_file_size
from app.utils import load_json_file
from app.utils import load_yaml_file
from app.validators.definition_validator import MetricsDefinitionValidator

logger = logging.getLogger(__name__)


class MetricsValidator:
    """Consolidated metrics validator that handles all validation steps."""

    def __init__(self, settings: MetricsSettings, verbose: bool = False):
        """Initialize the validator with settings and verbosity level."""
        self.settings = settings
        self.verbose = verbose
        self.definition_validator = MetricsDefinitionValidator()

    def validate(self, input_file: str, definitions_file: str) -> ValidationResult:
        """Validate a metrics file against Pydantic model and schema."""
        start_time = time.time()
        result = ValidationResult(is_valid=False)

        try:
            metrics_payload = self._validate_file_size_and_load(input_file, result)
            if metrics_payload is None:
                return result

            schema = self._load_definitions_schema(definitions_file, result)
            if schema is None:
                return result

            if not self._validate_definitions_schema(schema, result, metrics_payload):
                return result

            if not self._validate_json_schema(metrics_payload, schema, result):
                return result

            fields_metadata = self.definition_validator.extract_metric_metadata(schema)
            metrics_data = {
                'commit_sha': self.settings.commit_sha,
                'project_url': self.settings.project_url,
                'project_id': self.settings.project_id,
                'schema_version': self.settings.schema_version,
                'timestamp': datetime.utcnow().isoformat(timespec='milliseconds'),
                'metrics': metrics_payload,
                'metadata': {'metric_fields': fields_metadata},
            }
            if not self._validate_model(metrics_data, result):
                return result

            result.is_valid = not result.errors
            result.data = metrics_data

            if self.verbose:
                logger.info(f'Validation completed: {result.is_valid=}')
                logger.info(f'Found {result.metrics_count} metrics')

        except Exception as e:
            logger.exception('Unexpected error during validation')
            result.errors.append(f'Unexpected validation error: {e}')
        finally:
            result.validation_time = time.time() - start_time

        return result

    def _validate_file_size_and_load(self, input_file: str, result: ValidationResult) -> dict | None:
        """Validate file size and load metrics file."""
        try:
            result.file_size = get_file_size(input_file)
            if self.verbose:
                logger.info(f'Metrics file size: {format_bytes(result.file_size)}')

            if result.file_size > self.settings.max_metrics_size:
                max_mb = self.settings.max_metrics_size / (1024 * 1024)
                file_mb = result.file_size / (1024 * 1024)
                result.errors.append(
                    f'File {input_file} is too large ({file_mb:.1f}MB), maximum allowed is {max_mb:.1f}MB'
                )
                return None

            if self.verbose:
                logger.info(f'Loading metrics file: {input_file}')

            return load_json_file(input_file)  # type: ignore

        except Exception as e:
            result.errors.append(f'Error loading metrics file: {e}')
            return None

    def _load_definitions_schema(self, definitions_file: str, result: ValidationResult) -> t.Any:
        """Load definitions file and extract schema."""
        if self.verbose:
            logger.info(f'Loading definitions file: {definitions_file}')
        try:
            return load_yaml_file(definitions_file)
        except Exception as e:
            result.errors.append(f'Error loading definitions file: {e}')
            return None

    def _validate_definitions_schema(
        self, schema: dict, result: ValidationResult, metrics_data: dict[t.Any, t.Any]
    ) -> bool:
        """Validate that the definitions schema contains required metric fields and check field consistency."""
        if self.verbose:
            logger.info('Validating definitions schema for required metric fields')

        try:
            if metrics_data is not None:
                if self.verbose:
                    logger.info('Performing field consistency validation between metrics and definitions')
                is_valid, errors = self.definition_validator.validate_schema_with_metrics(schema, metrics_data)
            else:
                is_valid, errors = self.definition_validator.validate_schema(schema)

            for error in errors:
                result.errors.append(f'Definition schema validation error: {error}')

            if self.verbose:
                if is_valid:
                    logger.info('Definitions schema validation passed')
                else:
                    logger.error(f'Definitions schema validation failed with {len(errors)} errors')

            return is_valid
        except Exception as e:
            result.errors.append(f'Unexpected definition validation error: {e}')
            return False

    def _validate_json_schema(self, metrics_data: dict, schema: dict, result: ValidationResult) -> bool:
        """Validate metrics data against JSON schema."""
        if self.verbose:
            logger.info('Validating metrics against JSON schema')
        try:
            jsonschema.validate(metrics_data, schema)
            if self.verbose:
                logger.info('Metrics passed JSON schema validation')
            return True
        except Exception as e:
            result.errors.append(f'JSON schema validation error: {e}')
            return False

    def _validate_model(self, metrics_data: dict, result: ValidationResult) -> bool:
        """Validate metrics data against Pydantic model."""
        if self.verbose:
            logger.info('Validating metrics against schema model')
        try:
            validated_metrics = MetricsData(**metrics_data)
            result.metrics_count = len(validated_metrics.metrics)
            if self.verbose:
                logger.info('Metrics structure validated successfully')
                logger.info(f'Metrics keys: {list(validated_metrics.metrics.keys())}')
            return True
        except ValidationError as e:
            for error in e.errors():
                field_path = ' -> '.join(str(p) for p in error['loc']) if error['loc'] else 'root'
                result.errors.append(f'Pydantic validation failed at {field_path}: {error["msg"]}')
            return False
        except Exception as e:
            result.errors.append(f'Unexpected Pydantic validation error: {e}')
            return False
