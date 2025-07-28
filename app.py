from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




class Rodada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    letra_id = db.Column(db.ForeignKey('letras.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    data_fim = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Rodada {self.numero} - Letra: {self.letra} - Palavra: {self.palavra} - Pontos: {self.pontos}>'
    

class Tema(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)



class Sala(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_rodadas = db.Column(db.Integer, nullable=False)
    rodadas = db.relationship('Rodada', backref='sala', lazy=True)
    temas = db.relationship('Tema', secondary='sala_tema', backref='salas', lazy=True)
    tempo = db.Column(db.Integer, nullable=False)
    jogadores = db.relationship('Jogador', secondary='sala_jogador', backref='salas', lazy=True)
    letras = db.relationship('Letras', secondary='sala_letras', backref='salas', lazy=True)
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


class SalaJogador(db.Model):
    __tablename__ = 'sala_jogador'
    id = db.Column(db.Integer, primary_key=True)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogador.id'), nullable=False)
    sala = db.relationship('Sala', backref='sala_jogadores')
    jogador = db.relationship('Jogador', backref='jogador_salas')





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


with app.app_context():
    db.create_all() 

@app.route('/')
def inicio():
    return render_template('inicio.html')   


@app.route('/criar_sala', methods=['GET', 'POST'])
def criar_sala():
    if request.method == 'POST':
        numero_rodadas = request.form.get('numero_rodadas')
        numero_jogadores = request.form.get('numero_jogadores')
        import pdb
        #pdb.set_trace()
        senha = request.form.get('senha')
        tempo = request.form.get('tempo')
        letras_ids = request.form.getlist('letras')
        temas_ids = request.form.getlist('temas')

        letras = Letras.query.filter(Letras.id.in_(letras_ids)).all()
        temas = Tema.query.filter(Tema.id.in_(temas_ids)).all()

        sala = Sala(numero_rodadas=numero_rodadas, tempo=60, numero_jogadores=numero_jogadores, senha=senha, temas=temas, letras=letras)
        
        db.session.add(sala)
        db.session.commit()

        return redirect(url_for('inicio'))
    
    letras = Letras.query.all()
    temas = Tema.query.all()
    numero_jogadores = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 50]
    numero_rodadas = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    tempo = [60, 120, 180]

    return render_template('criar_sala.html', letras=letras, temas=temas , numero_jogadores=numero_jogadores, numero_rodadas=numero_rodadas, tempo=tempo) 

@app.route('/sala/<int:sala_id>')
def sala(sala_id):
    sala = Sala.query.get_or_404(sala_id)
    
    return render_template('sala.html', sala=sala, rodadas=sala.rodadas, letras=sala.letras, temas=sala.temas, jogadores=sala.jogadores)


@app.route('/salas', methods=['GET'])
def salas():
    salas = Sala.query.all()
    return render_template('salas_criadas.html', salas=salas)

@app.route('/admin/tema', methods=['GET', 'POST'])
def admin_tema():
    if request.method == 'POST':
        nome = request.form.get('nome')
        tema = Tema(nome=nome)
        db.session.add(tema)
        db.session.commit()

    temas = Tema.query.all()
    return render_template('tema.html', temas=temas)

@app.route('/sala/iniciar', methods=['GET', 'POST'])
def iniciar_sala():
    if request.method == 'POST':
        sala_id = request.form.get('sala_id')
        sala = Sala.query.get_or_404(sala_id)
        sala.data_inicio = db.func.current_timestamp()
        db.session.add(sala)
        db.session.commit()
           
        return redirect(url_for('sala', sala_id=sala.id))
    

@app.route('/admin/letra', methods=['GET', 'POST'])
def admin_letras():
    if request.method == 'POST':
        letra = request.form.get('letra')
        letra_db = Letras(letra=letra)
        db.session.add(letra_db)
        db.session.commit()

    letras = Letras.query.all()
    return render_template('letra.html', letras=letras)
    

















if __name__ == '__main__':
    app.run(debug=True)
