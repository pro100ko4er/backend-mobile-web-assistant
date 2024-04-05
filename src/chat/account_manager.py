# Management of user account in a chat

class AccountMgr(object):
    """Base class for user account management"""
    def __init__(self, user_id, session_id):
        self.buffer = {}

    def create_msg(self, msg, label):
        return {"msg": msg, "label": label}

    def next_flow(self, direction, msg=None, msg_label=None):
        """Decides what flow to start next"""
        print(f"next_flow: {direction}, {msg}, {msg_label}")

        return self.create_msg("Message from Server", 'chat')


if __name__ == "__main__":
    chat_mode = 'text'
    print(chat_mode)
