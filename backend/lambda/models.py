from typing import List, Dict

class IssueVector:
    def __init__(self, text_id: str, embedding: List[float], text: str, url: str):
        self.id = text_id
        self.values = embedding
        self.metadata = {
            "text": text,
            "length": len(text),
            "ticket-url": url
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "values": self.values,
            "metadata": self.metadata
        }