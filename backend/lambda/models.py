from typing import List, Dict

class IssueVector:
    def __init__(self, text_id: str, embedding: List[float],id, text: str, creator ,url: str):
        self.id = text_id
        self.values = embedding
        self.metadata = {
            "id": id,
            "text": text,
            "creator": creator,
            "ticket-url": url
        }
    def set_embedding(self, embedding: List[float]):
        self.values = embedding
        
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "values": self.values,
            "metadata": self.metadata
        }
    def get_metadata(self):
        return self.metadata