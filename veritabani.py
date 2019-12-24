from datetime import datetime
from flask import Flask, request, render_template_string, render_template
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin, user_logged_out
from sqlalchemy.sql import table, column, select 
from sqlalchemy import MetaData

""" Flask application factory """
    
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///basic_app.sqlite'
app.config["SECRET_KEY"] = 'This is an INSECURE secret!! DO NOT use this in production!!'
app.config["USER_ENABLE_EMAIL"] = False

babel = Babel(app)
@babel.localeselector

def get_locale():
    translations = [str(translation) for translation in babel.list_translations()]

db = SQLAlchemy(app)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    username = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    roles = db.relationship('Role', secondary='user_roles')
    bonus = db.Column(db.Integer(), server_default='0')
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
class ucus(db.Model):
    __tablename__ = 'ucus'
    id = db.Column(db.Integer(), primary_key=True)
    rota = db.Column(db.String(250), nullable=False)
    tarih = db.Column(db.Integer(), nullable=False)
    saat = db.Column(db.Integer(), nullable=False)
    koltuk = db.Column(db.Integer(), nullable=False)
    ucret = db.Column(db.REAL, nullable=False)
    doluluk = db.Column(db.Integer())
    oran = db.Column(db.Integer())
class rezervasyon(db.Model):
    __tablename__ = 'rezervasyon'
    id = db.Column(db.Integer(), primary_key=True)
    rota = db.Column(db.String(250), nullable=False)
    tarih = db.Column(db.Integer(), nullable=False)
    saat = db.Column(db.Integer(), nullable=False)
    koltuk = db.Column(db.Integer(), nullable=False)
    ucret = db.Column(db.REAL, nullable=False)
    kullanici_id = db.Column(db.Integer(), nullable=False)
    alistarihi = db.Column(db.String(250))
    ucus_id = db.Column(db.Integer())
class bilet(db.Model):
    __tablename__ = 'bilet'
    id = db.Column(db.Integer(), primary_key=True)
    rota = db.Column(db.String(250), nullable=False)
    tarih = db.Column(db.Integer(), nullable=False)
    saat = db.Column(db.Integer(), nullable=False)
    koltuk = db.Column(db.Integer(), nullable=False)
    ucret = db.Column(db.REAL, nullable=False)
    kullanici_id = db.Column(db.Integer(), nullable=False)
    alistarihi = db.Column(db.String(250))
user_manager = UserManager(app, db, User)
db.create_all()
if not User.query.filter(User.username == 'admin').first():
    user = User(
        username = 'admin',
        password = user_manager.hash_password('Password1')
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()
@app.route('/')
def home_page():
    return render_template('home.html')
    
@app.route('/ucus_ekle')
@roles_required('Admin')
def ucus_ekle():
      return render_template('ucus_ekle.html')
@app.route('/sefer_ekle', methods = ['POST', 'GET'])
@roles_required('Admin')
def sefer_ekle():
    if request.method == 'POST':
        try:
            nereden = request.form['rota']
            trh = request.form['tarih']
            zaman = request.form['saat']
            kltk = request.form['koltuk']
            para = request.form['ucret']
            dolu = 0
            orann = 0
            ekle = ucus(rota = nereden, tarih = trh, saat = zaman, koltuk = kltk, ucret = para, doluluk = dolu, oran = orann)
            db.session.add(ekle)
            db.session.commit()
            msg = "Sefer Bilgileri Başarılı Şekilde Sisteme Eklenmiştir, Uçuş Listesini Kontrol Ediniz." 
        except:
            msg = "Kayıt işlemi sırasında hata oluştu"
        finally:
            return render_template("mesaj.html", kayitlar = msg)
@app.route('/ucus_duzenle')
@roles_required('Admin')
def ucus_duzenle():
      row = ucus.query.filter_by().all()
      return render_template('ucus_duzenle.html', kayitlar = row)

@app.route('/bilgileri_guncelle', methods = ['POST', 'GET'])
@roles_required('Admin')
def bilgileri_guncelle():
    if request.method == 'POST':
        no_id = request.form['no']
        roww = ucus.query.filter_by(id = no_id).all()
        return render_template('bilgileri_guncelle.html', kayitlar = roww)
@app.route('/guncelle', methods = ['POST', 'GET'])
@roles_required('Admin')
def guncelle():
    if request.method == 'POST':
        try:
            idd = request.form['id']
            nereden = request.form['rota']
            trh = request.form['tarih']
            zaman = request.form['saat']
            kltk = request.form['koltuk']
            para = request.form['ucret']
            guncelle = ucus.query.filter_by(id = idd).first()
            guncelle.rota = nereden
            guncelle.tarih = trh
            guncelle.saat = zaman
            guncelle.koltuk = kltk
            guncelle.ucret = para
            db.session.commit()
            msg = "Sefer Bilgilerini Güncelleme İşlemi Başarılı Şekilde Sisteme Eklenmiştir, Uçuş Listesini Kontrol Ediniz."
        
        except:
            msg = "Kayıt güncelleme işlemi sırasında hata oluştu"
  
        finally:
            return render_template("mesaj.html", kayitlar = msg)
@app.route('/ucus_sil')
@roles_required('Admin')
def ucus_sil():
      row = ucus.query.filter_by().all()
      return render_template('ucus_sil.html', kayitlar = row)
@app.route('/seferi_sil', methods = ['POST', 'GET'])
@roles_required('Admin')
def seferi_sil():
    if request.method == 'POST':
        try:
            no_id = request.form['no']
            row = ucus.query.filter_by(id = no_id).first()
            nereden = row.rota
            trh = row.tarih
            zaman = row.saat
            kltk = row.koltuk
            para = row.ucret
            sil = ucus.query.get(row.id)
            db.session.delete(sil)
            db.session.commit()
            msg = no_id + " No'lu Uçuş Seferi Silindi.."
        except:
            msg = "Kayıt silme işlemi sırasında hata oluştu"
  
        finally:
            return render_template("mesaj.html", kayitlar = msg)
@app.route('/ucus_listele')
def ucus_listele():
      row = ucus.query.filter_by().all()
      return render_template('ucus_listele.html', kayitlar = row)
@app.route('/sepeti_bosalt', methods = ['POST', 'GET'])
def sepeti_bosalt():
    rezervasyon.query.filter_by(kullanici_id = current_user.id).delete()
    db.session.commit()
    msg = "Sepetiniz Boşaltılmıştır."
    return render_template("mesaj.html", kayitlar = msg)
@app.route('/rezervasyon_yap', methods = ['POST', 'GET'])
@login_required 
def rezervasyon_yap():
    if request.method == 'POST':
        try:
            no_id = request.form['no']
            row = ucus.query.filter_by(id = no_id).first()
            no = row.id
            nereden = row.rota
            trh = row.tarih
            zaman = row.saat
            kltk = row.koltuk
            para = row.ucret
            k_id = current_user.id
            alis = datetime.now()
            alistarih = alis.strftime("%A, %d %B, %Y saat %X")
            ekle = rezervasyon(rota = nereden, tarih = trh, saat = zaman, koltuk = kltk, ucret = para, kullanici_id = k_id, alistarihi = alistarih, ucus_id = no)
            db.session.add(ekle)
            db.session.commit()
            msg = "Rezervasyon İşleminiz Başarılı Şekilde Tamamlanmıştır, Sepetinizi Kontrol Ediniz." 
        
        except:
            msg = "Kayıt işlemi sırasında hata oluştu"
  
        finally:
            return render_template("sepet.html", kayitlar = msg)

@app.route('/doluluk_orani')
@login_required 
def doluluk_orani():
      row = ucus.query.filter_by().order_by((ucus.oran).desc()).all() 

      return render_template('doluluk_orani.html', kayitlar = row)

@app.route('/sepetim')
@login_required 
def sepetim():
    row = rezervasyon.query.filter_by(kullanici_id = current_user.id).all()
    row2 = User.query.filter(User.id == current_user.id).first()
    return render_template('sepetim.html', kayitlar = row, a = row2.bonus)   
@user_logged_out.connect_via(app)
def _after_login_hook(sender, user, **extra):
    if rezervasyon.query.filter_by(kullanici_id = current_user.id).delete():
        db.session.commit()
    
@app.route('/bilet_al', methods = ['POST', 'GET'])
@login_required 
def bilet_al(): 
    if request.method == 'POST':
        try:
            no_id = request.form['no']
            row = rezervasyon.query.filter_by(id = no_id).first()
            no = row.id
            nereden = row.rota
            trh = row.tarih
            zaman = row.saat
            kltk = row.koltuk
            para = row.ucret
            k_id = current_user.id
            alis = datetime.now()
            alistarih = alis.strftime("%A, %d %B, %Y saat %X")
            ucusid = row.ucus_id
            ekle = bilet(rota = nereden, tarih = trh, saat = zaman, koltuk = kltk, ucret = para, kullanici_id = k_id, alistarihi = alistarih)
            db.session.add(ekle)
            db.session.commit()
            sil = rezervasyon.query.get(no)
            db.session.delete(sil)
            db.session.commit()
            guncelle = ucus.query.filter_by(id = ucusid).first()
            eski = guncelle.doluluk
            yeni = eski + 1
            guncelle.doluluk = yeni
            db.session.commit()
            guncelle2 = ucus.query.filter_by(id = ucusid).first()
            koltukoran = guncelle2.koltuk
            dolulukoran = guncelle2.doluluk
            yenioran = (dolulukoran / koltukoran) * 100
            guncelle2.oran = yenioran
            db.session.commit()
            
            guncel = User.query.filter_by(id = k_id).first()
           
            eskibonus = guncel.bonus
            yenibonus = para * 0.03
            toplambonus = eskibonus + yenibonus
            guncel.bonus = toplambonus
            db.session.commit()
            
            msg = "Bilet Alma İşleminiz Başarılı Şekilde Tamamlanmıştır, Sepetinizi Kontrol Ediniz." 
        
        except:
            msg = "Kayıt işlemi sırasında hata oluştu"
  
        finally:
            return render_template("sepet.html", kayitlar = msg)
@app.route('/biletlerim')
@login_required
def biletlerim():
      row = bilet.query.filter_by(kullanici_id = current_user.id).all()
      return render_template('biletlerim.html', kayitlar = row)
@app.route('/rezervasyon_sil', methods = ['POST', 'GET'])
@login_required
def rezervasyon_sil():
    if request.method == 'POST':
        try:
            no_id = request.form['no']
            row = rezervasyon.query.filter_by(id = no_id).first()
            nereden = row.rota
            trh = row.tarih
            zaman = row.saat
            kltk = row.koltuk
            para = row.ucret
            sil = rezervasyon.query.get(row.id)
            db.session.delete(sil)
            db.session.commit()
            msg = "Rezervasyon İptal işleminiz başarılı şekilde tamamlanmıştır, sepetinizi kontrol ediniz.."
        except:
            msg = "Kayıt silme işlemi sırasında hata oluştu"
  
        finally:
            return render_template("mesaj.html", kayitlar = msg)

if __name__ == '__main__':
    app.run(threaded=True, port=5000)