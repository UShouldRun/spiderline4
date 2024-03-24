from game_settings import *
from bots import Bot0, Bot1, Bot2, Bot3
from player import Player
from objects import Board, Button, Clock
from copy import deepcopy

class SpiderLine4:
    def __init__(self) -> None:
        '''Initializes all necessary variables.'''
        self.screen = screen
        self.running = True

        # menus
        self.current_state = 0 
        self.states = {0: "main_menu", 1: "in_game", 2: "win_label"}

        # mouse
        self.mouse_pos = [0,0]
        self.mouse_clicked = False

        self.tested = False

        # play button
        self.play_button = Button(self.screen, WIDTH//2 - BUTTON_WIDTH//2, HEIGHT//2 - BUTTON_HEIGHT//2, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, FONT_COLOR, "PLAY", TEXT_SIZE, MAIN_FONT)
        self.legal_moves_button = Button(self.screen, (WIDTH//2 - BOARD_WIDTH//2)//2 - BUTTON_WIDTH//4, HEIGHT//16, BUTTON_WIDTH//2, BUTTON_HEIGHT//2, BUTTON_COLOR, FONT_COLOR, "DISPLAY MOVES", TEXT_SIZE//2, MAIN_FONT)

        # FPS
        self.ticks = 1000//FPS
        self.timer = 0

        # board and game variables
        self.board = Board(N,M,WIDTH//2 - BOARD_WIDTH//2, HEIGHT//2 - BOARD_HEIGHT//2, BOARD_WIDTH, BOARD_HEIGHT)
        self.game_state = 0
        self.turn = 1
        self.display_switch = True

        # entities
        self.selected_bot = 0
        self.bots = [Bot0(self.board), Bot1(self.board), Bot2(self.board), Bot3(self.board)]

        self.player = Player(self.board, "1")
        self.player1 = self.player # by default the user is the player 1

        # winning label
        self.win_label_clock = 0
        self.win_label_limit = 300
        self.win_player = 0
        self.win_font = pygame.font.SysFont(MAIN_FONT, TEXT_SIZE)

    def initialize_board(self) -> None:
        self.board = Board(N,M,WIDTH//2 - BOARD_WIDTH//2, HEIGHT//2 - BOARD_HEIGHT//2, BOARD_WIDTH, BOARD_HEIGHT)
        self.game_state = 0
        self.turn = 1
        self.win_player = 0
        self.player.board = self.board
        for bot in self.bots: bot.board = self.board

    def isRunning(self) -> bool:
        '''Returns True if the current game is still running.'''
        return self.running
    def get_current_state(self) -> int:
        '''Returns the current menu.'''
        return self.current_state

    def get_game_state(self) -> int:
        '''Returns 0 if the game is still on going, 1 if the player 1 won the game, 2 if the player 2 won the game and 3 if the game was a draw.'''
        return self.game_state
    def get_turn(self) -> int:
        '''Return the which player is supposed to play. 1 for player 1 and 2 for player 2.'''
        return self.turn
    def set_turn(self, turn: int) -> None:
        '''Defines which player is playing.'''
        self.turn = turn
    def get_display(self) -> bool:
        '''Returns True if the user wants to see the possible legal moves on the board.'''
        return self.display_switch
    def set_display(self, state: bool = None) -> None:
        if state is not None: self.display_switch = state
        else: self.display_switch = not self.display_switch

    def isMouseClicked(self) -> bool: return self.mouse_clicked
    def get_mouse_pos(self) -> tuple: return self.mouse_pos
    def mouse_switch(self, state: bool = None) -> None:
        if state is not None: self.mouse_clicked = state 
        else: self.mouse_clicked = not self.mouse_clicked

    def get_selected_bot(self) -> int:
        '''Returns the current selected bot to play against the player. Notice that this returns player 2.'''
        return self.selected_bot
    def get_player1(self): return self.player1
    def get_player2(self): return self.bots[self.get_selected_bot()]
    def get_players(self) -> list:
        '''Returns a list with the player 1 and the player 2.'''
        return [self.get_player1(), self.get_player2()]

    def set_player1(self, entity) -> None:
        '''Sets who is playing, the player or one of the bots.'''
        self.player1 = entity

    def get_win_label_limit(self) -> int: return self.win_label_limit 
    def get_win_player(self) -> int: return self.win_player

    def print_board(self) -> None:
        '''Testing purposes.'''
        for row in self.board.get_matrix(): print(row)

    # Input Section

    def update_mouse(self, event) -> None: self.mouse_pos = event.pos

    def handle_events(self) -> None:
        '''Depending on which menu the user is, redefines variables to change the app state.'''
        match self.states[self.get_current_state()]:

            case "main_menu":
                if self.play_button.isClicked(self.get_mouse_pos()) and self.isMouseClicked():
                    self.current_state = 1
                    self.mouse_switch()

            case "in_game":
                if self.get_game_state() != 0:
                    self.current_state = 2
                    self.win_player = self.get_game_state()

                if self.isMouseClicked():
                    if self.legal_moves_button.isClicked(self.get_mouse_pos()): self.set_display()

                    if self.get_player1() == self.player and self.get_turn() == int(self.player.getPiece()):
                        board_pos = self.identify_board_click(self.get_mouse_pos())
                        if board_pos in self.get_legal_moves():
                            self.player.play(board_pos)
                            self.check_game_status()
                            self.set_turn(2)

                    self.mouse_switch()

    def get_inputs(self) -> None:
        '''Loops over all pygame events and handles the events.'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN: self.mouse_switch(True)
            else: self.mouse_switch(False)
            if event.type == pygame.MOUSEMOTION: self.update_mouse(event)
        self.handle_events()

    # Process Input and Bot play

    def identify_board_click(self, pos: tuple[int,int]) -> tuple[int,int]:
        if pygame.Rect(pos[0],pos[1],0,0) not in self.board.get_rect(): return (-1,-1)
        return (int((pos[1] - self.board.get_rect().y)// SQUARE_SIZE), int((pos[0] - self.board.get_rect().x) // SQUARE_SIZE))

    def check_game_status(self) -> None:
        directions = [(-1,-1),(-1,0),(0,1),(1,1),(1,0),(0,-1),(1,-1),(-1,1)]
        for vector in directions:
            if self.checkWin(self.board.get_matrix(),vector,self.turn): self.game_state = self.turn
        if self.turn == 0 and self.checkDraw(self.board.get_matrix()): self.game_state = 3

    def checkWin(self, matrix, vector: tuple[int,int], turn: int) -> bool:
        def verify(i: int, j: int, vector: tuple[int,int], turn: int, count: int):
            if count == 4: return True
            elif not (-1 < i < len(matrix) and -1 < j < len(matrix[0])): return False
            elif matrix[i][j] != str(turn): return False
            return verify(i + vector[0], j + vector[1], vector, turn, count + 1)

        for i, row in enumerate(matrix):
            for j, entry in enumerate(row):
                if entry == str(turn):
                    check = verify(i, j, vector, turn, 0)
                    if check: return check
        return False

    def checkDraw(self, matrix) -> None:
        for row in matrix:
            for entry in row:
                if entry == "0": return False
        return True

    def get_legal_moves(self) -> list[tuple[int,int]]:

        moves = []
        for i in {0, self.board.get_rows() - 1}:
            for j in range(self.board.get_columns()):
                for k in range(0, self.board.get_rows(), 1):
                    if i > 0: k = -k
                    if (i+k,j) in moves: break
                    if self.board.get_matrix()[i+k,j] == "0":
                        moves.append((i+k,j))
                        break

        for j in {0, self.board.get_columns() - 1}:
            for i in range(1, self.board.get_rows() - 1):
                for k in range(0, self.board.get_columns()):
                    if j > 0: k = -k
                    if (i,j+k) in moves: break
                    if self.board.get_matrix()[i,j+k] == "0":
                        moves.append((i,j+k))
                        break

        return moves

    def play(self) -> None:
        if self.get_game_state() == 0:
            match self.get_turn():
                case 1:
                    if self.get_player1() != self.player:
                        self.get_player1().play("1", self.get_legal_moves)
                        self.set_turn(2)
                case 2:
                    self.get_player2().play("2", self.get_legal_moves)
                    self.set_turn(1)
            self.check_game_status()

    # Draw on the screen section

    def resize(self) -> None:
        '''Resizes all objects in case the game enters full screen or goes to the default state.'''
        pass

    def cleanScreen(self) -> None: self.screen.fill(BACKGROUND)

    def draw_board(self) -> None:
        '''Draws a background. Loops over all the board positions and draws the colored squares on even i + j positions. If a place is on the board, then the code recognizes and draws a circle on that position.'''
        pygame.draw.rect(self.screen, BOARD_COLOR, self.board.get_rect())
        for i in range(self.board.get_rows()):
            for j in range(self.board.get_columns()):
                x, y = (self.board.get_rect().x + j * SQUARE_SIZE, self.board.get_rect().y + i * SQUARE_SIZE)
                if (i+j)%2 == 0: pygame.draw.rect(self.screen, SQUARE_COLOR, pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE))
                if self.board.get_matrix()[i,j] != "0": pygame.draw.circle(self.screen, PLAYER_COLORS[self.board.get_matrix()[i,j]], (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), SQUARE_SIZE//2)

    def display_legal_moves(self) -> None:
        for move in self.get_legal_moves():
            pos = (self.board.get_rect().x + move[1] * SQUARE_SIZE + SQUARE_SIZE//4, self.board.get_rect().y + move[0] * SQUARE_SIZE + SQUARE_SIZE//4)
            pygame.draw.line(self.screen, COLORS["green"], (pos[0], pos[1]), (pos[0] + SQUARE_SIZE//2, pos[1] + SQUARE_SIZE//2), 5)
            pygame.draw.line(self.screen, COLORS["green"], (pos[0], pos[1] + SQUARE_SIZE//2), (pos[0] + SQUARE_SIZE//2, pos[1]), 5)

    def draw_winning_label(self) -> None:
        self.cleanScreen()
        text = f"PLAYER {self.get_win_player()} WON" if self.get_win_player() != 3 else "DRAW"
        label = self.win_font.render(text, True, COLORS["red"])
        self.screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//2 - label.get_height()//2))

        if self.win_label_clock == self.win_label_limit:
            self.win_label_clock = 0
            self.current_state = 0
            self.initialize_board()
        elif self.timer == self.ticks: self.win_label_clock += 1

    def draw_chat(self) -> None: pass
    def draw_clocks(self) -> None: pass

    def draw_main_menu(self) -> None:
        self.cleanScreen()
        self.play_button.draw()

    def draw_game(self) -> None:
        self.cleanScreen()
        self.draw_board()
        if self.get_display(): self.display_legal_moves()
        self.legal_moves_button.draw()
        self.draw_chat() # needs to be built
        self.draw_clocks() # needs to be built

    def draw(self) -> None:
        match self.states[self.get_current_state()]:
            case "main_menu": self.draw_main_menu()
            case "in_game": self.draw_game()
            case "win_label": self.draw_winning_label()

    # main function

    def run(self) -> None:
        while self.isRunning():
            if self.timer == self.ticks:
                self.get_inputs()
                self.play()
                self.draw()
                pygame.display.update()
                self.timer = 0
            self.timer += 1