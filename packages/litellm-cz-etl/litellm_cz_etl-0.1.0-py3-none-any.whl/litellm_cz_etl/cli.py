"""Command line interface for LiteLLM to CloudZero ETL tool."""

import json
import sys

import click

from .analysis import DataAnalyzer
from .database import LiteLLMDatabase
from .output import CloudZeroStreamer, CSVWriter
from .transform import CBFTransformer


@click.command()
@click.option('--input', 'db_connection',
              help='LiteLLM PostgreSQL database connection URL')
@click.option('--csv', 'csv_file',
              help='Output CSV file name')
@click.option('--cz-api-key', 'cz_api_key',
              help='CloudZero API key')
@click.option('--cz-connection-id', 'cz_connection_id',
              help='CloudZero connection ID')
@click.option('--analysis', 'analysis_records', type=int,
              help='Number of records to analyze (enables analysis mode)')
@click.option('--json', 'json_output',
              help='JSON output file for analysis results')
def main(
    db_connection: str | None,
    csv_file: str | None,
    cz_api_key: str | None,
    cz_connection_id: str | None,
    analysis_records: int | None,
    json_output: str | None
) -> None:
    """Transform LiteLLM database data into CloudZero AnyCost CBF format."""

    if not db_connection:
        click.echo("Error: --input (database connection) is required", err=True)
        sys.exit(1)

    try:
        database = LiteLLMDatabase(db_connection)

        if analysis_records is not None:
            click.echo(f"Running analysis mode on {analysis_records} records...")
            analyzer = DataAnalyzer(database)
            results = analyzer.analyze(limit=analysis_records)

            click.echo("Analysis Results:")
            click.echo("=" * 50)
            analyzer.print_results(results)

            if json_output:
                with open(json_output, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                click.echo(f"Analysis results saved to {json_output}")

        else:
            click.echo("Loading data from LiteLLM database...")
            data = database.get_usage_data()

            if data.is_empty():
                click.echo("No data found in database")
                return

            click.echo(f"Processing {len(data)} records...")
            transformer = CBFTransformer()
            cbf_data = transformer.transform(data)

            if csv_file:
                writer = CSVWriter(csv_file)
                writer.write(cbf_data)
                click.echo(f"Data written to {csv_file}")

            elif cz_api_key and cz_connection_id:
                streamer = CloudZeroStreamer(cz_api_key, cz_connection_id)
                streamer.send(cbf_data)
                click.echo("Data sent to CloudZero AnyCost API")

            else:
                error_msg = (
                    "Error: Must specify either --csv or both "
                    "--cz-api-key and --cz-connection-id"
                )
                click.echo(error_msg, err=True)
                sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

