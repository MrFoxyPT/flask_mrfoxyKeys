from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    desenvolvedor = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    chaves = db.relationship('Chave', backref='item', lazy=True)

class Chave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(50), unique=True, nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

class Utilizador(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Carrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilizador_id = db.Column(db.Integer, db.ForeignKey('utilizador.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    data_adicionado = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utilizador = db.relationship('Utilizador', backref='carrinho_itens')
    item = db.relationship('Item')

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    utilizador_id = db.Column(db.Integer, db.ForeignKey('utilizador.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    chave_id = db.Column(db.Integer, db.ForeignKey('chave.id'), nullable=False)
    preco_pago = db.Column(db.Float, nullable=False)
    data_compra = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    utilizador = db.relationship('Utilizador', backref='compras')
    item = db.relationship('Item')
    chave = db.relationship('Chave')
    
    
