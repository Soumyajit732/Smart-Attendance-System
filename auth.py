from flask import Blueprint,render_template,request,redirect,url_for,flash
from init import db
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from flask_login import login_user, login_required, logout_user,current_user
import cv2
import joblib
import json
import face_recognition
from json import JSONEncoder
import numpy as np
import urllib
import os
from datetime import datetime



auth = Blueprint('auth', __name__)


#face detection xml file used to detect face landmarks in an image
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

#array to store encodings of faces and names of recptive people whose faces are detected
known_face_encodings = []
known_face_names = []



  

#function to derive open cv compatible image from base64 encoding
def gen_image_from_base64(url):
    with urllib.request.urlopen(url) as resp:
        # read image as an numpy array
        image = np.asarray(bytearray(resp.read()), dtype="uint8")

        # use imdecode function
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

#function to derive frames of an image where face is detected
def gen_frames(frame):
        faces = faceCascade.detectMultiScale(frame, 1.1, 4)
        for (x, y, w, h) in faces:
            # return frame[y:y+h,x:x+w]
            return frame
        return ""

#function to train a particular image with the respective face detection model
def train_model(link):
    frame = face_recognition.load_image_file(link)
    try:
        face_encoding = face_recognition.face_encodings(frame)[0]
        return face_encoding
    
    except:
        print(link)
        return " "
    
   



#function to identify the face in the particular frame 
def identify_face(frame,user):
    # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    userimagefolder = 'static/faces/' + user.stu_name + '_' + str(user.id)
    test_image=user.stu_name+"_"+str(user.id)+"_test.jpg"
    cv2.imwrite(userimagefolder + '/' + test_image, frame)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    frame2 = face_recognition.load_image_file(f'{userimagefolder}/{test_image}')
    face_encodings = face_recognition.face_encodings(frame2)
    # Find all the faces and face encodings in the current frame of video
    # face_locations = face_recognition.face_locations(rgb_small_frame)
    # face_encodings = face_recognition.face_encodings(rgb_small_frame)
    name = "Unknown"
    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)


        # If a match was found in known_face_encodings, just use the first one.
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
    os.remove(f'{userimagefolder}/{test_image}')

    return name



userlist = os.listdir('static/faces')
for user in userlist:
    for imgname in os.listdir(f'static/faces/{user}'):
        known_face_encodings.append(train_model(f'static/faces/{user}/{imgname}'))
        known_face_names.append(user)














@auth.route('/login', methods=['POST'])
#route handling login of a particular user
def login_post():
    # login code goes here
    username = request.form.get('username')
    password = request.form.get('password')
    user_to_login= request.form.get('type')
    remember = True if request.form.get('remember') else False
    if(user_to_login=="Admin"):
          user = Admin.query.filter_by(user_ad=username).first()
          # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
          if not user or not check_password_hash(user.password_ad, password):
             flash('Please check your login details and try again.')
             return redirect("/")
          check_id="ad"+str(user.id)
          user_auth=User.query.filter_by(user_id=check_id).first()
          login_user(user_auth, remember=remember)
          return redirect("/profile/admin")
    else:
         user = Students.query.filter_by(user_stu=username).first()
         # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
         if not user or not check_password_hash(user.password_stu, password):
             flash('Please check your login details and try again.')
             return redirect("/")
         check_id="stu"+str(user.id)
         user_auth=User.query.filter_by(user_id=check_id).first()
         login_user(user_auth, remember=remember)
         return redirect("/profile/student")


    

  

    
   

    # if the above check passes, then we know the user has the right credentials
    


#logout redirect
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@auth.route('/Student_signup')
def signup_student():
    universities=Universities.query.all()
    
    return render_template("student_registration.html",uni=universities)


#to sign up a particular student in with the details needed
@auth.route('/Student_signup', methods=['POST'])
def signup_post_student():
    #take the data from the user
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    roll = request.form.get('roll')
    gender = request.form.get('gender')
    name=first_name+" "+last_name
    username = request.form.get('username')
    password = request.form.get('password')
    con_password=request.form.get('conf_password')
    mobile = request.form.get('mobile_no')
    email = request.form.get('email_id')
    university = request.form.get('universities')
    print(university)
    profile_pic = request.form.get('profile_pic')
    img_data=request.form.get("photo_data")
    img_data=img_data.split("*")

    #for every base64 encoded image we generate an opencv image
    for frame in img_data:
        if frame=='':
          flash("No Face was detected in the process of registration.Please keep in mind to properly put your face in camera while registering")
          return redirect('/Student_signup')


    user_check_usrname = Students.query.filter_by(user_stu=username).first()
    user_check_email = Students.query.filter_by(stu_email=email).first()
    # if this returns a user, then the email already exists in database

    if user_check_usrname or user_check_email:# if a user is found, we want to redirect back to signup page so user can try again
        flash('Username and Email address already exists')
        return redirect("/Student_signup")
    
   
   
    uni_id=Universities.query.filter_by(uni_name=university).first().uni_id

    new_user = Students(stu_name=name,stu_gender=gender,stu_roll=roll,stu_phone=mobile,stu_email=email,uni_id=uni_id,photo_stu=profile_pic,user_stu=username,password_stu=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()

    user_auth_id=Students.query.filter_by(user_stu=username).first().id
    user_auth_id="stu"+str(user_auth_id)
    user_auth=User(user_id=user_auth_id,user_type="Student")

    db.session.add(user_auth)
    db.session.commit()

    user=Students.query.filter_by(stu_name=name,stu_roll=roll,uni_id=uni_id).first()
    global known_face_encodings, known_face_names
    
    #image data is divided into n strings of base64 encoded images
    img_data=request.form.get("photo_data")
    img_data=img_data.split("*")

    #for every base64 encoded image we generate an opencv image
    for frame in img_data:
        if frame=='':
          flash("No Face was detected in the process of registration.Please keep in mind to properly put your face in camera while registering")
          redirect('/Student_signup')

        frame_2 = gen_image_from_base64(frame)
        frame_3=gen_frames(frame_2)
        if frame_3!="":
            userimagefolder = 'static/faces/' + user.stu_name + '_' + str(user.id)
            if not os.path.isdir(userimagefolder):
                os.makedirs(userimagefolder)
                name=user.stu_name +'_'+str(user.id)+'.jpg'
                new_img=Students_photo_data(stu_id=user.id,photo_stu=frame)
                db.session.add(new_img)
                db.session.commit()
                cv2.imwrite(userimagefolder + '/' + name, frame_3)
                break
    userimagefolder = 'static/faces/' + user.stu_name + '_' + str(user.id)
    if not os.path.isdir(userimagefolder):
        flash("No Face was detected in the process of registration.Please keep in mind to properly put your face in camera while registering")
        redirect("/Student_signup")
    #train the data with the new user added
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            known_face_encodings.append(train_model(f'static/faces/{user}/{imgname}'))
            known_face_names.append(user)
  

    
   
    flash("You have been successfully registered")
    return redirect("/")



@auth.route('/Admin_signup')
def signup_admin():
    universities = Universities.query.all()
    return render_template("Admin_registration.html",uni=universities)


#post method for admin signup
@auth.route('/Admin_signup', methods=['POST'])
def signup_post_admin(): 
    # code to validate and add user to database goes here
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    name=first_name+" "+last_name
    gender = request.form.get('gender')
    username = request.form.get('username')
    password = request.form.get('password')
    mobile = request.form.get('mobile_no')
    email = request.form.get('email_id')
    university_existing = request.form.get('universities')
    university_new = request.form.get('new_institute')
    profile_pic = request.form.get('profile_pic')


    user_check_usrname = Admin.query.filter_by(user_ad=username).first()
    user_check_email = Admin.query.filter_by(ad_email=email).first()# if this returns a user, then the email already exists in database

    if user_check_usrname or user_check_email:# if a user is found, we want to redirect back to signup page so user can try again
        flash('Username and Email address already exists')
        return redirect("/Admin_signup")

    uni_id=0
    if university_existing!="others":
        uni_id=Universities.query.filter_by(uni_name=university_existing).first().uni_id

    if university_new:
        university=university_new
        new_uni=Universities(uni_name=university_new)
        db.session.add(new_uni)
        db.session.commit()

        uni_id = Universities.query.filter_by(uni_name=university_new).first().uni_id


    new_user = Admin(ad_name=name,ad_gender=gender,ad_phone=mobile,ad_email=email,uni_id=uni_id,photo_ad=profile_pic,user_ad=username,password_ad=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()

    user_auth_id=Admin.query.filter_by(user_ad=username).first().id
    user_auth_id="ad"+str(user_auth_id)
    user_auth=User(user_id=user_auth_id,user_type="Admin")

    db.session.add(user_auth)
    db.session.commit()

    return redirect("/")

#route to enter attendance portal for a student
@auth.route("/profile/student/attendance/")
@login_required
def attendance_page():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")

    class_name=request.args.get('class')
    class_id=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first().class_id
    portal=Portal.query.filter_by(class_id=class_id).first()
    if portal.open_portal==1:
        return render_template("attendance_panel.html",class_name=class_name)
    else:
        flash('The attendance portal for this particular class isnt opened yet')
        return redirect("/profile/student")


#route to enter attendance portal for an admin
@auth.route("/profile/admin/attendance/")
@login_required
def attendance_portal():

    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    now = datetime.now()
    exist_count=request.args.get("exist_count")
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    date_string=dt_string.split(' ')[0]
    time_string=dt_string.split(' ')[1]
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_name=request.args.get('class')
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    portal.open_portal=1
    db.session.add(portal)
    db.session.commit()
    count=0
    file_sheet=f"Attendance-{class_det.class_name}-{uni_name}-{date_string}-{count}.csv"
    csv_file_created=Attendance_csv_files.query.filter_by(ad_id=class_det.ad_id,class_id=class_det.class_id,date_of_attnd=date_string,attnd_file=file_sheet).first()
    if not csv_file_created:
        csv_file=Attendance_csv_files(ad_id=class_det.ad_id,class_id=class_det.class_id,count=0,date_of_attnd=date_string,time_of_attnd=time_string,attnd_file=file_sheet)
        db.session.add(csv_file)
        db.session.commit()
    else:
        count=csv_file_created.count

        if not exist_count or int(exist_count)!=count:
          count+=1
          csv_file_created.count=count
          db.session.add(csv_file_created)
          db.session.commit()
        

    
    


    

    
    return render_template("attendance_portal.html",class_name=class_name,count=count,date_of_attnd=date_string)

@auth.route("/profile/admin/status/")
@login_required
def status():
    class_name=request.args.get('class')
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    try:
        if portal.open_portal==0:
            return redirect("/profile/admin")
        if current_user.stu_name:
           return redirect("/logout")
        
    except:
        print("isss okay")
    class_name=request.args.get('class')
    count=request.args.get('count')
    date_string=request.args.get('date')
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    attendance_files=Attendance.query.filter_by(ad_id=current_user.id,class_id=class_det.class_id,count=count,date_of_attnd=date_string)
    attendance_photos=[]

    for attendance_column in attendance_files:
        student=Students.query.filter_by(id=attendance_column.stu_id).first()
        print(student)
        student_photo=attendance_column.attnd_photo
        attendance_photos.append([student.stu_name,student_photo])
    return render_template("attendance_status.html",class_name=class_name,count=count,date_of_attnd=date_string,attendance_photo_base64=attendance_photos)



@auth.route("/profile/admin/download/")
@login_required
def download_portal():
    class_name=request.args.get('class')
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    try:
        # if portal.open_portal==0:
        #     return redirect("/profile/admin")
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    class_name=request.args.get('class')
    count=request.args.get('count')
    date_string=request.args.get('date')
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    print(current_user.id,class_det.class_id,count,date_string)
    attendance_files=Attendance.query.filter_by(ad_id=current_user.id,class_id=class_det.class_id,count=count,date_of_attnd=date_string)
    attendance_data=[]
    print(attendance_files)
    


    file_sheet=f"Attendance-{class_det.class_name}-{uni_name}-{date_string}-{count}.csv"
    for attendance_column in attendance_files:
        
        student=Students.query.filter_by(id=attendance_column.stu_id).first()
        print(student)
        attendance_data.append([student.stu_name,student.stu_roll,attendance_column.time_of_attnd])
           
    return render_template("download_page.html",attendance=attendance_data,file_sheet=file_sheet,class_name=class_name)


@auth.route("/profile/admin/close/")
@login_required
def close_portal():
    class_name=request.args.get('class')
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    try:
        if portal.open_portal==0:
            return redirect("/profile/admin")
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")

    class_name=request.args.get('class')
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    portal.open_portal=0
    db.session.add(portal)
    db.session.commit()

    

    

    return redirect("/profile/admin")


#route to give attendance for students
@auth.route("/give_attendance",methods=["POST"])
@login_required
def give_attendance():
   class_name=request.form.get("class_name")
   class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
   portal=Portal.query.filter_by(class_id=class_det.class_id).first()
   try:
       if portal.open_portal==0:
            return redirect("/profile/admin")
       if current_user.ad_name:
           return redirect("/logout")

   except:
       print("isss okay")

   global known_face_names
   now = datetime.now()
   dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
   date_string=dt_string.split(' ')[0]
   time_string=dt_string.split(' ')[1]

   class_name=request.form.get("class_name")
   class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()

   
   img_data=request.form.get("photo_data")
   img_data=img_data.split("*")
   prediction=""
   for frame in img_data:
       if frame == '':
         flash('Seems Like either your not registered in the system or the scanner hasnt recognized your face correctly')
         return redirect(f"/profile/student/attendance/?class={class_det.class_name}")
       frame_2 = gen_image_from_base64(frame)
       frame_3 = gen_frames(frame_2)
       if (frame_3 != ""):
           prediction=identify_face(frame_3,current_user)
           print(prediction)
           student_name=current_user.stu_name+"_"+str(current_user.id)
           if prediction == "Unknown" or prediction!=student_name:
               flash('Seems Like either your not registered in the system or the scanner hasnt recognized your face correctly')
               return redirect(f"/profile/student/attendance/?class={class_det.class_name}")
           else:
               count=0
               csv_file=Attendance_csv_files.query.filter_by(ad_id=class_det.ad_id,class_id=class_det.class_id,date_of_attnd=date_string).first()
               if csv_file:
                count=csv_file.count
               else:
                count=0
               check_field=Attendance.query.filter_by(stu_id=current_user.id,ad_id=class_det.ad_id,class_id=class_det.class_id,count=count,date_of_attnd=date_string).first()
               if check_field:
                flash('Your attendance has already been recorded for this class at this time')
                return redirect("/profile/student")
               new_field=Attendance(stu_id=current_user.id,ad_id=class_det.ad_id,class_id=class_det.class_id,count=count,date_of_attnd=date_string,time_of_attnd=time_string,attnd_photo=frame)
               
               db.session.add(new_field)
               db.session.commit()
               flash('Your attendance is recorded')
               return redirect("/profile/student")
           break


 
    
   return redirect("/")
