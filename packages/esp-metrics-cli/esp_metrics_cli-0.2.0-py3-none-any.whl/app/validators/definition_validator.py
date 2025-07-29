"""Metrics Definition file validator"""

import typing as t


class MetricsDefinitionValidator:
    """Validates ESP metrics schema definitions."""

    REQUIRED_FIELDS = {'unit', 'friendly_name', 'description'}

    def __init__(self):
        self.errors: list[str] = []

    def extract_metric_metadata(self, definitions: dict, path: str = '') -> dict[str, dict]:
        """Extract metadata (unit, friendly_name, description) for each metric from definitions."""
        metadata: dict = {}

        if not isinstance(definitions, dict):
            return metadata

        properties = definitions.get('properties', {})
        pattern_properties = definitions.get('patternProperties', {})

        # Check if this is a metric definition (has required metadata fields)
        if 'properties' in definitions:
            metric_props = definitions['properties']
            if any(field in metric_props for field in self.REQUIRED_FIELDS):
                metadata[path] = {}
                for field in self.REQUIRED_FIELDS:
                    if field in metric_props:
                        metadata[path][field] = metric_props[field]

        # Recurse through properties
        for prop_name, prop_def in properties.items():
            new_path = f'{path}.{prop_name}' if path else prop_name
            metadata.update(self.extract_metric_metadata(prop_def, new_path))

        # Recurse through pattern properties (for dynamic keys)
        for _pattern, pattern_def in pattern_properties.items():
            new_path = f'{path}.*' if path else '*'
            metadata.update(self.extract_metric_metadata(pattern_def, new_path))

        return metadata

    def validate_metric(self, metric_path: str, metric_def: dict[str, t.Any]) -> bool:
        """Validate a single metric definition."""
        if not isinstance(metric_def, dict):
            self.errors.append(f'{metric_path}: Metric must be an object, got {type(metric_def).__name__}')
            return False

        missing_fields = self.REQUIRED_FIELDS - set(metric_def.get('properties', {}).keys())
        if missing_fields:
            self.errors.append(f'{metric_path}: Missing required fields: {", ".join(sorted(missing_fields))}')
            return False

        properties = metric_def.get('properties', {})

        for field in ['unit', 'friendly_name', 'description']:
            field_def = properties.get(field, {})
            if field_def.get('type') != 'string':
                self.errors.append(f"{metric_path}.{field}: Should be type 'string', got '{field_def.get('type')}'")

        return len([e for e in self.errors if e.startswith(metric_path)]) == 0

    def validate_metrics_in_object(self, obj: dict[str, t.Any], path: str = '') -> None:
        """Recursively validate all metrics in an object."""
        if not isinstance(obj, dict):
            return

        properties = obj.get('properties', {})
        pattern_properties = obj.get('patternProperties', {})

        if self.is_metric_value_definition(obj):
            self.validate_metric(path, obj)
            return

        for prop_name, prop_def in properties.items():
            new_path = f'{path}.{prop_name}' if path else prop_name
            self.validate_metrics_in_object(prop_def, new_path)

        for pattern, pattern_def in pattern_properties.items():
            new_path = f'{path}.<{pattern}>' if path else f'<{pattern}>'
            self.validate_metrics_in_object(pattern_def, new_path)

    def is_metric_value_definition(self, obj: dict[str, t.Any]) -> bool:
        """Check if an object is a metric definition."""
        if 'properties' not in obj:
            return False

        props = obj.get('properties', {})
        return any(field in props for field in self.REQUIRED_FIELDS)

    def _extract_field_paths_from_definitions(self, schema: dict, path: str = '') -> set[str]:
        """Recursively extract all field paths from YAML definitions."""
        paths = set()

        if not isinstance(schema, dict):
            return paths

        properties = schema.get('properties', {})
        pattern_properties = schema.get('patternProperties', {})

        if self.is_metric_value_definition(schema):
            if path:
                paths.add(path)
            return paths

        for prop_name, prop_def in properties.items():
            new_path = f'{path}.{prop_name}' if path else prop_name
            paths.update(self._extract_field_paths_from_definitions(prop_def, new_path))

        for _pattern, pattern_def in pattern_properties.items():
            new_path = f'{path}.*' if path else '*'
            paths.update(self._extract_field_paths_from_definitions(pattern_def, new_path))

        return paths

    def _extract_field_paths_from_metrics(self, data: dict, path: str = '') -> set[str]:
        """Recursively extract all field paths from JSON metrics."""
        paths = set()

        if not isinstance(data, dict):
            if path:
                paths.add(path)
            return paths

        for key, value in data.items():
            new_path = f'{path}.{key}' if path else key

            if isinstance(value, dict):
                if all(not isinstance(v, dict) for v in value.values()):
                    for sub_key in value.keys():
                        sub_path = f'{new_path}.{sub_key}'
                        paths.add(sub_path)
                else:
                    paths.update(self._extract_field_paths_from_metrics(value, new_path))
            else:
                # Leaf value
                paths.add(new_path)

        return paths

    def _extract_type_definitions(self, schema: dict, path: str = '') -> dict[str, str]:
        """Recursively extract type definitions for each field path."""
        type_defs = {}

        if not isinstance(schema, dict):
            return type_defs

        properties = schema.get('properties', {})
        pattern_properties = schema.get('patternProperties', {})

        if 'type' in schema and path:
            type_defs[path] = schema['type']

        for prop_name, prop_def in properties.items():
            new_path = f'{path}.{prop_name}' if path else prop_name
            type_defs.update(self._extract_type_definitions(prop_def, new_path))

        for _pattern, pattern_def in pattern_properties.items():
            new_path = f'{path}.*' if path else '*'
            type_defs.update(self._extract_type_definitions(pattern_def, new_path))

        return type_defs

    def _extract_values_with_types(self, data: dict, path: str = '') -> dict[str, tuple[t.Any, str]]:
        """Recursively extract values and their Python types from JSON metrics."""
        values = {}

        if not isinstance(data, dict):
            if path:
                python_type = type(data).__name__
                values[path] = (data, python_type)
            return values

        for key, value in data.items():
            new_path = f'{path}.{key}' if path else key

            if isinstance(value, dict):
                # Check if this dict contains only non-dict values (leaf node)
                if all(not isinstance(v, dict) for v in value.values()):
                    # This is a metrics object with actual values
                    for sub_key, sub_value in value.items():
                        sub_path = f'{new_path}.{sub_key}'
                        python_type = type(sub_value).__name__
                        values[sub_path] = (sub_value, python_type)
                else:
                    # Continue recursing
                    values.update(self._extract_values_with_types(value, new_path))
            else:
                # Leaf value
                python_type = type(value).__name__
                values[new_path] = (value, python_type)

        return values

    def _normalize_path_for_comparison(self, path: str) -> str:
        """Normalize paths for comparison by replacing specific patterns with wildcards."""
        parts = path.split('.')
        normalized_parts = []

        for part in parts:
            # Replace specific paths (like "apps/my_app/build") with wildcard
            if '/' in part:
                normalized_parts.append('*')
            else:
                normalized_parts.append(part)

        return '.'.join(normalized_parts)

    def _python_type_to_json_schema_type(self, python_type: str) -> str:
        """Convert Python type name to JSON schema type."""
        type_mapping = {
            'int': 'integer',
            'float': 'number',
            'str': 'string',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object',
            'NoneType': 'null',
        }
        return type_mapping.get(python_type, python_type)

    def _json_schema_types_compatible(self, schema_type: str, python_type: str) -> bool:
        """Check if JSON schema type is compatible with Python type."""
        json_schema_type = self._python_type_to_json_schema_type(python_type)

        if schema_type == json_schema_type:
            return True

        if schema_type == 'number' and json_schema_type in ['integer', 'number']:
            return True

        return False

    def validate_field_consistency(self, metrics_data: dict, schema: dict) -> tuple[bool, list[str]]:
        """Validate consistency between fields in JSON metrics and YAML definitions."""
        field_errors: list[str] = []

        try:
            definition_paths = self._extract_field_paths_from_definitions(schema)
            metrics_paths = self._extract_field_paths_from_metrics(metrics_data)

            normalized_definition_paths = {self._normalize_path_for_comparison(path) for path in definition_paths}
            normalized_metrics_paths = {self._normalize_path_for_comparison(path) for path in metrics_paths}

            missing_in_metrics = normalized_definition_paths - normalized_metrics_paths
            missing_in_definitions = normalized_metrics_paths - normalized_definition_paths

            for missing_field in missing_in_metrics:
                error_msg = f"Field '{missing_field}' is defined in YAML but missing in JSON metrics"
                field_errors.append(error_msg)

            for extra_field in missing_in_definitions:
                error_msg = f"Field '{extra_field}' is present in JSON metrics but not defined in YAML"
                field_errors.append(error_msg)

            has_errors = len(missing_in_metrics) > 0 or len(missing_in_definitions) > 0

            return not has_errors, field_errors

        except Exception as e:
            field_errors.append(f'Field consistency validation error: {e}')
            return False, field_errors

    def validate_type_consistency(self, metrics_data: dict, schema: dict) -> tuple[bool, list[str]]:
        """Validate that value types in JSON metrics match types defined in YAML schema."""
        type_errors: list[str] = []

        try:
            type_definitions = self._extract_type_definitions(schema)
            metrics_values = self._extract_values_with_types(metrics_data)

            normalized_type_defs = {}
            for path, schema_type in type_definitions.items():
                normalized_path = self._normalize_path_for_comparison(path)
                normalized_type_defs[normalized_path] = schema_type

            normalized_metrics = {}
            for path, (value, python_type) in metrics_values.items():
                normalized_path = self._normalize_path_for_comparison(path)
                normalized_metrics[normalized_path] = (value, python_type)

            for metrics_path, (value, python_type) in normalized_metrics.items():
                if metrics_path in normalized_type_defs:
                    expected_type = normalized_type_defs[metrics_path]

                    if not self._json_schema_types_compatible(expected_type, python_type):
                        json_schema_type = self._python_type_to_json_schema_type(python_type)
                        error_msg = (
                            f"Type mismatch for field '{metrics_path}': expected '{expected_type}' "
                            f"but got '{json_schema_type}' (value: {repr(value)})"
                        )
                        type_errors.append(error_msg)

            has_errors = len(type_errors) > 0

            return not has_errors, type_errors

        except Exception as e:
            type_errors.append(f'Type consistency validation error: {e}')
            return False, type_errors

    def validate_schema(self, schema: dict[str, t.Any]) -> tuple[bool, list[str]]:
        """Validate a metrics definition schema."""
        if not isinstance(schema, dict):
            self.errors.append('Root element must be an object')
            return False, self.errors

        self.validate_metrics_in_object(schema)
        return (
            len(self.errors) == 0,
            self.errors,
        )

    def validate_schema_with_metrics(self, schema: dict[str, t.Any], metrics_data: dict) -> tuple[bool, list[str]]:
        """Validate schema and check field consistency with metrics data."""
        schema_valid, schema_errors = self.validate_schema(schema)

        field_valid, field_errors = self.validate_field_consistency(metrics_data, schema)
        type_valid, type_errors = self.validate_type_consistency(metrics_data, schema)
        all_errors = schema_errors + field_errors + type_errors

        return schema_valid and field_valid and type_valid, all_errors
