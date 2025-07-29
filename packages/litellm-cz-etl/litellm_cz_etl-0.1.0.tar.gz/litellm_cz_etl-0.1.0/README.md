# LiteLLM to CloudZero ETL Tool

Transform LiteLLM database data into CloudZero AnyCost CBF format for cost tracking and analysis.

## Features

- Extract usage data from LiteLLM PostgreSQL database
- Transform data into CloudZero Billing Format (CBF)
- Analysis mode for data inspection and validation
- Multiple output options: CSV files or direct CloudZero API streaming
- Built with modern Python tools: uv, ruff, pytest

## Installation

```bash
# Install from PyPI (once published)
uv add litellm-cz-etl

# Or install from source
git clone <repository-url>
cd litellm-cz-etl
uv sync
```

## Usage

### Analysis Mode

Inspect your LiteLLM data to understand its structure:

```bash
# Analyze 100 recent records
litellm-cz-etl --input "postgresql://user:pass@host:5432/litellm_db" --analysis 100

# Save analysis results to JSON
litellm-cz-etl --input "postgresql://user:pass@host:5432/litellm_db" --analysis 100 --json analysis.json
```

### Export to CSV

```bash
litellm-cz-etl --input "postgresql://user:pass@host:5432/litellm_db" --csv output.csv
```

### Stream to CloudZero AnyCost API

```bash
litellm-cz-etl --input "postgresql://user:pass@host:5432/litellm_db" \
  --cz-api-key "your-cloudzero-api-key" \
  --cz-connection-id "your-connection-id"
```

## Data Transformation

The tool transforms LiteLLM usage logs into CloudZero's CBF format with the following mappings:

- `spend` → `cost`
- `total_tokens` → `usage_quantity`
- `model`, `user_id`, `call_type` → `dimensions`
- `metadata` fields → additional `dimensions`
- Duration calculated from `startTime` and `endTime`

## Development

```bash
# Setup development environment
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check src/ tests/

# Fix linting issues
uv run ruff check --fix src/ tests/
```

## Requirements

- Python ≥ 3.12
- PostgreSQL database with LiteLLM data
- CloudZero API key and connection ID (for streaming mode)

## License

Open source - see LICENSE file for details.
EOF < /dev/null