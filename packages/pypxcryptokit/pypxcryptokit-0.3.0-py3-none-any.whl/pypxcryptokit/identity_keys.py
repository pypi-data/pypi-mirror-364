class IdentityKeyStore:
    def init(self, state):
        self.state = state  # instance of x3dh.State

    def get_identity_key_pair(self):
        return self.state._BaseState__identity_key

    def get_signed_prekey(self):
        return self.state._BaseState__signed_pre_key

    def get_one_time_prekey(self):
        try:
            return next(iter(self.state._BaseState__pre_keys)).pub
        except StopIteration:
            raise Exception("No available one-time prekeys.")

    def remove_used_one_time_prekey(self, pub_key: bytes):
        self.state.delete_pre_key(pub_key)
