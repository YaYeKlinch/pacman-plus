
from time import sleep
import random
from tkinter import Tk, Canvas

FOOD_POINT = 5
GHOST_STEP = 5
PENALTY = 9
GHOST_PACMAN_PROFIT = 2
INF = 99999999999999999999999999999999999999999999999
BLOCK_SIZE = 20
PACMAN_SIZE = 3
SPEED_OF_MOVES = 0.1  # Час затримки між кроками
SEARCH_DEPTH = 10  # Глибина пошуку стратегій
NUMBER_OF_FOOD = 0  # К-сть точок на рівні, які треба з'їсти
eated_food = 0  # К-сть з'їдених точок
ghost_step_number = 0  # К-сть зроблених кроків привидами
map = []  # Поле
WIDTH, LENGTH = 21, 27  # Розміри поля
levels = [
    'level_1.txt',
    ##'level_2.txt',    #    На цьому рівні пакмен точно програє
    'level_3.txt',
    'level_4.txt',
    'level_5.txt',
]
pacman = (0, 0)  # Координати пакмена
ghosts = []  # Координати привидів

tk = Tk()  # Діч для графіки
tk.title('Pacman')
tk.resizable(0, 0)  # заборона зміни розміру
tk.wm_attributes('-topmost', 1)  # розміщуємо вікно зверху
canvas = Canvas(tk, width=WIDTH * BLOCK_SIZE, height=LENGTH * BLOCK_SIZE, highlightthickness=0)
canvas.pack()
tk.update()


def stepVisualization(pcmn, sprts):  # Візуалізація поля з пакменом та привидами
    canvas.delete("all")
    canvas.create_rectangle(  # Заливаємо повністю поверхню
        0, 0, WIDTH * BLOCK_SIZE, LENGTH * BLOCK_SIZE,
        outline='#fb0', fill='#f50'
    )
    for x in range(WIDTH):
        for y in range(LENGTH):
            if map[y][x] == '.':  # Порожня клітинка
                canvas.create_rectangle(
                    x * BLOCK_SIZE, y * BLOCK_SIZE, (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                    fill='#4d443f', outline='black'
                )
            elif map[y][x] == 'X':  # Малюємо стіну
                canvas.create_rectangle(
                    x * BLOCK_SIZE, y * BLOCK_SIZE, (x + 1) * BLOCK_SIZE, (y + 1) * BLOCK_SIZE,
                    fill='black', outline='blue'
                )
            elif map[y][x] == '1':
                canvas.create_oval(  # Малюємо ціль
                    x * BLOCK_SIZE + 2 * PACMAN_SIZE, y * BLOCK_SIZE + 2 * PACMAN_SIZE,
                    (x + 1) * BLOCK_SIZE - 2 * PACMAN_SIZE, (y + 1) * BLOCK_SIZE - 2 * PACMAN_SIZE,
                    fill='orange', outline='green'
                )
            else:
                pass

    canvas.create_arc(  # Малюємо пакмена
        pcmn[0] * BLOCK_SIZE + PACMAN_SIZE, pcmn[1] * BLOCK_SIZE + PACMAN_SIZE,
        (pcmn[0] + 1) * BLOCK_SIZE - PACMAN_SIZE, (pcmn[1] + 1) * BLOCK_SIZE - PACMAN_SIZE,
        start=30, extent=300, fill='yellow', outline='yellow'
    )

    colors = ['blue', 'pink', 'gray', ]
    for i in range(len(sprts)):
        canvas.create_arc(  # Малюємо привида
            sprts[i][0] * BLOCK_SIZE + PACMAN_SIZE, sprts[i][1] * BLOCK_SIZE + PACMAN_SIZE,
            (sprts[i][0] + 1) * BLOCK_SIZE - PACMAN_SIZE, (sprts[i][1] + 1) * BLOCK_SIZE - PACMAN_SIZE,
            start=300, extent=300, fill=colors[i], outline=colors[i]
        )

    tk.update()
    sleep(SPEED_OF_MOVES)





def minimaxAlgorithm(position, depth=0, maximizing=True, score=0, prev_pos=()):
    #   Мінімаксний алгоритм пошуку оптимального шляху

    stop_game = False
    if prev_pos and depth % 2 == 0:  # Перевірка, чи з'їдають привиди пакмена
        for i in range(len(position[1])):
            if position[1][i] == position[0] or \
                    (position[1][i] == prev_pos[0] and prev_pos[1][i] == position[0]):
                stop_game = True
                score -= PENALTY ** (SEARCH_DEPTH - depth)

    if depth % 2 == 0:  # І пакмен, і привиди зробили крок
        prev_pos = position

    #   Пакмен з'їдає точку
    if map[position[0][1]][position[0][0]] == '1':
        score += FOOD_POINT
        if eated_food + score // FOOD_POINT >= NUMBER_OF_FOOD:
            #   Пакмен з'їв усі точки
            score += FOOD_POINT ** (SEARCH_DEPTH - depth)
            stop_game = True

    if depth == SEARCH_DEPTH or stop_game:
        return (score, position[0], position[1])

    if maximizing:  # This is pacman's move
        #   Можливі ходи пакмена та рахунок, який він може отримати
        pac_benefit = {move: minimaxAlgorithm((move, position[1]), depth + 1, False, score, prev_pos)[0] \
                       for move in freeBlocksSearcher(position[0])}
        max_benefit = max(pac_benefit.values())
        best_strategies = list(filter(lambda x: pac_benefit[x] == max_benefit, pac_benefit.keys()))
        pacman_next = random.choice(best_strategies)
        return (max_benefit, pacman_next, position[1])
    else:  # This is spirits move
        #   Заповнюємо всі можливі комбінації переміщень привидів
        sp_pos_moves = [[]]
        for spirit in position[1]:
            buf = []
            for move in freeBlocksSearcher(spirit):
                buf += [m + [move] for m in sp_pos_moves]
            sp_pos_moves = buf
        #   Переміщення привидів та рахунок, який можна здобути
        sp_benefit = {tuple(move): minimaxAlgorithm((position[0], move), depth + 1, True, score, prev_pos)[0] \
                      for move in sp_pos_moves}
        min_benefit = min(sp_benefit.values())
        best_strategies = list(filter(lambda x: sp_benefit[x] == min_benefit, sp_benefit.keys()))
        sp_next = random.choice(best_strategies)
        return (min_benefit, position[0], sp_next)
    return (score, pacman, ghosts)


def alphaBetaAlgorithm(position, depth=0, maximizing=True, score=0, prev_pos=(), alpha=-INF, beta=INF):
    #   Альфа-бета відтинання

    stop_game = False
    if prev_pos and depth % 2 == 0:  # Перевірка, чи з'їдають привиди пакмена
        for i in range(len(position[1])):
            if position[1][i] == position[0] or \
                    (position[1][i] == prev_pos[0] and prev_pos[1][i] == position[0]):
                stop_game = True
                score -= PENALTY ** (SEARCH_DEPTH - depth)

    if depth % 2 == 0:  # І пакмен, і привиди зробили крок
        prev_pos = position

    #   Пакмен з'їдає точку
    if map[position[0][1]][position[0][0]] == '1':
        score += FOOD_POINT
        if eated_food + score // FOOD_POINT >= NUMBER_OF_FOOD:
            #   Пакмен з'їв усі точки
            score += FOOD_POINT ** (SEARCH_DEPTH - depth)
            stop_game = True

    if depth == SEARCH_DEPTH or stop_game:
        return (score, position[0], position[1])

    if maximizing:  # This is pacman's move
        max_eval = -INF
        pac_benefit = {}  # Можливі комбінації
        for move in freeBlocksSearcher(position[0]):
            ev = alphaBetaAlgorithm((move, position[1]), depth + 1, False, score, prev_pos, alpha, beta)[0]
            pac_benefit[move] = ev
            max_eval = max(max_eval, ev)
            alpha = max(alpha, ev)
            if beta <= alpha:
                break

        max_benefit = max(pac_benefit.values())
        best_strategies = list(filter(lambda x: pac_benefit[x] == max_benefit, pac_benefit.keys()))
        pacman_next = best_strategies[0] if len(best_strategies) != len(pac_benefit) else random.choice(best_strategies)
        return (max_eval, pacman_next, position[1])

    else:  # This is spirits move
        sp_pos_moves = [[]]
        for spirit in position[1]:
            buf = []
            for move in freeBlocksSearcher(spirit):
                buf += [m + [move] for m in sp_pos_moves]
            sp_pos_moves = buf

        min_eval = INF
        sp_benefit = {}  # Можливі комбінації
        for move in sp_pos_moves:
            ev = alphaBetaAlgorithm((position[0], move), depth + 1, True, score, prev_pos, alpha, beta)[0]
            sp_benefit[tuple(move)] = ev
            min_eval = min(min_eval, ev)
            beta = min(beta, ev)
            if beta <= alpha:
                break

        min_benefit = min(sp_benefit.values())
        best_strategies = list(filter(lambda x: sp_benefit[x] == min_benefit, sp_benefit.keys()))
        sp_next = best_strategies[0] if len(best_strategies) != len(sp_benefit) else random.choice(best_strategies)
        return (min_eval, position[0], sp_next)
    return (score, pacman, ghosts)

def mapReader(inp):  # Зчитує поле з файлу
    global map
    global WIDTH
    global LENGTH

    with open(inp) as sr:
        x = sr.read().splitlines()
    map = [[s for s in line] for line in x]

    WIDTH = len(map[0])
    LENGTH = len(map)


def elementReader():  # Шукає координати пакмена та привидів
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


def freeBlocksSearcher(point):  # Шукає всі досяжні вершини із заданої точки
    next_nodes = [(point[0] + 1, point[1]), (point[0] - 1, point[1]),
                  (point[0], point[1] + 1), (point[0], point[1] - 1)]
    return [node for node in next_nodes if map[node[1]][node[0]] != 'X']
#######################################################################################
isPacmanAlive = True
for level in levels:
    mapReader(level)
    elementReader()
    eated_food = 0

    if not isPacmanAlive:
        sleep(2)
        break

    stepVisualization(pacman, ghosts)
    while isPacmanAlive:
        f = alphaBetaAlgorithm
        pacman_next = f((pacman, ghosts))[1]
        spirits_next = f((pacman, ghosts), maximizing=False)[2]

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
                isPacmanAlive = False

        pacman = pacman_next
        ghosts = spirits_next
        stepVisualization(pacman_next, spirits_next)