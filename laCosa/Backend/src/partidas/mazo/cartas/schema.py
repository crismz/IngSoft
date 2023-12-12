from pydantic import BaseModel

class CardSchema(BaseModel):
    id: int
    num_players: int
    type: str
    name: str
    effect: str
    target: str

    def get_id(self):
        return self.id

    def get_numplayers(self):
        return self.num_players

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def get_effect(self):
        return self.effect

    def get_target(self):
        return self.target