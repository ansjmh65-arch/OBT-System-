import logging
import os

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    filename='logs/obt_system.log',
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    encoding='utf-8'
)

logger = logging.getLogger('OBTSystem')
