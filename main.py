from flask import Blueprint,render_template,request,redirect,flash
from flask_login import login_required, current_user
from datetime import date
from init import db
from models import *
main = Blueprint('main', __name__)



@main.route('/')
def homepage():
    return render_template("home.html")

@main.route('/', methods=['POST'])
def homepage_post():
    return render_template("home.html")

@main.route('/profile/admin')
@login_required
def profile_admin():
    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    class_details=[]
    class_det=classes.query.filter_by(ad_id=current_user.id)
    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        for details in class_det:
           uni_name=Universities.query.filter_by(uni_id=details.uni_id).first().uni_name
           class_details.append([details.class_name,uni_name])
    
    return render_template('Admin_after_login_page.html', user=current_user,class_details=class_details)

@main.route('/profile/admin/account')
@login_required
def profile_admin_account():
    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    
    return render_template('account_admin.html', user=current_user,uni=uni_name)




@main.route('/profile/admin/class', methods=['POST'])
@login_required
def profile_admin_class():
    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    class_name=request.form.get('class_name')
    uni_id=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_id
    class_registered=classes.query.filter_by(uni_id=uni_id,class_name=class_name).first()
    if not class_registered:
      class_register=classes(ad_id=current_user.id,uni_id=uni_id,class_name=class_name)
    
      db.session.add(class_register)
      db.session.commit()
      class_id=classes.query.filter_by(ad_id=current_user.id,class_name=class_name).first().class_id
      portal_register=Portal(class_id=class_id,open_portal=0)
      db.session.add(portal_register)
      db.session.commit()
    else:
        flash("This class has already been registered in this universities database.Input a different class name to register")
        redirect("/profile/admin")

    return redirect("/profile/admin")



@main.route('/profile/student')
@login_required
def profile_student():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")


   
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    admins=Admin.query.filter_by(uni_id=current_user.uni_id)
    registered_classes=Registered_Classes.query.filter_by(stu_id=current_user.id)
    classes_det={}
    for register_class in registered_classes:
        class_details=classes.query.filter_by(class_id=register_class.class_id).first()
        admin=Admin.query.filter_by(id=class_details.ad_id).first()
        if admin.ad_name in classes_det:
            classes_det[admin.ad_name].append(class_details.class_name)
        else:
            classes_det[admin.ad_name]=[]
            classes_det[admin.ad_name].append(class_details.class_name)


    return render_template('student_after_login_page.html', user=current_user,admins=admins,classes=classes_det,uni_name=uni_name)


@main.route('/profile/student/account')
@login_required
def profile_student_account():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")

    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    
    return render_template('account_student.html', user=current_user,uni=uni_name)


@main.route('/profile/student/class', methods=['POST'])
@login_required
def profile_student_class():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")

    admin=request.form.get('admin')
    admin_id=Admin.query.filter_by(ad_name=admin).first().id
    classes_registered=classes.query.filter_by(ad_id=admin_id)
    classes_registered_students={}
    classes_registered_students["1"]=[]
    classes_registered_students["0"]=[]
    registered_classes=Registered_Classes.query.filter_by(stu_id=current_user.id)
    print(list(classes_registered))
    for registered_admin_class in classes_registered:
        class_details=Registered_Classes.query.filter_by(class_id=registered_admin_class.class_id)
        for class_det in class_details: 
            if class_det and class_det.stu_id==current_user.id:
                classes_registered_students["1"].append(registered_admin_class.class_name)
        try:
            classes_registered_students["1"].index(registered_admin_class.class_name)
                
        except:
            classes_registered_students["0"].append(registered_admin_class.class_name) 

        
        
    print(classes_registered_students)

    return render_template('register_class.html', classes=classes_registered_students,admin=admin,user=current_user)

@main.route('/profile/student/register', methods=['POST'])
@login_required
def profile_student_register():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")

    classes_names=request.form.getlist('class')
    print(classes_names)
    uni_id=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_id
    for class_detail in classes_names:
        class_id=classes.query.filter_by(class_name=class_detail).first().class_id
        register_class=Registered_Classes(stu_id=current_user.id,class_id=class_id)
        db.session.add(register_class)
        db.session.commit()
    
    return redirect("/profile/student")


@main.route('/profile/student/logs/')
@login_required
def profile_student_logs():
    try:
        if current_user.ad_name:
           return redirect("/logout")
    except:
        print("isss okay")

    class_name=request.args.get('class')
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_id=classes.query.filter_by(uni_id=current_user.uni_id,class_name=class_name).first().class_id
    attendance_records=Attendance.query.filter_by(stu_id=current_user.id,class_id=class_id)


    
    return render_template("logs_student.html",attendance_records=attendance_records,user=current_user,class_name=class_name)

    

@main.route('/profile/admin/logs/')
@login_required
def profile_admin_logs():
    try:
        if current_user.stu_name:
           return redirect("/logout")
    except:
        print("isss okay")
    class_name=request.args.get('class')
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_det=classes.query.filter_by(uni_id=current_user.uni_id,class_name=class_name).first()
    attendance_records=Attendance_csv_files.query.filter_by(ad_id=current_user.id,class_id=class_det.class_id)
    attendance_records_updated=[]
    
    for attendance_column in attendance_records:
        count=attendance_column.count
        for num in range(count+1):
            file_name=attendance_column.attnd_file.split("-")
            file_name_update=file_name[0]+"-"+file_name[1]+"-"+file_name[2]+"-"+file_name[3]+"-"+str(num)+".csv"
            attendance_records_updated.append(file_name_update)




    
    return render_template("logs_admin.html",attendance_records=attendance_records_updated,user=current_user,class_name=class_name)


@main.route('/profile/admin/download_csv_file/')
@login_required
def profile_admin_csv_file():
    file_name=request.args.get('file')
    class_name=file_name.split("-")[1]
    date_string=file_name.split("-")[3]
    count=int(file_name.split("-")[4].split(".")[0])
    class_det=classes.query.filter_by(class_name=class_name,uni_id=current_user.uni_id).first()
    portal=Portal.query.filter_by(class_id=class_det.class_id).first()
    try:
        if portal.open_portal==0:
            return redirect("/profile/admin")
        if current_user.stu_name:
           return redirect("/logout")

    except:
        print("isss okay")
   
    uni_name=Universities.query.filter_by(uni_id=current_user.uni_id).first().uni_name
    class_det=classes.query.filter_by(uni_id=current_user.uni_id,class_name=class_name).first()
    attendance_files=Attendance.query.filter_by(ad_id=current_user.id,class_id=class_det.class_id,count=count,date_of_attnd=date_string)
    attendance_data=[]
    for attendance_column in attendance_files:
        
        student=Students.query.filter_by(id=attendance_column.stu_id).first()
        attendance_data.append([student.stu_name,student.stu_roll,attendance_column.time_of_attnd])
    
    return render_template("download_csv_file.html",attendance=attendance_data,user=current_user,class_name=class_name,file_sheet=file_name)

    
   



    
   