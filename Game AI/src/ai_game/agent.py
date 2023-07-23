from ai_game.knowledge import KnowledgeBase
from ai_game.parser import load_params

class Agent:
    """
    The agent class that will be playing the game.

    The agent will be holding a knowledge base
    which it will be basing its decisions upon.
    The knowledge base has a limited size
    and new knowledge will replace the old ones
    in a 'least recently used' manner.
    """
    def __init__(self, init_knowledge=None):
        self.kb = KnowledgeBase(init_knowledge)
        self.kb_size = load_params()["kb_size"]
        self.score = 0
