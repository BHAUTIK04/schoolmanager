# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import utils
from django.db import models
from django.contrib.auth.models import User 
import datetime

class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=100,blank=True,null=True)
    role = models.PositiveSmallIntegerField()
    qualification = models.CharField(max_length=50, null=True)
    expertise = models.CharField(max_length=150, null=True)
    sex = models.CharField(max_length=1, null=False, blank=False)