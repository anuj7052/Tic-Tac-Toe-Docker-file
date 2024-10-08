from flask import Flask, render_template, request,redirect,url_for
import sqlite3

app = Flask(__name__)

xstate = [0] * 9
ystate = [0] * 9
turn = 1  # 1 for X, 0 for O
moves_log = []  # Log of all moves

# Database setup
def init_db():
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moves TEXT,
            winner TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Utility functions
def sum_three(a, b, c):
    return a + b + c

def printBoard(xstate, ystate):
    board = []
    for i in range(9):
        if xstate[i]:
            board.append('X')
        elif ystate[i]:
            board.append('O')
        else:
            board.append(i)
    return board

def checkwin(xstate, ystate):
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]
    for win in wins:
        if sum_three(xstate[win[0]], xstate[win[1]], xstate[win[2]]) == 3:
            return "X won the match"
        if sum_three(ystate[win[0]], ystate[win[1]], ystate[win[2]]) == 3:
            return "O won the match"
    return None

def is_draw(xstate, ystate):
    return sum(xstate) + sum(ystate) == 9

# Minimax Algorithm for AI Moves
def minimax(board, depth, is_maximizing, xstate, ystate):
    winner = checkwin(xstate, ystate)
    if winner:
        return 1 if winner == "X won the match" else -1
    if is_draw(xstate, ystate):
        return 0
    
    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if xstate[i] == 0 and ystate[i] == 0:
                xstate[i] = 1
                score = minimax(board, depth + 1, False, xstate, ystate)
                xstate[i] = 0
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if xstate[i] == 0 and ystate[i] == 0:
                ystate[i] = 1
                score = minimax(board, depth + 1, True, xstate, ystate)
                ystate[i] = 0
                best_score = min(score, best_score)
        return best_score

# AI's Recommended Move
def recommend_move(board, xstate, ystate):
    best_move = None
    best_score = -float('inf') if turn == 1 else float('inf')
    
    for i in range(9):
        if xstate[i] == 0 and ystate[i] == 0:  # Empty cell
            if turn == 1:
                xstate[i] = 1
                score = minimax(board, 0, False, xstate, ystate)
                xstate[i] = 0
                if score > best_score:
                    best_score = score
                    best_move = i
            else:
                ystate[i] = 1
                score = minimax(board, 0, True, xstate, ystate)
                ystate[i] = 0
                if score < best_score:
                    best_score = score
                    best_move = i
    return best_move

# Save game to the database
def save_game(moves, winner):
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO games (moves, winner) VALUES (?, ?)', (str(moves), winner))
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    board = printBoard(xstate, ystate)
    return render_template('index.html', board=board, turn=turn, moves_log=moves_log, move_message=None, winner=None)

@app.route('/move', methods=['POST'])
def move():
    global turn, moves_log
    value = int(request.form['cell'])  # Get the clicked cell value

    if xstate[value] or ystate[value]:  # Prevent moving in the same spot twice
        move_message = "Cell already booked!"
        board = printBoard(xstate, ystate)
        return render_template('index.html', board=board, turn=turn, move_message=move_message, moves_log=moves_log)

    if turn == 1:
        xstate[value] = 1
        move_message = f"X clicked {value}"
    else:
        ystate[value] = 1
        move_message = f"O clicked {value}"
    
    moves_log.append(move_message)  # Append the move to the log

    winner = checkwin(xstate, ystate)
    board = printBoard(xstate, ystate)

    if winner:
        save_game(moves_log, winner)
        return render_template('index.html', board=board, winner=winner, move_message=move_message, moves_log=moves_log, game_over=True)
    
    if is_draw(xstate, ystate):
        save_game(moves_log, "It's a draw!")
        return render_template('index.html', board=board, winner="It's a draw!", move_message=move_message, moves_log=moves_log, game_over=True)

    # AI recommendation
    ai_suggested_move = recommend_move(board, xstate, ystate)
    if ai_suggested_move is not None:
        ai_message = f"AI suggests moving to {ai_suggested_move}"
    else:
        ai_message = "AI could not suggest a move."

    turn = 1 - turn  # Switch turn
    return render_template('index.html', board=board, turn=turn, move_message=move_message, ai_message=ai_message, moves_log=moves_log, game_over=False)

@app.route('/history')
def history():
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM games')
    games = cursor.fetchall()
    conn.close()
    return render_template('history.html', games=games)

def reset_game_history():
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM games')  # This deletes all records from the games table
    conn.commit()
    conn.close()
    
@app.route('/reset')
def reset():
    global xstate, ystate, turn, moves_log
    # Reset the in-memory game state
    xstate = [0] * 9
    ystate = [0] * 9
    turn = 1
    moves_log = []  # Reset the log

    # Reset the game history in the database
    reset_game_history()  # Clear the saved game moves and winner

    return redirect(url_for('index'))


# @app.route('/reset')
# def reset():
#     global xstate, ystate, turn, moves_log
#     xstate = [0] * 9
#     ystate = [0] * 9
#     turn = 1
#     moves_log = []  # Reset the log
#     # return index()
#     return redirect(url_for('history'))

if __name__ == "__main__":
    init_db()  # Initialize the database when the app starts
    app.run(host='0.0.0.0', port=5000)



