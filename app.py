from flask import Flask,redirect,session
import tweepy
from flask import request
from flask import render_template
from flask_mysqldb import MySQL

from constants import *


app = Flask(__name__)
app.secret_key = "3242342342"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'user_token'
mysql = MySQL(app)


# @app.route('/auth')
@app.route('/')
def auth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(url)
    

@app.route('/callback')
def twitter_callback():
    request_token = session['request_token']
    print(request_token)
    del session['request_token']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    print(verifier)
    auth.get_access_token(verifier)
    session['token'] = (auth.access_token, auth.access_token_secret)
    print(session['token'])
    return redirect('/app')

@app.route('/app')
def request_twitter():
    try:
        
        token, token_secret = session['token']
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
        
        auth.set_access_token(token, token_secret)
        api = tweepy.API(auth)
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_login where access_token = %s",(token,))


        data = cursor.fetchall()
        print(f'data: {data}')
        if (len(data)==0):
            cursor.execute("INSERT INTO user_login (access_token, access_token_secret) VALUES (%s, %s)", (token, token_secret))
            mysql.connection.commit()
            api.retweet(get_last_tweet(username_for_last_tweet)) 

        
        
        cursor.close()



        
        return render_template('index.html')
    except Exception as e:
        return render_template('rt.html')


def get_last_tweet(screen_name):
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    public_tweets =api.user_timeline(screen_name=screen_name ,count=1, tweet_mode="extended")

    print(public_tweets[0].id)
    return public_tweets[0].id



    

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=30006, debug=True)