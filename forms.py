from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, EqualTo, Length

class ItemForm(FlaskForm):
    nome = StringField('Nome do Item', validators=[DataRequired()])
    desenvolvedor = StringField('Desenvolvedor', validators=[DataRequired()])
    ano = IntegerField('Ano', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    preco = FloatField('Preço (€)', validators=[DataRequired(), NumberRange(min=0.01)])
    chaves = TextAreaField('Chaves (uma por linha)', validators=[DataRequired()])
    submeter = SubmitField('Gravar')

class LoginForm(FlaskForm):
    username = StringField('Utilizador', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submeter = SubmitField('Entrar')

class RegistoForm(FlaskForm):
    username = StringField('Utilizador', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmar = PasswordField('Confirmar Password', validators=[EqualTo('password')])
    submeter = SubmitField('Registar')