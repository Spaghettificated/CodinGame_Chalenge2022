import sys
import math
import numpy as np
from numpy import array as arr
from dataclasses import dataclass, astuple
import random


directions = [arr((1,0)), arr((0,1))]; directions += [-direction for direction in directions]
owner_translation = {1:1, 0:-1, -1:0}

@dataclass(eq=False)
class Tile:
    pos: np.array
    scrap: int
    owner: int
    units: int
    recycler: bool
    can_build: bool
    can_spawn: bool
    in_range_of_recycler: bool

    def owner_id(self):
        return 0 if self.owner>0 else 1

    def unit_power(self):
        return self.owner*self.units

    def __eq__(self, other):
        return astuple(self)[1:] == astuple(other)[1:] and np.all(self.pos==other.pos)


size = width, height = arr([int(i) for i in input().split()])
# board = [height*[None] for _ in range(width)]
board = [[Tile(arr((x,y)),0,0,0,False,True,True,False) for y in range(height)] for x in range(width)]
borders = my_border, enemy_border = [[],[]]
bots = my_bots, enemy_bots = [[],[]]
centers = [np.zeros(2), np.zeros(2)]
score = [0,0]
turn = -1

def remove_pos(ls, pos):
    # ls.pop(ls.index(pos))
    for i,x in enumerate(ls):
        if np.all(x==pos):
            ls.pop(i)
            return


def get_tile(pos):
    if np.all(pos>=0) and np.all(pos<size):
        return board[pos[0]][pos[1]]
    return None

def adjacent(center):
    out=[]
    for direction in directions:
        pos = center + direction
        if (tile:=get_tile(pos)):
            if tile.scrap>0:
                out.append(tile)
    return out


# game loop
while True:
    turn+=1
    my_matter, opp_matter = [int(i) for i in input().split()]
    changed_tiles = []
    commands = []
    for y in range(height):
        for x in range(width):
            # owner: 1 = me, 0 = foe, -1 = neutral
            tile = scrap_amount, owner, units, recycler, can_build, can_spawn, in_range_of_recycler = [int(k) for k in input().split()]
            owner = owner_translation[owner]
            tile[1] = owner
            pos = arr((x,y))
            tile = Tile(pos,*tile)

            old_tile = board[x][y]
            if old_tile != tile:
                changed_tiles.append(tile)
                board[x][y] = tile

                if old_tile.owner != tile.owner:
                    if old_tile.owner:
                        id_ = old_tile.owner_id()
                        # borders[id_].remove(old_tile.pos)
                        remove_pos(borders[id_], old_tile.pos)
                        centers[id_] = (score[id_] * centers[id_] + old_tile.pos)/(score[id_]-1)
                        score[id_]-=1
                    if tile.owner:
                        id_ = tile.owner_id()
                        borders[id_].append(tile.pos)
                        centers[id_] = (score[id_] * centers[id_] + tile.pos)/(score[id_]+1)
                        score[id_]+=1

                old_units, new_units = old_tile.unit_power(), tile.unit_power()
                if np.sign(old_units) != np.sign(new_units):    #detect only changes in are there units and whos
                    if old_tile.owner:
                        id_ = old_tile.owner_id()
                        # bots[id_].remove(old_tile.pos)
                        remove_pos(bots[id_], old_tile.pos)
                    if tile.owner:
                        id_ = tile.owner_id()
                        bots[id_].append(tile.pos)

    print(f"board read: \n{my_border = }\n{my_bots = }", file=sys.stderr, flush=True)
                            

    ### Moving Bots
    for bot_pos in my_bots:
        x0,y0 = bot_pos
        tile = get_tile(bot_pos)
        amount = tile.units
        direction = random.choice(directions)
        x1,y1 = pos = bot_pos + direction
        if get_tile(pos):
            commands.append(f"MOVE {amount} {x0} {y0} {x1} {y1}")

    print("bots moved", file=sys.stderr, flush=True)


    ### Building Recyclers
    if my_matter>=10:
        rec_tile = get_tile(random.choice(my_border))
        if rec_tile.can_build:
            my_matter-=10
            x,y = tile.pos
            commands.append(f"BUILD {x} {y}")
            rec_tile.can_spawn=False    # may require updating also other parameters

    print("recyclers built", file=sys.stderr, flush=True)


    ### Spawning Bots
    tries = 0
    while my_matter>10 and tries<100: #spawning bots
        tries+=1
        tile = get_tile(random.choice(my_border))
        if tile.can_spawn:
            my_matter-=10
            x,y = tile.pos
            commands.append(f"SPAWN 1 {x} {y}")

    print("bots spawned", file=sys.stderr, flush=True)




    if not commands:
        commands.append("WAIT")

    # if len(commands)>390:
    #     commands = ';'.join(commands.split(';')[26] )

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    print(*commands, sep=';')
