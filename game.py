import random

class Backgammon:
    def __init__(self):
        self.board = self.initialize_board()
        self.dice = (0, 0)
        self.current_player = 1 # 1 for white, -1 for black
        self.game_over = False
        self.bar_white = 0 # jail
        self.bar_black = 0
        self.moves_remaining = []
        self.borne_off_white = 0
        self.borne_off_black = 0
        self.ai_move_fn = None # current AI agent playing


    def initialize_board(self):
        """
        init the backgammon board state.
        24 points (locations on the board)
        each point contains a list of checkers (positive for user, negative for AI agent)
        the amount is how many pips are in that location
        """
        board = [0] * 24
        board[0] = 2
        board[5] = -5
        board[7] = -3
        board[11] = 5
        board[12] = -5
        board[16] = 3
        board[18] = 5
        board[23] = -2


        # tester end game
        # board[18] = 1
        # board[19] = 3
        # board[20] = 3
        # board[21] = 3

 

        # board[3] = -3
        # board[4] = -2
        # board[6] = -1
        return board
    
    def ai_move(self, delay: float = 1.0):
        """
        used for the different agents to move
        """
        if not self.ai_move_fn:
            return self.get_board_state()
        return self.ai_move_fn(self, delay)

    def roll_dice(self):
        """
        rolls two dice, sets the dice attribute and the moves_remaining based on the roll.
        """
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        self.dice = (die1, die2)
        
        # if doubles are rolled, the player gets four moves.
        if die1 == die2:
            self.moves_remaining = [die1] * 4
        else:
            self.moves_remaining = [die1, die2]
        
        return self.dice

    def is_valid_move(self, start, end):
        """
        checks if a move is valid based on the rules of backgammon and movement direction.
        """
        # check bounds
        if start < 0 or start >= 24 or end < 0 or end >= 24:
            return False

        # there must be a pip at the starting point.
        if self.board[start] == 0:
            return False

        # makes sure that the pip belongs to the current player.
        if (self.board[start] > 0 and self.current_player == -1) or (self.board[start] < 0 and self.current_player == 1):
            return False

        # enforce movement direction:
        if self.current_player == 1 and end <= start:
            return False
        if self.current_player == -1 and end >= start:
            return False

        # check destination occupancy:
        # if more than one, invalid move. 
        if self.board[end] < -1 and self.current_player == 1:
            return False
        if self.board[end] > 1 and self.current_player == -1:
            return False
        return True

    def make_move(self, start, end):
        """
        executes a move if it's legal by checking if (start, end) exists in get_all_available_moves().
        removes the corresponding dice value and updates the board state.
        """
        # get a list of legal moves
        available_moves = self.get_all_available_moves()
        
        # check if move is in legal moves
        move = None
        for m in available_moves:
            if m[0] == start and m[1] == end:
                move = m
                break
        if move is None:
            return False
        
        # get the required dice value and move type from the move tuple
        d = move[2]
        move_type = move[3]
        
        # execute based on move type:
        if move_type == "re-entry":
            # for white re entry: start should be -1, destination between 0-5.
            if self.current_player == 1:
                if self.board[end] < 0:
                    self.board[end] = 0
                    self.bar_black += 1
                self.board[end] += 1
                self.bar_white -= 1
            # For black re entry: start should be 24, destination between 18-23.
            else:
                if self.board[end] > 0:
                    self.board[end] = 0
                    self.bar_white += 1
                self.board[end] += -1
                self.bar_black -= 1
            self.moves_remaining.remove(d)
        
        elif move_type == "bear_off":
            # bearing off: remove checker from board and increment borne-off counter.
            if self.current_player == 1:
                self.board[start] -= 1
                self.borne_off_white += 1
            else:
                self.board[start] += 1
                self.borne_off_black += 1
            self.moves_remaining.remove(d)
        
        elif move_type == "normal":
            # normal moves: update board positions and handle hitting if needed.
            piece = 1 if self.current_player == 1 else -1
            if self.current_player == 1 and self.board[end] == -1:
                self.board[end] = 0
                self.bar_black += 1
            elif self.current_player == -1 and self.board[end] == 1:
                self.board[end] = 0
                self.bar_white += 1
            self.board[end] += piece
            self.board[start] -= piece
            self.moves_remaining.remove(d)
        
        # check for game over.
        winner = self.check_game_over()
        if winner:
            self.game_over = winner


        # if no moves remain or no legal moves exist, switch turn and roll new dice.
        if not self.moves_remaining or not self.can_make_any_move():
            self.current_player *= -1
            self.roll_dice()

        return True


    def check_game_over(self):
        """
        checks if a player won the game and returns 1 is white wins or -1 if black wins or false if game is not over
        """
        player1_checkers = sum(1 for i in self.board if i > 0)
        player2_checkers = sum(1 for i in self.board if i < 0)
        if player1_checkers == 0:
            return 1
        elif player2_checkers == 0:
            return -1
        return False


    def get_board_state(self):
        """
        return board state
        """
        # if the game is not over and the current player has no legal moves,
        # automatically switch turns and roll new dice.
        if not self.game_over and not self.can_make_any_move():
            self.current_player *= -1
            self.roll_dice()
        return {
            "board": self.board,
            "dice": self.dice,
            "moves_remaining": self.moves_remaining,
            "current_player": self.current_player,
            "game_over": self.game_over,
            "bar_white": self.bar_white,
            "bar_black": self.bar_black,
            "borne_off_white": self.borne_off_white,
            "borne_off_black": self.borne_off_black,
            "all_in_home": self.all_in_home(),
            "all_moves": self.get_all_available_moves()
        }
    
    def can_make_any_move(self):
        """
        returns true if can make any move or false if otherwise
        """
        return len(self.get_all_available_moves()) > 0


    def all_in_home(self):
        """
        returns true if all pips for the player are in his home
        """
        if self.current_player == 1:
            for i in range(24):
                if self.board[i] > 0 and not (18 <= i <= 23):
                    return False
            if self.bar_white > 0:
                return False
        else:
            for i in range(24):
                if self.board[i] < 0 and not (0 <= i <= 5):
                    return False
            if self.bar_black > 0:
                return False
        return True

    def get_all_available_moves(self):
        """
        returns a list of all available moves for the current player.
        tuples: (start, end, dice_value, move_type)
        where move_type is "re-entry", "normal", or "bear_off".
        """
        moves = []

        # re entry moves:
        if self.current_player == 1 and self.bar_white > 0:
            for end in range(0, 6):
                d = end + 1
                if d in self.moves_remaining and self.board[end] >= -1:
                    moves.append((-1, end, d, "re-entry"))
        elif self.current_player == -1 and self.bar_black > 0:
            for end in range(18, 24):
                d = 24 - end
                if d in self.moves_remaining and self.board[end] <= 1:
                    moves.append((24, end, d, "re-entry"))

        # normal moves:
        if (self.current_player == 1 and self.bar_white == 0) or (self.current_player == -1 and self.bar_black == 0):
            for start in range(24):
                if self.current_player == 1 and self.board[start] <= 0:
                    continue
                if self.current_player == -1 and self.board[start] >= 0:
                    continue
                for d in self.moves_remaining:
                    if self.current_player == 1:
                        end = start + d
                    else:
                        end = start - d
                    if 0 <= end < 24 and self.is_valid_move(start, end):
                        moves.append((start, end, d, "normal"))
        
        # bearing Off moves:
        if self.all_in_home():
            if self.current_player == 1:
                white_home = [i for i in range(18, 24) if self.board[i] > 0]
                furthest = min(white_home) if white_home else None
                for start in range(18, 24):
                    if self.board[start] <= 0:
                        continue
                    required = 24 - start
                    if required in self.moves_remaining:
                        moves.append((start, 24, required, "bear_off"))
                    else:
                        higher_options = [d for d in self.moves_remaining if d > required]
                        if higher_options and furthest is not None and start == furthest:
                            d = min(higher_options)
                            moves.append((start, 24, d, "bear_off"))
            elif self.current_player == -1:
                black_home = [i for i in range(0, 6) if self.board[i] < 0]
                furthest = max(black_home) if black_home else None
                for start in range(0, 6):
                    if self.board[start] >= 0:
                        continue
                    required = start + 1
                    if required in self.moves_remaining:
                        moves.append((start, -1, required, "bear_off"))
                    else:
                        higher_options = [d for d in self.moves_remaining if d > required]
                        if higher_options and furthest is not None and start == furthest:
                            d = min(higher_options)
                            moves.append((start, -1, d, "bear_off"))
        
        return moves
