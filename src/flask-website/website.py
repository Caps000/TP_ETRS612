from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
# Crucial pour utiliser flash()
app.secret_key = "cle_secrete_pour_le_tp"

API_URL = "http://127.0.0.1:5001/config"

def fetch_from_api(endpoint):
    try:
        r = requests.get(f"{API_URL}/{endpoint}")
        return r.json() if r.status_code == 200 else []
    except: return []

@app.route("/")
def start(): return render_template('start.html')

# --- WEB SERVERS ---
@app.route("/ws/list")
def list_ws(): return render_template('list_ws.html', serveurs=fetch_from_api('ws'))

@app.route("/ws/create", methods=['GET', 'POST'])
def create_ws():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        port = request.form.get('port', '')
        root = request.form.get('root', '').strip()

        if not name or not port or not root:
            flash("Erreur : Tous les champs sont obligatoires.", "danger")
            return render_template('create_ws.html')
        
        try:
            port_val = int(port)
            if port_val < 1 or port_val > 65535:
                flash("Erreur : Le port doit être entre 1 et 65535.", "warning")
                return render_template('create_ws.html')
        except:
            flash("Erreur : Le port doit être un nombre.", "warning")
            return render_template('create_ws.html')

        requests.post(f"{API_URL}/ws", json={"server_name": name, "port": port_val, "root": root})
        flash(f"Serveur {name} créé !", "success")
        return redirect(url_for('list_ws'))
    return render_template('create_ws.html')

# --- REVERSE PROXIES ---
@app.route("/rp/list")
def list_rp(): return render_template('list_rp.html', proxies=fetch_from_api('rp'))

@app.route("/rp/create", methods=['GET', 'POST'])
def create_rp():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        target = request.form.get('target', '').strip()

        if not name or not target:
            flash("Erreur : Nom et Cible requis.", "danger")
            return render_template('create_rp.html')

        requests.post(f"{API_URL}/rp", json={"name": name, "target": target})
        flash(f"Proxy {name} créé !", "success")
        return redirect(url_for('list_rp'))
    return render_template('create_rp.html')

# --- LOAD BALANCERS ---
@app.route("/lb/list")
def list_lb(): return render_template('list_lb.html', lbs=fetch_from_api('lb'))

@app.route("/lb/create", methods=['GET', 'POST'])
def create_lb():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        backends = request.form.get('backends', '').strip()

        if not name or not backends:
            flash("Erreur : Nom et Backends requis.", "danger")
            return render_template('create_lb.html')

        requests.post(f"{API_URL}/lb", json={"name": name, "backends": backends})
        flash(f"Load Balancer {name} créé !", "success")
        return redirect(url_for('list_lb'))
    return render_template('create_lb.html')

# --- SUPPRESSIONS ---
@app.route("/ws/delete/<int:id>")
def delete_ws_action(id):
    requests.delete(f"{API_URL}/ws/{id}")
    flash("Serveur supprimé.", "info")
    return redirect(url_for('list_ws'))

@app.route("/rp/delete/<int:id>")
def delete_rp_action(id):
    requests.delete(f"{API_URL}/rp/{id}")
    flash("Proxy supprimé.", "info")
    return redirect(url_for('list_rp'))

@app.route("/lb/delete/<int:id>")
def delete_lb_action(id):
    requests.delete(f"{API_URL}/lb/{id}")
    flash("Load Balancer supprimé.", "info")
    return redirect(url_for('list_lb'))

@app.route("/ws/<int:id>")
def detail_ws(id): return render_template('detail_ws.html', id=id)
@app.route("/rp/<int:id>")
def detail_rp(id): return render_template('detail_rp.html', id=id)
@app.route("/lb/<int:id>")
def detail_lb(id): return render_template('detail_lb.html', id=id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)