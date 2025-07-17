from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def inicio():
    return render_template('inicio.html')   


@app.route('/criar_sala', methods=['GET', 'POST'])
def criar_sala():
    if request.method == 'POST':
        numero_rodadas = request.form.get('numero_rodadas')
        numero_jogadores = request.form.get('numero_jogadores')
        senha = request.form.get('senha')
        tempo = request.form.get('tempo')
        letras = request.form.get('letras')
        temas = request.form.getlist('temas')

        sala = Sala(numero_rodadas=numero_rodadas, tempo=tempo, letras=letras, numero_jogadores=numero_jogadores, senha=senha, temas=temas)
        
        db.session.add(sala)
        db.session.commit()
        return redirect(url_for('inicio'))
    
    letras = Letras.query.all()
    temas = Tema.query.all()
    return render_template('criar_sala.html', letras=letras, temas=temas) 


class Rodada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    letra_id = db.Column(db.ForeignKey('letra.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    data_fim = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Rodada {self.numero} - Letra: {self.letra} - Palavra: {self.palavra} - Pontos: {self.pontos}>'
    
class Sala(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_rodadas = db.Column(db.Integer, nullable=False)
    rodadas = db.relationship('Rodada', backref='sala', lazy=True)
    temas = db.relationship('Tema', secondary='sala_tema', backref='salas', lazy=True)
    tempo = db.Column(db.Integer, nullable=False)
    jogadores = db.relationship('Jogador', backref="jogador", lazy=True)
    numero_jogadores = db.Column(db.Integer, nullable=False)
    senha = db.Column(db.String(120), nullable=True)
    finalizado = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    data_inicio = db.Column(db.DateTime, nullable=True)

class Jogador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True, unique=True)
    senha = db.Column(db.String(120), nullable=True)
    def __repr__(self):
        return f'<Jogador {self.nome} - Pontos: {self.pontos}>'


class Tema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)



class SalaTema(db.Model):
    __tablename__ = 'sala_tema'
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    sala = db.relationship('Sala', backref='sala_temas')
    tema = db.relationship('Tema', backref='tema_salas')
    

class SalaLetras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    letra_id = db.Column(db.Integer, db.ForeignKey('letras.id'), nullable=False)
    sala = db.relationship('Sala', backref='sala_letras')
    letra = db.relationship('Letras', backref='letra_salas')
    sorteada = db.Column(db.Boolean, default=False)    

class Letras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letra = db.Column(db.String(1), nullable=False)
   

    def __repr__(self):
        return f'<Tema {self.nome}>'
















if __name__ == '__main__':
    app.run(debug=True)
