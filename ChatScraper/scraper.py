from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import pandas as pd
import time
import whois

SITE = "site"
ACESSLINK = "links"
ALLINKS = f"{ACESSLINK}.txt"
ARQUIVO = f"{SITE}.txt"

def get_informations(url):
    print(f'Carregando {url}...')
    
    LINKS = []

    start_time = time.time()
    elapsed_time = 0
    
    try:
        response = requests.get(url, timeout=10)
        html = response.text
        bs = BeautifulSoup(html, 'html.parser')
        LINKS.append(url)
        base_domain = urlparse(url).netloc
        
        for item in bs.find_all('a', href=True):
            elapsed_time = time.time() - start_time
            if elapsed_time > 5:  # Tempo limite de 5 segundos
                break
            link = item['href']
            absolute_url = urljoin(url, link) if link.startswith('/') else link
            link_domain = urlparse(absolute_url).netloc
            
            if link_domain == base_domain:
                # Adiciona links internos
                if absolute_url not in LINKS:
                    LINKS.append(absolute_url)
                    print(f"Adicionado ao LINKS: {absolute_url}")
            else:
                # Verifica se o domínio externo pertence ao mesmo proprietário
                if is_same_owner(url, absolute_url):
                    if absolute_url not in LINKS:
                        LINKS.append(absolute_url)
                        print(f"Adicionado ao LINKS: {absolute_url}")
                    
    except Exception as e:
        print(f"Erro ao acessar {url}: {str(e)}")
        return
    
    with open(ARQUIVO, 'w', encoding='utf-8') as file:
        for link in LINKS:
            try:
                response = requests.get(link, timeout=10)
                link_html = response.text
                bs_internal = BeautifulSoup(link_html, 'html.parser')
                txt = bs_internal.get_text()
                
                file.write(txt.strip() + '\n')
                
                print(f"Processado e salvo em {ARQUIVO}: {link}")
            
            except Exception as e:
                print(f"Erro ao processar página {link}: {str(e)}")
    
    file2 = pd.DataFrame({'absolute_url': LINKS})
    file2.to_csv(ALLINKS, index=False, encoding='utf-8')

    return ARQUIVO

def is_same_owner(url1, url2):
    try:
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        
        whois1 = whois.whois(domain1)
        whois2 = whois.whois(domain2)
        
        if whois1 and whois2:
            registrant1 = whois1.get('registrant_name') or whois1.get('org') or whois1.get('emails')
            registrant2 = whois2.get('registrant_name') or whois2.get('org') or whois2.get('emails')
            return registrant1 == registrant2
    except Exception as e:
        print(f"Erro ao realizar consulta WHOIS: {str(e)}")
    
    return False
