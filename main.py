from flask import Flask, render_template, redirect, request, jsonify, session, send_from_directory, make_response, send_from_directory
import sqlite3
import random
import string
import os


app = Flask(__name__)
app.secret_key = str(hash("hagfs bcgds bgsgvbag gggggs"))


# normal functions

def checkLoggin(username, password):
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute("SELECT * FROM Users")
    for i in cursor:
        if username == i[1] and password == i[2]:
            return True
    return False


def checkIfLoggedIn(s):
    isloggedin = "loggedin" in s.keys()
    if isloggedin:
        isloggedin = s["loggedin"]
        if isloggedin:
            try:
                isloggedin = checkLoggin(s["username"], s["password"])
            except:
                isloggedin = False
    else:
        isloggedin = False
    return isloggedin


def generateRandomPostId():
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    random.shuffle(characters)
    password = []
    for i in range(20):
        password.append(random.choice(characters))
    random.shuffle(password)
    final = int(hash("".join(password)))
    if final < 0:
        final *= -1
    return final


# get

@app.route("/")
def index():
    isloggedin = checkIfLoggedIn(session)
    return render_template("mainPage.html", isloggedin=isloggedin)


@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/service-worker.js') 
def sw():
    response = make_response(send_from_directory(path='static', directory='static', filename='service-worker.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response


@app.route("/sub")
@app.route("/sub/")
def sub():
    return redirect("/")


@app.route("/sub/<string:subName>")
def subRoute(subName):
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute(f"SELECT Name FROM Subs WHERE Name = '{subName}'")
    conn.commit()
    names = list(map(lambda x: x[0], cursor.fetchall()))
    cursor = conn.execute(f"SELECT * FROM Posts WHERE Sub = '{subName}'")
    conn.commit()
    posts = list(cursor.fetchall())
    print(posts)
    if len(names) == 1:
        return render_template("subPage.html", isloggedin=isloggedin, subName=names[0], posts=posts)
    else:
        return redirect("/errorPage/sub-not-exist")


@app.route("/sub/<string:subName>/<int:postId>")
def postRoute(subName="", postId=""):
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute(f"SELECT Name FROM Subs WHERE Name = '{subName}'")
    conn.commit()
    names = list(map(lambda x: x[0], cursor.fetchall()))
    if len(names) == 1:
        cursor = conn.execute(f"SELECT PostId FROM Posts WHERE Sub = '{subName}'")
        conn.commit()
        ids = list(map(lambda x: x[0], cursor.fetchall()))
        if postId in ids:
            cursor = conn.execute(f"SELECT * FROM Posts WHERE PostId = '{postId}'")
            conn.commit()
            return render_template("postPage.html", isloggedin=isloggedin, subName=subName, post=cursor.fetchone())
    return redirect("/errorPage")


@app.route("/user")
@app.route("/user/")
def user():
    return redirect("/")


@app.route("/user/<string:username>")
def userPage(username=""):
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False
    if username == "":
        return redirect("/")
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute(f"SELECT * FROM Users WHERE Username = '{username}'")
    conn.commit()
    user = cursor.fetchone()
    if user is None:
        return redirect("/errorPage/user-not-found")
    cursor = conn.execute(f"SELECT * FROM Posts WHERE Poster = '{username}'")
    conn.commit()
    posts = cursor.fetchall()
    return render_template("userPage.html", isloggedin=isloggedin, user=user, posts=posts)


@app.route("/createNewSub")
def createNewSub():
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False
    if isloggedin:
        return render_template("createNewSubPage.html", isloggedin=isloggedin)
    return redirect("/errorPage/you-need-to-log-in-to-enter-this-page")


@app.route("/errorPage")
@app.route("/errorPage/<string:type_>")
def errorPage(type_=""):
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False

    if type_ == "sub-already-exist":
        return render_template("errorPage.html", titel="sub already exist", message="sub already exist", isloggedin=isloggedin)
    elif type_ == "sub-not-exist":
        return render_template("errorPage.html", titel="sub not exist", message="sub not exist", isloggedin=isloggedin)
    elif type_ == "post-not-exist":
        return render_template("errorPage.html", titel="post not exist", message="post not exist", isloggedin=isloggedin)
    elif type_ == "item-not-found":
        return render_template("errorPage.html", titel="item not found", message="item not found", isloggedin=isloggedin)
    elif type_ == "email-in-use":
        return render_template("errorPage.html", titel="email in use", message="email in use", isloggedin=isloggedin)
    elif type_ == "user-not-found":
        return render_template("errorPage.html", titel="user not found", message="user not found", isloggedin=isloggedin)
    elif type_ == "username-is-already-taken":
        return render_template("errorPage.html", titel="username is already taken", message="username is already taken", isloggedin=isloggedin)
    elif type_ == "you-need-to-log-in-to-enter-this-page":
        return render_template("errorPage.html", titel="you need to log in to enter this page", message="you need to log in to enter this page", isloggedin=isloggedin)
    elif type_ == "there-is-missed-information":
        return render_template("errorPage.html", titel="there is missed information", message="there is missed information, fill the form again", isloggedin=isloggedin)
    return render_template("errorPage.html", titel="an error accured please try again", message="an error accured please try again", isloggedin=isloggedin)


@app.route("/successPage/<string:type_>")
def successPage(type_=""):
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False

    if type_ == "sub-was-created":
        return render_template("successPage.html", titel="sub was created", message="sub was created", isloggedin=isloggedin)
    elif type_ == "user-was-created":
        return render_template("successPage.html", titel="user was created", message="user was created", isloggedin=isloggedin)
    elif type_ == "post-was-uploaded":
        return render_template("successPage.html", titel="post was uploaded", message="post was uploaded", isloggedin=isloggedin)
    return redirect("/errorPage")


@app.route("/createNewUser")
def createNewUser():
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False

    return render_template("createNewUserPage.html", isloggedin=isloggedin)


@app.route("/logInPage")
def logInPage():
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        isloggedin = session["loggedin"]
    else:
        isloggedin = False
    return render_template("logInPage.html", isloggedin=isloggedin)


# post


@app.route("/createSub", methods=["POST"])
@app.route("/createSub/<string:subName>", methods=["POST"])
@app.route("/createSub/<string:subName>/<string:creator>", methods=["POST"])
@app.route("/createSub/<string:subName>/<string:creator>/<string:type_>", methods=["POST"])
def createSub(subName="", creator="", type_=""):
    conn = sqlite3.connect("db/forum.db")
    isloggedin = checkIfLoggedIn(session)
    if not isloggedin:
        return "/errorPage", 502
    if subName == "" or creator == "":
        return "/errorPage", 502
    cursor = conn.execute("SELECT Name FROM Subs")
    names = map(lambda x: x[0], cursor.fetchall())
    if subName in names:
        return "/errorPage/sub-already-exist", 502
    cursor = conn.execute("INSERT INTO Subs VALUES (?, ?, ?)", (subName, type_, creator))
    conn.commit()
    return "/successPage/sub-was-created", 200

@app.route("/createUser", methods=["POST"])
@app.route("/createUser/<string:email>", methods=["POST"])
@app.route("/createUser/<string:email>/<string:username>", methods=["POST"])
@app.route("/createUser/<string:email>/<string:username>/<string:password>", methods=["POST"])
def createUser(email="", username="", password=""):
    if email == "" or username == "" or password == "":
        return "you need to fill ol the form", 405
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute("SELECT * FROM Users")
    for i in cursor:
        print(i)
        if email == i[0]:
            return "/errorPage/email-in-use", 405
        elif username == i[1]:
            return "/errorPage/username-is-already-taken", 405
    cursor = conn.execute("INSERT INTO Users VALUES (?, ?, ?)", (email, username, password))
    conn.commit()
    return "/successPage/user-was-created"


@app.route("/logIn", methods=["POST"])
@app.route("/logIn/<string:username>", methods=["POST"])
@app.route("/logIn/<string:username>/<string:password>", methods=["POST"])
def logIn(username="", password=""):
    if username == "" or password == "":
        return "you need to fill ol the form", 405
    isOk = checkLoggin(username, password)
    if isOk:
        session["loggedin"] = True
        session["username"] = username
        session["password"] = password
        return "you logged in"
    return "username or password is incorrect"


@app.route("/logout", methods=["POST"])
def logout():
    isloggedin = checkIfLoggedIn(session)
    if isloggedin:
        session["loggedin"] = False
        session.pop("username", None)
        session.pop("password", None)
        return "loged out"
    return "there was a problem"


@app.route("/createPost", methods=["POST"])
@app.route("/createPost/<string:sub>", methods=["POST"])
@app.route("/createPost/<string:sub>/<string:username>", methods=["POST"])
@app.route("/createPost/<string:sub>/<string:username>/<string:head>", methods=["POST"])
@app.route("/createPost/<string:sub>/<string:username>/<string:head>/<string:body>", methods=["POST"])
def createPost(sub="", username="", head="", body=""):
    isloggedin = checkIfLoggedIn(session)
    if not isloggedin:
        return "/errorPage/you-need-to-log-in-to-enter-this-page", 405
    if sub == "" or username == "" or head == "":
        return "/errorPage/there-is-missed-information", 405
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute("SELECT Name FROM Subs")
    conn.commit()
    subs = list(map(lambda x: x[0], cursor.fetchall()))
    print(subs)
    if sub not in subs:
        return "/errorPage/sub-not-exist", 405
    postId = generateRandomPostId()
    cursor = conn.execute("SELECT PostId FROM Posts")
    conn.commit()
    print(cursor.fetchall())
    while postId in cursor.fetchall():
        postId = generateRandomPostId()
    cursor = conn.execute("INSERT INTO Posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (postId, head, body, username, sub, 0, 0, "", ""))
    conn.commit()
    return "/successPage/post-was-uploaded", 200
    

@app.route("/like/<int:postId>/<string:likedBy>", methods=["POST"])
def like(postId="", likedBy=""):
    isloggedin = checkIfLoggedIn(session)
    if not isloggedin:
        return "/errorPage/you-need-to-log-in-to-enter-this-page", 405
    if postId == "" or likedBy == "":
        return "/errorPage/there-is-missed-information", 405
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute("SELECT PostId FROM Posts")
    conn.commit()
    postsIds = list(map(lambda x: x[0], cursor.fetchall()))
    if postId not in postsIds:
        return "/errorPage/post-not-exist", 405
    cursor = conn.execute(f"SELECT Likes FROM Posts WHERE PostId={postId}")
    conn.commit()
    likes = cursor.fetchone()[0]
    cursor = conn.execute(f"SELECT LikedBy FROM Posts WHERE PostId={postId}")
    conn.commit()
    likedBy = cursor.fetchone()[0].split(",")
    if session["username"] in likedBy:
        return "you liked already", 405
    likes += 1
    likedBy.append(session["username"])
    cursor = conn.execute(f"SELECT DisLikes FROM Posts WHERE PostId={postId}")
    conn.commit()
    disLikes = cursor.fetchone()[0]
    cursor = conn.execute(f"SELECT DisLikedBy FROM Posts WHERE PostId={postId}")
    conn.commit()
    disLikedBy = cursor.fetchone()[0].split(",")
    if session["username"] in disLikedBy:
        disLikedBy.remove(session["username"])
        disLikes -= 1
    likedBy = ",".join(likedBy)
    disLikedBy = ",".join(disLikedBy)
    cursor = conn.execute(f"""
        UPDATE Posts
        SET Likes = {likes}, LikedBy = "{likedBy}", DisLikes = {disLikes}, DisLikedBy = "{disLikedBy}"
        WHERE PostId = {postId};
    """)
    conn.commit()
    return "liked"


@app.route("/disLike/<int:postId>/<string:likedBy>", methods=["POST"])
def diLike(postId="", likedBy=""):
    isloggedin = checkIfLoggedIn(session)
    if not isloggedin:
        return "/errorPage/you-need-to-log-in-to-enter-this-page", 405
    if postId == "" or likedBy == "":
        return "/errorPage/there-is-missed-information", 405
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute("SELECT PostId FROM Posts")
    conn.commit()
    postsIds = list(map(lambda x: x[0], cursor.fetchall()))
    if postId not in postsIds:
        return "/errorPage/post-not-exist", 405
    cursor = conn.execute(f"SELECT Likes FROM Posts WHERE PostId={postId}")
    conn.commit()
    likes = cursor.fetchone()[0]
    cursor = conn.execute(f"SELECT LikedBy FROM Posts WHERE PostId={postId}")
    conn.commit()
    likedBy = cursor.fetchone()[0].split(",")
    if session["username"] in likedBy:
        likes -= 1
        likedBy.remove(session["username"])
    cursor = conn.execute(f"SELECT DisLikes FROM Posts WHERE PostId={postId}")
    conn.commit()
    disLikes = cursor.fetchone()[0]
    cursor = conn.execute(f"SELECT DisLikedBy FROM Posts WHERE PostId={postId}")
    conn.commit()
    disLikedBy = cursor.fetchone()[0].split(",")
    if session["username"] in disLikedBy:
        return "you disliked already", 405
    disLikedBy.append(session["username"])
    disLikes += 1
    likedBy = ",".join(likedBy)
    disLikedBy = ",".join(disLikedBy)
    cursor = conn.execute(f"""
        UPDATE Posts
        SET Likes = {likes}, LikedBy = "{likedBy}", DisLikes = {disLikes}, DisLikedBy = "{disLikedBy}"
        WHERE PostId = {postId};
    """)
    conn.commit()
    return "disliked"


@app.route("/search/<string:wts>", methods=["POST"])
def search(wts=""):
    if wts == "":
        return "/errorPage/item-not-found"
    conn = sqlite3.connect("db/forum.db")
    cursor = conn.execute(f"SELECT Name FROM Subs WHERE Name = '{wts}'")
    conn.commit()
    name = cursor.fetchone()
    if not name is None:
        return "/sub/" + wts
    cursor = conn.execute(f"SELECT Username FROM Users WHERE Username = '{wts}'")
    conn.commit()
    name = cursor.fetchone()
    if not name is None:
        return "/user/" + wts
    cursor = conn.execute(f"SELECT * FROM Posts WHERE PostId = '{wts}'")
    conn.commit()
    name = cursor.fetchone()
    if not name is None:
        return "/sub/" + name[4] + "/" + wts
    return "/errorPage/item-not-found"



app.run(host="localhost", port=8080, debug=True) # #  https:, ssl_context='adhoc')
