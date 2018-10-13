import gamelib
import random
import math
import warnings
from sys import maxsize


class AlgoStrategy(gamelib.AlgoCore):
    attack_turn = False
    attack_lane = []
    attack_direction = 0  # 1 if placing units on left, 0 for right

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
        self.attack_lane = get_lane(0, 0)

    def on_turn(self, turn_state):
        # GET GAME STATE
        game_state = gamelib.GameState(self.config, turn_state)
        # START DEBUG
        gamelib.debug_write('-----{}-----'.format(game_state.turn_number))
        # game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.
        # RUN STRATEGY
        self.starter_strategy(game_state)
        # SUBMIT TURN
        game_state.submit_turn()

    def starter_strategy(self, game_state):
        if game_state.turn_number >= 0:
            self.attack_direction = self.get_best_direction(game_state)
            self.build_defences(game_state)
            self.determine_attack(game_state)
            if self.attack_turn:
                self.deploy_attackers(game_state)

    def determine_attack(self, game_state):
        if game_state.get_resource(game_state.BITS) >= 10 and 0 < game_state.turn_number < 8:
            move_path = get_path(game_state, self.attack_direction, 0)
            # if the last element of the path is on their side or top of ours, then attack
            if move_path[-1][1] >= 13:
                self.attack_turn = True
                return
        elif game_state.get_resource(game_state.BITS) >= 12 and game_state.turn_number >= 8:
            move_path = get_path(game_state, self.attack_direction, 0)
            # if the last element of the path is on their side or top of ours, then attack
            if move_path[-1][1] >= 13:
                self.attack_turn = True
                return
        self.attack_turn = False

    def remove_lane_defences(self, game_state):
        game_state.attempt_remove(self.attack_lane)

    def build_defences(self, game_state):
        # build points
        destructor_locations = [[3, 12], [4, 12], [23, 12], [24, 12], [4, 11], [5, 11], [6, 11], [11, 11], [13, 11],
                                [14, 11], [16, 11], [21, 11], [22, 11], [23, 11]]
        left_destructor_locations = [[0, 13], [1, 12], [2, 12], [3, 11]]
        right_destructor_locations = [[27, 13], [25, 12], [26, 12], [24, 11]]
        filter_locations = [[2, 13], [3, 13], [4, 13], [5, 13], [22, 13], [23, 13], [24, 13], [25, 13], [5, 12],
                            [6, 12], [7, 12], [20, 12], [21, 12], [22, 12], [7, 11], [8, 11], [9, 11], [10, 11],
                            [12, 11], [15, 11], [17, 11], [18, 11], [19, 11], [20, 11]]
        left_filter_locations = [[1, 13]]
        right_filter_locations = [[26, 13]]
        remove_locations = []
        # putting together what we want to build
        if self.attack_direction == 1:
            destructor_locations += left_destructor_locations
            filter_locations += left_filter_locations
            remove_locations += right_destructor_locations
            remove_locations += right_filter_locations
        else:
            destructor_locations += right_destructor_locations
            filter_locations += right_filter_locations
            remove_locations += left_destructor_locations
            remove_locations += left_filter_locations
        # building, priority to destructors
        for location in destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        for location in filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
        # marking for removal
        for location in remove_locations:
            if game_state.contains_stationary_unit(location):
                game_state.remove_unit(location)

    def deploy_attackers(self, game_state):
        spawn_point = [14 - self.attack_direction, 0]
        if game_state.turn_number > 8:
            if game_state.can_spawn(EMP, spawn_point):
                num_spawn = game_state.number_affordable(EMP)
                game_state.attempt_spawn(EMP, spawn_point, num_spawn)
        else:
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

    def get_best_lane(self, game_state):
        damage_map = self.get_damage_map(game_state)
        best_lane = get_lane(0, 0)
        best_score = -9999
        for lane in get_all_lanes():
            score = get_lane_score(lane, damage_map)
            if score > best_score:
                best_lane = lane
                best_score = score
        return best_lane

    def get_best_direction(self, game_state):
        damage_map = self.get_damage_map(game_state)
        left_lane = get_lane_score(get_lane(1, 0), damage_map)
        right_lane = get_lane_score(get_lane(0, 0), damage_map)
        if left_lane > right_lane:
            return 1
        return 0

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


def get_path_using_lane(game_state, lane):
    first_point_x = lane[0][0]
    if first_point_x <= 13:
        return get_path(game_state, 1, 13 - first_point_x)
    else:
        return get_path(game_state, 0, first_point_x - 14)


# 14 possible lanes, input 0-13, 0 is at bottom, 13 is on middle corners || PASS 1 FOR LEFT LANE, PASS 0 FOR RIGHT LANE
def get_path(game_state, left_lane, lane_num):
    if left_lane == 1:
        starting_point = [13 - lane_num, 0 + lane_num]
        target_edge = game_state.game_map.TOP_RIGHT
    else:
        starting_point = [14 + lane_num, 0 + lane_num]
        target_edge = game_state.game_map.TOP_LEFT
    return game_state.find_path_to_edge(starting_point, target_edge)


# 14 possible lanes, input 0-13, 0 is at bottom, 13 is on middle corners || PASS 1 FOR LEFT LANE, PASS 0 FOR RIGHT LANE
def get_lane(left_lane, lane_num):
    lane = []
    if left_lane == 1:
        lane.append([13 - lane_num, 0 + lane_num])
        for dist in range(1, 15):
            lane.append([13 - lane_num + dist - 1, 0 + lane_num + dist])
            lane.append([13 - lane_num + dist, 0 + lane_num + dist])
    else:
        lane.append([14 + lane_num, 0 + lane_num])
        for dist in range(1, 15):
            lane.append([14 + lane_num - dist + 1, 0 + lane_num + dist])
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
