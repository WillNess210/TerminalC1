import gamelib
import random
import math
import warnings
from sys import maxsize


class AlgoStrategy(gamelib.AlgoCore):
    spawnBottomLeft = 1

    def __init__(self):
        super().__init__()
        random.seed()
        self.spawnBottomLeft = 1

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
        gamelib.debug_write('-----{}-----'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.
        self.starter_strategy(game_state)
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        if game_state.turn_number > 0:
            if game_state.turn_number == 1:
                self.spawnBottomLeft = 0
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
        damage_map = self.get_damage_map(game_state)
        best_lane = get_lane(0, 0)
        best_score = -9999
        for lane in get_all_lanes():
            score = get_lane_score(lane, damage_map)
            if score > best_score:
                best_lane = lane
                best_score = score
        spawn_point = best_lane[0]
        if game_state.can_spawn(PING, spawn_point):
            num_spawn = game_state.number_affordable(PING)
            game_state.attempt_spawn(PING, spawn_point, num_spawn)

    def get_opponent_destructors(self, game_state):
        destructors = []
        for enemyPoint in get_enemy_points():
            units = game_state.game_map[enemyPoint[0], enemyPoint[1]]
            for unit in units:
                if unit.unit_type == 'DF':
                    destructors.append([unit.x, unit.y])
        return destructors

    def get_damage_map(self, game_state):
        damage_map = [[0 for x in range(28)] for y in range(28)]
        destructors = self.get_opponent_destructors(game_state)
        for destructor in destructors:
            locs = game_state.game_map.get_locations_in_range(destructor, 3)
            for location in locs:
                damage_map[location[0]][location[1]] += 4
        return damage_map


# scores a lane - takes in a lane and the damage map
def get_lane_score(lane, damage_map):
    # subtract the starting points y from the score to break ties
    # to prioritize lanes that will travel most of it's path on my side
    score = 1000 - lane[0][1]
    for point in lane:
        x = point[0]
        y = point[1]
        score -= (damage_map[x][y] * 10)
    return score

# returns a list of all lanes
def get_all_lanes():
    lanes = []
    for direction in [0, 1]:
        for lane_num in range(0, 14):
            lanes.append(get_lane(direction, lane_num))
    return lanes


# 14 possible lanes, input 0-13, 0 is at bottom, 13 is on middle corners || PASS 1 FOR LEFT LANE, PASS 0 FOR RIGHT LANE
def get_lane(left_lane, lane_num):
    lane = []
    if left_lane == 1:
        for dist in range(0, 15):
            lane.append([13 - lane_num + dist, 0 + lane_num + dist])
    else:
        for dist in range(0, 15):
            lane.append([14 + lane_num - dist, 0 + lane_num + dist])
    return lane


def point_inside_map(self, point):
    if point in self.get_all_points():
        return True
    return False


def get_all_points():
    return get_my_points() + get_enemy_points()


def get_my_points():
    points = []
    y = 0
    startx = 13
    width = 2
    while startx >= 0:
        for newx in range(startx, startx + width):
            points.append([newx, y])
        y = y + 1
        startx = startx - 1
        width = width + 2
    return points


def get_enemy_points():
    points = []
    y = 27
    startx = 13
    width = 2
    while startx >= 0:
        for newx in range(startx, startx + width):
            points.append([newx, y])
        y = y - 1
        startx = startx - 1
        width = width + 2
    return points


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
