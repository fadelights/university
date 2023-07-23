import pandas as pd
from ai_game.dtypes import ActionDType, OutcomeDType
from ai_game.parser import load_params

class KnowledgeBase():
    """
    The knowledge base will contain the following data
    in tabular format.

    Fields
    ------
    action: ActionDType
        The type of action carried out by the actor.
            `atk` -> attack
            `blk` -> block
            `ddg` -> dodge

    self_res: OutcomeDType
        Result of the action on oneself.
            `damaged` -> The actor was damaged
            `scored`  -> The actor inflicted damage
            `none`    -> Neither were damaged

    other_res: OutcomeDType
        Result of the action on the enemy.

    score: int
        A score calculated based on the type of action
        and its result for oneself and the enemy.

    Parameters
    ----------
    data: ndarray (structured or homogeneous), Iterable, dict, or DataFrame
        The initial knowledge for the knowledge base.
    """
    def __init__(self, data=None):
        col_types = {
            "action"   : ActionDType,
            "self_res" : OutcomeDType,
            "other_res": OutcomeDType,
            "score"    : int
        }
        data_template = {c: pd.Series(dtype=t) for c, t in col_types.items()}
        self._df = pd.DataFrame(data_template)

        if data is not None:
            col_names = [key for key in col_types]
            data = pd.DataFrame(data, columns=col_names)
            self._df = pd.concat([self._df, data])


    def _score(self, x, path=None):
        """
        By receiving a specific type of action or outcome,
        will provide the relevant information associated with it
        according to a specified configuration file.
        """
        params = load_params(path)
        scores = params["scores"]
        return scores[x]


    def _total_score(self, action, self_res, other_res):
        """
        By receiving row data from the KB, will determine
        its score.
        """
        return (
            self._score(action) +
            self._score(self_res) -
            self._score(other_res)//2
        )


    def _local_search(self, precept):
        # search possible next states
        # this assumes that our action
        # is different from the other agent
        possible_actions = self._df[self._df['action'] != precept]
        if possible_actions.empty:
            return "ddg"

        max_score = possible_actions["score"].max()
        action = possible_actions[possible_actions["score"] == max_score]["action"]
        if len(action) == 0:
            return "ddg"

        return action[0]


    def ask(self, precept):
        """Based on information provided, this will
        ask the KB for a course of action.
        Main algorithm implemented here."""
        if precept is None:
            return "atk"

        else:
            return self._local_search(precept)


    def tell(self, action, self_res, other_res):
        """Will tell the KB what action it took and
        what the result of it was. New information
        is added to the KB via this method."""
        score = self._total_score(action, self_res, other_res)

        # append to kb
        self._df.loc[len(self._df.index)] = [
            action,
            self_res,
            other_res,
            score
        ]
