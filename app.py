import os
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3

app = Flask(__name__)


def init_db():
    try:
        
        db_path = os.path.join(os.path.dirname(__file__), 'itens.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS itens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                valor TEXT,
                vendedor TEXT,
                parcelas_valor TEXT,
                avaliacao TEXT,
                cupons_desconto TEXT
            )
        ''')

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")


def calcular_valor_medio(itens):
    valores = []
    for item in itens:
        valor_str = item['Valor'].replace('R$', '').strip()
        try:
            valor_float = float(valor_str.replace('.', '').replace(',', '.'))
            valores.append(valor_float)
        except ValueError:
            print(f"Valor inválido encontrado: {valor_str}")
    if valores:
        return sum(valores) / len(valores)
    else:
        return 0.0


init_db()

@app.route('/')
def homepage():
    return render_template("index.html", dados=[], valor_medio=0)

@app.route('/scrape')
def scrape_data():
    try:
        termo_busca = request.args.get('termo_busca', 'chuveiro')  
        print(f"chuveiro: {termo_busca}")

        termo_busca = request.args.get('termo_busca', 'bicicleta')
        print(f"biclicleta: {termo_busca}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless') 
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        url = f'https://lista.mercadolivre.com.br/{termo_busca}'  
        print(f"https://lista.mercadolivre.com.br/chuveiro, https://lista.mercadolivre.com.br/bicicleta: {url}")

        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'ui-search-layout')))

        itens = driver.find_elements(By.CLASS_NAME, 'ui-search-layout__item')[:10] #limitar a 10 itens  

        dados = []
        for item in itens:
            try:
                nome_element = item.find_element(By.CLASS_NAME, 'ui-search-item__title')
                nome = nome_element.text.strip()
            except:
                nome = ''

            try:
                valor_element = item.find_element(By.CLASS_NAME, 'ui-search-price__second-line')
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
                cupom_element = item.find_element(By.CLASS_NAME, 'ui-pb-container')
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

        driver.quit()

        
        valor_medio = calcular_valor_medio(dados)

        return render_template('index.html', dados=dados, valor_medio=valor_medio)

    except Exception as e:
        print(f"Erro durante a raspagem de dados: {e}")
        return render_template('error.html', message="Ocorreu um erro durante a raspagem de dados. Por favor, tente novamente mais tarde.")

if __name__ == '__main__':
    app.run(debug=True)






