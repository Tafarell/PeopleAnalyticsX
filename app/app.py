from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import joblib
import os
import random

app = Flask(__name__)

# Caminho relativo do modelo
model_path = 'app/models/model_supervisao.pkl'

# Verificar se o arquivo do modelo existe
if not os.path.exists(model_path):
    app.logger.error(f"Erro: Arquivo de modelo não encontrado no caminho {model_path}.")
    clf = None
else:
    try:
        clf = joblib.load(model_path)
        app.logger.info(f"Modelo carregado com sucesso do caminho: {model_path}")
    except Exception as e:
        app.logger.error(f"Erro ao carregar o modelo: {str(e)}")
        clf = None

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

@app.route('/')
def index():
    """
    Página inicial.
    """
    return render_template('index.html')

@app.route('/process')
def process():
    """
    Página de processo.
    """
    return render_template('process.html')

@app.route("/formdisc")
def form_page():
    """
    Página de DISC.
    """
    return render_template("formdisc.html")


@app.route('/resultdisc')
def form_disc():
    # Pegue os parâmetros da URL
    D = request.args.get('D')
    I = request.args.get('I')
    E = request.args.get('E')
    C = request.args.get('C')

     # Passe esses valores para o template
    return render_template('resultdisc.html', D=D, I=I, E=E, C=C)

    # Passe esses valores para o template

@app.route('/formsupervisao')
def form_supervisao():
    """
    Página de formulário de supervisão.
    """
    return render_template('formsupervisao.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    Processa os dados enviados pelo formulário de supervisão.
    """
    if clf is None:
        return jsonify({"erro": "Modelo não carregado no servidor. Verifique o arquivo de modelo."}), 500

    try:
        # Receber os dados enviados
        dados = request.json
        app.logger.info(f"Dados recebidos: {dados}")

        if not dados:
            return jsonify({"erro": "Nenhum dado foi enviado!"}), 400

        # Converter dados para DataFrame e aplicar pesos
        df = pd.DataFrame([dados])
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Aplicar pesos às colunas conforme definido
        for coluna in df.columns:
            if coluna in pesos:
                df[coluna] *= pesos[coluna]

        app.logger.info(f"Dados após aplicação de pesos: \n{df}")

        # Fazer a predição
        resultado = clf.predict(df)
        status = "Aprovado" if resultado[0] == 1 else "Reprovado"

        app.logger.info(f"Redirecionando para a página de resultado com status: {status}")
        return jsonify({"redirect_url": url_for('resultado', resultado=status)})

    except Exception as e:
        app.logger.error(f"Erro ao processar a requisição: {str(e)}")
        return jsonify({'erro': str(e)}), 500
    

@app.route('/resultado')
def resultado():
    """
    Página de resultado do formulário de supervisão.
    """
    resultado = request.args.get('resultado', 'Resultado não encontrado')

    # Sugestões de cursos caso o resultado seja "Reprovado"
    sugestoes_cursos = [
        ("Curso de Comunicação Eficaz - Udemy", "https://www.udemy.com/course/comunicacao-eficaz/?srsltid=AfmBOooydmQc7nHpanX2-lukVdvXy3tCy2mEUqQ-nFvAXz1Ub1woy1U9&couponCode=BFCPSALE24"),
        ("Curso de Liderança e Gestão - Coursera", "https://www.coursera.org/specializations/leadership-negotiation-skills/paidmedia?utm_medium=sem&utm_source=gg&utm_campaign=B2C_LATAM_leadership-negotiation-skills_tecdemonterrey_FTCOF_specializations_countrygroup-1&campaignid=21463941786&adgroupid=166419456124&device=c&keyword=leadership%20courses&matchtype=b&network=g&devicemodel=&adposition=&creativeid=705894320810&hide_mobile_promo&gad_source=1&gclid=Cj0KCQiAgJa6BhCOARIsAMiL7V8840aKpDYvWI_G1QVJlji4c6qcSA1maU4tb0uDY88U5AjWwf15ngMaArkOEALw_wcB&utm_medium=sem&utm_source=gg&utm_campaign=B2C_LATAM_leadership-negotiation-skills_tecdemonterrey_FTCOF_specializations_countrygroup-1&campaignid=21463941786&adgroupid=166419456124&device=c&keyword=leadership%20courses&matchtype=b&network=g&devicemodel=&adposition=&creativeid=705894320810&gad_source=1&gclid=Cj0KCQiAgJa6BhCOARIsAMiL7V8840aKpDYvWI_G1QVJlji4c6qcSA1maU4tb0uDY88U5AjWwf15ngMaArkOEALw_wcB"),
        ("Curso de Resolução de Conflitos - LinkedIn Learning", "https://www.linkedin.com/learning/fundamentos-da-resolucao-de-conflitos"),
        ("Curso de Desenvolvimento de Talentos - Udemy", "https://www.udemy.com/course/desenvolvimento-de-talentos/?srsltid=AfmBOorGIjNQfmAJG6vm_QQgdL35zTQlICFmqRkXiTqN3z4t2fLXEhzO"),
        ("Curso de Tomada de Decisões com Dados - Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics?utm_medium=sem&utm_source=gg&utm_campaign=B2C_LATAM_analise-de-dados-do-google_google_FTCOF_professional-certificates_country-br-language-PT&campaignid=21179153449&adgroupid=157727684141&device=c&keyword=curso%20data%20science&matchtype=b&network=g&devicemodel=&adposition=&creativeid=696780772238&hide_mobile_promo&gad_source=1&gclid=Cj0KCQiAgJa6BhCOARIsAMiL7V8JY1SYxv9DHXZRBzM78hyl6eJkAVyb6QbZ9rnjoMAaWklG-D8SPzoaAimEEALw_wcB"),
        ("Curso de Planejamento Estratégico - LinkedIn Learning", "https://www.linkedin.com/learning/fundamentos-do-planejamento-estrategico/boas-vindas"),
        ("Curso de Inovação e Criatividade - Udemy", "https://www.udemy.com/course/criatividade-e-inovacao/?srsltid=AfmBOorA-uT2IFrwXA76K_oIhBUp1QsGd66wdx2_ogd-PXf66aF0DU0N&couponCode=BFCPSALE24"),
        ("Curso de Flexibilidade e Adaptação - Coursera", "https://www.coursera.org/career-academy?utm_medium=sem&utm_source=gg&utm_campaign=B2C_LATAM__coursera_FTCOF_career-academy_countrygroup-1&campaignid=20849786070&adgroupid=156704859036&device=c&keyword=online%20courses&matchtype=b&network=g&devicemodel=&adposition=&creativeid=kwd-10605931&hide_mobile_promo&gad_source=1&gclid=Cj0KCQiAgJa6BhCOARIsAMiL7V8M0FyQ6thEgDrSJCKg0TN1b9eA1TxR8pwFd64s4VFthZFFs9C8RAQaArhYEALw_wcB"),
    ]

    cursos = random.sample(sugestoes_cursos, 2) if resultado == 'Reprovado' else []

    return render_template('resultado.html', resultado=resultado, cursos=cursos)

if __name__ == '__main__':
    app.run(debug=True)
