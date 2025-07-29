"""Database connection and data extraction for LiteLLM."""

import polars as pl
import psycopg2


class LiteLLMDatabase:
    """Handle LiteLLM PostgreSQL database connections and queries."""

    def __init__(self, connection_string: str):
        """Initialize database connection."""
        self.connection_string = connection_string
        self._connection: psycopg2.extensions.connection | None = None

    def connect(self) -> psycopg2.extensions.connection:
        """Establish database connection."""
        if self._connection is None or self._connection.closed:
            self._connection = psycopg2.connect(self.connection_string)
        return self._connection

    def get_usage_data(self, limit: int | None = None) -> pl.DataFrame:
        """Retrieve usage data from LiteLLM database."""
        query = """
        SELECT
            id,
            request_id,
            call_type,
            cache_hit,
            cache_key,
            model,
            model_id,
            user_id,
            spend,
            startTime,
            endTime,
            total_tokens,
            prompt_tokens,
            completion_tokens,
            metadata
        FROM LiteLLM_SpendLogs
        ORDER BY startTime DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        conn = self.connect()
        try:
            return pl.read_database(query, conn)
        finally:
            conn.close()

    def get_table_info(self) -> dict:
        """Get information about the LiteLLM_SpendLogs table structure."""
        query = """
        SELECTcolumn_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'litellm_spendlogs'
        ORDER BY ordinal_position;
        """

        conn = self.connect()
        try:
            columns_df = pl.read_database(query, conn)
            return {
                'columns': columns_df.to_dicts(),
                'row_count': self._get_row_count(conn)
            }
        finally:
            conn.close()

    def _get_row_count(self, conn: psycopg2.extensions.connection) -> int:
        """Get total row count from LiteLLM_SpendLogs table."""
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM LiteLLM_SpendLogs")
            return cursor.fetchone()[0]

