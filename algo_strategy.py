import gamelib
import random
import math
import warnings
from sys import maxsize


class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()

    def on_game_start(self, config):
        gamelib.debug_write('----- START -----')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

    def on_turn(self, turn_state):
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('----- {} -----'.format(game_state.turn_number))
        self.starter_strategy(game_state)
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        self.build_defences(game_state)
        self.deploy_attackers(game_state)

    def build_defences(self, game_state):
        to_build = [["DESTRUCTOR", [27, 13]], ["DESTRUCTOR", [1, 12]], ["DESTRUCTOR", [13, 11]],
                    ["DESTRUCTOR", [7, 11]], ["DESTRUCTOR", [18, 11]], ["DESTRUCTOR", [9, 11]],
                    ["DESTRUCTOR", [24, 10]], ["DESTRUCTOR", [25, 11]], ["FILTER", [0, 13]], ["FILTER", [1, 13]],
                    ["FILTER", [2, 13]],
                    ["FILTER", [3, 13]], ["FILTER", [4, 12]], ["FILTER", [5, 12]], ["FILTER", [6, 12]],
                    ["FILTER", [7, 12]], ["FILTER", [8, 12]], ["FILTER", [9, 12]], ["FILTER", [10, 12]],
                    ["FILTER", [11, 12]], ["FILTER", [12, 12]], ["FILTER", [13, 12]], ["FILTER", [14, 12]],
                    ["FILTER", [15, 12]], ["FILTER", [16, 12]], ["FILTER", [17, 12]], ["FILTER", [18, 12]],
                    ["FILTER", [19, 12]], ["FILTER", [20, 12]], ["FILTER", [21, 12]], ["FILTER", [22, 12]],
                    ["DESTRUCTOR", [26, 12]], ["FILTER", [26, 13]], ["FILTER", [25, 12]],
                    ["FILTER", [24, 11]], ["FILTER", [23, 10]], ["DESTRUCTOR", [2, 12]], ["DESTRUCTOR", [3, 12]],
                    ["DESTRUCTOR", [21, 11]], ["ENCRYPTOR", [19, 11]], ["FILTER", [6, 9]], ["FILTER", [7, 9]],
                    ["FILTER", [8, 9]], ["FILTER", [9, 9]], ["FILTER", [10, 9]], ["FILTER", [11, 9]],
                    ["FILTER", [12, 9]], ["FILTER", [13, 9]], ["FILTER", [14, 9]], ["FILTER", [15, 9]],
                    ["FILTER", [16, 9]], ["FILTER", [17, 9]], ["FILTER", [18, 9]], ["FILTER", [19, 9]],
                    ["FILTER", [20, 9]], ["FILTER", [21, 9]], ["FILTER", [22, 9]], ["DESTRUCTOR", [16, 11]],
                    ["DESTRUCTOR", [4, 11]], ["DESTRUCTOR", [10, 11]], ["DESTRUCTOR", [9, 11]],
                    ["DESTRUCTOR", [11, 11]], ["DESTRUCTOR", [15, 11]], ["DESTRUCTOR", [12, 11]],
                    ["DESTRUCTOR", [14, 11]], ["DESTRUCTOR", [5, 11]], ["DESTRUCTOR", [8, 11]],
                    ["DESTRUCTOR", [17, 11]], ["DESTRUCTOR", [20, 11]], ["DESTRUCTOR", [6, 11]],
                    ["DESTRUCTOR", [23, 9]], ["DESTRUCTOR", [22, 8]], ["DESTRUCTOR", [21, 8]], ["DESTRUCTOR", [19, 8]],
                    ["DESTRUCTOR", [17, 8]], ["DESTRUCTOR", [15, 8]], ["DESTRUCTOR", [13, 8]], ["DESTRUCTOR", [11, 8]],
                    ["DESTRUCTOR", [9, 8]], ["DESTRUCTOR", [7, 8]]]
        for item in to_build:
            itemtype = item[0]
            type = DESTRUCTOR
            if itemtype == "FILTER":
                type = FILTER
            elif itemtype == "ENCRYPTOR":
                type = ENCRYPTOR
            elif itemtype != "DESTRUCTOR":
                gamelib.debug_write("preset build loadin is messed up with an input of: " + itemtype)
            location = item[1]
            if game_state.can_spawn(type, location):
                game_state.attempt_spawn(type, location)

    def deploy_attackers(self, game_state):
        if game_state.get_resource(game_state.BITS) < 10 and game_state.turn_number < 8:
            return
        if game_state.get_resource(game_state.BITS) < 12 and game_state.turn_number >= 8:
            return
        type_to_spawn = PING
        if game_state.turn_number >= 8:
            type_to_spawn = EMP
        spawn_point = [13, 0]
        num_spawn = game_state.number_affordable(type_to_spawn)
        game_state.attempt_spawn(type_to_spawn, spawn_point, num_spawn)


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
