import os
import random
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import enum
import json
import time
pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 512, 512
SQUARE_SIZE = 64
GRID_COLOURS = [(233, 237, 204), (119, 153, 84)]

GAME_SAVE_PATH = "chess.json"

piece_images = {}
icons = {}
sounds = {
    "move": pygame.mixer.Sound("assets\\sound\\move.mp3"),
    "take": pygame.mixer.Sound("assets\\sound\\capture.mp3"),
    "check": pygame.mixer.Sound("assets\\sound\\check.mp3"),
    "promote": pygame.mixer.Sound("assets\\sound\\promote.mp3"),
    "castle": pygame.mixer.Sound("assets\\sound\\castle.mp3"),
    "end": pygame.mixer.Sound("assets\\sound\\game-end.mp3")
}
fonts = {
    "norm": pygame.font.Font("assets\\font\\montserrat.ttf", 12),
    "bold": pygame.font.Font("assets\\font\\montserrat-bold.ttf", 24),
    "bold-small": pygame.font.Font("assets\\font\\montserrat-bold.ttf", 16),
}

class Team(enum.Enum):
    BLACK = enum.auto()
    WHITE = enum.auto()

    @staticmethod
    def get_opposing_team(team):
        return Team.BLACK if team == Team.WHITE else Team.WHITE
    
    @staticmethod
    def to_string(team) -> str:
        return "Black" if team == Team.BLACK else "White"
    
    @staticmethod
    def get_multiplier(team) -> int:
        return 1 if team == Team.WHITE else -1
    
class GameEnd(enum.Enum):
    CHECKMATE = enum.auto()
    STALEMATE = enum.auto()
    DRAW_MATERIAL = enum.auto()

class GUIReturnType(enum.Enum):
    CONTINUE = enum.auto()
    LEAVE = enum.auto()
    LEAVE_QUEEN = enum.auto()
    LEAVE_KNIGHT = enum.auto()
    LEAVE_ROOK = enum.auto()
    LEAVE_BISHOP = enum.auto()

class CastleMove():
    def __init__(self, old_pos, new_pos):
        self.old_pos = old_pos
        self.new_pos = new_pos

class Move():
    def __init__(self, new_index: pygame.Vector2, castle: CastleMove = None, en_passant: pygame.Vector2 = None, promotion = None):
        self.new_index = new_index
        self.castle = castle
        self.en_passant = en_passant
        self.promotion = promotion

    def is_in_bounds(self) -> bool:
        return self.new_index.y >= 0 and self.new_index.y < 8 and self.new_index.x >= 0 and self.new_index.x < 8

    def is_free(self, board) -> bool:
        return board.piece_at(self.new_index) == None
    
    def is_blocked_vertical(self, inital_position: pygame.Vector2, board, team) -> bool:
        dy = -1 if team == team.WHITE else 1
        return board.piece_at(pygame.Vector2(inital_position.x, inital_position.y + dy))
    
    def is_on_enemy(self, board, team) -> bool:
        if not board.piece_at(self.new_index): return
        return board.piece_at(self.new_index).team != team
    
    def causes_check(self, board, team, old_position) -> bool:
        new_board = PhantomBoard(board)
        new_board.move(old_position, self)
        return new_board.is_in_check(team)
    
    def to_json_obj(self, old_position) -> str:
        if self.castle:
            castle_dict = {
                "old_pos": tuple(self.castle.old_pos),
                "new_pos": tuple(self.castle.new_pos),
            }
        else:
            castle_dict = None     
        
        move_dict = {
            "old_pos": tuple(old_position),
            "new_pos": tuple(self.new_index),
            "castle": castle_dict,
            "en_passant": tuple(self.en_passant) if self.en_passant else None,
        }

        return move_dict
    
    def __eq__(self, other) -> bool:
        return self.new_index == other.new_index
    
    def __repr__(self) -> str:
        return str(self.new_index)
    
class Piece():
    def __init__(self, image, team, position, board):
        self.image = image
        self.team = team
        self.position = position
        self.board = board
        self.moved = False

    def get_valid_moves(self) -> list[Move]:
        raise NotImplementedError()

    def generate_valid_horizontal_moves(self, check_check = True) -> list[Move]:
        moves: list[Move] = []
        for multiplier in [1, -1]:
            d = multiplier
            while d + self.position.x < 8 and d + self.position.x >= 0:
                move = Move(pygame.Vector2(self.position.x + d, self.position.y))
                if not move.is_on_enemy(self.board, self.team) and self.board.piece_at(move.new_index):
                    break

                moves.append(move)
                d += multiplier

                if move.is_on_enemy(self.board, self.team):
                    break

            d = multiplier
            while d + self.position.y < 8 and d + self.position.y >= 0:
                move = Move(pygame.Vector2(self.position.x, self.position.y + d))
                if not move.is_on_enemy(self.board, self.team) and self.board.piece_at(move.new_index):
                    break

                moves.append(move)
                d += multiplier

                if move.is_on_enemy(self.board, self.team):
                    break

        if check_check:
            moves = self.elimate_illegal_check_reveals(moves)

        return moves
    
    def generate_valid_diagonal_moves(self, check_check = True) -> list[Move]:
        moves = []
        for multiplier in [1, -1]:
            for multiplier2 in [1, -1]:
                dx = multiplier
                dy = multiplier2

                while dx + self.position.x < 8 and dx + self.position.x >= 0 and dy + self.position.y < 8 and dy + self.position.y >= 0:
                    move = Move(pygame.Vector2(self.position.x + dx, self.position.y + dy))

                    if not move.is_on_enemy(self.board, self.team) and self.board.piece_at(move.new_index):
                        break

                    moves.append(move)
                    dx += multiplier
                    dy += multiplier2

                    if move.is_on_enemy(self.board, self.team):
                        break
        
        if check_check:
            moves = self.elimate_illegal_check_reveals(moves)

        return moves
    
    def elimate_illegal_check_reveals(self, moves) -> list[Move]:
        moves_copy = moves[:]
        for move in moves:
            if move.causes_check(self.board, self.team, self.position):
                moves_copy.remove(move)
        return moves_copy

class Pawn(Piece):
    def __init__(self, team, position, board):
        img = piece_images["bp"] if team == Team.BLACK else piece_images["wp"]
        super().__init__(img, team, position, board)

    def get_valid_moves(self, check_check = True) -> list[Move]:
        considered_moves: list[Move] = []
        take_moves: list[Move] = []
        moves = []

        team_multiplier = 1 if self.team == Team.BLACK else -1

        considered_moves.append(Move(pygame.Vector2(self.position.x, self.position.y + 1 * team_multiplier)))
        if not self.moved:
            considered_moves.append(Move(pygame.Vector2(self.position.x, self.position.y + 2 * team_multiplier)))
            
        take_left = pygame.Vector2(self.position.x - 1, self.position.y + 1 * team_multiplier)
        take_moves.append(Move(take_left))

        take_right = pygame.Vector2(self.position.x + 1, self.position.y + 1 * team_multiplier)
        take_moves.append(Move(take_right))

        for move in considered_moves:
            if move.is_in_bounds() and move.is_free(self.board) and not move.is_blocked_vertical(self.position, self.board, self.team):
                moves.append(move)
        for move in take_moves:
            if move.is_in_bounds() and self.board.piece_at(move.new_index) and self.board.piece_at(move.new_index).team != self.team:
                moves.append(move)
            elif move.is_in_bounds() and self.board.move_history:
                last_piece = self.board.piece_at(pygame.Vector2(self.board.move_history[-1]["new_pos"]))
                if last_piece:
                    direction = 1 if last_piece.team == Team.WHITE else -1
                    if isinstance(last_piece, Pawn) and abs(self.board.move_history[-1]["new_pos"][1] - self.board.move_history[-1]["old_pos"][1]) == 2 and pygame.Vector2(last_piece.position.x, last_piece.position.y + direction) == move.new_index:
                        if move.is_free(self.board):
                            moves.append(Move(move.new_index, en_passant = last_piece.position))

        if check_check:
            moves = self.elimate_illegal_check_reveals(moves)

        more_moves = []
        for move in moves:
            if move.new_index.y == 7 or move.new_index.y == 0:
                move.promotion = Queen
                more_moves.append(Move(move.new_index, promotion = Bishop))
                more_moves.append(Move(move.new_index, promotion = Knight))
                more_moves.append(Move(move.new_index, promotion = Rook))

        moves += more_moves

        return moves
    
class Rook(Piece):
    def __init__(self, team, position, board):
        img = piece_images["br"] if team == Team.BLACK else piece_images["wr"]
        super().__init__(img, team, position, board)
    
    def get_valid_moves(self, check_check = True) -> list[Move]:
        return self.generate_valid_horizontal_moves(check_check)

class Bishop(Piece):
    def __init__(self, team, position, board):
        img = piece_images["bb"] if team == Team.BLACK else piece_images["wb"]
        super().__init__(img, team, position, board)

    def get_valid_moves(self, check_check = True) -> list[Move]:
        return self.generate_valid_diagonal_moves(check_check)

class Knight(Piece):
    def __init__(self, team, position, board):
        img = piece_images["bn"] if team == Team.BLACK else piece_images["wn"]
        super().__init__(img, team, position, board)

    def get_valid_moves(self, check_check = True) -> list[Move]:
        position_differences = [[-2, -1], [-1, -2], [1, -2], [2, -1], [2, 1], [1, 2], [-1, 2], [-2, 1]]
        considered_moves = [Move(pygame.Vector2(self.position.x + dv[0], self.position.y + dv[1])) for dv in position_differences]
        moves = []

        for move in considered_moves:
            if move.is_in_bounds() and (move.is_free(self.board) or move.is_on_enemy(self.board, self.team)):
                moves.append(move)

        if check_check:
            moves = self.elimate_illegal_check_reveals(moves)

        return moves

class Queen(Piece):
    def __init__(self, team, position, board):
        img = piece_images["bq"] if team == Team.BLACK else piece_images["wq"]
        super().__init__(img, team, position, board)

    def get_valid_moves(self, check_check = True) -> list[Move]:
        return self.generate_valid_diagonal_moves(check_check) + self.generate_valid_horizontal_moves(check_check)

class King(Piece):
    def __init__(self, team, position, board):
        img = piece_images["bk"] if team == Team.BLACK else piece_images["wk"]
        super().__init__(img, team, position, board)

    def get_castle_moves(self):
        if self.moved: return []

        considered_moves = []

        pieces = self.board.get_pieces_of_team(self.team)
        for piece in pieces:
            if isinstance(piece, Rook) and not piece.moved:
                rook_offset = -int(self.position.x - piece.position.x)
                direction = 1 if rook_offset > 0 else -1
                
                has_line_of_sight = True
                for dx in range(1, abs(rook_offset)):
                    if self.board.piece_at(pygame.Vector2(self.position.x + dx * direction, self.position.y)):
                        has_line_of_sight = False
                if has_line_of_sight:
                    considered_moves.append(Move(pygame.Vector2(self.position.x + 2 * direction, self.position.y), castle = CastleMove(piece.position, pygame.Vector2(self.position.x + direction, self.position.y))))

        for move in considered_moves:
            if not move.is_in_bounds():
                considered_moves.remove(move)

        return considered_moves

    def get_valid_moves(self, check_check = True) -> list[Move]:
        considered_moves: list[Move] = []
        moves: list[Move] = []
        for x in range(int(self.position.x - 1), int(self.position.x + 2)):
            for y in range(int(self.position.y - 1), int(self.position.y + 2)):
                if self.position.xy == (x, y): continue
                considered_moves.append(Move(pygame.Vector2(x, y)))

        for move in considered_moves:
            if move.is_in_bounds() and (move.is_free(self.board) or move.is_on_enemy(self.board, self.team)):
                moves.append(move)

        moves += self.get_castle_moves()

        if check_check:
            moves = self.elimate_illegal_check_reveals(moves)

        return moves

class PhantomBoard():
    def __init__(self, board):
        board_matrix = board.board
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for y, row in enumerate(board_matrix):
            for x, piece in enumerate(row):
                if piece != None:
                    new_piece = piece.__class__(piece.team, piece.position, self)
                    new_piece.moved = piece.moved
                    self.set_piece(new_piece)
        self.move_history = board.move_history

    def is_in_check(self, king_team):
        king_index = self.find_king(king_team)
        for row in self.board:
            for piece in row:
                if piece != None and piece.team == Team.get_opposing_team(king_team):
                    moves = piece.get_valid_moves(check_check = False)
                    for move in moves:
                        if move.new_index == king_index:
                            piece.get_valid_moves(check_check = False)
                            return True
        return False
    
    def piece_at(self, index):
        return Board.piece_at(self, index)
    
    def set_piece(self, piece):
        return Board.set_piece(self, piece)
    
    def empty_square(self, index):
        return Board.empty_square(self, index)
    
    def find_king(self, team):
        return Board.find_king(self, team)
    
    def get_pieces_of_team(self, team):
        return Board.get_pieces_of_team(self, team)

    def move(self, old_index: pygame.Vector2, move: Move):
        piece = self.piece_at(old_index)
        piece.position = move.new_index

        self.empty_square(old_index)
        self.set_piece(piece)

        if move.en_passant:
            self.empty_square(move.en_passant)

        if move.promotion:
            new_piece = move.promotion(piece.team, piece.position, piece.board)
            self.set_piece(new_piece)

        if move.castle:
            rook = self.piece_at(move.castle.old_pos)
            rook.position = move.castle.new_pos

            self.set_piece(rook)
            self.empty_square(move.castle.old_pos)

class GameOver():
    def __init__(self, type, winner = None):
        self.screen = pygame.display.get_surface()

        self.status = GUIReturnType.CONTINUE

        self.image = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (38, 36, 33), [0, 0, self.image.get_width(), self.image.get_height()], border_radius = 15)
        self.image = pygame.transform.smoothscale(self.image, (self.image.get_width() * 0.9, self.image.get_height() * 0.9))
        self.rect = self.image.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        if type == GameEnd.CHECKMATE:
            title_str = Team.to_string(winner) + " Won"
            sub_str = "by checkmate"
            icon = pygame.transform.smoothscale(icons["medal_icon"], (self.rect.width // 4, self.rect.height // 4))

        elif type == GameEnd.STALEMATE:
            title_str = "Draw"
            sub_str = "by stalemate"
            icon = pygame.transform.smoothscale(icons["draw_icon"], (self.rect.width // 4, self.rect.height // 4))

        elif type == GameEnd.DRAW_MATERIAL:
            title_str = "Draw"
            sub_str = "by insufficient material"
            icon = pygame.transform.smoothscale(icons["draw_icon"], (self.rect.width // 4, self.rect.height // 4))

        title_text = fonts["bold"].render(title_str, True, (255, 255, 255))
        sub_text = fonts["norm"].render(sub_str, True, (255, 255, 255))
        icon_image = icon if icon else pygame.Surface((1, 1), pygame.SRCALPHA)

        font_height = fonts["bold"].size("qwertyuiopasdfghjklzxcvbnm")[1]

        title_rect = title_text.get_rect(centerx = self.rect.width // 2, top = font_height / 2)
        sub_rect = sub_text.get_rect(centerx = self.rect.width // 2, top = title_rect.bottom + font_height / 5)
        self.image.blit(title_text, title_rect)
        self.image.blit(sub_text, sub_rect)

        restart_image = pygame.Surface((self.rect.width * 0.8, self.rect.height * 0.2), pygame.SRCALPHA)
        self.restart_rect = restart_image.get_rect(centerx = self.rect.width // 2, bottom = self.rect.height - font_height / 2)
        restart_text = fonts["bold-small"].render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center = (self.restart_rect.width // 2, self.restart_rect.height // 2 - 2.5))
        
        pygame.draw.rect(restart_image, (69, 117, 60), [0, 5, self.restart_rect.width, self.restart_rect.height - 5], border_radius=10)
        pygame.draw.rect(restart_image, (129, 182, 76), [0, 0, self.restart_rect.width, self.restart_rect.height - 5], border_radius=10)
        restart_image.blit(restart_text, restart_text_rect)

        icon_image_rect = icon_image.get_rect(center = (self.rect.width // 2, self.rect.height // 2))
        self.image.blit(icon_image, icon_image_rect)

        self.image.blit(restart_image, self.restart_rect)

    def on_mouse_down(self):
        pos = pygame.mouse.get_pos()
        actual_restart_rect = pygame.Rect(self.rect.x + self.restart_rect.x, self.rect.y + self.restart_rect.y, self.restart_rect.width, self.restart_rect.height)
        if actual_restart_rect.collidepoint(pos):
            self.status = GUIReturnType.LEAVE

    def render(self):
        self.screen.blit(self.image, self.rect)
        mouse_pos = pygame.mouse.get_pos()
        actual_restart_rect = pygame.Rect(self.rect.x + self.restart_rect.x, self.rect.y + self.restart_rect.y, self.restart_rect.width, self.restart_rect.height)
        if actual_restart_rect.collidepoint(mouse_pos):
            hover_overlay = pygame.Surface(actual_restart_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(hover_overlay, (255, 255, 255), [0, 0, actual_restart_rect.width, actual_restart_rect.height], border_radius=10)
            hover_overlay.set_alpha(30)

            self.screen.blit(hover_overlay, actual_restart_rect)
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class PromoteGUI():
    def __init__(self, piece: Piece):
        self.screen = pygame.display.get_surface()
        self.status = GUIReturnType.CONTINUE
        self.piece = piece

        self.image = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE * 4))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(x = piece.position.x * SQUARE_SIZE)
        if piece.team == Team.WHITE:
            self.rect.top = 0
        else:
            self.rect.bottom = 8 * SQUARE_SIZE

        team_str = "b" if self.piece.team == Team.BLACK else "w"
        dir_multi = 1 if self.piece.team == Team.WHITE else -1
        offset = self.rect.bottom if self.piece.team == Team.BLACK else self.rect.y - SQUARE_SIZE

        self.queen_image = piece_images[team_str + "q"]
        self.knight_image = piece_images[team_str + "n"]
        self.rook_image = piece_images[team_str + "r"]
        self.bishop_image = piece_images[team_str + "b"]

        self.queen_rect = self.queen_image.get_rect(x = self.rect.x, y = offset + dir_multi * SQUARE_SIZE)
        self.knight_rect = self.knight_image.get_rect(x = self.rect.x, y = offset + dir_multi * SQUARE_SIZE * 2)
        self.rook_rect = self.rook_image.get_rect(x = self.rect.x, y = offset + dir_multi * SQUARE_SIZE * 3)
        self.bishop_rect = self.bishop_image.get_rect(x = self.rect.x, y = offset + dir_multi * SQUARE_SIZE * 4)

    def on_mouse_down(self):
        pos = pygame.mouse.get_pos()
        if self.queen_rect.collidepoint(pos):
            self.status = GUIReturnType.LEAVE_QUEEN
        elif self.knight_rect.collidepoint(pos):
            self.status = GUIReturnType.LEAVE_KNIGHT
        elif self.rook_rect.collidepoint(pos):
            self.status = GUIReturnType.LEAVE_ROOK
        elif self.bishop_rect.collidepoint(pos):
            self.status = GUIReturnType.LEAVE_BISHOP

    def render(self):
        self.screen.blit(self.image, self.rect)
        self.screen.blit(self.queen_image, self.queen_rect)
        self.screen.blit(self.knight_image, self.knight_rect)
        self.screen.blit(self.rook_image, self.rook_rect)
        self.screen.blit(self.bishop_image, self.bishop_rect)

        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

class Board():
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.overide_sounds = False

        self.board_image = self.generate_board_image()

        self.board: list[list[Piece | None]]
        self.generate_board()

        self.gui_overide = None

        self.selected = None
        self.current_team = Team.WHITE

        self.move_history = []

    def generate_board_image(self) -> pygame.Surface:
        image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for x in range(8):
            for y in range(8):
                pygame.draw.rect(image, GRID_COLOURS[(x % 2 + y % 2) % 2], [x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE])
            
        return image
    
    def generate_board(self) -> None:
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for i in range(8):
            self.set_piece(Pawn(Team.BLACK, pygame.Vector2(i, 1), self))
            self.set_piece(Pawn(Team.WHITE, pygame.Vector2(i, 6), self))

        self.set_piece(Rook(Team.BLACK, pygame.Vector2(0, 0), self))
        self.set_piece(Rook(Team.BLACK, pygame.Vector2(7, 0), self))
        self.set_piece(Rook(Team.WHITE, pygame.Vector2(0, 7), self))
        self.set_piece(Rook(Team.WHITE, pygame.Vector2(7, 7), self))

        self.set_piece(Knight(Team.BLACK, pygame.Vector2(1, 0), self))
        self.set_piece(Knight(Team.BLACK, pygame.Vector2(6, 0), self))
        self.set_piece(Knight(Team.WHITE, pygame.Vector2(1, 7), self))
        self.set_piece(Knight(Team.WHITE, pygame.Vector2(6, 7), self))

        self.set_piece(Bishop(Team.BLACK, pygame.Vector2(2, 0), self))
        self.set_piece(Bishop(Team.BLACK, pygame.Vector2(5, 0), self))
        self.set_piece(Bishop(Team.WHITE, pygame.Vector2(2, 7), self))
        self.set_piece(Bishop(Team.WHITE, pygame.Vector2(5, 7), self))

        self.set_piece(Queen(Team.BLACK, pygame.Vector2(3, 0), self))
        self.set_piece(Queen(Team.WHITE, pygame.Vector2(3, 7), self))

        self.set_piece(King(Team.BLACK, pygame.Vector2(4, 0), self))
        self.set_piece(King(Team.WHITE, pygame.Vector2(4, 7), self))

        self.selected = None
        self.current_team = Team.WHITE
        self.move_history = []

    def on_mouse_down(self) -> None:
        if self.gui_overide:
            self.gui_overide.on_mouse_down()
            return
        
        mouse_pos = pygame.mouse.get_pos()
        clicked_index = pygame.Vector2(mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE)

        valid_castle_pos = []
        if self.selected != None:
            valid_moves = self.piece_at(self.selected).get_valid_moves(check_check = True)
            for move in valid_moves:
                if move.castle:
                    valid_castle_pos.append(move.castle.old_pos)

        if self.piece_at(clicked_index) != None:
            if self.selected and self.selected == clicked_index:
                self.selected = None
            elif self.piece_at(clicked_index).team == self.current_team and not clicked_index in valid_castle_pos:
                self.selected = clicked_index

        # start_time = time.time()
        if self.selected != None:
            for move in self.piece_at(self.selected).get_valid_moves(check_check = True):
                if clicked_index == move.new_index or (move.castle and clicked_index == move.castle.old_pos):
                    move.promotion = None
                    self.move_piece(self.selected, move)
                    self.selected = None
                    # print(f"Move {self.index_to_notation(clicked_index)} completed in {time.time() - start_time} seconds.")
                    break

    def on_key_down(self, key) -> None:
        keys = pygame.key.get_pressed()
        if key == pygame.K_s and keys[pygame.K_LCTRL]:
            self.save_game_to_file(GAME_SAVE_PATH)
        elif key == pygame.K_l and keys[pygame.K_LCTRL]:
            self.load_game_from_file(GAME_SAVE_PATH)

    def piece_at(self, index: pygame.Vector2) -> Piece:
        return self.board[int(index.y)][int(index.x)]
    
    def set_piece(self, piece: Piece | None) -> None:
        self.board[int(piece.position.y)][int(piece.position.x)] = piece

    def empty_square(self, index: pygame.Vector2) -> None:
        self.board[int(index.y)][int(index.x)] = None

    def move_piece(self, old_index: pygame.Vector2, move: Move) -> None:
        #start_time = time.time()
        self.move_history.append(move.to_json_obj(old_index))

        taken = self.piece_at(move.new_index) != None

        piece = self.piece_at(old_index)
        piece.position = move.new_index

        self.empty_square(old_index)
        self.set_piece(piece)

        piece.moved = True

        castled = False
        if move.castle:
            rook = self.piece_at(move.castle.old_pos)
            rook.position = move.castle.new_pos

            self.set_piece(rook)
            self.empty_square(move.castle.old_pos)

            castled = True

        if move.en_passant:
            self.empty_square(move.en_passant)
            taken = True

        promoted = False
        if move.promotion:
            self.promote_piece(piece, move.promotion)
            promoted = True

        if self.is_checkmate(Team.get_opposing_team(self.current_team)):
            sounds["end"].play()
            self.gui_overide = GameOver(type = GameEnd.CHECKMATE, winner = self.current_team)
            return

        if self.is_stalemate(Team.BLACK) or self.is_stalemate(Team.WHITE):
            sounds["end"].play()
            self.gui_overide = GameOver(type = GameEnd.STALEMATE)
            return

        if self.is_draw_insufficient_material():
            sounds["end"].play()
            self.gui_overide = GameOver(type = GameEnd.DRAW_MATERIAL)

        self.current_team = Team.WHITE if self.current_team == Team.BLACK else Team.BLACK

        if isinstance(piece, Pawn):
            if (piece.position.y == 0 or piece.position.y == 7) and not promoted:
                self.gui_overide = PromoteGUI(piece)
                return
        
        if not self.overide_sounds:
            # enemy team is in check
            if self.is_in_check(self.current_team):
                sounds["check"].play()
            elif promoted:
                sounds["promote"].play()
            elif castled:
                sounds["castle"].play()
            elif taken:
                sounds["take"].play()
            else:
                sounds["move"].play()

        self.selected = None

        #print(f"Move piece function took {time.time() - start_time} seconds")

    def promote_piece(self, piece: Piece, new_piece_class) -> None:
        new_piece = new_piece_class(piece.team, piece.position, piece.board)
        self.set_piece(new_piece)

    def find_king(self, team) -> pygame.Vector2:
        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if isinstance(piece, King) and piece.team == team:
                    return pygame.Vector2(x, y)
                
        raise Exception("No king found of " + str(team) + " team")

    def is_in_check(self, king_team) -> bool:
        king_index = self.find_king(king_team)
        for piece in self.get_pieces_of_team(Team.get_opposing_team(king_team)):
            for move in piece.get_valid_moves(check_check = True):
                if move.new_index == king_index:
                    return True
        return False
    
    def get_pieces_of_team(self, team) -> list[Piece]:
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != None and piece.team == team:
                    pieces.append(piece)
        return pieces

    def get_pieces_with_valid_move(self, team) -> list[Piece]:
        rl = []
        for piece in self.get_pieces_of_team(team):
            if len(piece.get_valid_moves()) > 0:
                rl.append(piece)
        return rl
    
    def get_all_pieces(self) -> list[Piece]:
        return self.get_pieces_of_team(Team.BLACK) + self.get_pieces_of_team(Team.WHITE)

    def get_all_moves_of_team(self, team) -> list[Move]:
        l = []
        for x in self.get_pieces_with_valid_move(team).get_valid_moves():
            l += x
        return l

    def is_checkmate(self, king_team) -> bool:
        if self.is_in_check(king_team):
            for piece in self.get_pieces_of_team(king_team):
                if len(piece.get_valid_moves()) != 0:
                    return False
            return True
        else:
            return False

    def is_stalemate(self, team) -> bool:
        if not self.is_in_check(team):
            for piece in self.get_pieces_of_team(team):
                if len(piece.get_valid_moves()) != 0:
                    return False
            return True    

    def is_draw_insufficient_material(self) -> bool:
        if len(self.get_pieces_of_team(Team.BLACK) + self.get_pieces_of_team(Team.WHITE)) == 2:
            return True
        return False

    def notation_to_index(self, notation: str) -> pygame.Vector2:
        return pygame.Vector2(ascii(notation[0] - 97), int(8 - notation[1]))

    def index_to_notation(self, index: pygame.Vector2) -> str:
        letter = chr(97 + int(index.x))
        num = str(8 - int(index.y))
        return letter + num

    def save_game_to_file(self, path) -> None:
        with open(path, "w") as f:
            json.dump(self.move_history, f, indent=4)
        print("Saved game to " + path)

    def load_game_from_file(self, path) -> None:
        with open(path, "r") as f:
            moves = json.load(f)
        
        self.generate_board()

        for move_dict in moves:
            if move_dict["castle"]:
                castle = CastleMove(pygame.Vector2(move_dict["castle"]["old_pos"]), pygame.Vector2(move_dict["castle"]["new_pos"]))
            else:
                castle = None

            move = Move(pygame.Vector2(move_dict["new_pos"]), castle, move_dict["en_passant"])
            self.move_piece(pygame.Vector2(move_dict["old_pos"]), move)
            self.move_history.append(move.to_json_obj(move_dict["old_pos"]))

        print("Loaded game from " + path)

    def print_board(self) -> None:
        piece_dict = {
            Pawn: "p",
            Rook: "r",
            Knight: "n",
            Bishop: "b",
            Queen: "q",
            King: "k",
            None.__class__: " ",
        }
        for row in self.board:
            print([piece_dict[piece.__class__] for piece in row])
        print("\n\n")

    def update(self) -> None:
        if self.gui_overide:
            if self.gui_overide.status == GUIReturnType.CONTINUE:
                return
            
            if self.gui_overide.status == GUIReturnType.LEAVE:
                self.generate_board()
                self.gui_overide = None
            
            if isinstance(self.gui_overide, PromoteGUI):
                piece_class = None
                if self.gui_overide.status == GUIReturnType.LEAVE_QUEEN:
                    piece_class = Queen
                elif self.gui_overide.status == GUIReturnType.LEAVE_KNIGHT:
                    piece_class = Knight
                elif self.gui_overide.status == GUIReturnType.LEAVE_ROOK:
                    piece_class = Rook
                elif self.gui_overide.status == GUIReturnType.LEAVE_BISHOP:
                    piece_class = Bishop

                self.promote_piece(self.gui_overide.piece, piece_class)
                sounds["promote"].play()

                self.gui_overide = None

        mouse_pos = pygame.mouse.get_pos()
        hover_index = pygame.Vector2(mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE)
        hover_piece = self.piece_at(hover_index)
        if hover_piece != None and hover_piece.team == self.current_team:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def render(self) -> None:
        self.screen.blit(self.board_image, (0, 0))

        if self.selected != None:
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            overlay.fill((255, 255, 0))
            overlay.set_alpha(50)
            self.screen.blit(overlay, (self.selected.x * SQUARE_SIZE, self.selected.y * SQUARE_SIZE))

        for y, row in enumerate(self.board):
            for x, piece in enumerate(row):
                if piece:
                    self.screen.blit(piece.image, (x * SQUARE_SIZE, y * SQUARE_SIZE))

        if self.selected != None:
            selected_piece = self.piece_at(self.selected)
            if selected_piece:
                for move in selected_piece.get_valid_moves(check_check = True):
                    if move.promotion and move.promotion != Queen:
                            continue
                    if move.is_on_enemy(self, selected_piece.team):
                        self.screen.blit(icons["ring_hover"], (move.new_index.x * SQUARE_SIZE, move.new_index.y * SQUARE_SIZE))
                    else:
                        nasty_constant = SQUARE_SIZE // 2 - icons["circle_hover"].get_width() // 2
                        self.screen.blit(icons["circle_hover"], (move.new_index.x * SQUARE_SIZE + nasty_constant, move.new_index.y * SQUARE_SIZE + nasty_constant))
                        if move.castle:
                            self.screen.blit(icons["ring_hover"], (move.castle.old_pos.x * SQUARE_SIZE, move.castle.old_pos.y * SQUARE_SIZE ))

        if self.gui_overide:
            self.gui_overide.render()

class Computer():
    def __init__(self, team, board: Board):
        self.team = team
        self.board = board

    def make_move(self):
        raise NotImplementedError()

class RandomComputer(Computer):
    def make_move(self):
        random_piece = random.choice(self.board.get_pieces_with_valid_move(self.team))
        random_move = random.choice(random_piece.get_valid_moves())
        self.board.move_piece(random_piece.position, random_move)

class ComputerController():
    def __init__(self, delay, board: Board, moves_per_computation = 1):
        self.delay = delay
        self.moves_per_computation = moves_per_computation
        self.timer = 0
        self.board = board

        self.computers = {
            Team.BLACK: RandomComputer(Team.BLACK, self.board),
            Team.WHITE: None,
        }

        if self.moves_per_computation / self.delay > 2:
            self.board.overide_sounds = True

    def update(self):
        self.timer += 1
        if self.timer > self.delay and not isinstance(self.board.gui_overide, GameOver):
            for _ in range(self.moves_per_computation):
                if self.board.gui_overide == None:
                    if self.computers[self.board.current_team]:
                        self.computers[self.board.current_team].make_move()
            self.timer = 0

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Chess")
    pygame.mixer.set_num_channels(64)
    clock = pygame.time.Clock()

    for fn in os.listdir("assets\\image"):
        piece_images[fn.removesuffix(".png")] = pygame.transform.smoothscale(pygame.image.load("assets\\image\\" + fn).convert_alpha(), (SQUARE_SIZE, SQUARE_SIZE))

    pygame.display.set_icon(piece_images["bp"])

    # icons["circle_hover"] = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    # pygame.draw.circle(icons["circle_hover"], (0, 0, 0), (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 4)
    icons["circle_hover"] = pygame.transform.smoothscale(pygame.image.load("assets\\image\\circle.png").convert_alpha(), (SQUARE_SIZE // 2.5, SQUARE_SIZE // 2.5))
    icons["circle_hover"].set_alpha(30)

    icons["ring_hover"] = pygame.transform.smoothscale(pygame.image.load("assets\\image\\ring.png").convert_alpha(), (SQUARE_SIZE, SQUARE_SIZE))
    icons["ring_hover"].set_alpha(30)

    icons["medal_icon"] = pygame.image.load("assets\\image\\medal.png").convert_alpha()
    icons["draw_icon"] = pygame.image.load("assets\\image\\handshake.png").convert_alpha()

    board = Board(screen)
    computers = ComputerController(delay = 1, board = board, moves_per_computation = 1)

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.on_mouse_down()
            if event.type == pygame.KEYDOWN:
                board.on_key_down(event.key)

        board.update()
        computers.update()

        screen.fill((0, 0, 0))
        board.render()

        pygame.display.update()
        # print(clock.get_fps())
            
    pygame.quit()

if __name__ == "__main__":
    main()










































