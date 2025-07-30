from message_pb2 import MessageEnvelope

def create_envelope(header, ciphertext):
    envelope = MessageEnvelope()
    envelope.sender_identity_key = header.identity_key
    envelope.sender_ephemeral_key = header.ephemeral_key
    envelope.sender_signed_prekey = header.signed_pre_key
    if header.pre_key:
        envelope.one_time_prekey = header.pre_key
    envelope.ciphertext = ciphertext
    return envelope.SerializeToString()

def parse_envelope(serialized_msg):
    envelope = MessageEnvelope()
    envelope.ParseFromString(serialized_msg)
    return envelope
