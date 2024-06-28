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

@app.route('/')
def scrape_data():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Execução sem interface gráfica
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = 'https://lista.mercadolivre.com.br/chuveiro'

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-search')))

        itens = driver.find_elements(By.CLASS_NAME, 'ui-search')[:10]  # Limitar a 10 itens

        dados = []
        for item in itens:
            nome_element = item.find_element(By.CSS_SELECTOR, '.ui-search-item__title')
            nome = nome_element.text.strip() if nome_element else ''
            print(f"Nome: {nome}")

            valor_element = item.find_element(By.CSS_SELECTOR, 'ui-search-price ui-search-price--size-medium')
            valor = valor_element.text.strip() if valor_element else ''
            print(f"Valor: {valor}")

            vendedor_element = item.find_element(By.CSS_SELECTOR, ".ui-search-reviews ui-search-item__group__element")
            vendedor = vendedor_element.text.strip() if vendedor_element else ''
            print(f"Vendedor: {vendedor}")

            parcelas_element = item.find_element(By.CSS_SELECTOR, '.ui-search-item__group__element ui-search-installments ui-search-color--LIGHT_GREEN')
            parcelas = parcelas_element.text.strip() if parcelas_element else ''
            print(f"Parcelas e Valor: {parcelas}")

            avaliacao_element = item.find_elements(By.CSS_SELECTOR, '.ui-search-reviews__rating-number')
            if len(avaliacao_element) >= 2:
                avaliacao_valor = avaliacao_element[0].text.strip()
                avaliacao_quantidade = avaliacao_element[1].text.strip()
                avaliacao = f'{avaliacao_valor} ({avaliacao_quantidade})'
            else:
                avaliacao = ''
            print(f"Avaliação: {avaliacao}")

            cupom_element = item.find_element(By.CSS_SELECTOR, '.ui-search-item__discount')
            cupom = cupom_element.text.strip() if cupom_element else ''
            print(f"Cupons de Desconto: {cupom}")

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
