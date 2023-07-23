from ai_game.agent import Agent
from random import randint

class Game:
    """
    The game to be played along with its rules.

    The game may be played in either autonomous
    mode (between two agents) or manual mode
    (between a player and an agent, which is the default).
    To instantiate a game, simply initialize two
    agents (with or without some prior knowledgebase)
    and call the `run` method:
    ```
    >>> from agent import Agent
    >>> from game import Game
    >>> agent = Agent()
    >>> game = Game(agent)
    >>> game.run()
    ```

    In order to achieve a more realistic fighting
    scenario, 'turns' don't have their usual meaning---
    first, a turn is decided randomly.
    second, an action is taken by the chosen agent.
    third, the opponent MUST provide a response.
    fourth, the next turn cycle is, again, decided randomly.
    Using this strategy, an agent might be able to attack
    three times in a row before having to start defending.
    """
    def __init__(self, agent_1: Agent, agent_2: Agent = None):
        self.agent_1 = agent_1
        if agent_2 is not None:
            self.auto = True
            self.agent_2 = agent_2
        else:
            self.auto = False
            self.agent_2 = Agent()


    def run(self):
        try:
            while True:
                # TODO: Add auto mode
                turn = self._turn()
                if turn:
                    action_2 = self._menu()
                    action_1 = self.agent_1.kb.ask(action_2)
                    print(f"Enemy's action: {action_1}")
                    self._do(self.agent_2, self.agent_1, action_2, action_1)

                else:
                    # TODO: Add precept
                    action_1 = self.agent_1.kb.ask(precept=None)
                    print(f"Enemy's action: {action_1}")
                    action_2 = self._menu()
                    self._do(self.agent_1, self.agent_2, action_1, action_2)

                self._print_results()
                print("--------------")

        except KeyboardInterrupt:
            print("\n==============")
            print("Final Results:")
            self._print_results()
            if self.agent_1.score > self.agent_2.score:
                print("Agent 1 wins.")
            elif self.agent_1.score < self.agent_2.score:
                print("Agent 2 wins.")
            else:
                print("Draw.")
            print("==============")
            exit()


    def _menu(self):
        message = "0) Attack\n1) Dodge\n2) Block"
        option = input(f"{message}\nChoose an action: ")

        match option:
            case "0":
                return "atk"
            case "1":
                return "ddg"
            case "2":
                return "blk"
            case _:
                print("Unknown option, try again.")
                return self._menu()


    def _turn(self):
        return randint(0, 1)


    def _do(self, actor: Agent, receiver: Agent, actor_action, receiver_action):
        """The `actor` does an action on `receiver`
        and the receiver responds with another action.
        The scores gained/lost are calculated here and
        applied in-place"""
        # useless actions
        if actor_action in {"blk", "ddg"} and receiver_action in {"blk", "ddg"}:
            actor_res = "none"
            receiver_res = "none"
        elif actor_action == "atk" and receiver_action == "atk":
            actor_res = "scored"
            receiver_res = "damaged"
        elif actor_action == "atk" and receiver_action == "ddg":
            actor_res = "none"
            receiver_res = "none"
        elif actor_action == "atk" and receiver_action == "blk":
            actor_res = "scored"
            receiver_res = "damaged"
        elif actor_action == "ddg" and receiver_action == "atk":
            actor_res = "none"
            receiver_res = "none"
        elif actor_action == "blk" and receiver_action == "atk":
            actor_res = "damaged"
            receiver_res = "scored"

        actor.kb.tell(actor_action, actor_res, receiver_res)
        receiver.kb.tell(receiver_action, receiver_res, actor_res)
        actor.score += \
            actor.kb._total_score(actor_action, actor_res, receiver_res)
        receiver.score += \
            actor.kb._total_score(receiver_action, receiver_res, actor_res)


    def _print_results(self):
        print(f"Agent 1's score: {self.agent_1.score}")
        print(f"Agent 2's score: {self.agent_2.score}")
