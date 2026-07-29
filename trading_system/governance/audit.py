import logging
from datetime import datetime
import os

class AuditLogger:
    def __init__(self, log_dir="logs"):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.logger = logging.getLogger("GovernanceAudit")
        self.logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if instantiated multiple times
        if not self.logger.handlers:
            log_file = os.path.join(log_dir, f"audit_{datetime.now().strftime('%Y%m%d')}.log")
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            fh.setFormatter(formatter)
            
            self.logger.addHandler(fh)
        
    def log(self, entity: str, rationale: str):
        """
        Commits blocked or modified trade rationales to an immutable log.
        """
        self.logger.info(f"[{entity}] {rationale}")
