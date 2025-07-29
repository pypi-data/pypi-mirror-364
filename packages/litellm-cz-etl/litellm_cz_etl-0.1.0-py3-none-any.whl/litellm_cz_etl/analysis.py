"""Data analysis module for LiteLLM database inspection."""

from typing import Any

import click
import polars as pl

from .database import LiteLLMDatabase


class DataAnalyzer:
    """Analyze LiteLLM database data for inspection and validation."""

    def __init__(self, database: LiteLLMDatabase):
        """Initialize analyzer with database connection."""
        self.database = database

    def analyze(self, limit: int = 100) -> dict[str, Any]:
        """Perform comprehensive analysis of LiteLLM data."""
        data = self.database.get_usage_data(limit=limit)
        table_info = self.database.get_table_info()


        return {
            'table_info': table_info,
            'data_summary': self._analyze_data_summary(data),
            'column_analysis': self._analyze_columns(data),
            'sample_records': data.head(5).to_dicts() if not data.is_empty() else []
        }

    def _analyze_data_summary(self, data: pl.DataFrame) -> dict[str, Any]:
        """Analyze basic data summary statistics."""
        if data.is_empty():
            return {'message': 'No data available'}

        columns = data.columns

        return {
            'total_records_analyzed': len(data),
            'date_range': {
                'start': (
                    str(data['starttime'].min())
                    if 'starttime' in columns else None
                ),
                'end': (
                    str(data['starttime'].max())
                    if 'starttime' in columns else None
                )
            },
            'total_spend': (
                float(data['spend'].sum())
                if 'spend' in columns else None
            ),
            'total_tokens': (
                int(data['total_tokens'].sum())
                if 'total_tokens' in columns else None
            ),
            'data_types': {
                col: str(dtype)
                for col, dtype in zip(columns, data.dtypes, strict=False)
            }
        }

    def _analyze_columns(self, data: pl.DataFrame) -> dict[str, dict[str, Any]]:
        """Analyze each column for unique values and statistics."""
        column_analysis = {}

        for column in data.columns:
            series = data[column]
            dtype = series.dtype

            analysis = {
                'unique_count': series.n_unique(),
                'null_count': series.null_count(),
                'data_type': str(dtype)
            }

            if dtype in [pl.String, pl.Utf8]:
                value_counts = series.value_counts().limit(10)
                if not value_counts.is_empty():
                    analysis['top_values'] = {
                        row[column]: row['count']
                        for row in value_counts.to_dicts()
                    }
            elif dtype.is_numeric():
                if not data.is_empty():
                    analysis['stats'] = {
                        'min': (
                            float(series.min())
                            if series.min() is not None else None
                        ),
                        'max': (
                            float(series.max())
                            if series.max() is not None else None
                        ),
                        'mean': (
                            float(series.mean())
                            if series.mean() is not None else None
                        ),
                        'median': (
                            float(series.median())
                            if series.median() is not None else None
                        ),
                    }

            column_analysis[column] = analysis

        return column_analysis

    def print_results(self, analysis: dict[str, Any]) -> None:
        """Print analysis results to console in a readable format."""
        table_info = analysis['table_info']
        data_summary = analysis['data_summary']
        column_analysis = analysis['column_analysis']

        click.echo("Table Structure:")
        click.echo(f"  Total rows in database: {table_info['row_count']:,}")
        click.echo(f"  Columns: {len(table_info['columns'])}")

        click.echo("\nData Summary:")
        if 'message' in data_summary:
            click.echo(f"  {data_summary['message']}")
        else:
            records_analyzed = data_summary['total_records_analyzed']
            click.echo(f"  Records analyzed: {records_analyzed:,}")
            if data_summary['date_range']['start']:
                start_date = data_summary['date_range']['start']
                end_date = data_summary['date_range']['end']
                click.echo(f"  Date range: {start_date} to {end_date}")
            if data_summary['total_spend']:
                click.echo(f"  Total spend: ${data_summary['total_spend']:.2f}")
            if data_summary['total_tokens']:
                click.echo(f"  Total tokens: {data_summary['total_tokens']:,}")

        click.echo("\nColumn Analysis:")
        for column, stats in column_analysis.items():
            click.echo(f"  {column}:")
            click.echo(f"    Type: {stats['data_type']}")
            click.echo(f"    Unique values: {stats['unique_count']:,}")
            click.echo(f"    Null values: {stats['null_count']:,}")

            if 'top_values' in stats:
                click.echo("    Top values:")
                for value, count in list(stats['top_values'].items())[:5]:
                    click.echo(f"      '{value}': {count}")

            if 'stats' in stats:
                stats_info = stats['stats']
                click.echo("    Statistics:")
                click.echo(f"      Min: {stats_info['min']}")
                click.echo(f"      Max: {stats_info['max']}")
                click.echo(f"      Mean: {stats_info['mean']:.2f}")
                click.echo(f"      Median: {stats_info['median']:.2f}")

            click.echo("")

