from flask import Flask, redirect, url_for, render_template, request, session, flash, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Gz9RWw4LDT'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(30), nullable=False)

    def __str__(self):
        return f'{self.id}, {self.username}, {self.email}, {self.password}, {self.gender}, {self.date}'


class Post_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    tweet_text = db.Column(db.String(30), nullable=False)
    time = db.Column(db.String(30), nullable=False)

    def __str__(self):
        return f'{self.id}, {self.username}, {self.email}, {self.tweet_text}, {self.time}'


# db.create_all()


# all_user = User_data.query.filter_by(email='natroshvilI@gmail.com').first()
# print(all_user)
# print(all_user.username)
# for each in all_user:
#     print(each.username)
#     if each.username == "":
#         print("test")


@app.route('/', methods=['POST', 'GET'])
def home_page():
    if "email" not in session:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            if email == "" or password == "":
                flash('Enter email and password !', 'validation_msg')
                return render_template('index.html')
            else:
                login_user = User_data.query.filter_by(email=email, password=password).first()
                print(login_user)
                if login_user is None:
                    flash('Couldn\'t find your account, wrong email or password, Try again ! ', 'validation_msg')
                    return render_template('index.html')
                else:
                    session['email'] = email
                    return redirect(url_for('feed'))
        else:
            return render_template('index.html')
    else:
        return redirect(url_for("feed"))


@app.route('/profile')
def profile():
    if "email" in session:
        user_info = User_data.query.filter_by(email=session['email']).first()
        user_name = user_info.username
        gender = user_info.gender
        date = user_info.date
        # print(user_info.gender)
        return render_template('profile.html', user_name=user_name, gender=gender, date=date)
    else:
        error_type = 'Session key not found !'
        return render_template('error_page.html', error_type=error_type)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        gender = str(request.form['gender'])
        date = str(request.form['date'])
        if username == "" or email == '' or password == '' \
                or gender == '' or date == '':
            flash("Please enter all fields!")
            return render_template('register.html')
        elif len(password) <= 8:
            flash("Password must be at least 8 characters!")
            return render_template('register.html')
        else:
            register_user = User_data.query.filter_by(email=email).first()
            # print(register_user)
            if register_user is not None:
                flash("Email already exists, Try again!")
                return render_template('register.html')
            else:
                new_user = User_data(username=username, email=email, password=password,
                                     gender=gender, date=date)
                db.session.add(new_user)
                db.session.commit()
                # login side
                session['email'] = email
                return redirect(url_for('feed'))
    else:
        return render_template('register.html')


@app.route('/feed')
def feed():
    if "email" in session:
        posts = Post_data.query.order_by(Post_data.id.desc()).all()

        # API - Weather
        url = "https://api.openweathermap.org/data/2.5/weather?" \
              "q=Tbilisi&" \
              "appid=2fc733a15fa2d4981de58f7462ddb75a&" \
              "units=metric"

        response = requests.get(url)
        # print(response)
        json_text = response.json()
        json_structured = json.dumps(json_text, indent=4)
        # print(json_structured)
        current_temp = json_text['main']['temp']
        return render_template('feed.html', posts=posts, current_temp=round(current_temp, 1))
    else:
        abort(404)


@app.route('/post', methods=['POST', 'GET'])
def post():
    if "email" in session:
        if request.method == 'POST':
            tweet_text = request.form['tweet_text']
            if tweet_text == "":
                flash('Box is clear!')
                return render_template("post.html")
            else:
                # print(tweet_text)
                user_info = User_data.query.filter_by(email=session['email']).first()

                user_name = user_info.username
                hours = 4
                hours_added = timedelta(hours = hours)
                now = datetime.now() + hours_added
                current_time = now.strftime("%H:%M")
                new_post = Post_data(username=user_name, email=session['email'],
                                     tweet_text=tweet_text, time=current_time)
                db.session.add(new_post)
                db.session.commit()
                return redirect(url_for("feed"))
        else:
            return render_template("post.html")
    else:
        abort(404)


@app.route('/logout')
def logout():
    if "email" in session:
        session.pop("email")
        return redirect(url_for("home_page"))
    else:
        abort(404)


@app.route('/edit_profile', methods=['POST', 'GET'])
def edit_profile():
    if "email" in session:
        if request.method == 'POST':
            user_input = request.form['update_name']
            pass_input = request.form['update_pass']
            if user_input == "" and pass_input == "":
                flash('You cant save clear boxes!')
                return render_template('edit_profile.html')
            elif user_input != '' and pass_input == '':
                old_user_info = User_data.query.filter_by(email=session['email']).first()
                old_user_info.username = user_input
                db.session.commit()
                return redirect(url_for('profile'))
            elif user_input == '' and pass_input != '':
                old_user_info = User_data.query.filter_by(email=session['email']).first()
                old_user_info.password = pass_input
                db.session.commit()
                return redirect(url_for('profile'))
            else:
                pass
        else:
            return render_template('edit_profile.html')
    else:
        abort(404)



@app.route('/<visit_profile>')
def user(visit_profile):
    # print(visit_profile)
    guest_profile = User_data.query.filter_by(email=visit_profile).first()
    username = guest_profile.username
    gender = guest_profile.gender
    birthdate = guest_profile.date
    return render_template('visit_profile.html', username=username,
                           gender=gender, birthdate=birthdate)


@app.errorhandler(404)
def page_not_found(e):
    error_type = e
    return render_template('error_page.html', error_type=e)


if __name__ == '__main__':
    app.run(debug=True)
