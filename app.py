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
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz  # タイムゾーンをインポート

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cash.db"
app.config["SECRET_KEY"] = os.urandom(24)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)

UPLOAD_FOLDER = "./static/image"


class Save(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cash = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    saved_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(pytz.timezone("Asia/Tokyo"))
    )
    bought_at = db.Column(db.String(20), nullable=True)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(120), unique=False)

    def change_password(self, new_password):
        self.password = generate_password_hash(new_password)


with app.app_context():
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
@login_required
def upload_user_files():
    if request.method == "POST":
        upload_file = request.files["upload_file"]
        img_path = os.path.join(UPLOAD_FOLDER, upload_file.filename)
        upload_file.save(img_path)
        result = detect_text(img_path)
        if result == None:
            flash("読み取りに失敗しました")
            redirect("/upload1")
        else:
            return render_template(
                "result.html", result=result[0], date=result[1], img_path=img_path
            )


@app.route("/upload1", methods=["GET", "POST"])
@login_required
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
@login_required
def create():
    if request.method == "POST":
        result = int(request.form.get("result"))
        date = request.form.get("date")
        # POSTリクエストからresultを取得
        # タイムゾーンを指定して現在の日時を取得
        # current_user = current_user
        current_time = datetime.now(pytz.timezone("Asia/Tokyo"))
        save = Save(
            cash=int(result),
            username=current_user.username,
            user_id=current_user.id,
            saved_at=current_time,
            bought_at=date,
        )
        # saved_at=current_time
        # データベースに登録
        db.session.add(save)
        db.session.commit()
        return redirect(url_for("save"))  # /saveにリダイレク


@app.route("/save")
@login_required
def save():
    # 全てのデータを取得
    # current_user = current_user
    # Flask-Loginを使用していると仮定
    saves = Save.query.filter_by(user_id=current_user.id).all()
    # saves = Save.query.all()
    return render_template("save.html", saves=saves)


@app.route("/calender_data")
@login_required
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
@login_required
def delete(save_id):
    save_to_delete = Save.query.get(save_id)

    if save_to_delete:
        # 該当のIDのデータが存在する場合、削除
        db.session.delete(save_to_delete)
        db.session.commit()

    return redirect(url_for("save"))  # /saveにリダイレクト


@app.route("/edit/<int:save_id>", methods=["GET", "POST"])
@login_required
def edit(save_id):
    save = Save.query.get(save_id)
    if request.method == "POST":
        if request.form["cash"] != save.cash and len(request.form["cash"]) != 0:
            save.cash = request.form["cash"]
            db.session.commit()
            return redirect(url_for("save"))
        else:
            return redirect(url_for("save"))
    else:
        return render_template("edit.html", save=save)


@app.route("/scan2")
@login_required
def scan2():
    return render_template("scan2.html")


# パスワードを変更する
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not check_password_hash(current_user.password, current_password):
            flash("現在のパスワードが正しくありません", "error")
            return render_template("change_password.html")

        if new_password != confirm_password:
            flash("新しいパスワードが一致しません", "error")
            return render_template("change_password.html")

        # Update the user's password
        current_user.change_password(new_password)
        db.session.commit()

        flash("パスワードが変更されました", "success")
        return redirect("/index")
    else:
        return render_template("change_password.html")


if __name__ == "__main__":
    app.run(debug=True)
