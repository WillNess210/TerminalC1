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
        firewall_locations = []
        for newx in range(0, 27, 5):
            firewall_locations.append([newx, 13])
        for location in firewall_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)

    def deploy_attackers(self, game_state):
        if (game_state.get_resource(game_state.BITS) < 10):
            return

        if game_state.can_spawn(EMP, [3, 10]):
            game_state.attempt_spawn(EMP, [3, 10])

        if game_state.can_spawn(PING, [14, 0], 3):
            game_state.attempt_spawn(PING, [14, 0], 3)

        friendly_edges = game_state.game_map.get_edge_locations(
            game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

        deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

        while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
            deploy_index = random.randint(0, len(deploy_locations) - 1)
            deploy_location = deploy_locations[deploy_index]

            game_state.attempt_spawn(SCRAMBLER, deploy_location)

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
