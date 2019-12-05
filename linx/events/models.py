from django.db import models
 
 class User(models.Model):
     username = models.CharField('username', max_length=50)
     password = models.CharField('password', max_length=50)
     info = models.TextField(blank=True)

 class Messages(models.Model):
     user_id = models.CharField('user_id', max_length=50)
     other_id = models.CharField('other_id', max_length=50)
     msg = models.CharField('msg', max_length=250)
     ts = models.CharField('ts', max_length =100)
