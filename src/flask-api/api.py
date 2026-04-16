from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

WS_FILE = os.path.join(DATA_DIR, 'webserver.json')
RP_FILE = os.path.join(DATA_DIR, 'reverseproxy.json')
LB_FILE = os.path.join(DATA_DIR, 'loadbalancer.json')

def read_json(filepath):
    if not os.path.exists(filepath): return []
    with open(filepath, 'r') as f: return json.load(f)

def write_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f: json.dump(data, f, indent=4)

# --- GÉNÉRATEUR DE ROUTES (pour éviter de répéter 3 fois le code) ---
def get_routes(type_name, filepath):
    @app.route(f'/config/{type_name}', methods=['GET'], endpoint=f'get_all_{type_name}')
    def get_all():
        return jsonify(read_json(filepath)), 200

    @app.route(f'/config/{type_name}/<int:id>', methods=['GET'], endpoint=f'get_{type_name}')
    def get_one(id):
        data = read_json(filepath)
        item = next((i for i in data if i.get('id') == id), None)
        return jsonify(item), 200 if item else 404

    @app.route(f'/config/{type_name}', methods=['POST'], endpoint=f'create_{type_name}')
    def create():
        item = request.json
        data = read_json(filepath)
        item['id'] = 1 if not data else max(i.get('id', 0) for i in data) + 1
        data.append(item)
        write_json(filepath, data)
        return jsonify(item), 201

    @app.route(f'/config/{type_name}/<int:id>', methods=['DELETE'], endpoint=f'delete_{type_name}')
    def delete(id):
        data = read_json(filepath)
        new_data = [i for i in data if i.get('id') != id]
        write_json(filepath, new_data)
        return jsonify({"message": "Supprimé"}), 200

# Activation des routes pour les 3 types
get_routes('ws', WS_FILE)
get_routes('rp', RP_FILE)
get_routes('lb', LB_FILE)

if __name__ == '__main__':
    app.run(debug=True, port=5001)