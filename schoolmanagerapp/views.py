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
# from .models import AuthUser
# Create your views here.

def index_view(request):
    if request.user.is_authenticated():
        return redirect("/dashboard")
    else:
        return render(request, "index.html")

@csrf_exempt
def loggin(request):
    try:
        if request.method=="POST":
            if request.user.is_authenticated():
                return redirect("/dashboard")
            else:
                username = request.POST.get("username")
                password = request.POST.get("password")
                try:
                    user_info = User.objects.get(username=username)
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
                        ur.qualification = req_data.get('qualification' , '')
                        ur.expertise = req_data.get('expertise' , '')
                        ur.sex = req_data.get('sex', '')
                        col = db["school_teacher"]
                        req_data["_id"] = oid
                        col.insert_one(req_data)
                    elif req_data["role"] == 4:
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

@login_required(login_url="/login")
def classList(request):
    user_role = request.session.get('role')
    return render(request, "class.html", {"username":request.user,"role":user_role})

@login_required(login_url="/login")
def studentList(request):
    user_role = request.session.get('role')
    return render(request, "dashboard.html", {"username":request.user,"role":user_role})

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
    conn = MongoClient('localhost', 27017)
    db = conn['school']
    if user_role == 2:
        coll = "school_data"
    elif user_role == 3:
        coll = 'school_teacher'
    elif user_role == 4:
        coll = 'school_student'    
    user_in =  db[coll].find_one({"_id": ObjectId(oid)},{"_id":0})
    print user_in
    return render(request, "profile.html", {"username":request.user,"role":user_role, "userdata":user_in, "user_info":user_info})
    
def loggout(request):
    logout(request)
    return redirect("/login/")