import json

from requests import get

_BASE_URL = 'https://mail.remotix.app'

class Message:
    def __init__(self, data: dict[str, object]):
        self.id = data['id']
        self.sender = data['sender']
        self.subject = data['subject']
        self.body: str = str(data['body'])
        self.received_at = data['received_at']

    def __str__(self):
        return self.body.replace('\r\n', ' ').replace('\n', ' ')[:100] + ('...' if len(self.body) > 100 else '')

    def __repr__(self):
        return f'<Message id={self.id} sender={self.sender} subject={self.subject}>'

def messages(email: str) -> list[Message]:
    return [Message(message) for message in get(f'{_BASE_URL}/inbox/{email.split('@')[0]}').json()]

if __name__ == '__main__':
    print(messages('hazem@remotix.app')[0])
