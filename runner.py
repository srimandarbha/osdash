#!/usr/bin/env python

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@127.0.0.1/cindervol'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
Bootstrap(app)
db = SQLAlchemy(app)
db.create_all()

class Cindervol(db.Model):
    __tablename__='cindervol'
    id = db.Column(db.Integer, primary_key=True)
    total_cinder_vols = db.Column(db.Integer)
    available_marked_cinder_vols = db.Column(db.Integer)

db.create_all()
c = Cindervol(total_cinder_vols=11,available_marked_cinder_vols=5)
db.session.add(c)
db.session.commit()

@app.route('/')
def homepage():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=80)
