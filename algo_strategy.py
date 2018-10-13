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
        if game_state.turn_number > 0:
            self.build_defences(game_state)
            self.deploy_attackers(game_state)


    def build_defences(self, game_state):
        firewall_locations = []
        for radius in range(0, 5):
            for direction in [-1, 1]:
                start = 12
                if direction == -1:
                    start = 15
                newx = start + (direction * radius * 3)
                firewall_locations.append([newx, 12])
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        filter_locations = []
        for radius in range(0, 12):
            for direction in [-1, 1]:
                start = 13
                if direction == -1:
                    start = 14
                newx = start + (direction * radius)
                filter_locations.append([newx, 13])
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
        encryptor_locations = [[2, 13]]
        for location in encryptor_locations:
            if game_state.attempt_spawn(ENCRYPTOR, location):
                game_state.attempt_spawn(ENCRYPTOR, location)

    def deploy_attackers(self, game_state):
        if game_state.get_resource(game_state.BITS) < 10:
            return
        if game_state.can_spawn(PING, [14, 0]):
            bits = int(math.floor(game_state.get_resource(game_state.BITS)))
            game_state.attempt_spawn(PING, [14, 0], bits)

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
