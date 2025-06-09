from flask import Flask, flash, render_template, redirect, url_for, request, flash
from models import db, Item, Utilizador, Carrinho, Compra, Chave
from forms import ItemForm, LoginForm, RegistoForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.secret_key = 'foxyclub3dlol'
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Utilizador.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Acesso restrito a administradores.", "erro")
            return redirect(url_for('listar'))
        return f(*args, **kwargs)
    return decorated_function

# Criar a Base de dados
@app.before_request
def criar_bd():
    db.create_all()

@app.route('/')
def index():
    return redirect(url_for('listar'))

@app.route('/loja')
def listar():
    itens = Item.query.all()
    carrinho_count = Carrinho.query.filter_by(utilizador_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('lista.html', itens=itens, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/loja/adicionar', methods=['GET', 'POST'])
@login_required
@admin_required
def adicionar():
    form = ItemForm()
    try:
        if form.validate_on_submit():
            item = Item(
                nome=form.nome.data,
                desenvolvedor=form.desenvolvedor.data,
                ano=form.ano.data,
                preco=form.preco.data
            )
            db.session.add(item)
            db.session.flush()
            chaves = form.chaves.data.strip().splitlines()
            for chave_valor in chaves:
                if chave_valor.strip():
                    chave = Chave(chave=chave_valor.strip(), item_id=item.id)
                    db.session.add(chave)
            db.session.commit()
            flash("Item e chaves adicionados com sucesso!", "sucesso")
            return redirect(url_for('listar'))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar item: {str(e)}", "erro")
    carrinho_count = Carrinho.query.filter_by(utilizador_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('adicionar.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/loja/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(id):
    item = Item.query.get_or_404(id)
    form = ItemForm(obj=item, chaves='\n'.join([chave.chave for chave in item.chaves]))
    if form.validate_on_submit():
        try:
            item.nome = form.nome.data
            item.desenvolvedor = form.desenvolvedor.data
            item.ano = form.ano.data
            item.preco = form.preco.data
            Chave.query.filter_by(item_id=item.id).delete()
            chaves = form.chaves.data.strip().splitlines()
            for chave_valor in chaves:
                if chave_valor.strip():
                    chave = Chave(chave=chave_valor.strip(), item_id=item.id)
                    db.session.add(chave)
            db.session.commit()
            flash("Item e chaves atualizados com sucesso!", "sucesso")
            return redirect(url_for('listar'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar item: {str(e)}", "erro")
            return render_template('editar.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=Carrinho.query.filter_by(utilizador_id=current_user.id).count())
    carrinho_count = Carrinho.query.filter_by(utilizador_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('editar.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/loja/apagar/<int:id>')
@login_required
@admin_required
def apagar(id):
    try:
        item = Item.query.get_or_404(id)
        for chave in item.chaves:
            db.session.delete(chave)
        db.session.delete(item)
        db.session.commit()
        flash("Item removido com sucesso!", "sucesso")
        return redirect(url_for('listar'))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao remover item: {str(e)}", "erro")
        return redirect(url_for('listar'))

@app.route('/loja/adicionar_carrinho/<int:id>')
@login_required
def adicionar_carrinho(id):
    item = Item.query.get_or_404(id)
    if not Chave.query.filter_by(item_id=id, disponivel=True).first():
        flash("Nenhuma chave disponível para este item.", "erro")
        return redirect(url_for('listar'))
    if Carrinho.query.filter_by(utilizador_id=current_user.id, item_id=id).first():
        flash("Item já está no carrinho.", "erro")
        return redirect(url_for('listar'))
    carrinho = Carrinho(utilizador_id=current_user.id, item_id=id)
    db.session.add(carrinho)
    db.session.commit()
    flash("Item adicionado ao carrinho!", "sucesso")
    return redirect(url_for('listar'))

@app.route('/loja/carrinho')
@login_required
def carrinho():
    itens_carrinho = Carrinho.query.filter_by(utilizador_id=current_user.id).all()
    total = sum(item.item.preco for item in itens_carrinho)
    carrinho_count = len(itens_carrinho)
    return render_template('carrinho.html', itens_carrinho=itens_carrinho, total=total, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/loja/remover_carrinho/<int:id>')
@login_required
def remover_carrinho(id):
    carrinho = Carrinho.query.filter_by(utilizador_id=current_user.id, item_id=id).first_or_404()
    db.session.delete(carrinho)
    db.session.commit()
    flash("Item removido do carrinho.", "sucesso")
    return redirect(url_for('carrinho'))

@app.route('/loja/comprar/<int:id>')
@login_required
def comprar(id):
    item = Item.query.get_or_404(id)
    chave = Chave.query.filter_by(item_id=id, disponivel=True).first()
    if not chave:
        flash("Nenhuma chave disponível para este item.", "erro")
        return redirect(url_for('listar'))
    carrinho = Carrinho.query.filter_by(utilizador_id=current_user.id, item_id=id).first()
    if carrinho:
        db.session.delete(carrinho)
    chave.disponivel = False
    compra = Compra(
        utilizador_id=current_user.id,
        item_id=item.id,
        chave_id=chave.id,
        preco_pago=item.preco
    )
    db.session.add(compra)
    db.session.commit()
    flash("Compra realizada com sucesso!", "sucesso")
    return redirect(url_for('historico'))

@app.route('/loja/finalizar_compra')
@login_required
def finalizar_compra():
    itens_carrinho = Carrinho.query.filter_by(utilizador_id=current_user.id).all()
    if not itens_carrinho:
        flash("Carrinho vazio.", "erro")
        return redirect(url_for('carrinho'))
    for carrinho in itens_carrinho:
        item = Item.query.get(carrinho.item_id)
        chave = Chave.query.filter_by(item_id=item.id, disponivel=True).first()
        if chave:
            chave.disponivel = False
            compra = Compra(
                utilizador_id=current_user.id,
                item_id=item.id,
                chave_id=chave.id,
                preco_pago=item.preco
            )
            db.session.add(compra)
            db.session.delete(carrinho)
    db.session.commit()
    flash("Compra finalizada com sucesso!", "sucesso")
    return redirect(url_for('historico'))

@app.route('/loja/historico')
@login_required
def historico():
    compras = Compra.query.filter_by(utilizador_id=current_user.id).all()
    carrinho_count = Carrinho.query.filter_by(utilizador_id=current_user.id).count()
    return render_template('historico.html', compras=compras, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Utilizador.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login efetuado com sucesso!", "sucesso")
            return redirect(url_for('index'))
        flash("Login inválido. Tente novamente!", "erro")
    carrinho_count = Carrinho.query.filter_by(utilizador_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('login.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/registo', methods=['GET', 'POST'])
def registo():
    form = RegistoForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        if not username or not password:
            flash("Preencha todos os campos corretamente.", "erro")
            return render_template('registo.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=0)
        if Utilizador.query.filter_by(username=username).first():
            flash("O utilizador já existe, escolha outro nome.", "erro")
            return render_template('registo.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=0)
        novo_utilizador = Utilizador(username=username, role='user')
        novo_utilizador.set_password(password)
        db.session.add(novo_utilizador)
        db.session.commit()
        flash("Registo efetuado com sucesso!", "sucesso")
        return redirect(url_for('login'))
    carrinho_count = 0
    return render_template('registo.html', form=form, loja_nome="MrFoxy Keys", carrinho_count=carrinho_count)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)