from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec 
from urllib.parse import  urljoin
import pandas as Pandas

SITE = "site"
ACESSLINK = "links"
ALLINKS = f"{ACESSLINK}.txt"
ARQUIVO = f"{SITE}.txt"
LINKSSITE = []
LINKS =  []

def get_informations(url):
    print(f'Carregando...');

    bOptions = Options()
    bOptions.add_argument('--headless')
    driver = webdriver.Chrome()
    driver.get(url)

    try:

        try:
            html = driver.find_elements(By.TAG_NAME,'body')[0]
        except:
            print('not found')
            driver.refresh()
    
        html = html.get_attribute('innerHTML')
        bs = BeautifulSoup(html,'html.parser')

        for item in bs.find_all('a', href=True):
            link = item['href']
            if link.startswith('/'):
                absolute_url = urljoin(url, link)

                if absolute_url not in LINKS:
                    LINKS.append(absolute_url)
                    print(f"Adicionado ao LINKS: {absolute_url}")
    except:
        print('alo')
        driver.quit()


    for link in LINKS:
        try:
            driver.get(link)
            WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.TAG_NAME, 'body')))
            link_html = driver.find_element(By.TAG_NAME, 'body').get_attribute('innerHTML')
            
            bs_internal = BeautifulSoup(link_html, 'html.parser')
            
            for script in bs_internal.find_all('script'):
                script.decompose()
            
            LINKSSITE.append(bs_internal.prettify())
            
            print(f"Processado: {link}")
        
        except Exception as e:
            print(f"Erro ao processar página {link}: {str(e)}")
    
    driver.quit()

    file = Pandas.DataFrame()
    file['absolute_url'] = LINKSSITE
    file.to_csv(ARQUIVO)
    file2 = Pandas.DataFrame()
    file2['absolute_url'] = LINKS
    file2.to_csv(ALLINKS)


    