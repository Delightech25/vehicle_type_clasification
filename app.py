from flask import Flask, render_template, request, redirect, url_for, session
import tensorflow as tf
import numpy as np
import os, requests
from tensorflow.keras.preprocessing import image

app = Flask(__name__)
app.secret_key = "vehicle123"

model = tf.keras.models.load_model("model.h5")

classes = [
    'bike_heavy','bike_normal',
    'bus_heavy','bus_normal',
    'car_heavy','car_normal',
    'motorcycle_heavy','motorcycle_normal',
    'truck_heavy','truck_normal'
]

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------- REGISTER --------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        with open("users.txt","a") as f:
            f.write(f"{u},{p}\n")
        return redirect(url_for("login"))
    return render_template("register.html")

# -------- LOGIN --------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        with open("users.txt","r") as f:
            users = f.readlines()
        for user in users:
            uu,pp = user.strip().split(",")
            if uu==u and pp==p:
                session["user"] = u
                return redirect(url_for("upload"))
    return render_template("login.html")

# -------- UPLOAD & PREDICT --------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None

    if request.method == "POST":
        path = None

        # File upload
        if request.files["file"].filename != "":
            file = request.files["file"]
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

        # URL upload
        if request.form["url"] != "":
            url = request.form["url"]
            r = requests.get(url)
            filename = url.split("/")[-1]
            path = os.path.join(UPLOAD_FOLDER, filename)
            with open(path,"wb") as f:
                f.write(r.content)

        if path:
            img = image.load_img(path, target_size=(224,224))
            img = image.img_to_array(img)/255.0
            img = np.expand_dims(img, axis=0)

            pred = model.predict(img)
            label = classes[np.argmax(pred)]
            vehicle, load = label.split("_")
            result = f"Vehicle: {vehicle.upper()} | Load: {load.upper()}"

    return render_template("upload.html", result=result)

@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)