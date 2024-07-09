from init import db
from flask_login import UserMixin

#database model for the entire application
#- every class here represents a table in the database
#-every field represents a column in the table

class User(UserMixin,db.Model):
     id = db.Column(db.Integer, primary_key=True)
     user_id=db.Column(db.String(),nullable=False)
     user_type=db.Column(db.String(100),nullable=False)

class Admin(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_name = db.Column(db.String(100),nullable=False) 
    ad_gender =db.Column(db.String(100),nullable=False) 
    ad_phone=db.Column(db.Integer,nullable=False)
    ad_email=db.Column(db.String(100),nullable=False)
    uni_id=db.Column(db.Integer(),db.ForeignKey('universities.uni_id'),nullable=False)
    photo_ad=db.Column(db.String())
    user_ad = db.Column(db.String(15),nullable=False)
    password_ad = db.Column(db.String(100),nullable=False)

class Students(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stu_name = db.Column(db.String(100),nullable=False)
    stu_gender =db.Column(db.String(100),nullable=False) 
    stu_phone = db.Column(db.Integer,nullable=False)
    stu_roll = db.Column(db.String(100),nullable=False)
    stu_email = db.Column(db.String(100),nullable=False)
    uni_id = db.Column(db.Integer(), db.ForeignKey('universities.uni_id'))
    photo_stu = db.Column(db.String())
    user_stu = db.Column(db.String(15),nullable=False)
    password_stu = db.Column(db.String(100),nullable=False)


class Students_photo_data(db.Model):
    student_photo_id=db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.Integer(), db.ForeignKey('students.id'),nullable=False)
    photo_stu = db.Column(db.String(),nullable=False)

class classes(db.Model):
    class_id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer(), db.ForeignKey('admin.id'),nullable=False)
    uni_id = db.Column(db.Integer(), db.ForeignKey('universities.uni_id'),nullable=False)
    class_name = db.Column(db.String(),nullable=False)

class Registered_Classes(db.Model):
    registered_class_id = db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.Integer(), db.ForeignKey('students.id'),nullable=False)
    class_id=db.Column(db.Integer(), db.ForeignKey('classes.class_id'),nullable=False)


class Universities(db.Model):
    uni_id=db.Column(db.Integer, primary_key=True)
    uni_name=db.Column(db.String(100),nullable=False)

class Attendance(db.Model):
    attendance_id=db.Column(db.Integer, primary_key=True)
    stu_id = db.Column(db.Integer(), db.ForeignKey('students.id'),nullable=False)
    ad_id = db.Column(db.Integer(), db.ForeignKey('admin.id'),nullable=False)
    class_id = db.Column(db.Integer(), db.ForeignKey('classes.class_id'),nullable=False)
    count =  db.Column(db.Integer(),nullable=False)
    date_of_attnd=db.Column(db.String(),nullable=False)
    time_of_attnd=db.Column(db.String(),nullable=False)
    attnd_photo = db.Column(db.String(),nullable=False)

class Attendance_csv_files(db.Model):
    csv_id=db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer(), db.ForeignKey('admin.id'),nullable=False)
    class_id = db.Column(db.Integer(), db.ForeignKey('classes.class_id'),nullable=False)
    count =  db.Column(db.Integer(),nullable=False)
    date_of_attnd=db.Column(db.String(),nullable=False)
    time_of_attnd=db.Column(db.String(),nullable=False)
    attnd_file = db.Column(db.String(),nullable=False)

class Portal(db.Model):
    portal_id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer(), db.ForeignKey('classes.class_id'),nullable=False)
    open_portal = db.Column(db.Integer,nullable=False)

# with app.app_context():
#      db.create_all()




