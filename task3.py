import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from googletrans import Translator
import httpx
from urllib.parse import urlparse
import os
from pathlib import Path
# --- 
def translate_text(text, target="hi"):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    import os
    from google.cloud import translate_v2 as translate

    credential_path = r"googlekey.json"
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    # print(u"Text: {}".format(result["input"]))
    # print(u"Translation: {}".format(result["translatedText"]))
    # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))
    return result["translatedText"]

def getPath(url):
    
    final_url = url.strip().strip("/").rsplit('/', 1)
    print('final_urlgetpath', final_url)
    if final_url[0] == "https:/":
        path = os.path.join("index.html").replace("\\","/")
    else:
        folderPath = urlparse(final_url[0]).path
        path = os.path.join(folderPath.strip('/'), final_url[1] + ".html").replace("\\","/")
    directory = os.getcwd()
    url = urljoin(directory, path) 
    return path
def translate_html_text(driver, url, domain):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    
    s = []
    for e in soup(['script','style']):
        s.append(e.extract())
        
    for e in soup.find_all(text=True):
        if str(e.string) != "\n" and e.string.strip():
            translation = translate_text(
            text=str(e.string.strip()),
            target="hi")
            e.string.replace_with(translation)
                
    # print(soup.prettify())
    
    elements = soup.find_all('img')
    for ele in elements: 
        # print(type(ele['src']))
        # print("eleSrc",ele['src'])
        if ele.has_attr('data-src'):
            ele['src'] = ele['src'].replace(ele['src'], ele['data-src'])
        # print("eleSrc1",ele['src'])

    for atag in soup.find_all('a', href=True):
        url = atag.get('href')
        if not url.startswith("http") and "?" not in url and "@" not in link:
            print('urlfirst',url)
            # if url.startswith('http')
            directory = os.getcwd()
            url = urljoin(domain, url) 
            print(type(url))
            print('url',url)
            url = url.replace(url,getPath(url))
            print('urlhref',url)

    htm = soup.prettify() 
    print(type(htm))
    for i in s:
        htm+= "\n" +str(i)
        
    
    return htm.replace('&amp;', '&')
    

def get_links(driver, url):
    driver.get(url)
    time.sleep(5)
    links = []
    soup = BeautifulSoup(driver.page_source,"html.parser")
    
    for new_url in soup.find_all('a', href=True):
         new_url = new_url.get('href')
         new_url = urljoin(url, new_url) 
         links.append(new_url)
         


    return links

# ---

options = Options()
options.add_argument('--incognito')
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--profile-directory=Default")
driver = webdriver.Chrome("./chromedriver",options=options)
#driver = webdriver.Firefox()

# ---

domain = 'https://www.classcentral.com/' # to filter external links
start_url = 'https://www.classcentral.com/'
max_level = 1

links_visited = set([start_url])  # to test visited links
links_with_levels = [(start_url, 0)] # to control levels 

# ---

for link, level in links_with_levels:
    if level >= max_level:
        # print('skip:', level, link)
        continue

    print('visit:', level, link)

    links = get_links(driver, link)

    print('found:', len(links))
    links = list(set(links) - links_visited)
    print('after filtering:', len(links))

    level += 1

    for new_link in links:
        if new_link.startswith(domain): # filter external links
            links_visited.add(new_link)
            links_with_levels.append( (new_link, level) )

# ---
print('links_with_levels', links_with_levels)

for link, level in links_with_levels:

    html = translate_html_text(driver, link, domain)
    print('skip:', level, link)
    if "?" not in link and "@" not in link:
        final_url = link.strip().strip("/").rsplit('/', 1)
        # print(final_url)
        
        if final_url[0] == "https:/":
            os.makedirs("classCentral", exist_ok=True) 
            path = os.path.join("classCentral", "index.html").replace("\\","/")        
        else:
            folderPath = urlparse(final_url[0]).path
            os.makedirs(os.path.join("classCentral",  folderPath.strip('/')).replace("\\","/"), exist_ok=True)
            path = os.path.join("classCentral", folderPath.strip('/'), final_url[1] + ".html").replace("\\","/")
            
        with open(path, "w+", encoding='utf8') as file:
            file.write(html)
        print(path)