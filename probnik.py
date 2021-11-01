from library import *

url = 'https://coinmarketcap.com/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
quotes_price = soup.find_all("a", class_="cmc-link")
quotes_name = soup.find_all("p", class_="q7nmo0-0 krbrab coin-item-symbol")

result_name = [elem.text for elem in quotes_name[9::]]
result_price_usd = [float(q.text[1:].replace(",", "")) for q in quotes_price[66:104:4]]

dct_crypto_price = {}
for i in range(10):
    dct_crypto_price[result_name[i]] = result_price_usd[i]

print(dct_crypto_price)
