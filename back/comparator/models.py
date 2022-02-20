from django.db import models

class ImageCheck(models.Model):
    id = models.AutoField(primary_key=True)
    img = models.ImageField(max_length=256,blank=True,null=True)
    sha1 = models.CharField(max_length=256,blank=True,null=True)
    ssdeep = models.CharField(max_length=256, blank=True,null=True)
    averagehash = models.CharField(max_length=256,blank=True,null=True)
    phash = models.CharField(max_length=256,blank=True,null=True)
    dhash = models.CharField(max_length=256,blank=True,null=True)