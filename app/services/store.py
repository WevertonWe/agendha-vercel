import json
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Define path for the JSON store using a relative path that works with the app structure
# Assuming app/ is the root for code, lets put data in app/data
BASE_DIR = Path(__file__).resolve().parent.parent # app/
DATA_DIR = BASE_DIR / "data"
FILA_FILE = DATA_DIR / "fila_validacao.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(FILA_FILE):
        with open(FILA_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_queue() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    try:
        with open(FILA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler fila de validação: {e}")
        return []

def save_queue(queue: List[Dict[str, Any]]):
    _ensure_data_dir()
    try:
        with open(FILA_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar fila de validação: {e}")

def add_to_queue(item: Dict[str, Any]) -> Dict[str, Any]:
    queue = load_queue()
    # Add ID if not present
    if 'id' not in item:
        # Simple ID generation: max id + 1 or timestamp
        # Using timestamp + random or just length for simplicity in this context
        item['id'] = str(int(datetime.now().timestamp() * 1000))
    
    if 'data_criacao' not in item:
        item['data_criacao'] = datetime.now().isoformat()
        
    queue.insert(0, item) # Add to top
    save_queue(queue)
    return item

def get_item(item_id: str) -> Dict[str, Any]:
    queue = load_queue()
    for item in queue:
        if str(item.get('id')) == str(item_id):
            return item
    return None

def delete_item(item_id: str) -> bool:
    """
    Remove item from queue by ID. Returns True if found and removed.
    """
    queue = load_queue()
    original_len = len(queue)
    queue = [item for item in queue if str(item.get('id')) != str(item_id)]
    
    if len(queue) < original_len:
        save_queue(queue)
        return True
    return False
