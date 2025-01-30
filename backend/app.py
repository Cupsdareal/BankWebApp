from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modèle utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Float, default=0.0)

# Modèle transaction
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
# Initialisation de la base de données
def init_db():
    db.create_all()
    print("Base de données initialisée")

# Route pour inscription
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur enregistré avec succès'})

# Route pour connexion
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Connexion réussie'})
    return jsonify({'message': 'Échec de connexion'}), 401

# Route pour consulter le solde
@app.route('/balance/<username>', methods=['GET'])
def get_balance(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'balance': user.balance})
    return jsonify({'message': 'Utilisateur introuvable'}), 404

# Route pour transfert d'argent
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    sender = User.query.filter_by(username=data['sender']).first()
    receiver = User.query.filter_by(username=data['receiver']).first()
    amount = data['amount']
    
    if sender and receiver and sender.balance >= amount:
        sender.balance -= amount
        receiver.balance += amount
        transaction = Transaction(sender_id=sender.id, receiver_id=receiver.id, amount=amount)
        db.session.add(transaction)
        db.session.commit()
        return jsonify({'message': 'Transfert réussi'})
    return jsonify({'message': 'Fonds insuffisants ou utilisateur introuvable'}), 400

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
