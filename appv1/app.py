from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test_post():
    data = request.json  # Recebe os dados no formato JSON
    response = {
        "message": "Dados recebidos com sucesso!",
        "data": data
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(debug=True)
