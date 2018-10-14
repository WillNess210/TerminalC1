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
        gamelib.debug_write('Configuring your custom algo strategy...')
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
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.
        self.starter_strategy(game_state)
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        self.build_defences(game_state)
        self.deploy_attackers(game_state)

    def build_defences(self, game_state):
        to_build = [["DESTRUCTOR", [0, 13]], ["DESTRUCTOR", [27, 13]], ["DESTRUCTOR", [7, 11]],
                    ["DESTRUCTOR", [20, 11]], ["FILTER", [1, 13]], ["FILTER", [2, 13]], ["FILTER", [25, 13]],
                    ["FILTER", [26, 13]], ["FILTER", [3, 12]], ["FILTER", [24, 12]], ["FILTER", [4, 11]],
                    ["FILTER", [5, 11]], ["FILTER", [6, 11]], ["FILTER", [21, 11]], ["FILTER", [22, 11]],
                    ["FILTER", [23, 11]], ["FILTER", [9, 12]], ["DESTRUCTOR", [9, 11]], ["FILTER", [12, 12]],
                    ["DESTRUCTOR", [12, 11]], ["FILTER", [15, 12]], ["DESTRUCTOR", [15, 11]], ["FILTER", [18, 12]],
                    ["DESTRUCTOR", [18, 11]]]
        for item in to_build:
            itemtype = item[0]
            firewall_type = DESTRUCTOR
            if itemtype == "FILTER":
                firewall_type = FILTER
            elif itemtype == "ENCRYPTOR":
                firewall_type = ENCRYPTOR
            elif itemtype != "DESTRUCTOR":
                gamelib.debug_write("preset build loadin is messed up with an input of: " + itemtype)
            location = item[1]
            if game_state.can_spawn(firewall_type, location):
                game_state.attempt_spawn(firewall_type, location)
        # TODO implement destructor replacement
        # TODO implement path creation

    def deploy_attackers(self, game_state):
        # TODO place units at location that will travel the longest
        # TODO choose unit type based on if they can reach wall or if we want to do building damage
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
