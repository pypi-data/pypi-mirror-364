import pickle
import os

class SessionStore:
    def init(self, path='sessions'):
        self.path = path
        os.makedirs(path, exist_ok=True)

    def _session_file(self, recipient_id: str) -> str:
        return os.path.join(self.path, f"{recipient_id}.pkl")

    def store_session(self, recipient_id: str, session):
        with open(self._session_file(recipient_id), 'wb') as f:
            pickle.dump(session, f)

    def load_session(self, recipient_id: str):
        try:
            with open(self._session_file(recipient_id), 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None
