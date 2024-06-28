from flask import Flask, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("index.html", dados=[])

@app.route('/scrape')
def scrape_data():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Execução sem interface gráfica
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = 'https://lista.mercadolivre.com.br/chuveiro'

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-layout')))

        itens = driver.find_elements(By.CLASS_NAME, 'ui-search-layout__item')[:12]  # Limitar a 12 itens

        dados = []
        for item in itens:
            try:
                nome_element = item.find_element(By.CLASS_NAME, 'ui-search-item__title')
                nome = nome_element.text.strip()
            except:
                nome = ''

            try:
                valor_element = item.find_element(By.CLASS_NAME, 'ui-search-price__part')
                valor = valor_element.text.strip()
            except:
                valor = ''

            try:
                vendedor_element = item.find_element(By.CLASS_NAME, 'ui-search-official-store-label')
                vendedor = vendedor_element.text.strip()
            except:
                vendedor = ''

            try:
                parcelas_element = item.find_element(By.CLASS_NAME, 'ui-search-installments')
                parcelas = parcelas_element.text.strip()
            except:
                parcelas = ''

            try:
                avaliacao_element = item.find_element(By.CLASS_NAME, 'ui-search-reviews__rating-number')
                avaliacao = avaliacao_element.text.strip()
            except:
                avaliacao = ''

            try:
                cupom_element = item.find_element(By.CLASS_NAME, 'ui-search-item__discount')
                cupom = cupom_element.text.strip()
            except:
                cupom = ''

            dados.append({
                'Nome': nome,
                'Valor': valor,
                'Vendedor': vendedor,
                'Parcelas e Valor': parcelas,
                'Avaliação': avaliacao,
                'Cupons de Desconto': cupom
            })

    finally:
        driver.quit()

    return render_template('index.html', dados=dados)

if __name__ == '__main__':
    app.run(debug=True)

