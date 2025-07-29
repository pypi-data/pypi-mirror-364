"""Transform LiteLLM data to CloudZero AnyCost CBF format."""

import json
from datetime import datetime
from typing import Any

import polars as pl


class CBFTransformer:
    """Transform LiteLLM usage data to CloudZero Billing Format (CBF)."""

    def transform(self, data: pl.DataFrame) -> pl.DataFrame:
        """Transform LiteLLM data to CBF format."""
        if data.is_empty():
            return pl.DataFrame()

        cbf_data = []

        for row in data.iter_rows(named=True):
            cbf_record = self._create_cbf_record(row)
            cbf_data.append(cbf_record)

        return pl.DataFrame(cbf_data)

    def _create_cbf_record(self, row: dict[str, Any]) -> dict[str, Any]:
        """Create a single CBF record from LiteLLM row."""

        start_time = self._parse_timestamp(row.get('starttime'))
        end_time = self._parse_timestamp(row.get('endtime'))

        dimensions = {
            'model': str(row.get('model', '')),
            'user_id': str(row.get('user_id', '')),
            'call_type': str(row.get('call_type', '')),
            'cache_hit': str(row.get('cache_hit', False)),
        }

        if row.get('metadata'):
            try:
                if isinstance(row['metadata'], str):
                    metadata = json.loads(str(row['metadata']))
                else:
                    metadata = row['metadata']
                if isinstance(metadata, dict):
                    for key, value in metadata.items():
                        dimensions[f'metadata_{key}'] = str(value)
            except (json.JSONDecodeError, TypeError):
                pass


        return {
            'timestamp': start_time.isoformat() if start_time else None,
            'service': 'litellm',
            'resource_id': str(row.get('request_id', '')),
            'cost': float(row.get('spend', 0.0)),
            'usage_quantity': int(row.get('total_tokens', 0)),
            'usage_unit': 'tokens',
            'dimensions': dimensions,
            'duration_seconds': self._calculate_duration(start_time, end_time),
            'prompt_tokens': int(row.get('prompt_tokens', 0)),
            'completion_tokens': int(row.get('completion_tokens', 0)),
        }

    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp from various formats."""
        if timestamp is None:
            return None

        if isinstance(timestamp, datetime):
            return timestamp

        if isinstance(timestamp, str):
            try:
                # Use polars datetime parsing
                return pl.Series([timestamp]).str.to_datetime().item()
            except Exception:
                return None

        return None

    def _calculate_duration(self, start_time: datetime, end_time: datetime) -> float:
        """Calculate duration in seconds between start and end time."""
        if start_time and end_time:
            try:
                delta = end_time - start_time
                return delta.total_seconds()
            except Exception:
                return 0.0
        return 0.0

