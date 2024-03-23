import logging
import os
import sys

project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
if project_root not in sys.path:
    sys.path.append(project_root)


class SuppressOpenAIRequestOptions(logging.Filter):
    def filter(self, record):
        return not (record.levelname == 'DEBUG' and 
                    record.name == 'openai._base_client' and 
                    'Request options' in record.getMessage())


logging.getLogger('openai._base_client').addFilter(SuppressOpenAIRequestOptions())
logging.getLogger('scrapy').propagate = False
