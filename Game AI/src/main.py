import ai_game

if __name__  == "__main__":
    agent = ai_game.Agent()
    game = ai_game.Game(agent)

    game.run()
