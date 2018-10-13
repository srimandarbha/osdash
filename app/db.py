from app import app
from flask_sqlalchemy import SQLAlchemy

app.config.from_pyfile('../scripts/settings.py')
db=SQLAlchemy(app)

class Vm_stats(db.Model):
    __tablename__ = 'vm_stats'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    vm_data = db.Column(db.JSON)

class Hypstats(db.Model):
    __tablename__ = 'hypstats'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    hyp_count = db.Column(db.Integer)
    running_vms = db.Column(db.Integer)
    vcpus = db.Column(db.Integer)
    vcpus_used = db.Column(db.Integer)
    vcpus_free = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    memory_used = db.Column(db.Integer)
    memory_free = db.Column(db.Integer)
    total_disk = db.Column(db.Integer)
    disk_used = db.Column(db.Integer)
    disk_free = db.Column(db.Integer)

class Hyp_serv_stats(db.Model):
    __tablename__ = 'hyp_serv_stats'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    hypervisor_data = db.Column(db.JSON)

class Cinder_stats(db.Model):
    __tablename__ = 'cinder_stats'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Time)
    date = db.Column(db.Date)
    cinder_data = db.Column(db.JSON)
    total_vols = db.Column(db.Integer)
    avail_vols = db.Column(db.Integer)

db.create_all()

#hypstats_result=Hypstats.query.get_or_404(Hypstats.query.count())
#hyp_serv_stats_result=Hyp_serv_stats.query.get_or_404(Hyp_serv_stats.query.count())
#c_c=Cindervol.query.count()
#if c_c == 0:
#    c = Cindervol(id=1,total_cinder_vols=0,available_marked_cinder_vols=0)
#    db.session.add(c)
#    db.session.commit()
