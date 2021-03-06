
from time import sleep
import random
from tkinter import Tk, Canvas

map = []
SPEED_OF_MOVES = 0.1
WIDTH, LENGTH = 21, 25
levels = [
    'level_1.txt',
    #'level_2.txt',
    'level_3.txt',
    'level_4.txt',
    'level_5.txt',
]

GHOST_STEP = 5
ghost_step_number = 0
PENALTY = 5
GHOST_PACMAN_PROFIT = 2
BLOCK_SIZE = 20
PACMAN_SIZE = 3
SEARCH_DEPTH = 5
NUMBER_OF_FOOD = 0
FOOD_POINT = 5
eated_food = 0



pacman = (0, 0)
ghosts = []

tk = Tk()
tk.title('Pacman PLUS')
tk.resizable(0, 0)
tk.wm_attributes('-topmost', 1)
canvas = Canvas(tk, width=WIDTH * BLOCK_SIZE, height=LENGTH * BLOCK_SIZE, highlightthickness=0)
canvas.pack()
tk.update()


def mapReader(inp):
    global map
    global WIDTH
    global LENGTH

    with open(inp) as sr:
        x = sr.read().splitlines()
    map = [[s for s in line] for line in x]

    WIDTH = len(map[0])
    LENGTH = len(map)


def gameElementsReader():
    global pacman
    global ghosts
    global NUMBER_OF_FOOD

    NUMBER_OF_FOOD = 0
    ghosts = []

    for x in range(WIDTH):
        for y in range(LENGTH):
            if map[y][x] == 'P':
                pacman = (x, y)
                map[y][x] = '.'
            elif map[y][x] == '1':
                NUMBER_OF_FOOD += 1
            elif map[y][x] == 'G':
                map[y][x] = '.'
                ghosts.append((x, y))


def stepVisualization(pcmn, sprts):
    canvas.delete("all")
    canvas.create_rectangle(
        0, 0, WIDTH * BLOCK_SIZE, LENGTH * BLOCK_SIZE,
        outline='#fb0', fill='#f50'
    )
    for x in range(WIDTH):
        for y in range(LENGTH):
            if map[y][x] == '.':
                canvas.create_rectangle(
                    x*BLOCK_SIZE, y*BLOCK_SIZE, (x+1)*BLOCK_SIZE, (y+1)*BLOCK_SIZE,
                    fill='#4d443f', outline='black'
                )
            elif map[y][x] == 'X':
                canvas.create_rectangle(
                    x*BLOCK_SIZE, y*BLOCK_SIZE, (x+1)*BLOCK_SIZE, (y+1)*BLOCK_SIZE,
                    fill='black', outline='blue'
                )
            elif map[y][x] == '1':
                canvas.create_oval(
                    x * BLOCK_SIZE + 2 * PACMAN_SIZE, y * BLOCK_SIZE + 2 * PACMAN_SIZE,
                    (x+1) * BLOCK_SIZE - 2 * PACMAN_SIZE, (y + 1) * BLOCK_SIZE - 2 * PACMAN_SIZE,
                    fill='orange', outline='green'
                )
            else:
                pass

    canvas.create_arc( #?????????????? ??????????????
        pcmn[0] * BLOCK_SIZE + PACMAN_SIZE, pcmn[1] * BLOCK_SIZE + PACMAN_SIZE,
        (pcmn[0]+1) * BLOCK_SIZE - PACMAN_SIZE, (pcmn[1] + 1) * BLOCK_SIZE - PACMAN_SIZE,
        start=30, extent=300, fill='yellow', outline='yellow'
    )

    colors = ['blue', 'pink', 'gray', ]
    for i in range(len(sprts)):
        canvas.create_arc( #?????????????? ??????????????
            sprts[i][0] * BLOCK_SIZE + PACMAN_SIZE, sprts[i][1] * BLOCK_SIZE + PACMAN_SIZE,
            (sprts[i][0]+1) * BLOCK_SIZE - PACMAN_SIZE, (sprts[i][1] + 1) * BLOCK_SIZE - PACMAN_SIZE,
            start=300, extent=300, fill=colors[i], outline=colors[i]
        )

    tk.update()
    sleep(SPEED_OF_MOVES)

def bfs(spirit, trgt):
    paths = [[(spirit[0], spirit[1])]]
    visited = [(spirit[0], spirit[1])]
    while paths:
        buf_paths = []
        for path in paths:
            if path[-1] == trgt:
                return path
        for path in paths:
            next_node = [(path[-1][0]+1, path[-1][1]), (path[-1][0]-1, path[-1][1]),
                (path[-1][0], path[-1][1]+1), (path[-1][0], path[-1][1]-1)]
            for node in next_node:
                if node in visited:
                    continue
                if map[node[1]][node[0]] == 'X':
                    continue
                visited += [node]
                buf_paths.append(path+[node])

        paths = buf_paths

    return spirit


def freeBlocksSearcher(point):
    
    paths = [[point]]
    for _ in range(SEARCH_DEPTH):
        buf_paths = []
        for path in paths:
            next_nodes = [(path[-1][0]+1, path[-1][1]), (path[-1][0]-1, path[-1][1]),
                (path[-1][0], path[-1][1]+1), (path[-1][0], path[-1][1]-1)]
            for node in next_nodes:
                if map[node[1]][node[0]] == 'X':
                    continue
                buf_paths.append(path+[node])
            
            paths = buf_paths
    return [tuple(p) for p in paths]

def makeStep():
    pacman_possible_moves = freeBlocksSearcher(pacman)
    spirits_possible_moves = [freeBlocksSearcher(spirit) for spirit in ghosts]

    pac_benefit = {}
    for path in pacman_possible_moves:
        pac_benefit[path] = 0
        for point in path:
            if map[point[1]][point[0]] == '1':
                pac_benefit[path] += FOOD_POINT
        if eated_food + pac_benefit[path]//FOOD_POINT >= NUMBER_OF_FOOD:
            pac_benefit[path] += FOOD_POINT ** 10

        for spirit_possible_moves in spirits_possible_moves:
            for sp_path in spirit_possible_moves:
                for i in range(1, len(sp_path)):
                    if path[i] == sp_path[i]:
                        pac_benefit[path] -= PENALTY ** (SEARCH_DEPTH - i)
                        break
                for i in range(2, len(sp_path)):
                    if (path[i]==sp_path[i-1] and path[i-1]==sp_path[i]):
                        pac_benefit[path] -= PENALTY ** (SEARCH_DEPTH - i)
                        break
    max_benefit = max(pac_benefit.values())
    best_strategies = list(filter(lambda x: pac_benefit[x]==max_benefit, pac_benefit.keys()))
    pacman_next = random.choice(best_strategies)

    spirits_next = []
    use_different_strategy = False
    for spirit_possible_moves in spirits_possible_moves:
        spirit_benefit = {}
        use_different_strategy = False if use_different_strategy else True
        if use_different_strategy:
            global ghost_step_number
            ghost_step_number += 1
            if ghost_step_number >= GHOST_STEP:
                spirits_next.append(random.choice(spirit_possible_moves)[1])
                ghost_step_number = 0
                continue
            for path in spirit_possible_moves:
                spirit_benefit[path] = 0
                for pacman_path in pacman_possible_moves:
                    for i in range(1, len(pacman_path)):
                        if path[i] == pacman_path[i]:
                            spirit_benefit[path] += GHOST_PACMAN_PROFIT ** (SEARCH_DEPTH - i)
                            break
                    for i in range(2, len(pacman_path)):
                        if (path[i]==pacman_path[i-1] and path[i-1]==pacman_path[i]):
                            spirit_benefit[path] += GHOST_PACMAN_PROFIT ** (SEARCH_DEPTH - i)
                            break
            max_profit = max(spirit_benefit.values())
            best_strategies = list(filter(lambda x: spirit_benefit[x]==max_profit, spirit_benefit.keys()))
            spirits_next.append(random.choice(best_strategies)[1])
        else:
            spirits_next.append(bfs(spirit_possible_moves[0][0], pacman)[1])

    return pacman_next[1], spirits_next


#######################################################################################  
PAC_ALIVE = True
for level in levels:
    mapReader(level)
    gameElementsReader()
    eated_food = 0

    if not PAC_ALIVE:
        sleep(2)
        break
    
    stepVisualization(pacman, ghosts)
    while PAC_ALIVE:
        pacman_next, spirits_next = makeStep()
        if map[pacman_next[1]][pacman_next[0]] == '1':
            eated_food += 1
            map[pacman_next[1]][pacman_next[0]] = '.'
            if eated_food >= NUMBER_OF_FOOD:
                stepVisualization(pacman_next, ghosts)
                sleep(2)
                break
        
        for i in range(len(spirits_next)):
            if pacman_next == spirits_next[i] or \
                (pacman_next == ghosts[i] and pacman == spirits_next[i]):
                PAC_ALIVE = False

        pacman = pacman_next
        ghosts = spirits_next
        stepVisualization(pacman_next, spirits_next)

