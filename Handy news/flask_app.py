from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
from sqlalchemy import Table
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from random import randint
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsdatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db=SQLAlchemy(app)
def topnewsofcategories(business,entertainment,health,science,sports,technology):
	temp_results=[]
	results = []
	open_bbc_page = requests.get(business).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])

	open_bbc_page = requests.get(entertainment).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])
	open_bbc_page = requests.get(health).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])
	open_bbc_page = requests.get(science).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])
	open_bbc_page = requests.get(sports).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])
	open_bbc_page = requests.get(technology).json()
	ar = open_bbc_page["articles"]
	temp_results.append(ar[0]["title"])
	temp_results.append(ar[0]["urlToImage"])

	return temp_results;

def allurls():
	business=" https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	entertainment="https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	sports="https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	science="https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	health="https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	technology="https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	res=topnewsofcategories(business,entertainment,health,science,sports,technology)
	return res;

def authenticate(e, p):
    print(e)

    details=Login.query.filter_by(email=e).filter_by(password=p).all()
    print(details)
    if(len(details)>0):
        return True
    else:
        return False
def subscription(e):
	details= Login.query.filter_by(email=e).all()
	issubcribed=details[0].subscription
	if issubcribed=="False":
		return False
	else:
		return True

class Login(db.Model):
    # __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    password = db.Column(db.String(240))
    business=db.Column(db.Integer)
    entertainment=db.Column(db.Integer)
    science=db.Column(db.Integer)
    sports=db.Column(db.Integer)
    technology=db.Column(db.Integer)
    health=db.Column(db.Integer)
    subscription=db.Column(db.String(50))
    def __init__(self, email, password,business,entertainment,science,sports,technology,health,subscription):
    	self.email = email
    	self.password = password
    	self.business=business
    	self.entertainment=entertainment
    	self.science=science
    	self.sports=sports
    	self.technology=technology
    	self.health=health
    	self.subscription=subscription

db.create_all()

@app.route('/login',methods=['GET','POST'])
def login():


	error = None
	if request.method == 'POST':

		if(authenticate(request.form['username'], request.form['password'])):
		    session['logged_in'] = True
		    session['email'] = request.form['username']
		    subs_value=subscription(request.form['username'])

		    session['subscription']=subs_value


		    flash("You are logged in")
		    return redirect(url_for('index'))
		else:

			count1=Login.query.filter_by(email=request.form['username']).count()
			if(count1>0):
				error="passwords dont match"
			else:
				error='user does not exist'
	return render_template('login.html', error=error)

@app.route('/signup',methods=['GET','POST'])
def signup():
	error=None
	if request.method=='POST':
		email=request.form['username']
		password=request.form['password']
		conformpassword = request.form['conformpassword']
		user=Login(email=email,password=password,entertainment=0,sports=0,health=0,technology=0,business=0,science=0,subscription="False")
		count=Login.query.filter_by(email=email).count()

		if(count>0):
			error="User Already exists"
		else:
			if password!=conformpassword:
				error="passwords did not match"

			else:
				db.session.add(user)

				db.session.commit()
				return redirect(url_for('login'))

	return render_template('signup.html',error=error)




def apis(main_url):
	# fetching data in json format
	open_bbc_page = requests.get(main_url).json()

	# getting all articles in a string article
	article = open_bbc_page["articles"]

	# empty list which will
	# contain all trending news
	temp_results=[]
	results = []


	for ar in article:
		temp_results.append(ar["author"])
		temp_results.append(ar["title"])
		temp_results.append(ar["description"])
		temp_results.append(ar["url"])
		temp_results.append(ar["urlToImage"])
		temp_results.append(ar["publishedAt"])
		results.append(temp_results)
		temp_results=[]


	return results;
def texts(results):
	text1=""
	for i in range(len(results)):

			# printing all trending news
		text1=text1+results[i][1]+".    "
	return text1;
def mail():
	main_url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	results=apis(main_url)
	text1=""
	fromaddr = "handynews"

	msg = MIMEMultipart()
	msg['From'] = fromaddr

	msg['Subject'] = "Today's headlines"







	html="""
	<html>
	<head></head>
	<body>

	<a href="https://handynews.pythonanywhere.com"><h1 align="center">"""+results[0][1]+"\n"+"""</h1></a>
	<center><img src="""+results[0][4]+""" alt="W3Schools.com" style="width:500px;height:420px;"></center>

	<a href="https://handynews.pythonanywhere.com"><h1 align="center">"""+results[1][1]+"\n"+"""</h1></a>
	<center><img src="""+results[1][4]+""" alt="W3Schools.com" style="width:500px;height:420px;"></center>
	<a href="https://handynews.pythonanywhere.com"><h1 align="center">"""+results[2][1]+"\n"+"""</h1></a>
	<center><img src="""+results[2][4]+""" alt="W3Schools.com" style="width:500px;height:420px;"></center>



	</body
	</html>

	 """


	part1=MIMEText(html,'html')
	msg.attach(part1)



	print("hey")

	mail= smtplib.SMTP('smtp.gmail.com',587)
	mail.ehlo()
	mail.starttls()
	mail.login('handynewslive@gmail.com','team7@msit')
	details=Login.query.all()
	m=msg.as_string()
	for k in details:
		mail.sendmail('handynewslive@gmail.com',k.email,m)
		print(k.email)

	mail.close()
T7 = datetime.datetime.utcnow().strftime("%H:%M")
if T7=="18:33":
	mail()



@app.route("/",methods=['GET','POST'])
def index():
	error = None
	text=""
	i=10
	if request.method=='GET':
		main_url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)
		if session.get('logged_in') is not None:
			if session['logged_in'] == True:
				email=session['email']
				print("heyyy")
				print(email)

				maxview1=Login.query.filter_by(email=email).count()
				maxview=Login.query.filter_by(email=email).first()
				if maxview1 != 1:
					return render_template('index.html',results=results,text=text,text2="")




				bus=maxview.business
				et=maxview.entertainment
				sp=maxview.sports
				sc=maxview.science
				tech=maxview.technology
				he=maxview.health
				maxvalue=max(bus,et,sp,sc,tech,he)
				if(maxvalue==0):
					return render_template('index.html',results=results,text=text,text2="")



				l=[bus,et,sp,sc,tech,he]
				for i in range(len(l)):
					if(l[i]==maxvalue):
						break


		# main_url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		# results=apis(main_url)
		# text=texts(results)




		print(text.encode('utf-8'))
		if(i==0):
			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)
			text2=texts(resultsofbus)
			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i==1):

			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)

			text2=texts(resultsofbus)
			print("heyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
			print(text2)

			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i==2):
			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)
			text2=texts(resultsofbus)
			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i==3):
			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)
			text2=texts(resultsofbus)
			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i==4):
			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)
			text2=texts(resultsofbus)
			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i==5):
			main_url = " https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
			resultsofbus=apis(main_url)
			text2=texts(resultsofbus)
			return render_template('index.html',results=results,resultsofbus=resultsofbus,text=text,text2=text2)
		elif(i>5):
			tot_res=allurls()
			return render_template('index.html',results=results,resultsofbus=tot_res,text=text,text2="")
	else:
		search=request.form.get('search')
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)

		text=texts(results)
		if len(results)<=2:
			error="Search appropriate words"

		return render_template('search.html',results=results,error=error,text=text,text2="")


@app.route("/search")
def search():
	return render_template('search.html')

@app.route('/dropdown/<location>',methods=['GET','POST'])
def dropdown(location):
	error=None
	main_url="https://newsapi.org/v2/everything?q="+location+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	results=apis(main_url)
	if len(results)<=2:
		error="News not available to this region"
	return render_template('dropdown.html',results=results,error=error)

@app.route("/Business",methods=['GET','POST'])
def business():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.business+=1
			db.session.commit()
		main_url = " https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)

		print(text.encode('utf-8'))
		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)

@app.route("/Entertainment",methods=['GET','POST'])
def entertainment():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.entertainment+=1
			db.session.commit()
		main_url = " https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)
		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)

@app.route("/Health",methods=['GET','POST'])
def health():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.health+=1
			db.session.commit()
		main_url = "  https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)

		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)


@app.route("/Science",methods=['GET','POST'])
def science():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.science+=1
			db.session.commit()
		main_url = "   https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)

		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)

@app.route("/Sports",methods=['GET','POST'])
def sports():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.sports+=1
			db.session.commit()
		main_url = "  https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)

		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)

@app.route("/Technology",methods=['GET','POST'])
def technology():
	text=""
	error=None
	if request.method=='GET':
		if session.get('logged_in') is not None:
			email=session['email']
			for c in Login.query.filter_by(email=email).all():
				c.technology+=1
			db.session.commit()
		main_url = "   https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		text=texts(results)

		return render_template('business.html',results=results,text=text)
	else:
		search=request.form.get('search')
		if search=="":
			error="Type any keyword to search"
			results="xyz"
			text="abc"

			return render_template('search.html',error=error,results=results,text=text)
		main_url="https://newsapi.org/v2/everything?q="+search+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
		results=apis(main_url)
		if len(results)<=2:
			error="search appropriate words"

		return render_template('search.html',results=results,error=error,text=text)
@app.route('/voicesearch/<searchkey>')
def voicesearch(searchkey):
	error=None
	print(searchkey)

	main_url="https://newsapi.org/v2/everything?q="+searchkey+"&apiKey=6ec8815b88544b79866c52d90e7a1ed7"
	results=apis(main_url)
	text=texts(results)
	if len(results)<=2:
		error="search appropriate words"

	return render_template('search.html',results=results,error=error,text=text)

@app.route('/logout',methods=["GET"])
def logout():
	if not session:
		return redirect(url_for('index'))
	sessionclear()

	return redirect(url_for('index'))

def sessionclear():
	if not session:
		return redirect(url_for('index'))
	email = session['email']
	session.pop('logged_in', None)
	session.pop('email',None)
	session.pop('subscription',None)
	return
@app.route('/unsubscribe',methods=["GET"])
def unsubscribe():
	email=session['email']
	sub=Login.query.filter_by(email=email).all()
	sub[0].subscription="False"
	session['subscription']="False"
	db.session.commit()
	return redirect(url_for('index'))




@app.route('/subscribe',methods=["GET"])
def subscribe():
	email=session['email']
	sub=Login.query.filter_by(email=email).all()

	print(email)
	sub[0].subscription="True"
	session['subscription']='True'

	db.session.commit()
	fromaddr = "handynews"

	msg = MIMEMultipart()
	msg['From'] = fromaddr

	msg['Subject'] = "You are subscribed to handynewslive"
	html="""
	<html>
	<head></head>
	<body>
	<center>
	<img src="https://lh3.googleusercontent.com/-34SG-fESNBs/Wxfmyklex8I/AAAAAAAAQZE/pf7AzGaEImg3cjuHtDRR6vpdrMSpntkvACK8BGAs/s214/logo.png" alt="logo" height="150" width="150">
	<h1> Thank you for subscribing</h1>
	</center>
	</body
	</html>

	 """
	part1=MIMEText(html,'html')
	msg.attach(part1)
	mail= smtplib.SMTP('smtp.gmail.com',587)
	mail.ehlo()
	mail.starttls()
	mail.login('handynewslive@gmail.com','team7@msit')

	m=msg.as_string()
	mail.sendmail('handynewslive@gmail.com',email,m)
	mail.close()


	return redirect(url_for('index'))
@app.route('/gsignin/<gmail>/<pid>',methods=["GET","POST"])
def gsignin(gmail,pid):
	allemail= Login.query.filter_by(email=gmail).count()
	if allemail==0:
		user=Login(email=gmail,password=pid,entertainment=0,sports=0,health=0,technology=0,business=0,science=0,subscription="False")
		db.session.add(user)

		db.session.commit()

	subs_value=subscription(gmail)
	
	session['subscription']= subs_value
	session['logged_in'] = True
	session['email'] = gmail


	return redirect(url_for('index'))






if __name__ =='__main__':
	app.run(debug=True)


