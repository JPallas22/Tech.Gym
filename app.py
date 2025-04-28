from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask import flash, get_flashed_messages

app = Flask(__name__)
app.secret_key = 'admin123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///academia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_admin'

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(10), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    endereco = db.Column(db.String(150), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    nacionalidade = db.Column(db.String(50), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    rg = db.Column(db.String(20), nullable=False)
    estado_civil = db.Column(db.String(20), nullable=False)
    nome_conjuge = db.Column(db.String(100), nullable=True)
    sexo = db.Column(db.String(1), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    nome_pai = db.Column(db.String(100), nullable=False)
    nome_mae = db.Column(db.String(100), nullable=False)
    faixa = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Aluno {self.nome}>'

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    senha_hash = db.Column(db.String(128), nullable=False)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
class Horario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    faixa = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Horario {self.dia_semana} {self.hora} - {self.faixa}>"
    
class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)

    aluno = db.relationship('Aluno', backref='agendamentos')
    horario = db.relationship('Horario', backref='agendamentos')

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/acessar_aluno', methods=['GET', 'POST'])
def acessar_aluno():
    if request.method == 'POST':
        id_aluno = request.form['id_aluno']
        aluno = Aluno.query.get(id_aluno)

        if aluno:
            faixa = aluno.faixa
            horarios = Horario.query.filter_by(faixa=faixa).all()
            return render_template('horarios_aluno.html', aluno=aluno, horarios=horarios)
        else:
            flash('Aluno não encontrado!', 'danger')
            return redirect(url_for('acessar_aluno'))

    return render_template('acessar_aluno.html')

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.verificar_senha(senha):
            login_user(admin)
            return redirect(url_for('admin_painel'))
        else:
            flash('Email ou senha incorretos!', 'danger')

    return render_template('login_admin.html')

@app.route('/cadastro_admin', methods=['GET', 'POST'])
def cadastro_admin():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        novo_admin = Admin(email=email)
        novo_admin.set_senha(senha)  # Criptografa a senha!

        db.session.add(novo_admin)
        db.session.commit()

        flash('Administrador cadastrado com sucesso!', 'success')
        return redirect(url_for('login_admin'))

    return render_template('cadastro_admin.html')

@app.route('/cadastrar_horario', methods=['GET', 'POST'])
@login_required
def cadastrar_horario():
    if request.method == 'POST':
        dia_semana = request.form['dia_semana']
        hora = request.form['hora']
        faixa = request.form['faixa']

        novo_horario = Horario(dia_semana=dia_semana, hora=hora, faixa=faixa)

        db.session.add(novo_horario)
        db.session.commit()

        flash('Horário cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_horarios'))

    return render_template('cadastrar_horario.html')

@app.route('/admin_painel')
@login_required
def admin_painel():
    return render_template('admin_painel.html')

@app.route('/novo_aluno', methods=['GET', 'POST'])
@login_required
def novo_aluno():
    if request.method == 'POST':
        ultimo_aluno = Aluno.query.order_by(Aluno.id.desc()).first()
        if ultimo_aluno:
            nova_matricula = str(int(ultimo_aluno.id) + 1).zfill(3)
        else:
            nova_matricula = '001'

        aluno = Aluno(
            matricula=nova_matricula,
            nome=request.form['nome'],
            idade=request.form['idade'],
            endereco=request.form['endereco'],
            bairro=request.form['bairro'],
            cidade=request.form['cidade'],
            estado=request.form['estado'],
            cep=request.form['cep'],
            nacionalidade=request.form['nacionalidade'],
            data_nascimento=request.form['data_nascimento'],
            cpf=request.form['cpf'],
            rg=request.form['rg'],
            estado_civil=request.form['estado_civil'],
            nome_conjuge=request.form.get('nome_conjuge', ''),
            sexo=request.form['sexo'],
            telefone=request.form['telefone'],
            email=request.form['email'],
            nome_pai=request.form['nome_pai'],
            nome_mae=request.form['nome_mae'],
            faixa=request.form['faixa']
        )

        db.session.add(aluno)
        db.session.commit()

        return redirect(url_for('listar_alunos'))

    return render_template('novo_aluno.html')

@app.route('/listar_alunos')
@login_required
def listar_alunos():
    alunos = Aluno.query.all()
    return render_template('listar_alunos.html', alunos=alunos)

@app.route('/listar_horarios')
@login_required
def listar_horarios():
    horarios = Horario.query.all()
    return render_template('listar_horarios.html', horarios=horarios)

@app.route('/excluir_horario/<int:horario_id>')
@login_required
def excluir_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    db.session.delete(horario)
    db.session.commit()
    flash('Horário excluído com sucesso!', 'success')
    return redirect(url_for('listar_horarios'))

@app.route('/agendar_aula/<int:aluno_id>', methods=['POST'])
def agendar_aula(aluno_id):
    horario_id = request.form['horario_id']
    aluno = Aluno.query.get_or_404(aluno_id)

    agendamento_existente = Agendamento.query.filter_by(aluno_id=aluno_id, horario_id=horario_id).first()

    if agendamento_existente:
        faixa = aluno.faixa
        horarios = Horario.query.filter_by(faixa=faixa).all()

        flash('Você já agendou esse horário!', 'danger')
        return render_template('horarios_aluno.html', aluno=aluno, horarios=horarios)

    novo_agendamento = Agendamento(aluno_id=aluno_id, horario_id=horario_id)
    db.session.add(novo_agendamento)
    db.session.commit()

    flash('Aula agendada com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/editar_horario/<int:horario_id>', methods=['GET', 'POST'])
@login_required
def editar_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)

    if request.method == 'POST':
        horario.dia_semana = request.form['dia_semana']
        horario.hora = request.form['hora']
        horario.faixa = request.form['faixa']

        db.session.commit()
        flash('Horário atualizado com sucesso!', 'success')
        return redirect(url_for('listar_horarios'))

    return render_template('editar_horario.html', horario=horario)

@app.route('/listar_agendamentos')
@login_required
def listar_agendamentos():
    agendamentos = Agendamento.query.all()
    return render_template('listar_agendamentos.html', agendamentos=agendamentos)

@app.route('/excluir_aluno/<int:aluno_id>')
@login_required
def excluir_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    return redirect(url_for('listar_alunos'))

@app.route('/editar_aluno/<int:aluno_id>', methods=['GET', 'POST'])
@login_required
def editar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)

    if request.method == 'POST':
        aluno.nome = request.form['nome']
        aluno.idade = request.form['idade']
        aluno.email = request.form['email']
        senha = request.form['senha']

        if senha:
            aluno.set_senha(senha)

        db.session.commit()
        return redirect(url_for('listar_alunos'))

    return render_template('editar_aluno.html', aluno=aluno)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
