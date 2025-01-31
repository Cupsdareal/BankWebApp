from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'  # Clé secrète pour JWT

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

# Décorateur pour vérifier le token JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'message': 'Token manquant'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token invalide'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Route pour inscription
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Utilisateur déjà existant'}), 400
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
        token = jwt.encode({'user_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, 
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': 'Échec de connexion'}), 401

# Route pour consulter le solde
@app.route('/balance', methods=['GET'])
@token_required
def get_balance(current_user):
    return jsonify({'balance': current_user.balance})

# Route pour transfert d'argent
@app.route('/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    data = request.json
    receiver = User.query.filter_by(username=data['receiver']).first()
    amount = data['amount']
    
    if not receiver:
        return jsonify({'message': 'Destinataire introuvable'}), 404
    
    if current_user.balance < amount:
        return jsonify({'message': 'Fonds insuffisants'}), 400
    
    current_user.balance -= amount
    receiver.balance += amount
    transaction = Transaction(sender_id=current_user.id, receiver_id=receiver.id, amount=amount)
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Transfert réussi'})

# Route pour historique de transactions
@app.route('/transactions', methods=['GET'])
@token_required
def get_transactions(current_user):
    transactions_sent = Transaction.query.filter_by(sender_id=current_user.id).all()
    transactions_received = Transaction.query.filter_by(receiver_id=current_user.id).all()

    transactions = [
        {"type": "sent", "receiver": User.query.get(t.receiver_id).username, "amount": t.amount}
        for t in transactions_sent
    ] + [
        {"type": "received", "sender": User.query.get(t.sender_id).username, "amount": t.amount}
        for t in transactions_received
    ]

    return jsonify({"transactions": transactions})

# Route pour dépôt d'argent
@app.route('/deposit', methods=['POST'])
@token_required
def deposit(current_user):
    data = request.json
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"message": "Montant invalide"}), 400

    current_user.balance += amount
    db.session.commit()
    return jsonify({"message": f"Dépôt de {amount} réussi", "new_balance": current_user.balance})

# Route pour retrait d'argent
@app.route('/withdraw', methods=['POST'])
@token_required
def withdraw(current_user):
    data = request.json
    amount = data.get("amount")

    if amount is None or amount <= 0:
        return jsonify({"message": "Montant invalide"}), 400

    if current_user.balance < amount:
        return jsonify({"message": "Fonds insuffisants"}), 400

    current_user.balance -= amount
    db.session.commit()
    return jsonify({"message": f"Retrait de {amount} réussi", "new_balance": current_user.balance})

# Route pour suppression de compte
@app.route('/delete_account', methods=['DELETE'])
@token_required
def delete_account(current_user):
    db.session.delete(current_user)
    db.session.commit()
    return jsonify({"message": "Compte supprimé avec succès"})

# Route pour màj de mot de passe
@app.route('/update_password', methods=['PUT'])
@token_required
def update_password(current_user):
    data = request.json
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not check_password_hash(current_user.password, old_password):
        return jsonify({"message": "Ancien mot de passe incorrect"}), 401

    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    return jsonify({"message": "Mot de passe mis à jour avec succès"})


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
