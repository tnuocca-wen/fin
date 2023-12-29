from django.db import models

# Create your models here.
class Company(models.Model):
    company_name = models.CharField(max_length = 1000)
    bse_ticker = models.CharField(default = 'ID', max_length = 15, primary_key = True)
    cur_year = models.IntegerField(default=0, null=True, blank=True)
    cur_quarter = models.IntegerField(default=0, null=True, blank=True)
    a_year = models.JSONField(default=list, null=True, blank=True)
    a_quarter = models.JSONField(default=list, null=True, blank=True)
    # nse_ticker = models.CharField(default = '', max_length = 15, null = True)
    def __str__(self):
        return self.company_name

class Pdf_Data(models.Model):
    company =  models.ForeignKey(Company, on_delete=models.CASCADE)
    pdfs = models.JSONField(default=list, null=True, blank=True)
    # pdf3 = models.JSONField(default=list, null=True, blank=True)
    # pdf2 = models.JSONField(default=list, null=True, blank=True)
    # pdf4 = models.JSONField(default=list, null=True, blank=True)

