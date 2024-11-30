from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import joblib
import os
import random

app = Flask(__name__)

# Caminho do modelo
MODEL_PATH = 'app/models/model_supervisao.pkl'

# Carregar o modelo
try:
    clf = joblib.load(MODEL_PATH)
    app.logger.info(f"Modelo carregado com sucesso: {MODEL_PATH}")
except Exception as e:
    clf = None
    app.logger.error(f"Erro ao carregar o modelo: {str(e)}")

# Pesos de relevância para cada competência
pesos = {
    'comunicacao_a': 8,
    'comunicacao_b': 6,
    'comunicacao_c': 7,
    'saber_ouvir_a': 5,
    'saber_ouvir_b': 6,
    'lideranca_a': 8,
    'lideranca_b': 7,
    'desenvolvimento_talentos_a': 6,
    'desenvolvimento_talentos_b': 5,
    'pensamento_analitico_a': 8,
    'pensamento_analitico_b': 7,
    'planejamento_a': 8,
    'planejamento_b': 6,
    'inovacao_a': 5,
    'inovacao_b': 6,
    'flexibilidade_a': 7,
    'flexibilidade_b': 5
}

@app.route("/")
def index_home():
    """
    Página inicial.
    """
    return render_template("index.html")

@app.route("/processos")
def processos_page():
    """
    Página de processos.
    """
    return render_template("process.html")

@app.route("/formsupervisao")
def form_supervisao():
    """
    Página de formulário de supervisão.
    """
    return render_template("formsupervisao.html")

@app.route("/formdisc")
def formdisc():
    """
    Página de DISC.
    """
    return render_template("formdisc.html")


@app.route('/resultdisc')
def result_disc():
    # Pegue os parâmetros da URL
    D = request.args.get('D')
    I = request.args.get('I')
    E = request.args.get('E')
    C = request.args.get('C')
    
    # Passe esses valores para o template
    return render_template('resultdisc.html', D=D, I=I, E=E, C=C)

@app.route("/submit", methods=["POST"])
def submit():
    """
    Processa os dados enviados pelo formulário de supervisão.
    """
    if clf is None:
        return jsonify({"erro": "Modelo não carregado no servidor. Verifique o arquivo de modelo."}), 500

    try:
        # Receber os dados enviados
        dados = request.json
        if not dados:
            return jsonify({"erro": "Nenhum dado foi enviado!"}), 400

        # Converter dados para DataFrame e aplicar pesos
        df = pd.DataFrame([dados])
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
        for coluna in df.columns:
            if coluna in pesos:
                df[coluna] *= pesos[coluna]

        # Fazer a predição
        resultado = clf.predict(df)
        status = "Aprovado" if resultado[0] == 1 else "Reprovado"

        # Retornar o redirecionamento para a página de resultado
        return jsonify({"redirect_url": url_for("resultado", resultado=status)})

    except Exception as e:
        app.logger.error(f"Erro ao processar a requisição: {str(e)}")
        return jsonify({'erro': str(e)}), 500
    

@app.route("/resultado")
def resultado():
    """
    Página de resultado do formulário de supervisão.
    """
    resultado = request.args.get("resultado", "Resultado não encontrado")

    # Sugestões de cursos caso o resultado seja "Reprovado"
    sugestoes_cursos = [
        ("Curso de Comunicação Eficaz - Udemy", "https://www.udemy.com/course/communication-skills/"),
        ("Curso de Liderança e Gestão - Coursera", "https://www.coursera.org/learn/leadership-management"),
        ("Curso de Resolução de Conflitos - LinkedIn Learning", "https://www.linkedin.com/learning/confronting-workplace-conflict"),
        ("Curso de Desenvolvimento de Talentos - Udemy", "https://www.udemy.com/course/employee-development/"),
        ("Curso de Tomada de Decisões com Dados - Coursera", "https://www.coursera.org/learn/data-driven-decision-making"),
        ("Curso de Planejamento Estratégico - LinkedIn Learning", "https://www.linkedin.com/learning/strategic-planning-foundations"),
        ("Curso de Inovação e Criatividade - Udemy", "https://www.udemy.com/course/innovation-and-creativity/"),
        ("Curso de Flexibilidade e Adaptação - Coursera", "https://www.coursera.org/learn/adaptability"),
    ]
    cursos = random.sample(sugestoes_cursos, 2) if resultado == "Reprovado" else []

    return render_template("resultado.html", resultado=resultado, cursos=cursos)

if __name__ == "__main__":
    app.run(debug=True)
