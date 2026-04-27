import logging
from typing import List
from fastapi import WebSocket

# ==============================================================================
# GERENCIADOR DE CONEXÕES WEBSOCKET
# ==============================================================================

class ConnectionManager:
    """Gerencia as conexões WebSocket ativas para comunicação em tempo real
    com os clientes."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info("Nova conexão WebSocket estabelecida.")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info("Conexão WebSocket fechada.")

    async def send_message(self, message: str, beneficiario_id: str = None):
        log_msg_prefix = "WS Enviando"
        if beneficiario_id:
            message_to_send = f"[{beneficiario_id}] {message}"
            log_msg_prefix += f" para Beneficiário ID [{beneficiario_id}]"
        else:
            message_to_send = message
        logging.info("%s: %s", log_msg_prefix, message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message_to_send)
            except Exception:
                logging.error("Erro ao enviar msg WS para %s",
                              connection.client, exc_info=True)


manager = ConnectionManager()


from app.core.database import get_db_connection  # noqa: E402
from fastapi import Request  # noqa: E402

# Dependency wrapper to inject request
def get_db(request: Request):
    # Properly yield from the generator to maintain context and cleanup
    yield from get_db_connection(request)
