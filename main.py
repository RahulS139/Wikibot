from flask import Flask, request, render_template
import string
import requests
from bs4 import BeautifulSoup as bs

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/wikibot', methods=['POST'])
def wikibot():
    enterinput = request.form['search']
    length = request.form['length']
    u_i = string.capwords(enterinput)
    word = " ".join(u_i.split())
    url = f"https://en.wikipedia.org/wiki/{word}"

    try:
        url_open = requests.get(url)
        url_open.raise_for_status()
    except requests.HTTPError as http_err:
        return render_template('index.html', error=f'HTTP error occurred: {http_err}')
    except requests.RequestException as req_err:
        return render_template('index.html', error=f'Request error occurred: {req_err}')
    except Exception as err:
        return render_template('index.html', error=f'Other error occurred: {err}')

    soup = bs(url_open.content, 'html.parser')
    details = soup.find('table', {'class': 'infobox'})
    if details is None:
        return render_template('index.html', error='Sorry No Data Found :(')

    result = ""
    rows = details.find_all('tr')
    for row in rows:
        heading = row.find('th')
        detail = row.find('td')
        if heading is not None and detail is not None:
            heading_text = heading.get_text().strip()
            detail_text = detail.get_text().strip()
            result += "{} :: {}\n".format(heading_text, detail_text)
        else:
            result += "\n"

    paragraphs = soup.find_all('p')
    num_paragraphs = len(paragraphs)

    if length == 'short':
        end = min(3, num_paragraphs)
    elif length == 'moderate':
        end = min(7, num_paragraphs)
    elif length == 'long':
        end = min(10, num_paragraphs)

    for i in range(1, end):
        paragraph = paragraphs[i]
        for sup in paragraph.find_all('sup', {'class': 'reference'}):
            sup.decompose()  # Remove reference links
        paragraph_text = paragraph.get_text().strip()
        result += "{}\n\n".format(paragraph_text)

    result = result.replace("<br>", "\n").replace("&nbsp;", " ").replace("&quot;", "\"")
    result = result.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")

    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
