import csv
from datetime import datetime
from typing import Dict, List
import logging
from config import CSV_HEADERS, OUTPUT_FILE

logger = logging.getLogger(__name__)

class DataExporter:
    def __init__(self, output_file: str = OUTPUT_FILE):
        self.output_file = output_file
        self._init_csv()

    def _init_csv(self):
        """Initialize CSV file with headers."""
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()
        except Exception as e:
            logger.error(f"Error initializing CSV file: {str(e)}")
            raise

    def export_result(self, result: Dict):
        """Export a single result to CSV file."""
        try:
            result['timestamp'] = datetime.now().isoformat()
            with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writerow(result)
        except Exception as e:
            logger.error(f"Error exporting result: {str(e)}")
            logger.error(f"Failed result: {result}")

    def export_batch(self, results: List[Dict]):
        """Export multiple results to CSV file."""
        try:
            timestamp = datetime.now().isoformat()
            with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                for result in results:
                    result['timestamp'] = timestamp
                    writer.writerow(result)
        except Exception as e:
            logger.error(f"Error exporting batch results: {str(e)}")
            logger.error(f"Failed batch: {results}")
