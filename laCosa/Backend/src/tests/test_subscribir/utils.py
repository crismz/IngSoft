from pydantic import BaseModel

class WelcomeMessage(BaseModel):
    msg: str = ""

    def set_msg(self, text: str):
        self.msg = text
        return

    def get_msg(self):
        return self.msg
