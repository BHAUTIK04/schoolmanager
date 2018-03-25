# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from bson import ObjectId
from .models import UserRole
import json
from django.contrib.auth.decorators import login_required
from pymongo import MongoClient
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http.response import JsonResponse

def mongoConnection():
    conn = MongoClient('localhost', 27017)
    db = conn["school"]
    return db

def index_view(request):
    if request.user.is_authenticated():
        return redirect("/dashboard")
    else:
        return render(request, "index.html")

@csrf_exempt
def loggin(request):
    try:
        u = User.objects.get(username="001SS18001")
        print u.password
        if request.method=="POST":
            if request.user.is_authenticated():
                return redirect("/dashboard")
            else:
                username = request.POST.get("username")
                password = request.POST.get("password")
                try:
                    user_info = User.objects.get(username=username.upper())
                    request.session["role"] = user_info.userrole.role
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    return redirect("/dashboard/")
                except:
                    return render_to_response("login.html", {"message":"Please enter correct credentials."})

        else:
            return render(request, "login.html")
    except Exception as e:
        return HttpResponse(json.dumps({"flag":"Error","msg":"Something went wrong. Please try again"+str(e)}))

@csrf_exempt
@login_required(login_url="/login")
def CreateUser(request):
    try:
        role = request.session.get('role')
        client = MongoClient('localhost', 27017)
        db = client['school']
        
        if request.method=="POST":
            
            req_data = request.POST
            req_data = req_data.dict()
            req_data["role"] = int(req_data["role"])
            req_data["username"] = req_data["username"].upper()
            print req_data
            avail = User.objects.filter(username=req_data["username"]).count()
            if avail>0:
                return HttpResponse(json.dumps({"flag":"Error","msg":"Email already Exists"}))
            else:
                oid = ObjectId()
                user=User.objects.create_user(username=req_data["username"], password=req_data["password"], email=req_data["email"])
                ur = UserRole()
                ur.object_id = str(oid)
                ur.role = req_data["role"]
                ur.user_id = user.id
                del req_data["password"]
                if role == 1:
                    col = db["school_data"]
                    req_data["_id"] = oid
                    col.insert_one(req_data)
                elif role == 2:
                    user.first_name=req_data.get("fname", '')
                    user.last_name=req_data.get("lname",'')
                    user.save()
                    if req_data["role"] == 3:
                        if "email_parent" in req_data:
                            del req_data["email_parent"]
                        if "parent_cntc_1" in req_data:
                            del req_data["parent_cntc_1"]
                        if "student_cntc_1" in req_data:
                            del req_data["student_cntc_1"]
                        if "parent_cntc_2" in req_data:
                            del req_data["parent_cntc_2"]
                        ur.qualification = req_data.get('qualification' , '')
                        ur.expertise = req_data.get('expertise' , '')
                        ur.sex = req_data.get('sex', '')
                        col = db["school_teacher"]
                        req_data["_id"] = oid
                        col.insert_one(req_data)
                    elif req_data["role"] == 4:
                        del req_data["teacher_cntc_2"]
                        del req_data["teacher_cntc_1"]
                        del req_data["expertise"]
                        del req_data["qualification"]
                        ur.sex = req_data.get('sex', '')
                        col = db["school_student"]
                        req_data["_id"] = oid
                        col.insert_one(req_data)
                ur.save()
                # return HttpResponse(json.dumps({"flag":"Success","msg":"Register Successfully"}))
                return redirect("/createuser", message="Successfully registered")
        else:
            user_role =request.session.get('role')
            if user_role == 1 or 2:
                return render(request, "createuser.html", {"role":user_role, "username": request.user})
            else:
                return redirect("/dashboard/", message="Successfully registered")
            
    except Exception as e:
        print str(e)
        return HttpResponse(json.dumps({"flag":"Error","msg":"Something went wrong. Please try again"}))
    
    
@login_required(login_url="/login")
def dashboard(request):
    user_role = request.session.get('role')
    return render(request, "dashboard.html",{"username":request.user,"role":user_role})

# @login_required(login_url="/login")
# def classList(request):
#     user_role = request.session.get('role')
#     return render(request, "class.html", {"username":request.user,"role":user_role})
# 
# @login_required(login_url="/login")
# def studentList(request):
#     user_role = request.session.get('role')
#     return render(request, "dashboard.html", {"username":request.user,"role":user_role})

@login_required(login_url="/login")
def teacherList(request):
    user_role = request.session.get('role')
    schoolcode = request.user.username[:3]
    if user_role == 2:
        teachers = User.objects.filter(username__startswith=schoolcode+"ST")
        return render(request, "teachers.html", {"username":request.user,"role":user_role, "teachers": teachers})
    else:
        return HttpResponse("You are not an authorized user.")      
    

@login_required(login_url="/login")
def allStudentList(request):
    user_role = request.session.get('role')
    schoolcode = request.user.username[:3]
    if user_role == 2:
        students = User.objects.filter(username__startswith=schoolcode+"SS")
        return render(request, "students.html", {"username":request.user,"role":user_role, "students": students})
    else:
        return HttpResponse("You are not an authorized user.")
    
@login_required(login_url="/login")
def allSchoolList(request):
    user_role = request.session.get('role')
    if user_role == 1:
        schools = User.objects.filter(username__icontains="SA")
        return render(request, "school.html", {"username":request.user,"role":user_role, "schools": schools})
    else:
        return HttpResponse("You are not an authorized user.")

@login_required(login_url="/login")
def profile(request):
    user_role = request.session.get('role')
    user_info = request.user
    oid = user_info.userrole.object_id
    print user_info
    db = mongoConnection()
    
    if user_role == 1:
        return redirect("/dashboard")
    if user_role == 2:
        _students = User.objects.filter(username__icontains="001SS")
        _teachers = User.objects.filter(username__icontains="001ST")
        coll = "school_data"
        _data = {"_id":0}
        user_profile =  db[coll].find_one({"_id": ObjectId(oid)},_data)
        user_profile["teachers"] = len(_teachers)
        user_profile["students"] = len(_students)
    elif user_role == 3:
        coll = 'school_teacher'
        _data = {"_id":0}
        user_profile =  db[coll].find_one({"_id": ObjectId(oid)},_data)
    elif user_role == 4:
        coll = 'school_student'
        _data = {"_id":0, "courses":0,"qualification":0,"role":0, "expertise":0}    
        user_profile =  db[coll].find_one({"_id": ObjectId(oid)},_data)
    print user_profile
    if user_profile:
        if user_role == 4:
            pass
    return render(request, "profile.html", {"username":request.user,"role":user_role, "userdata":user_profile, "user_info":user_info})

@login_required(login_url="/login")
def registeredStudents(request):
    oid = request.user.userrole.object_id
    user_role = request.session.get('role')
    db = mongoConnection()
    
    coll = db["marks"]
    marks = coll.find_one({"teacher_oid":oid},{"_id":0})
    exams = []
    data = []
    if marks and "year" and "subject_name" and "class" in marks:
        st = {i["student_id"]:i['exams'] for i in marks["students"]}
        students = User.objects.filter(username__in=st.keys())
        exams = st.values()[0].keys()
        print st
        if students:
            data = [{"username":i.username,"first_name":i.first_name, "last_name":i.last_name, "email": i.email, "progress":st[i.username]} for i in students]
        
    
        return render(request, "students.html", {"username":request.user,"role":user_role, "students": data,"exams":exams, "year":marks["year"],"subject": marks["subject_name"], "class":marks["class"]})
    return render(request, "students.html", {"username":request.user,"role":user_role})

@login_required(login_url="/login")
def report(request):
    username = request.user.username
    oid = request.user.userrole.object_id
    user_role = request.session.get('role')
    db = mongoConnection()
    
    coll = db["school_student"]
    courses = coll.find_one({"_id":ObjectId(oid)},{"_id":0, "courses":1})
    course_data = []
    if courses:
        courses = courses["courses"]
        for i in courses:
            if "grades" and "subjects" in courses[i]:
                _d = {"grade": courses[i]["grade"], "year": i}
                _subj = courses[i]["subjects"]
                teachers = {i.object_id:{"tfname":i.user.first_name, "tlname":i.user.last_name, "temail":i.user.email } for i in UserRole.objects.filter(object_id__in = courses[i]["subjects"].values())}
                a = UserRole.objects.filter(object_id__in = _subj.values())
                _d["subjects"] = {i:teachers[_subj[i]] for i in _subj}
                course_data.append(_d)
    return render(request, "course.html", {"username":request.user,"role":user_role, "courses": course_data }) 


@login_required(login_url="/login")
def progress(request):
    user_role = request.session.get('role')
    oid = request.user.userrole.object_id
    if user_role == 3:
        print oid
        db = mongoConnection()
        coll = db["marks"]
        coll = db["marks"]
        marks = coll.find_one({"teacher_oid":oid},{"_id":0})
        exams = []
        data = []
        if marks and "year" and "subject_name" and "class" in marks:
            st = {i["student_id"]:i['exams'] for i in marks["students"]}
            students = User.objects.filter(username__in=st.keys())
            exams = st.values()[0].keys()
            print st
            if students:
                data = [{"username":i.username,"first_name":i.first_name, "last_name":i.last_name, "email": i.email, "progress":st[i.username]} for i in students]
        return render(request, "progress.html", {"username":request.user,"role":user_role, "students": data,"exams":exams, "year":marks["year"],"subject": marks["subject_name"], "class":marks["class"]})        
    elif user_role == 4:
        user = request.user
        print user.userrole.object_id
        db = mongoConnection()
        data = db['marks'].find({"students.student_id":user.username},{"_id":0,"students.$.exams":1,"subject_name":1,"year":1,"class":1})
        marks = []
        for i in data:
            if i.get("students",[]):
                _dict = {}
                _dict["exams"] = i["students"][0]["exams"]
                _dict["subject"] = i["subject_name"]
                _dict["class_name"] = i["class"]
                _dict["year"] = i["year"]
                marks.append(_dict)
            print i["students"] 
        print marks
        return render(request, "progress.html", {"username":request.user,"role":user_role, "marks": marks})

@csrf_exempt
@login_required(login_url="/login")
def editMarks(request):
    user_role = request.session.get('role')
    if user_role == 2 or user_role == 3:
        req_data = request.POST
        req_data = req_data.dict()
        oid = request.user.userrole.object_id
        db = mongoConnection()
        student = db["marks"].find_one({"teacher_oid":oid,"students.student_id": req_data["student_id"]},{"students.$.student_id":1})
        _student_data = student["students"][0]
        _exams = _student_data["exams"]
        for i in _exams.keys():
            _exams[i]["obtained"] =  float(req_data[i])
        resp = db["marks"].update({"teacher_oid":oid, "students.student_id": req_data["student_id"]},{"$set":{"students.$.exams":_exams}})
        if resp["updatedExisting"] == True:
            response = {"status":"success"}
        else:
            response = {"status":"error"}
    else:
        response = {"status":"You are not authorize person to edit marks."}
    return JsonResponse(response)

@login_required(login_url="/login")
def change_password(request):
    user_role = request.session.get('role')
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form, 'role':user_role
    })
    
def loggout(request):
    logout(request)
    return redirect("/login/")
