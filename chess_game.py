import sys
import math
import pygame
import chess

# --- Config ---
WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8
FPS = 30

# Colors
LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
LAST_MOVE = (186, 202, 68)

# Piece values
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


def evaluate_board(board: chess.Board) -> int:
    """Simple material evaluation from White's perspective."""
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * (
            len(board.pieces(piece_type, chess.WHITE))
            - len(board.pieces(piece_type, chess.BLACK))
        )
    return score if board.turn == chess.WHITE else -score


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing:
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
            if eval_score > alpha:
                alpha = eval_score
            if beta <= alpha:
                break
        return int(max_eval)
    else:
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
            if eval_score < beta:
                beta = eval_score
            if beta <= alpha:
                break
        return int(min_eval)


def get_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    best_move: chess.Move | None = None
    best_value = -math.inf
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, -math.inf, math.inf, False)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move


# --- Rendering ---

def draw_board(screen: pygame.Surface) -> None:
    colors = [LIGHT, DARK]
    for r in range(8):
        for c in range(8):
            pygame.draw.rect(
                screen,
                colors[(r + c) % 2],
                pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
            )


def draw_last_move(screen: pygame.Surface, board: chess.Board) -> None:
    if len(board.move_stack) == 0:
        return
    last = board.peek()
    for square in [last.from_square, last.to_square]:
        file = chess.square_file(square)
        rank = 7 - chess.square_rank(square)
        pygame.draw.rect(
            screen,
            LAST_MOVE,
            pygame.Rect(file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE),
        )


def draw_pieces(screen: pygame.Surface, board: chess.Board, font: pygame.font.Font) -> None:
    # Draw using Unicode characters
    for r in range(8):
        for c in range(8):
            square = chess.square(c, 7 - r)
            piece = board.piece_at(square)
            if not piece:
                continue
            char = piece.unicode_symbol(invert_color=False)
            color = (10, 10, 10) if piece.color == chess.BLACK else (245, 245, 245)
            text = font.render(char, True, color)
            text_rect = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
            screen.blit(text, text_rect)


# --- Game loop ---

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cờ vua - Minimax AI")
    clock = pygame.time.Clock()

    # Choose a large Unicode font that has chess glyphs
    font_size = int(SQ_SIZE * 0.9)
    font = pygame.font.SysFont("DejaVu Sans", font_size, bold=True)

    board = chess.Board()
    running = True
    selected_square: int | None = None
    player_color = chess.WHITE
    ai_depth = 2

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if board.turn == player_color and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                col = x // SQ_SIZE
                row = 7 - (y // SQ_SIZE)
                square = chess.square(col, row)

                if selected_square is None:
                    piece = board.piece_at(square)
                    if piece and piece.color == player_color:
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None

        # AI move
        if not board.turn == player_color and not board.is_game_over():
            pygame.display.set_caption("Cờ vua - AI đang suy nghĩ...")
            ai_move = get_best_move(board, ai_depth)
            if ai_move is not None:
                board.push(ai_move)
            pygame.display.set_caption("Cờ vua - Lượt của bạn")

        # Draw
        draw_board(screen)
        draw_last_move(screen, board)
        if selected_square is not None:
            c = chess.square_file(selected_square)
            r = 7 - chess.square_rank(selected_square)
            pygame.draw.rect(
                screen,
                HIGHLIGHT,
                pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE),
                5,
            )
        draw_pieces(screen, board, font)
        pygame.display.flip()

        # End detection
        if board.is_game_over():
            result = board.result()
            print("Trò chơi kết thúc:", result)
            pygame.time.wait(1500)
            running = False

        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
