from flask import Flask, render_template, request

app = Flask(__name__)

xstate = [0] * 9
ystate = [0] * 9
turn = 1  # 1 for X, 0 for O

def sum(a, b, c):
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
        if sum(xstate[win[0]], xstate[win[1]], xstate[win[2]]) == 3:
            return "X won the match"
        if sum(ystate[win[0]], ystate[win[1]], ystate[win[2]]) == 3:
            return "O won the match"
    return None

@app.route('/')
def index():
    board = printBoard(xstate, ystate)
    return render_template('index.html', board=board, turn=turn)

@app.route('/move', methods=['POST'])
def move():
    global turn
    value = int(request.form['cell'])

    if turn == 1:
        xstate[value] = 1
    else:
        ystate[value] = 1
    
    winner = checkwin(xstate, ystate)
    if winner:
        return f"<h1>{winner}</h1><br><a href='/reset'>Play Again</a>"
    
    turn = 1 - turn
    return index()

@app.route('/reset')
def reset():
    global xstate, ystate, turn
    xstate = [0] * 9
    ystate = [0] * 9
    turn = 1
    return index()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
