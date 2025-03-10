from flask import Flask, request, jsonify


from game_logic.game_state import GameState

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


@app.route('/capture', methods=['POST'])
def capture():
    capture_request = request.json
    result = game.move_piece(capture_request.mill, capture_request.pos, capture_request.player)
    return jsonify({"status": result.status, "board": game.board})


@app.route('/reset', methods=['POST'])
def reset():
    game.reset()
    pass

if __name__ == '__main__':
    app.run(debug=True)

