from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
import string
import secrets
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.secret_key = 'jakfjhaAFGKMLajfnakk135682008'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return Jogador.query.get(int(user_id))


# configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

# pensar sobre
class JogadorRodada(db.Model):
    __tablename__ = 'jogador_rodada'
    id = db.Column(db.Integer, primary_key=True)
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogador.id'), nullable=False)
    rodada_id = db.Column(db.Integer, db.ForeignKey('rodada.id'), nullable=False)
    pontos = db.Column(db.Integer, default=0)
    jogador = db.relationship('Jogador', backref='jogador_rodadas')
    rodada = db.relationship('Rodada', backref='jogador_rodadas')

# pensar sobre
class JogadorRodadaTema(db.Model):
    __tablename__ = 'jogador_rodada_tema'
    id = db.Column(db.Integer, primary_key=True)
    jogador_rodada_id = db.Column(db.Integer, db.ForeignKey('jogador_rodada.id'), nullable=False)
    tema_id = db.Column(db.Integer, db.ForeignKey('tema.id'), nullable=False)
    resposta = db.Column(db.String(100), nullable=True)
    jogador_rodada = db.relationship('JogadorRodada', backref='jogador_rodada_temas')
    tema = db.relationship('Tema', backref='tema_jogador_rodadas')


class Rodada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    sala_id = db.Column(db.Integer, db.ForeignKey('sala.id'), nullable=False)
    letra_id = db.Column(db.ForeignKey('letras.id'), nullable=False)
    letra = db.relationship('Letras', backref='rodadas', lazy=True)
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Rodada {self.numero}>'
    

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
    rodada_atual = db.Column(db.Integer, nullable=False, default=0) 


class Jogador(db.Model, UserMixin):
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
        return f'<Tema {self.letra}>'


with app.app_context():
    db.create_all() 



def datetime_to_brl(dt):
    return dt+timedelta(hours=-3) if dt else None


@app.route('/')
@login_required
def inicio():   
    return render_template('inicio.html', current_user=current_user) 
  



@app.route('/criar_sala', methods=['GET', 'POST'])
def criar_sala():
    if request.method == 'POST':
        numero_rodadas = request.form.get('numero_rodadas')
        numero_jogadores = request.form.get('numero_jogadores')
        import pdb
       
        
        senha = request.form.get('senha')
        tempo = request.form.get('tempo')
        letras_ids = request.form.getlist('letras[]')
        temas_ids = request.form.getlist('temas[]')

        letras = Letras.query.filter(Letras.id.in_(letras_ids)).all()
        temas = Tema.query.filter(Tema.id.in_(temas_ids)).all()
        sala = Sala(numero_rodadas=numero_rodadas, tempo=tempo, numero_jogadores=numero_jogadores, senha=senha, temas=temas, letras=letras )
        
        db.session.add(sala)
        db.session.commit()
        import pdb
        #pdb.set_trace()
        return redirect(url_for('sala', sala_id=sala.id))
    
    letras = Letras.query.all()
    temas = Tema.query.all()
    numero_jogadores = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 50]
    numero_rodadas = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    tempo = [60, 120, 180]

    return render_template('criar_sala.html', letras=letras, temas=temas , numero_jogadores=numero_jogadores, numero_rodadas=numero_rodadas, tempo=tempo) 

@app.route('/sala/<int:sala_id>')
def sala(sala_id):
    sala = Sala.query.get_or_404(sala_id)
    rodada_atual = Rodada.query.filter_by(sala_id=sala.id, numero=sala.rodada_atual).first()
    data_inicio_brl = datetime_to_brl(rodada_atual.data_inicio) if rodada_atual and rodada_atual.data_inicio else None
    return render_template('sala.html', sala=sala, rodadas=sala.rodadas, letras=sala.letras, temas=sala.temas, jogadores=sala.jogadores, rodada=rodada_atual,data_inicio_brl=data_inicio_brl)


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
        letras = sala.letras
        letras_sorteadas = []

        rodadas = []
        for i in range(int(sala.numero_rodadas)):
            letras_disponiveis = [letra for letra in letras if letra not in letras_sorteadas]
            letra_sorteada = random.choice(letras_disponiveis)
            letras_sorteadas.append(letra_sorteada)
            rodada = Rodada(numero=i+1, sala=sala, letra_id=letra_sorteada.id)
            if rodada.numero == 1:
                rodada.data_inicio = db.func.current_timestamp()
            rodadas.append(rodada)
            
        
        sala.rodada_atual = 1

        sala.rodadas = rodadas
        sala.data_inicio = db.func.current_timestamp()
        db.session.add(rodada)
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
    
def criar_usuario(nome, email, senha):
    jogador = Jogador(nome=nome, email=email, senha=senha)
    db.session.add(jogador)
    db.session.commit()
    return jogador

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        _jogador = criar_usuario(nome, email, senha)

        return redirect(url_for('login'))
    
    return render_template('cadastro.html')


@app.route('/cadastro_anonimo', methods=['POST'])
def cadastro_anonimo():
    
    adjectives = ["Fast", "Silent", "Happy", "Dark", "Bright", "Wild", "Crazy", "Calm"]
    animals = ["Lion", "Tiger", "Eagle", "Shark", "Wolf", "Panda", "Falcon", "Fox"]

    username = random.choice(adjectives) + random.choice(animals) + str(random.randint(100, 999))

    domains = ["example.com", "mail.com", "anon.io", "temp.org"]
    email = username.lower() + "@" + random.choice(domains)


    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(12))

    jogador = criar_usuario(username, email, password)
    login_user(jogador)
    return redirect(url_for('inicio'))

  


@app.route('/login', methods=['GET', 'POST'])  
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('senha')
        jogador = Jogador.query.filter_by(email=email, senha=senha).first()
        if jogador:
            login_user(jogador)
            return redirect(url_for('inicio'))
        else:
            return 'Email ou senha inválidos', 401
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('cadastro'))







socketio = SocketIO(app)


# Evento para entrar em uma sala
@socketio.on('entrar_sala')
def entrar_sala(data):
    sala = data['sala']
    usuario = data['usuario']
    join_room(sala)
    emit('mensagem', f"{usuario} entrou na sala {sala}", room=sala)

# Evento para sair da sala
@socketio.on('sair_sala')
def sair_sala(data):
    sala = data['sala']
    usuario = data['usuario']
    leave_room(sala)
    emit('mensagem', f"{usuario} saiu da sala {sala}", room=sala)

# Enviar mensagem dentro da sala
@socketio.on('mensagem_sala')
def mensagem_sala(data):
    sala = data['sala']
    usuario = data['usuario']
    msg = data['msg']
    emit('mensagem', f"{usuario}: {msg}", room=sala)

if __name__ == '__main__':
    socketio.run(app, debug=True)








