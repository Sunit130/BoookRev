import os
import re
import requests
from flask import jsonify
from xml.etree import ElementTree
from flask import Flask, session, render_template, request, redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = "n7-mSfZoBBzXTZk59t4GKw"
Session(app)

engine = create_engine("postgres://zonlblmamoyibe:6a0a05b3e1d75d8eeb66e87d4413441cecc9c74243ffe878db9aadb05f9dddaa@ec2-54-211-210-149.compute-1.amazonaws.com:5432/dd840rgbb924lt")
db = scoped_session(sessionmaker(bind = engine))



##############################      INDEX      ###############################
@app.route("/")
def index():
    query ="SELECT books.isbn, books.title, books.author, books.year, images.url from books, images where books.isbn = images.isbn and year > 2015 limit 5"
    isbn = db.execute(query).fetchall()

    if session.get("username") is None:
        return render_template("INDEX.html",login=False, isbn=isbn)
    else:
        return render_template("index.html",login=True, isbn=isbn, username = session.get("username")[0][0])





##############################      LOGIN      ###############################
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("username") is None:
        return render_template("login.html")
    else:
        return "Already Signed in"
    # if session.get("USERNAME") is None:
    #     return render_template("login.html")
    # else:
    #     return "Already sign_in"





############################      LOGIN SUBMIT     #############################
@app.route("/login_submit", methods=["POST"])
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")
    fill = db.execute("select user_name from register where user_name= :username and password= :password",
                    {"username":username, "password":password}).fetchall()
    if(len(fill) != 0):
        session["username"] = fill
        return redirect('/')
    else:
        return "Username or Password didn't matched "





##############################      LOGOUT      ###############################
@app.route("/logout", methods=["GET","POST"])
def logout():
    session.pop("username", None)
    return redirect('/')





#############################      REGISTER      ##############################
@app.route("/register", methods=["GET", "POST"])
def register():

    if(request.method == "GET"):
        return render_template("register.html")

    fname = request.form.get("first_name")
    lname = request.form.get("last_name")
    username = request.form.get("username")
    password = request.form.get("password")
    cpassword = request.form.get("cpassword")

    fill = db.execute("select * from register where user_name= :username ",{"username":username}).fetchall()
    alreadyOccupied = False
    if(len(fill) != 0):
        alreadyOccupied = True
    push = True
    for e in password:
        if(e=="'" or e=='"' or e==" "):
            push = False
    if(fname=="" or lname=="" or username=="" or password=="" or password!=cpassword or alreadyOccupied==True or len(password)>32 or len(password)<7):
        push = False
        return render_template("completeRegistration.html",fname=fname,lname=lname,username=username,password=password,cpassword=cpassword,push=push,alreadyOccupied=alreadyOccupied)

    db.execute("INSERT INTO register (first_name, last_name, user_name, password) values (:first_name, :last_name, :user_name, :password)",
    {"first_name":fname, "last_name":lname, "user_name":username, "password":password})
    db.commit()
    return render_template("completeRegistration.html",fname=fname,lname=lname,username=username,password=password,cpassword=cpassword,push=push)





##############################      SEARCH      ###############################
@app.route('/search', methods=["POST"])
def search():
    str = request.form.get("search_bar")
    # "select books.isbn, books.title, books.author, books.year, images.url from books, images where books.isbn = images.isbn"
    query ="SELECT books.isbn, books.title, books.author, books.year, images.url from books, images where (books.isbn LIKE '%(pl)s' or books.title LIKE '%(pl)s' or books.author LIKE '%(pl)s') and books.isbn = images.isbn"
    isbn = db.execute(query % {'pl': '%' + str + '%'}).fetchall()
    # images = {}
    # for e in isbn:
    #     query ="https://www.goodreads.com/book/isbn/ISBN?format=xml"
    #     query = query.replace("ISBN",e[0])
    #     res = requests.get(query, params={"key":"otbDB4eqXRlXE2RQeAA"})
    #     string_xml = res.content
    #     tree = ElementTree.fromstring(string_xml)
    #     img = tree.findall('book/image_url')[0].text
    #     images[e[0]] = img
    if session.get("username") is None:
        return render_template("search.html",login=False, isbn=isbn)
    else:
        return render_template("search.html",login=True, isbn=isbn, username = session.get("username")[0][0])





###########################      Searched book      ############################
@app.route('/search/<string:isbn>')
def book(isbn):
    recived_isbn = isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "otbDB4eqXRlXE2RQeAA", "isbns": recived_isbn})
    final_isbn = recived_isbn

    data = res.json()
    avg = data["books"][0]["average_rating"]
    cnt = data["books"][0]["work_ratings_count"]

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn }).fetchall()

    query ="https://www.goodreads.com/book/isbn/ISBN?format=xml"
    query = query.replace("ISBN",isbn)
    res = requests.get(query, params={"key":"otbDB4eqXRlXE2RQeAA"})
    string_xml = res.content
    tree = ElementTree.fromstring(string_xml)
    img = tree.findall('book/image_url')[0].text
    disc = tree.findall('book/description')[0].text
    if disc is not None:
        disc = re.sub(r"<.*?>", " ", disc)
    reviews = db.execute("SELECT * FROM reviews WHERE isbn= :isbn",{"isbn":isbn}).fetchall()

    if session.get("username") is None:
        user_review = []
    else:
        user_review = db.execute("SELECT user_name FROM reviews WHERE isbn= :isbn and user_name=:user_name",{"isbn":isbn, "user_name":session.get("username")[0][0]}).fetchall()
    allowed = False
    if len(user_review)==0:
        allowed = True

    if session.get("username") is None:
        return render_template("book.html",avg=avg, cnt=cnt, reviews=reviews,book=book, login=False, isb=final_isbn, img=img, disc=disc, allowed=allowed)
    else:
        return render_template("book.html",avg=avg, cnt=cnt, reviews=reviews,book=book, login=True,isb=final_isbn, img=img,disc=disc,allowed=allowed, username = session.get("username")[0][0])





##############################      review      ###############################
@app.route('/reviews/<string:isbn>', methods=["POST"])
def reviews(isbn):
    ib = isbn
    un = session.get("username")[0][0]
    ra = request.form['rating']
    re = request.form['review']
    db.execute("INSERT INTO reviews values (:ib, :un, :ra, :re)", {"ib":ib, "un":un, "ra":ra, "re":re})
    db.commit()
    return redirect(url_for('book', isbn=ib))
    # fill = db.execute("select * from reviews").fetchall()
    # return render_template("temp1.html",isbn=(ib), user_name=(un),rating=(ra), review=(re), fill=fill)





################################      API      #################################

@app.route('/api/<string:isbn>')
def api(isbn):

    res = db.execute("select * from books where isbn= :isbn",{"isbn":isbn}).fetchall()
    isbn = res[0][0]
    title = res[0][1]
    author = res[0][2]
    year = res[0][3]
    res1 = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "otbDB4eqXRlXE2RQeAA", "isbns":isbn})
    data = res1.json()
    avg = data["books"][0]["average_rating"]
    cnt = data["books"][0]["work_ratings_count"]
    return jsonify(
        {
            "title": title,
            "author": author,
            "year": year,
            "isbn": isbn,
            "review_count": cnt,
            "average_score": avg
        }
    )
    # return render_template("temp1.html",isbn=isbn,title=title,author=author, year=year,avg=avg,cnt=cnt)


# {
#     "title": "Memory",
#     "author": "Doug Lloyd",
#     "year": 2015,
#     "isbn": "1632168146",
#     "review_count": 28,
#     "average_score": 5.0
# }


# def main():
#
#
# if __name__ == "__main__":
#     main()
