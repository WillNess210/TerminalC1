import gamelib
import random
import math
import warnings
from sys import maxsize


class AlgoStrategy(gamelib.AlgoCore):
    initialStageBuilt = False

    def __init__(self):
        super().__init__()
        random.seed()
        self.initialStageBuilt = False

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
        # game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.
        self.starter_strategy(game_state)
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        self.build_defences(game_state)
        self.deploy_attackers(game_state)

    def build_defences(self, game_state):
        # checking if all built, to move on to stage 2
        if self.initialStageBuilt == False:
            to_build = [["DESTRUCTOR", [0, 13]], ["DESTRUCTOR", [27, 13]], ["DESTRUCTOR", [7, 11]],
                        ["DESTRUCTOR", [20, 11]], ["FILTER", [1, 13]], ["FILTER", [2, 13]], ["FILTER", [25, 13]],
                        ["FILTER", [26, 13]], ["FILTER", [3, 12]], ["FILTER", [24, 12]], ["FILTER", [4, 11]],
                        ["FILTER", [5, 11]], ["FILTER", [6, 11]], ["FILTER", [21, 11]], ["FILTER", [22, 11]],
                        ["FILTER", [23, 11]], ["FILTER", [9, 12]], ["DESTRUCTOR", [9, 11]], ["FILTER", [12, 12]],
                        ["DESTRUCTOR", [12, 11]], ["FILTER", [15, 12]], ["DESTRUCTOR", [15, 11]], ["FILTER", [18, 12]],
                        ["DESTRUCTOR", [18, 11]], ["FILTER", [8, 11]], ["FILTER", [19, 11]], ["FILTER", [10, 11]],
                        ["FILTER", [17, 11]], ["FILTER", [11, 11]], ["FILTER", [16, 11]], ["ENCRYPTOR", [4, 9]],
                        ["FILTER", [5, 8]]]

            self.initialStageBuilt = True
            for item in to_build:
                if game_state.contains_stationary_unit(item[1]) == False:
                    self.initialStageBuilt = False
                    break
        # building initial stage
        if self.initialStageBuilt == False:
            to_build = [["DESTRUCTOR", [0, 13]], ["DESTRUCTOR", [27, 13]], ["DESTRUCTOR", [7, 11]],
                        ["DESTRUCTOR", [20, 11]], ["FILTER", [1, 13]], ["FILTER", [2, 13]], ["FILTER", [25, 13]],
                        ["FILTER", [26, 13]], ["FILTER", [3, 12]], ["FILTER", [24, 12]], ["FILTER", [4, 11]],
                        ["FILTER", [5, 11]], ["FILTER", [6, 11]], ["FILTER", [21, 11]], ["FILTER", [22, 11]],
                        ["FILTER", [23, 11]], ["FILTER", [9, 12]], ["DESTRUCTOR", [9, 11]], ["FILTER", [12, 12]],
                        ["DESTRUCTOR", [12, 11]], ["FILTER", [15, 12]], ["DESTRUCTOR", [15, 11]], ["FILTER", [18, 12]],
                        ["DESTRUCTOR", [18, 11]], ["FILTER", [8, 11]], ["FILTER", [19, 11]], ["FILTER", [10, 11]],
                        ["FILTER", [17, 11]], ["FILTER", [11, 11]], ["FILTER", [16, 11]], ["ENCRYPTOR", [4, 9]],
                        ["FILTER", [5, 8]]]

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

        else:  # STAGE TWO
            to_build = [["DESTRUCTOR", [13, 11]], ["DESTRUCTOR", [14, 11]], ["DESTRUCTOR", [0, 13]],
                        ["DESTRUCTOR", [27, 13]], ["DESTRUCTOR", [7, 11]],
                        ["DESTRUCTOR", [20, 11]], ["FILTER", [1, 13]], ["FILTER", [2, 13]], ["FILTER", [25, 13]],
                        ["FILTER", [26, 13]], ["FILTER", [24, 12]], ["FILTER", [3, 10]],
                        ["FILTER", [5, 11]], ["FILTER", [6, 11]], ["FILTER", [21, 11]], ["FILTER", [22, 11]],
                        ["FILTER", [23, 11]], ["FILTER", [9, 12]], ["DESTRUCTOR", [9, 11]], ["FILTER", [12, 12]],
                        ["DESTRUCTOR", [12, 11]], ["FILTER", [15, 12]], ["DESTRUCTOR", [15, 11]], ["FILTER", [18, 12]],
                        ["DESTRUCTOR", [18, 11]], ["FILTER", [8, 11]], ["FILTER", [19, 11]], ["FILTER", [10, 11]],
                        ["FILTER", [17, 11]], ["FILTER", [11, 11]], ["FILTER", [16, 11]], ["DESTRUCTOR", [2, 12]],
                        ["DESTRUCTOR", [2, 11]], ["DESTRUCTOR", [4, 12]]]
            for i in range(4, 25):
                to_build.append(["DESTRUCTOR", [i, 13]])
            # remove wall
            if game_state.contains_stationary_unit([3, 12]):
                game_state.attempt_remove([3, 12])
            if game_state.contains_stationary_unit([4, 11]):
                game_state.attempt_remove([4, 11])
            for item in to_build:
                location = item[1]
                if game_state.can_spawn(DESTRUCTOR, location):
                    game_state.attempt_spawn(DESTRUCTOR, location)
            for item in to_build:
                location = item[1]
                if game_state.can_spawn(FILTER, location):
                    game_state.attempt_spawn(FILTER, location)
            for i in range(5, 11):
                if game_state.can_spawn(ENCRYPTOR, [i, 9]):
                    game_state.attempt_spawn(ENCRYPTOR, [i, 9])

    def deploy_attackers(self, game_state):
        # If I can't make it to other side, don't spawn anything
        if game_state.find_path_to_edge([13, 0], game_state.game_map.TOP_RIGHT)[-1][1] < 13:
            return
        if game_state.get_resource(game_state.BITS) < 8:
            return
        if self.count_destroyables(game_state) > 20:
            game_state.attempt_spawn(EMP, [24, 10], game_state.number_affordable(EMP))
        else:
            game_state.attempt_spawn(PING, [24, 10], game_state.number_affordable(PING))

    def count_destroyables(self, game_state):
        score = 0
        locations = []
        for i in range(1, 27):
            locations.append([i, 15])
        for i in range(0, 28):
            locations.append([i, 14])
        for location in locations:
            units = game_state.game_map[location[0], location[1]]
            for unit in units:
                if unit.unit_type == FILTER:
                    score += 1
                else:
                    score += 5
        return score


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
