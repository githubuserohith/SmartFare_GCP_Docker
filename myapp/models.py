from django.db import models
from django.contrib.auth.models import User


class subplan(models.Model):
    title = models.CharField(max_length=150)
    price = models.IntegerField()
    max_members = models.IntegerField(null=True)
    highlight_status = models.BooleanField(null=True, default=True)

    def __str__(self):
        return self.title

class Wallet(models.Model):
    username = models.CharField(max_length=150)
    email = models.CharField(max_length=150)
    amount = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True) 
    
    def __str__(self):
        return self.username
    

class Fare(models.Model):
    username = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.IntegerField(default=0)
    
    def __str__(self):
        return self.username
    
    
    


