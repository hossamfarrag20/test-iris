from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Npages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    Birth_date = models.DateField()
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    suger_year = models.IntegerField()
    type_order = models.IntegerField()
    cumulative_glucose_test = models.FloatField()  # Changed to FloatField
    heart_diseases = models.CharField(max_length=100)
    blood_pressure = models.IntegerField()
    cholestrol_level = models.IntegerField()
    smoker = models.CharField(max_length=100)
    Notes = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    image = models.FileField(upload_to='modelphoto')
    
    # New fields for storing check results
    cumulative_status = models.CharField(max_length=50, null=True, blank=True)
    cumulative_require = models.CharField(max_length=50, null=True, blank=True)
    pressure_status = models.CharField(max_length=50, null=True, blank=True)
    cholestrol_status = models.CharField(max_length=50, null=True, blank=True)
    metabolic_syndrome = models.CharField(max_length=50, null=True, blank=True)
    smoker_status = models.CharField(max_length=50, null=True, blank=True)  # Added field
    heart_status = models.CharField(max_length=50, null=True, blank=True)   # Added field

    def __str__(self):
        return self.name
   
class nprofile(models.Model):
    usr = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profile')
    image = models.FileField(null=True, blank=True, upload_to = 'pics', default='defualt/default.jpg')
    is_doctor = models.BooleanField(default=False)
    def __str__(self):
        return self.usr.username
    
class Nimage(models.Model):
    iuser = models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    image = models.FileField(upload_to='modelphoto')
    def __str__(self):
        return self.image.name
    
