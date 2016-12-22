from flask import Flask
from flask import render_template
from flask import request
import feedparser
import json, requests
from bs4 import BeautifulSoup

app = Flask(__name__)
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
                'cnn': 'http://rss.cnn.com/rss/edition.rss',
                'fox': 'http://feeds.foxnews.com/foxnews/latest',
                'iol': 'http://www.iol.co.za/cmlink/1.640'}

api_url = "http://api.openweathermap.org/data/2.5/forecast/city?id=524901&APPID=228934117c8d0dffbd1cbbba41c34b4b"
res_weather = requests.get(api_url)
try:
    res_weather.raise_for_status()
except Exception as exc:
    print('There was an error in download {0}'.format(exc))

weather_soup = BeautifulSoup(res_weather.text, 'html.parser')

DEFAULTS = {'publication': 'bbc', 'city':'London'}

@app.route("/")
def home():
    # get publication based on user input
    publication = request.args.get("publication")
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)

    # get weather based on city
    city = request.args.get("city")
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    return  render_template("home.html",
        articles = articles,
        weather_dict = weather)



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


if __name__ == '__main__':
    app.run(port=5000, debug=True)