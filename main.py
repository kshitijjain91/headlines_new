from flask import Flask
import feedparser

app = Flask(__name__)
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
                'cnn': 'http://rss.cnn.com/rss/edition.rss',
                'fox': 'http://feeds.foxnews.com/foxnews/latest',
                'iol': 'http://www.iol.co.za/cmlink/1.640'}




@app.route("/")
@app.route("/<publication>")
def get_news(publication = "bbc"):
    feed = feedparser.parse(RSS_FEEDS[publication])
    first_article = feed['entries'][0]
    return '''<html>
     <body>
       <h1>BBC headlines</h1>
       <p>{0}</p>
       <p>{1}</p>
       <p>{2}</p>
       <br>
     </body>
     </html>'''.format(first_article.get("title"), first_article.get("published"), first_article.get("summary"))



if __name__ == '__main__':
    app.run(port=5000, debug=True)