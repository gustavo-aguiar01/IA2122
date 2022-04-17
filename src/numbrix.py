# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

import sys
import copy
import time
import tracemalloc
from search import Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, \
    recursive_best_first_search

i = 0
initial_numbers = set()
DEBUG_FLAG = True


def print_debug(string):
    global DEBUG_FLAG
    if DEBUG_FLAG:
        print(string)


class NumbrixState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NumbrixState.state_id
        NumbrixState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe


class Board:
    """ Representação interna de um tabuleiro de Numbrix. """

    board = {}
    board_size = 0
    numbers_to_go = {}
    local_min = ()
    local_max = ()
    global_min = ()
    global_max = ()
    extremes = False
    assigned_positions = {}
    free_spaces = set()

    def __init__(self, board, board_size):
        self.board_size = board_size
        min_initial = min(initial_numbers)
        max_initial = max(initial_numbers)
        for i in range(self.board_size):
            for j in range(self.board_size):
                self.board[(i, j)] = board[i][j]
                self.assigned_positions[board[i][j]] = (i, j)
                if board[i][j] == min_initial:
                    self.global_min = ((i, j), min_initial)
                if board[i][j] == max_initial:
                    self.global_max = ((i, j), max_initial)
                if self.board[(i, j)] == 0:
                    self.free_spaces.add((i, j))

        self.numbers_to_go = set(i for i in range(1, self.board_size * self.board_size + 1)) - initial_numbers

        self.local_max = self.island_dfs(self.global_min)
        self.local_min = ((0, 0), self.board_size ** 2 + 1)

        for i in range(self.board_size):
            for j in range(self.board_size):
                num = self.get_number(i, j)
                if self.local_max[1] < num < self.local_min[1]:
                    self.local_min = ((i, j), num)

        print_debug(f'Global Min: {self.global_min} ; Global Max: {self.global_max}')
        print_debug(f'Local Max: {self.local_max} ; Local Min: {self.local_min}')

    def get_adjacents(self, row, col):
        return list(filter(lambda x: 0 <= x[0] < self.board_size and 0 <= x[1] < self.board_size
                           , [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]))

    def get_number(self, row: int, col: int) -> int:
        """ Devolve o valor na respetiva posição do tabuleiro. """
        try:
            return self.board[row, col]
        except KeyError:
            return None

    def set_number(self, row: int, col: int, value):
        try:
            self.board[row, col] = value
        except KeyError:
            pass

    def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente abaixo e acima,
        respectivamente. """
        results = []
        for dir in [1, -1]:
            try:
                results.append(self.board[row + dir][col])
            except IndexError:
                results.append(None)
        return tuple(results)

    def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente à esquerda e à direita,
        respectivamente. """
        results = []
        for dir in [-1, 1]:
            try:
                results.append(self.board[row][col + dir])
            except IndexError:
                results.append(None)
        return tuple(results)

    @staticmethod
    def parse_instance(filename: str):
        """ Lê o ficheiro cujo caminho é passado como argumento e retorna
        uma instância da classe Board. """
        global initial_numbers
        file_board = []
        try:
            with open(filename) as f:
                board_size = int(f.readline())
                for line in f.readlines():
                    split = line.split('\t')
                    [initial_numbers.add(int(val)) for val in split if int(val) != 0]
                    file_board.append([int(val) for val in split])
            # TODO: Verificar construtor do Board
            return Board(file_board, board_size)
        except IOError:  # Couldn't open input file
            print("Something went wrong while attempting to read file.")
            sys.exit(-1)

    # TODO: outros metodos da classe

    def island_dfs(self, origin):
        max_local = (origin[0], origin[1])
        queue = [origin[0]]
        visited = set()
        while len(queue) > 0:
            u = queue[-1]
            visited.add(u)
            num = self.get_number(u[0], u[1])
            if num > max_local[1] and num != origin[1]:
                max_local = (u, num)
            neighbors = [adj for adj in self.get_adjacents(u[0], u[1])
                         if self.get_number(adj[0], adj[1]) != 0
                         and abs(self.get_number(adj[0], adj[1]) - num) == 1
                         and adj not in visited]
            if len(neighbors) > 0:
                queue.append(neighbors[0])
            else:
                queue = queue[:-1]
        return max_local

    def to_string(self):
        return '\n'.join('\t'.join(f'{self.get_number(i, j)}' for j in range(self.board_size))
                         for i in range(self.board_size))

    def dfs(self, origin, dest):
        # print(self.to_string())
        # print(f"From {origin} to {dest}")
        queue = [origin]
        visited = set()
        while len(queue) > 0:
            u = queue[-1]
            visited.add(u)
            # print(f"Analyzing {u}")
            if u == dest:
                return True
            neighbors = [adj for adj in self.get_adjacents(u[0], u[1]) \
                         if (self.get_number(adj[0], adj[1]) == 0 or adj == dest) \
                         and adj not in visited]
            if len(neighbors) > 0:
                queue.append(neighbors[0])
            else:
                queue = queue[:-1]
        return False

    def bfs(self, origin, dest):
        # print(self.to_string())
        # print(f"From {origin} to {dest}")
        queue = [origin]
        visited = set()
        while len(queue) > 0:
            u = queue[0]
            queue = queue[1:]
            # print(f"Analyzing {u}")
            visited.add(u)
            neighbors = [adj for adj in self.get_adjacents(u[0], u[1]) \
                         if (self.get_number(adj[0], adj[1]) == 0 or adj == dest) \
                         and adj not in visited and adj not in queue]
            if dest in neighbors:
                return True
            queue.extend(neighbors)
        return False

    def is_space_reachable(self, origin, length):
        # print(self.to_string())
        # print(f"From {origin}, length {length}")
        count = -1
        queue = [origin]
        visited = set()
        while len(queue) > 0:
            u = queue[-1]
            if u not in visited:
                count += 1
                visited.add(u)
            if count == length:
                return True
            neighbors = [adj for adj in self.get_adjacents(u[0], u[1]) \
                         if (self.get_number(adj[0], adj[1]) == 0) \
                         and adj not in visited]
            if len(neighbors) > 0:
                queue.append(neighbors[0])
            else:
                queue = queue[:-1]
        return False

    def check_free_spaces(self, start):

        list_free_spaces = self.free_spaces
        visited = set()
        lower_value = self.global_min[1]
        upper_value = self.global_max[1]
        lower = self.global_min[0]
        uppper = self.global_max[0]
        processed = set()

        for space in list_free_spaces:
            processed.update(processed.union(visited))
            if space in processed:
                continue
            visited = set()
            no_visited = 0
            bigger_count = 0
            bigger_list = []
            stack = [space]
            seen_upper = seen_lower = False
            while stack:
                # print(stack)
                u = stack[-1]
                print_debug(f"Currently in {u}")
                if u in processed:
                    bigger_count = 2
                    break;
                if u not in visited:
                    visited.add(u)
                    no_visited += 1
                    for n in [adj for adj in self.get_adjacents(u[0], u[1])]:
                        value_n = self.get_number(n[0], n[1])
                        if n not in visited and value_n == 0:
                            stack.append(n)
                        if value_n >= start and not n in bigger_list and not \
                                (len(bigger_list) == 1 and abs(
                                    self.get_number(n[0], n[1]) - self.get_number(bigger_list[0][0],
                                                                                  bigger_list[0][1])) == 1):
                            bigger_list.append(n)
                            bigger_count += 1
                            print_debug(f"Found {value_n} in {n}")
                            print_debug(f"Got {bigger_count}")
                        if bigger_count == 2:
                            print_debug("lezz go")
                            break
                        if lower_value == value_n:
                            seen_lower = True
                        if upper_value == value_n:
                            seen_upper = True
                    if bigger_count == 2:
                        print_debug("Got out!")
                        break
                else:
                    stack = stack[:-1]

            if not (bigger_count == 2 or (seen_lower and no_visited == lower_value - 1) or
                    (seen_upper and no_visited == self.board_size ** 2 - upper_value) or
                    (seen_upper and seen_lower and (
                            no_visited == lower_value - 1 + self.board_size ** 2 - upper_value))):
                print_debug("Formaram-se ilhas!")
                return False

        return True

    def manhattan_distance(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def __copy__(self):
        class Empty(self.__class__):
            def __init__(self): pass

        new_copy = Empty()
        new_copy.__class__ = self.__class__
        return new_copy


class Numbrix(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """
        self.initial = NumbrixState(board)

    def actions(self, state: NumbrixState):
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """

        global i
        # global initial_board
        # if tracemalloc.get_traced_memory()[1] // 1024 > 32768:
        # print_debug("Checking our own generated puzzles that exceed memory...")
        # print_debug(f'\n{initial_board.to_string()}')
        # raise AttributeError(f'\n{initial_board.to_string()}')
        # # print_debug(f"Está a haver merda? {sum([len(island) for island in state.board.islands]) == state.board.board_size ** 2 - len(state.board.numbers_to_go)}")
        actions = []
        # islands_len = len(state.board.islands)
        # print_debug("\n\n")
        # print_debug(f"Initial board {i}")
        i += 1
        # print_debug(state.board.islands)
        # print_debug(state.board.to_string())

        print('Going on actions with:')
        print(f'Global Min: {state.board.global_min} ; Global Max: {state.board.global_max}')
        print(f'Local Min: {state.board.local_min} ; Local Max: {state.board.local_max}')

        upper_bound = state.board.global_max[1]
        upper_bound_pos = state.board.global_max[0]

        lower_bound = state.board.global_min[1]
        lower_bound_pos = state.board.global_min[0]

        # Check if we can continue the board from the lowest and highest occupied position
        if not (state.board.is_space_reachable(lower_bound_pos, lower_bound - 1)
                and state.board.is_space_reachable(upper_bound_pos, state.board.board_size ** 2 - upper_bound)):
            print_debug("Bounds not continuable")
            return []

        if not state.board.extremes:

            maximum = state.board.local_max[1]
            maximum_pos = state.board.local_max[0]

            minimum = state.board.local_min[1]
            minimum_pos = state.board.local_min[0]
            # print_debug(f"Maximum:{maximum} Minimum:{minimum}")

            # Check if the real distance between numbers is smaller than their manhattan distance
            if abs(maximum_pos[0] - minimum_pos[0]) + abs(maximum_pos[1] - minimum_pos[1]) > minimum - maximum:
                print_debug("O que estas a fazer??")
                # print("Actions")
                # print(f"{[]}")
                return []

            # Check if the minimum and maximum are mutually reachable
            if not state.board.dfs(maximum_pos, minimum_pos):
                print_debug("Not reachable")
                # print("Actions")
                # print(f"{[]}")
                return []

            if maximum + 1 in state.board.numbers_to_go:
                for pos in [adj for adj in state.board.get_adjacents(maximum_pos[0], maximum_pos[1]) \
                            if state.board.get_number(adj[0], adj[1]) == 0]:

                    # Simulate attribution of position
                    print_debug("Simulating")
                    state.board.set_number(pos[0], pos[1], maximum + 1)
                    state.board.free_spaces.remove((pos[0], pos[1]))
                    print_debug(state.board.to_string())

                    if abs(pos[0] - minimum_pos[0]) + abs(pos[1] - minimum_pos[1]) > minimum - (maximum + 1):
                        print_debug("2 O que estas a fazer??")
                        state.board.free_spaces.add((pos[0], pos[1]))
                        state.board.set_number(pos[0], pos[1], 0)
                        continue

                    if not state.board.dfs(pos, minimum_pos):
                        print_debug("2 Not reachable")
                        state.board.free_spaces.add((pos[0], pos[1]))
                        state.board.set_number(pos[0], pos[1], 0)
                        continue

                    if abs(pos[0] - minimum_pos[0]) + abs(pos[1] - minimum_pos[1]) <= minimum - (maximum + 1) and \
                            state.board.check_free_spaces(maximum + 1):
                        actions.append((pos[0], pos[1], maximum + 1))
                    else:
                        print_debug("Nuh-uh")

                    state.board.free_spaces.add((pos[0], pos[1]))
                    state.board.set_number(pos[0], pos[1], 0)

        if state.board.extremes:
            print_debug('Aqui caralho')
            maximum = state.board.global_max[1]
            maximum_pos = state.board.global_max[0]
            if maximum != state.board.board_size ** 2:
                for pos in [adj for adj in state.board.get_adjacents(maximum_pos[0], maximum_pos[1]) \
                            if state.board.get_number(adj[0], adj[1]) == 0]:
                    actions.append((pos[0], pos[1], maximum + 1))

            minimum = state.board.global_min[1]
            minimum_pos = state.board.global_min[0]
            if minimum != 1:
                for pos in [adj for adj in state.board.get_adjacents(minimum_pos[0], minimum_pos[1]) \
                            if state.board.get_number(adj[0], adj[1]) == 0]:
                    actions.append((pos[0], pos[1], minimum - 1))
        print_debug("Actions")
        print_debug(f"{actions}")
        return actions

    def result(self, state: NumbrixState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state). """

        (row, col, value) = action
        # print(f"Before applying {action}")
        # print(state.board.islands)
        # print(state.board.island_map)
        # print(state.board.to_string())

        new_board = copy.copy(state.board)
        new_board.board_size = state.board.board_size
        new_board.board = copy.copy(state.board.board)
        new_board.set_number(row, col, value)
        new_board.numbers_to_go = state.board.numbers_to_go - {value}
        new_board.free_spaces = state.board.free_spaces - {(row, col)}
        new_board.assigned_positions = copy.copy(state.board.assigned_positions)
        new_board.assigned_positions[value] = (row, col)

        if value < state.board.global_min[1]:
            new_board.global_min = ((row, col), value)
        else:
            new_board.global_min = state.board.global_min

        if value > state.board.global_max[1]:
            new_board.global_max = ((row, col), value)
        else:
            new_board.global_max = state.board.global_max

        new_board.local_max = ((row, col), value)
        new_board.local_min = state.board.local_min
        if value + 1 == state.board.local_min[1]:
            new_board.local_max = new_board.island_dfs(((row, col), value))
            new_board.local_min = ((0, 0), state.board.board_size ** 2 + 1)
            for i in range(state.board.board_size):
                for j in range(state.board.board_size):
                    num = new_board.get_number(i, j)
                    if new_board.local_max[1] < num < new_board.local_min[1]:
                        new_board.local_min = ((i, j), num)

        if new_board.global_min == new_board.local_min or new_board.global_max == new_board.local_max:
            new_board.extremes = True

        print_debug('-----------------')
        print_debug('new_board:')
        print_debug(f'- board_size = {new_board.board_size}')
        print_debug(f'- board:\n{new_board.to_string()}')
        print_debug(f'- numbers_to_go = {new_board.numbers_to_go}')
        print_debug(f'- free_spaces = {new_board.free_spaces}')
        print_debug(f'- assigned_positions = {new_board.assigned_positions}')
        print_debug(f'- global_min = {new_board.global_min}')
        print_debug(f'- global_max = {new_board.global_max}')
        print_debug(f'- local_min = {new_board.local_min}')
        print_debug(f'- local_max = {new_board.local_max}')
        print_debug('-----------------')

        # print(f"Applying {action}")
        # print(new_board.islands)
        # print(new_board.island_map)
        # print(new_board.to_string())
        # print("\n")
        return NumbrixState(new_board)

    def goal_test(self, state: NumbrixState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes. """
        return state.board.extremes and len(state.board.numbers_to_go) == 0

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        # return len(node.state.board.islands)
        board = node.state.board
        total = 0
        empty_positions = [(i, j) for i in range(board.board_size) for j in range(board.board_size) \
                           if board.get_number(i, j) == 0]
        for pos in empty_positions:
            free_adj = [adj for adj in board.get_adjacents(pos[0], pos[1]) if board.get_number(adj[0], adj[1]) == 0]
            total += (4 - len(free_adj)) ** 2
        return total

    # TODO: outros metodos da classe


if __name__ == "__main__":
    board = Board.parse_instance(sys.argv[1])
    tic = time.perf_counter()
    tracemalloc.start()
    problem = Numbrix(board)
    goal_node = greedy_search(problem)
    print(f'Memória usada: {tracemalloc.get_traced_memory()[1] // 1024} kB')
    toc = time.perf_counter()
    print(f"Programa executado em {toc - tic:0.4f} segundos.")
    print('----------------------------')
    print(goal_node.state.board.to_string(), sep="")
