# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger("OBT.Utils")

class SecurityUtils:
    @staticmethod
    def sanitize_input(text: str) -> str:
        return text.strip().replace("<", "&lt;").replace(">", "&gt;")
      
