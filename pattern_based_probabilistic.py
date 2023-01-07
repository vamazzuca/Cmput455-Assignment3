from board_util import (
    GoBoardUtil,
    BLACK,
    WHITE,
    EMPTY,
    BORDER,
)
from gtp_connection import point_to_coord, format_point

def read_weights(base_ten_number):
    file = open("weights.txt", "r")
    for line in file:
        split_line = line.split()
        if int(split_line[0]) == base_ten_number:
            file.close()
            return split_line[1]
    
    file.close()
    return 0

def select_move(board, color):
    legal_moves = GoBoardUtil.generate_legal_moves(board, color)
    
    weights = []
    move_weights = []
    for move in legal_moves:
        neighbours = board._neighbors(move)
        neighbours_diag = board._diag_neighbors(move)

        neighbours = getPoints(board, neighbours)
        neighbours_diag = getPoints(board, neighbours_diag)

        base_four_num = neighbours_diag[3] + neighbours[3] + neighbours_diag[2] + neighbours[1] + neighbours[0] + neighbours_diag[1] + neighbours[2] + neighbours_diag[0]
        
        base_ten_number = base_ten_covert(base_four_num)
        weight_num = read_weights(base_ten_number)
        x, y = point_to_coord(move, board.size)
        move_string = format_point((x, y))
        
        
        move_weights.append((move_string, weight_num, move))
        weights.append(float(weight_num))

    
    best_move = calc_probability(move_weights, weights)
    return best_move

def base_ten_covert(base_four_num):
    number = 0
    count = 0
    for i in reversed(range(8)):
        num = int(base_four_num[i])
        number += num * pow(4, count)
        count += 1

    return number

def getPoints(board, points):
    point_list = []
    for point in points:
        point_list.append(str(board.get_color(point)))
    
    return point_list

def byProbability(pair):
    return pair[1]

def byCoord(pair):
    return pair[0]

def calc_probability(move_weights, weights):
    best_move = None
    move_weights_prob = []
    weight_sum = sum(weights)

    
    for i in range(len(move_weights)):
        weight = float(move_weights[i][1])
        if weight_sum != 0.0:
            probability = weight/weight_sum
        else:
            probability = 0.0
        
        move_weights_prob.append((move_weights[i][0], round(probability, 3), move_weights[i][2]))

    sorted_move_weight_prob = sorted(move_weights_prob, key = byProbability)
    length = len(sorted_move_weight_prob)
    if len(sorted_move_weight_prob) !=0:
        best_move = sorted_move_weight_prob[length -1][2]
        sorted_move_weight_prob = sorted(move_weights_prob, key = byCoord)
        return sorted_move_weight_prob, best_move
    else:
        sorted_move_weight_prob = sorted(move_weights_prob, key = byCoord)
        return sorted_move_weight_prob, None