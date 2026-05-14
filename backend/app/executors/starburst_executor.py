import os
import asyncio
import logging
from typing import List, Dict, Any

import trino

logger = logging.getLogger(__name__)


class StarburstExecutor:

    def __init__(self):
        self.mock_mode = (
            str(os.getenv("MOCK_EXECUTION", "false")).lower() == "true"
        )
        if self.mock_mode:
            logger.info("Running in MOCK mode")

    async def execute(self, sql: str, db: Any = None) -> List[Dict[str, Any]]:
        # Clean SQL before sending to Trino
        sql = sql.strip().rstrip(";").strip()

        if self.mock_mode:
            logger.info("EXECUTING MOCK SQL: %s", sql)
            await asyncio.sleep(0.1)
            return [{"delayed_flights": 342, "mock": True}]

        # --- DYNAMIC CONNECTION LOADING ---
        from app.services import connection_store, trino_service
        
        if db is None:
            # Fallback for tests or unexpected paths
            logger.warning("No DB session provided to executor. Falling back to .env defaults.")
            host = os.getenv("TRINO_HOST", "localhost")
            port = int(os.getenv("TRINO_PORT", 8080))
            user = os.getenv("TRINO_USER", "admin")
            catalog = os.getenv("TRINO_CATALOG", "aviation")
            schema = os.getenv("TRINO_SCHEMA", "public")
            password = None
            ssl = False
        else:
            active_conn = connection_store.get_active_connection(db)
            if not active_conn:
                logger.error("No active Trino connection found in database.")
                raise RuntimeError("No active Trino connection. Please connect via Settings first.")
            
            host = active_conn.host
            port = active_conn.port
            user = active_conn.username
            catalog = active_conn.catalog
            schema = active_conn.schema_name
            password = connection_store.decrypt_password(active_conn.encrypted_password)
            ssl = active_conn.ssl_enabled

        logger.info(f"Executing SQL on {host}:{port} (Catalog: {catalog}, Schema: {schema}, User: {user})")
        print(f"TRINO EXECUTION: {host}:{port} | {catalog}.{schema} | SQL: {sql}")

        try:
            from app.models.connection import TrinoConnectionRequest
            conn_req = TrinoConnectionRequest(
                host=host,
                port=port,
                username=user,
                password=password,
                catalog=catalog,
                schema_name=schema,
                ssl_enabled=ssl
            )
            
            conn = trino_service.get_trino_connection(conn_req)
            cursor = conn.cursor()
            cursor.execute(sql)

            rows = cursor.fetchall()
            cursor_desc = cursor.description
            
            if not cursor_desc:
                return []
                
            columns = [desc[0] for desc in cursor_desc]
            results = [dict(zip(columns, row)) for row in rows]

            logger.info("Returned %s rows", len(results))
            return results

        except Exception as e:
            logger.exception("Trino execution failed")
            raise RuntimeError(f"Trino error on {host}:{port}: {str(e)}")