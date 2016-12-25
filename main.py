from flask import Flask, render_template, request
from flask import make_response
import datetime
import feedparser
import json, requests
from bs4 import BeautifulSoup

app = Flask(__name__)
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
                'cnn': 'http://rss.cnn.com/rss/edition.rss',
                'fox': 'http://feeds.foxnews.com/foxnews/latest',
                'iol': 'http://www.iol.co.za/cmlink/1.640'}

api_url = "http://api.openweathermap.org/data/2.5/forecast/city?id=524901&APPID=228934117c8d0dffbd1cbbba41c34b4b"
currency_url = "https://openexchangerates.org/api/latest.json?app_id=59379dbb1b7743b19daa017bcdbf264e"
res_weather = requests.get(api_url)
try:
    res_weather.raise_for_status()
except Exception as exc:
    print('There was an error in download {0}'.format(exc))

weather_soup = BeautifulSoup(res_weather.text, 'html.parser')

DEFAULTS = {'publication': 'bbc', 'city':'London', 'currency_from':'GBP', 'currency_to':'USD'}

@app.route("/")
def home():
    # get publication based on user input
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)

    # get weather based on city
    city = get_value_with_fallback("city")
    weather = get_weather(city)


    # get currency exchange rates based on user input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")

    rate, currencies = get_rate(currency_from, currency_to)
    response = make_response(render_template("home.html",
        articles = articles,
        weather_dict = weather, currency_from = currency_from,
        currency_to = currency_to, rate = rate,
        currencies = currencies))
    expires = datetime.datetime.now() + datetime.timedelta(days = 365)
    #setting cookies to remember publication, city and currency_to/from
    response.set_cookie("publication", publication, expires = expires)
    response.set_cookie("city", city, expires =expires)
    response.set_cookie("currency_to", currency_to, expires = expires)
    response.set_cookie("currency_from", currency_from, expires = expires)
    return response

# fallback logic for getting input, cookie or default
def get_value_with_fallback(key):
        if request.args.get(key):
            return request.args.get(key)
        if request.cookies.get(key):
            return request.cookies.get(key)
        return DEFAULTS[key]




def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
      publication = DEFAULTS['publication']
    else:
      publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(city):
    api_key = "228934117c8d0dffbd1cbbba41c34b4b"
    api_base= "http://api.openweathermap.org/data/2.5/weather?q="
    api_url = api_base + city + "&appid=" + api_key
    res_weather = requests.get(api_url)
    try:
        res_weather.raise_for_status()
    except Exception as exc:
        print('There was an error in download {0}'.format(exc))

    weather_soup = BeautifulSoup(res_weather.text, 'html.parser')
    weather_dict = json.loads(str(weather_soup))
    return weather_dict



def get_rate(frm, to):
    res_currency = requests.get(currency_url)
    try:
        res_currency.raise_for_status()
    except Exception as exc:
        print("An error occured while fetching currency rates: {0}".format(exc))

    currency_soup = BeautifulSoup(res_currency.text, 'html.parser')
    currency_dict =json.loads(str(currency_soup))

    frm_value = currency_dict.get('rates')[frm.upper()]
    to_value = currency_dict.get('rates')[to.upper()]
    return (round(to_value/frm_value, 2), currency_dict['rates'].keys())

if __name__ == '__main__':
    app.run(port=5000, debug=True)

# weather api: 59379dbb1b7743b19daa017bcdbf264e
