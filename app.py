import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///content.db"
UPLOAD_FOLDER = "D:\Bharat Intern\Content Management\Static"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {
    # Image Extensions
    "jpg",
    "jpeg",
    "png",
    "gif",
    "bmp",
    "svg",
    "webp",
    "tiff",
    "ico",
    "jfif",
    "pjpeg",
    "pjp",
    # Video Extensions
    "mp4",
    "avi",
    "mkv",
    "mov",
    "wmv",
    "flv",
    "webm",
    "mpeg",
    "mpg",
    "3gp",
    "m4v",
    "f4v",
    "ogg",
    "qt",
    "swf",
    "vob",
    "rm",
    "rmvb",
    "m2v",
    "mxf",
    "mp2",
    "mpg2",
    "mpeg2",
    "mpe",
    "mpv",
    "mpg4",
    "divx",
    "dvd",
    "asf",
    "asx",
    "ts",
    "mts",
}

app.config["UPLOAD_FOLDER"] = os.path.join(APP_ROOT, UPLOAD_FOLDER)
db = SQLAlchemy(app)


class ContentManagement(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(3000), nullable=False)
    image = db.Column(db.String(500), default="None")
    video = db.Column(db.String(500), default="None")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["POST", "GET"])
def content_management():
    upload = False
    if request.method == "POST":
        print(request.method)
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        video = request.files["video"]

        if image.filename == "" and video.filename == "":
            cm = ContentManagement(
                title=title, content=content, image="Null", video="Null"
            )
            db.session.add(cm)
            db.session.commit()
            upload = True
            return render_template("index.html", upload=upload)

        elif (
            image.filename != ""
            and video.filename != ""
            and allowed_file(image.filename)
            and allowed_file(video.filename)
        ):
            filename_image = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_image))
            filename_video = secure_filename(video.filename)
            video.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_video))
            cm = ContentManagement(
                title=title,
                content=content,
                image=filename_image,
                video=filename_video,
            )
            db.session.add(cm)
            db.session.commit()
            upload = True
            return render_template("index.html", upload=upload)
            # print(os.path.join(app.config["UPLOAD_FOLDER"], filename_image))
        elif (
            image.filename != ""
            and video.filename == ""
            and allowed_file(image.filename)
        ):
            print(allowed_file(image.filename))
            filename_image = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_image))
            cm = ContentManagement(
                title=title,
                content=content,
                image=filename_image,
                video="Null",
            )
            db.session.add(cm)
            db.session.commit()
            upload = True
            return render_template("index.html", upload=upload)
        elif (
            image.filename == ""
            and video.filename != ""
            and allowed_file(video.filename)
        ):
            filename_video = secure_filename(video.filename)
            video.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_video))
            cm = ContentManagement(
                title=title,
                content=content,
                image="Null",
                video=filename_video,
            )
            db.session.add(cm)
            db.session.commit()
            upload = True
            return render_template("index.html", upload=upload)
        else:
            return render_template("index.html", upload=upload)
    # add to database for 3 conditions if both image and video are given if only image is given if only video is given or if none of them is given
    return render_template("index.html")


@app.route("/blog")
def blog():
    blogs = ContentManagement.query.all()
    return render_template("blog.html", blogs=blogs)


@app.route("/blog/delete/<int:sno>")
def delete(sno):
    cm = ContentManagement.query.filter_by(sno=sno).first()
    if cm.image != "Null":
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], cm.image))
    if cm.video != "Null":
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], cm.video))
    db.session.delete(cm)
    db.session.commit()
    return redirect("/blog")


@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.files["image"]
        video = request.files["video"]
        blog = ContentManagement.query.filter_by(sno=sno).first()
        blog.title = title
        blog.content = content
        if image.filename == "":
            if blog.image != "Null":
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], blog.image))
            blog.image = "Null"
        else:
            if allowed_file(image.filename):
                if blog.image != "Null":
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], blog.image))
                filename_image = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_image))
                blog.image = filename_image
            else:
                blog = ContentManagement.query.filter_by(sno=sno).first()
                return render_template("update.html", upload=False, blog=blog)
            # file type checking is remaining while updating
        if video.filename == "":
            if blog.video != "Null":
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], blog.video))
            blog.video = "Null"
        else:
            if allowed_file(video.filename):
                if blog.video != "Null":
                    os.remove(os.path.join(app.config["UPLOAD_FOLDER"], blog.video))
                filename_video = secure_filename(video.filename)
                video.save(os.path.join(app.config["UPLOAD_FOLDER"], filename_video))
                blog.video = filename_video
            else:
                blog = ContentManagement.query.filter_by(sno=sno).first()
                return render_template("update.html", upload=False, blog=blog)
            # file type checking is remaining while updating
        db.session.add(blog)
        db.session.commit()
        return redirect("/blog")

    blog = ContentManagement.query.filter_by(sno=sno).first()
    return render_template("update.html", blog=blog)


@app.route("/blog/view/<int:sno>")
def view(sno):
    blog = ContentManagement.query.filter_by(sno=sno).first()
    return render_template("view.html", blog=blog)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
