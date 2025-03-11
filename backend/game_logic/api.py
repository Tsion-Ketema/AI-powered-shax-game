from flask import Flask, request, jsonify


from backend.game_logic.game_state import GameState

app = Flask(__name__)

game = GameState()

@app.route('/place', methods=['POST'])
def place():
    place_request = request.json
    result = game.place_piece(place_request.position, place_request.player)
    return jsonify({"status": result.status, "board": game.board})


@app.route('/move', methods=['POST'])
def move():
    move_request = request.json
    result = game.move_piece(move_request.from_pos, move_request.to_pos, move_request.player)
    return jsonify({"status": result.status, "board": game.board})


@app.route('/getMoves', methods=['POST'])
def get_moves():
    move_request = request.json
    result = game.get_valid_move_player(move_request.player)
    return jsonify({"status": result.status, "board": game.board})

@app.route('/getGameState', methods=['GET'])
def get_game_state():
    status, result = game.get_game_state()
    # return jsonify({"status": status, "board": jsonify(result.board)})
    return jsonify({"status": status, "board": "it worked!!"})


@app.route('/capture', methods=['POST'])
def capture():
    capture_request = request.json
    result = game.capture(capture_request.pos, capture_request.player)
    return jsonify({"status": result.status, "board": game.board})


@app.route('/reset', methods=['POST'])
def reset():
    result = game.reset()
    return jsonify({"status": True, "game": result})

if __name__ == '__main__':
    app.run(debug=True)

