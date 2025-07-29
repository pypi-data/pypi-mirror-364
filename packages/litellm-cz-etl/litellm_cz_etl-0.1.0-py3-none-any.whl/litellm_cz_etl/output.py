"""Output modules for writing CBF data to various destinations."""

from typing import Any

import click
import httpx
import polars as pl


class CSVWriter:
    """Write CBF data to CSV file."""

    def __init__(self, filename: str):
        """Initialize CSV writer with filename."""
        self.filename = filename

    def write(self, data: pl.DataFrame) -> None:
        """Write CBF data to CSV file."""
        if data.is_empty():
            click.echo("No data to write to CSV")
            return

        flattened_data = self._flatten_dimensions(data)
        flattened_data.write_csv(self.filename)

    def _flatten_dimensions(self, data: pl.DataFrame) -> pl.DataFrame:
        """Flatten dimensions column into separate columns."""
        if 'dimensions' not in data.columns:
            return data

        flattened_records = []

        for row in data.iter_rows(named=True):
            record = dict(row)
            dimensions = record.pop('dimensions', {})

            if isinstance(dimensions, dict):
                for key, value in dimensions.items():
                    record[f'dim_{key}'] = value

            flattened_records.append(record)

        return pl.DataFrame(flattened_records)


class CloudZeroStreamer:
    """Stream CBF data to CloudZero AnyCost API."""

    def __init__(self, api_key: str, connection_id: str):
        """Initialize CloudZero streamer with credentials."""
        self.api_key = api_key
        self.connection_id = connection_id
        self.base_url = "https://api.cloudzero.com"

    def send(self, data: pl.DataFrame) -> None:
        """Send CBF data to CloudZero AnyCost Streaming API."""
        if data.is_empty():
            click.echo("No data to send to CloudZero")
            return

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        url = f"{self.base_url}/v2/anycost/stream/{self.connection_id}"

        with httpx.Client() as client:
            for row in data.iter_rows(named=True):
                payload = self._prepare_payload(row)

                try:
                    response = client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    click.echo(f"Sent record {row.get('resource_id', 'unknown')}")

                except httpx.RequestError as e:
                    resource_id = row.get('resource_id', 'unknown')
                    click.echo(f"Error sending record {resource_id}: {e}", err=True)
                    raise

    def _prepare_payload(self, row: dict[str, Any]) -> dict[str, Any]:
        """Prepare CBF payload for CloudZero API."""
        payload = {
            'timestamp': row.get('timestamp'),
            'service': row.get('service'),
            'resource_id': row.get('resource_id'),
            'cost': row.get('cost'),
            'usage_quantity': row.get('usage_quantity'),
            'usage_unit': row.get('usage_unit'),
            'dimensions': row.get('dimensions', {})
        }

        optional_fields = ['duration_seconds', 'prompt_tokens', 'completion_tokens']
        for field in optional_fields:
            if row.get(field) is not None:
                payload[field] = row.get(field)

        return payload

