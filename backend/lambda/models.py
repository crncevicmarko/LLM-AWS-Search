from typing import List, Dict

class IssueVector:
    def __init__(self, text_id: str, embedding: List[float],id, text: str, creator, assignee, time_created, time_updated, status, url: str):
        self.id = text_id
        self.values = embedding
        self.metadata = {
            "id": id,
            "text": text,
            "creator": creator,
            "assignee": assignee,
            "time-created": time_created,
            "time-updated": time_updated,
            "status": status,
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