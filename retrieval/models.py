from django.db import models

# Create your models here.
class Company(models.Model):
    company_name = models.CharField(max_length = 50)
    bse_ticker = models.CharField(default = '', max_length = 15, primary_key = True)
    # nse_ticker = models.CharField(default = '', max_length = 15, null = True)