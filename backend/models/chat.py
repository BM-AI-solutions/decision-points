from google.cloud import datastore

class Chat:
    def __init__(self, user_id, business_id, messages, created_at):
        self.user_id = user_id
        self.business_id = business_id
        self.messages = messages
        self.created_at = created_at

    @staticmethod
    def from_entity(entity):
        return Chat(
            user_id=entity['user_id'],
            business_id=entity['business_id'],
            messages=entity['messages'],
            created_at=entity['created_at']
        )

    def to_entity(self, client):
        entity = datastore.Entity(client.key('Chat'))
        entity.update({
            'user_id': self.user_id,
            'business_id': self.business_id,
            'messages': self.messages,
            'created_at': self.created_at
        })
        return entity