import requests
from bs4 import BeautifulSoup

url = 'https://www.benzinga.com/partner/forex/24/09/40791028/trading-strategies-and-mindsets-around-the-world-insights-from-india-south-asia-and-beyond-with-oct'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract Content
    article_body = soup.find('div', class_='article-content-body-only')  # Update the class name as per actual HTML
    if article_body:
        article_content = article_body.get_text(separator='\n', strip=True)
    else:
        article_content = ''

    # Print Extracted Information
    print("Content:")
    print(article_content)
else:
    print(f"Failed to retrieve the web page. Status code: {response.status_code}")
