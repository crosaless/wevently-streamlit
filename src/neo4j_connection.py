import os
import logging
from langchain_neo4j import Neo4jGraph

logger = logging.getLogger(__name__)

def get_graph():
    """Return a Neo4jGraph connected to Aura if available, otherwise fall back to local.

    Reads credentials from environment variables. Logs which endpoint is used
    but never writes credentials to logs.
    """
    # Read env vars
    aura_uri = os.getenv('NEO4J_URI') or os.getenv('NEO4J_URL_QUERY') or ''
    bolt_local = os.getenv('NEO4J_URL', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USERNAME', 'neo4j')
    pwd = os.getenv('NEO4J_PASSWORD', '')

    # Try remote (Aura) first if a URI is provided
    if aura_uri:
        try:
            logger.info('Intentando conectar a Neo4j remoto (Aura)...')
            graph = Neo4jGraph(url=aura_uri, username=user, password=pwd)
            # quick smoke-test query to validate connection
            try:
                graph.query('RETURN 1 AS ok')
                logger.info('Conexión Neo4j establecida en remoto (Aura).')
                return graph
            except Exception:
                # remote driver created but query failed; close and fallback
                logger.warning('No fue posible ejecutar consulta en Neo4j remoto; se probará conexión local.')
        except Exception:
            logger.warning('Fallo al inicializar conexión Neo4j remoto; se probará conexión local.')

    # Fallback to local
    try:
        logger.info('Intentando conectar a Neo4j local...')
        graph = Neo4jGraph(url=bolt_local, username=user, password=pwd)
        # test
        graph.query('RETURN 1 AS ok')
        logger.info('Conexión Neo4j establecida en local.')
        return graph
    except Exception as e:
        logger.error('No fue posible conectar a Neo4j (remoto ni local). Revisa las instancias.', exc_info=True)
        raise
