import sys
import math
import numpy as np
from numpy import array as arr
from dataclasses import dataclass
import random

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

width, height = [int(i) for i in input().split()]
directions = [arr((1,0)), arr((0,1))]; directions += [-direction for direction in directions]


@dataclass
class Tile:
    pos: np.array
    scrap: int
    owner: int
    units: int
    recycler: bool
    can_build: bool
    can_spawn: bool
    in_range_of_recycler: bool

@dataclass
class Bots:
    pos: np.array
    amount: int

def distance(pos1,pos2):
    return np.sum(pos2-pos1)

# game loop
while True:
    my_matter, opp_matter = [int(i) for i in input().split()]
    my_bots=[]
    my_tiles=[]
    enemy_tiles=[]
    neutral_tiles=[]
    tiles=[]
    commands=[]
    board = [height*[None] for _ in range(width)]
    for y in range(height):
        for x in range(width):
            # owner: 1 = me, 0 = foe, -1 = neutral
            tile = scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in input().split()]
            owner = {1:1, 0:-1, -1:0}[owner]
            tile[1] = owner
            pos = arr((x,y))
            tile = Tile(pos,*tile)

            board[x][y] = tile
            tiles.append(pos)
            if owner == 1:
                my_tiles.append(tile)
                # for _ in range(units):
                #     my_bots.append(pos)
                if units>0:
                    my_bots.append(Bots(pos, units))
            elif owner == -1:
                enemy_tiles.append(tile)
            elif owner == 0:
                neutral_tiles.append(tile)
    print("board read", file=sys.stderr, flush=True)

    attack_point = random.choice(enemy_tiles).pos
    for bot in my_bots: #moving bots
        random.seed(None)
        pos = x0, y0 = bot.pos
        adjacent_tiles = [bot.pos + direction for direction in directions if np.any(np.all(tiles == (bot.pos+direction), axis=1))]
        goal_tiles = [pos for pos in adjacent_tiles if (arr((x,y))<arr(board).shape).all() and (arr((x,y))>=0).all()]
        goal_tiles = [pos for pos in goal_tiles if board[pos[0]][pos[1]].owner<1 and board[pos[0]][pos[1]].scrap>0]
        if goal_tiles:
            x1,y1 = random.choice(goal_tiles)
        else:   
            # x1,y1 = random.choice(neutral_tiles+enemy_tiles).pos
            x1, y1 = attack_point
        if (arr((x1,y1))<arr(board).shape).all() and (arr((x1,y1))>=0).all():
            if board[x1][y1].scrap>0:
                commands.append(f"MOVE {bot.amount} {x0} {y0} {x1} {y1}")
    print("bots moved", file=sys.stderr, flush=True)

    recyclers_built = 0
    for tile in my_tiles: #building recyclers
        if my_matter<10:
            break
        if not tile.can_build:
            continue
        else:
            if random.randint(0,10)==2:
                my_matter-=10
                x,y = tile.pos
                commands.append(f"BUILD {x} {y}")
            break
        affected_area = [tile.pos + direction for direction in directions] + [tile.pos]
        priority = 0
        for x,y in affected_area:
            if (arr((x,y))<arr(board).shape).all() and (arr((x,y))>=0).all():
                affected_tile = board[x][y]
            else:
                continue
            priority += -affected_tile.owner * affected_tile.scrap
        if priority > recyclers_built * 10:
            my_matter-=10
            x,y = tile.pos
            commands.append(f"BUILD {x} {y}")
    print("recyclers built", file=sys.stderr, flush=True)

    while my_matter>10: #spawning bots
        my_matter-=10
        pos = x,y = random.choice([tile for tile in my_tiles if tile.can_spawn]).pos
        commands.append(f"SPAWN 1 {x} {y}")
    print("bots spawned", file=sys.stderr, flush=True)
            
    if not commands:
        commands.append("WAIT")

    # if len(commands)>390:
    #     commands = ';'.join(commands.split(';')[26] )

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    print(*commands, sep=';')
