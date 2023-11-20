import os
from flask import Flask, request, render_template, redirect, url_for, flash
from model3 import detect_text
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    UserMixin,
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz  # タイムゾーンをインポート

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cash.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = "./static/image"


# db.Modelの使い方を理解して
# save関数のところを修正
# save.htmlも修正


class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cash = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(30), unique=False, nullable=True)
    # user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    saved_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo"))
    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(120), unique=True)


with app.app_context():
    # db.drop_all()  # テーブルを削除
    # db.engine.execute("PRAGMA foreign_keys=on;")
    # Userテーブルを作成
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
# @login_required
def index():
    return render_template("home.html")


@app.route("/index")
@login_required
def scan():
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    try:
        if request.method == "POST":
            # username = request.form.get("username")
            # password = request.form.get("password ")

            user = User(
                username=request.form.get("username"),
                password=generate_password_hash(request.form.get("password")),
            )  # 256bitのランダムの数値を返す

            db.session.add(user)
            db.session.commit()
            return redirect("/login")
        else:
            return render_template("signup.html")
    except:
        flash("そのユーザー名はすでに使用されています", "error")
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            # if password == user.password:
            login_user(user)
            return redirect("/index")
        else:
            app.logger.error(f"Login failed for username: {username}")
            flash("パスワードが間違っています", "error")
            return redirect("/login")
            # return redirect("signup.html")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/upload", methods=["GET", "POST"])
# @login_required
def upload_user_files():
    try:
        if request.method == "POST":
            upload_file = request.files["upload_file"]
            img_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)
            upload_file.save(img_path)
            result = detect_text(img_path)
            return render_template("result.html", result=result, img_path=img_path)
    except:
        return render_template("index.html")


@app.route("/upload1", methods=["GET", "POST"])
# @login_required
def upload1_user_files():
    try:
        if request.method == "POST":
            upload_file = request.files["upload_file"]
            img_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)
            upload_file.save(img_path)
            return redirect("/index")
        else:
            return render_template("/index")
    except:
        return render_template("scan2.html")


@app.route("/create", methods=["GET", "POST"])
# @login_required
def create():
    # if request.method == "GET":
    # return render_template("create.html")
    if request.method == "POST":
        result = int(request.form.get("result"))
        # POSTリクエストからresultを取得
        # タイムゾーンを指定して現在の日時を取得
        # current_user = current_user
        current_time = datetime.now(pytz.timezone("Asia/Tokyo"))
        save = Save(
            cash=int(result),
            user_id=current_user.id,
            saved_at=current_time,
        )
        # saved_at=current_time
        # データベースに登録
        db.session.add(save)
        db.session.commit()
        return redirect(url_for("save"))  # /saveにリダイレク


@app.route("/save")
# @login_required
def save():
    # 全てのデータを取得
    # current_user = current_user
    # Flask-Loginを使用していると仮定
    saves = Save.query.filter_by(user_id=current_user.id).all()
    # saves = Save.query.all()
    return render_template("save.html", saves=saves)


@app.route("/calender_data")
# @login_required
def calendar_data():
    # データベースからデータを取得するクエリを実行
    # events = Save.query.all()
    try:
        events = Save.query.filter_by(user_id=current_user.id).all()

        # FullCalendarで必要な形式にデータを整形
        data = []
        date = events[0].saved_at.isoformat()[:10]
        sum = 0
        for event in events:
            if date == event.saved_at.isoformat()[:10]:
                sum += int(event.cash)
            else:
                data.append(
                    {
                        "title": f"合計使用額: {sum}円",
                        "start": date,
                        # ISO 8601形式で日時を表示
                    }
                )
                date = event.saved_at.isoformat()[:10]
                sum = int(event.cash)

            data.append(
                {
                    "title": f"使用金額: {event.cash}円",
                    "start": event.saved_at.isoformat()[:10],
                    # ISO 8601形式で日時を表示
                }
            )
        data.append(
            {
                "title": f"合計額: {sum}円",
                "start": date,
                # ISO 8601形式で日時を表示
            }
        )
        if len(data) != 0:
            return render_template("calender.html", data=data)
        else:
            return redirect(url_for("save"))
    except:
        return redirect(url_for("save"))


@app.route("/delete/<int:save_id>", methods=["POST"])
# @login_required
def delete(save_id):
    save_to_delete = Save.query.get(save_id)

    if save_to_delete:
        # 該当のIDのデータが存在する場合、削除
        db.session.delete(save_to_delete)
        db.session.commit()

    return redirect(url_for("save"))  # /saveにリダイレクト


@app.route("/scan2")
# @login_required
def scan2():
    return render_template("scan2.html")


if __name__ == "__main__":
    app.run(debug=True)
