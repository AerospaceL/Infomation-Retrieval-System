from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
import datetime
import time
import random


class View_type(models.TextChoices):
    front = "正面"
    back = "背面"

class Animal(models.Model):

    file_id = models.CharField(max_length=200, default="None", primary_key=True)
    url = models.CharField(max_length=1000, default="None")
    title = models.CharField(max_length=200, default="None")
    name = models.CharField(max_length=200, default="None")
    claSS = models.CharField(max_length=20, default="None")
    order = models.CharField(max_length=20, default="None")
    family = models.CharField(max_length=20, default="None")
    describe = models.CharField(max_length=2000, default="None")
    feature = models.CharField(max_length=2000, default="None")
    size = models.CharField(max_length=2000, default="None")
    habitat = models.CharField(max_length=2000, default="None")
    inner = models.CharField(max_length=1000, default="None")
    outer = models.CharField(max_length=1000, default="None")
    level = models.CharField(max_length=20, default="None")
    others = models.CharField(max_length=2000, default="None")
    time = models.DateTimeField(default=datetime.datetime(2021, 5, 1, 0, 0, 0, 0))

class Currency(models.Model):
    figure_id = models.CharField(max_length=200, default="None", primary_key=True)
    url = models.CharField(max_length=1000, default="None")
    real_type = models.CharField(max_length=50, default="None")
    real_denomination = models.CharField(max_length=50, default="None")
    real_code = models.CharField(max_length=50, default="None")
    real_year = models.CharField(max_length=50, default="None")
    view = models.CharField(max_length=50, default=View_type.front, choices=View_type.choices)
    predict_type = models.CharField(max_length=50, default="None")
    predict_denomination = models.CharField(max_length=50, default="None")
    predict_code = models.CharField(max_length=50, default="None")
    predict_year = models.CharField(max_length=50, default="None")
    time = models.DateTimeField(default=datetime.datetime(2021, 5, 1, 0, 0, 0, 0))

