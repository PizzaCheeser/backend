import json
from http import HTTPStatus
from typing import Optional, Dict

import requests
from requests import HTTPError

from app.database.base import EsConfig

ES_TIMEOUT = 5


class Client:
    def __init__(self, es: EsConfig):
        self.es = es
        self.client = requests.Session()

    def get_document_source(self, index: str, id: str) -> Optional[Dict]:
        r = self.client.get(f"{self.es.url}{index}/_source/{id}", timeout=ES_TIMEOUT)
        if r.status_code == HTTPStatus.OK:
            return json.loads(r.text)
        elif r.status_code == HTTPStatus.NOT_FOUND:
            return None

        r.raise_for_status()

    def index_document(self, index: str, id: str, body: Dict):
        r = self.client.put(f"{self.es.url}{index}/_doc/{id}",
                            data=json.dumps(body),
                            headers={"Content-Type": "application/json"},
                            timeout=ES_TIMEOUT)
        r.raise_for_status()

    def create_index(self, index: str, body: Dict):
        r = self.client.put(self.es.url + index, json=body, timeout=ES_TIMEOUT)
        r.raise_for_status()

    def delete_index(self, index: str):
        r = self.client.delete(self.es.url + index)
        r.raise_for_status()

    def index_exists(self, index: str) -> bool:
        r = self.client.head(self.es.url + index, timeout=ES_TIMEOUT)
        if r.status_code == HTTPStatus.OK:
            return True
        elif r.status_code == HTTPStatus.NOT_FOUND:
            return False
        raise HTTPError(f"{r.status_code} Server Error: {r.reason} for url: {r.url}", response=r)
