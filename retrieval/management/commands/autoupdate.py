from retrieval.models import Company
from retrieval.bucket import download_blob
import pandas as pd
import os
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Data Updation'

    def handle(self, *args, **kwargs):

        download_blob( 'company_curs.csv', 'static/documents/company_curs.csv')

        df = pd.read_csv('static/documents/company_curs.csv')

        co = list(df['company_name'])

        update_co = Company.objects.all()

        for i in update_co:
            for j in co:
                if i.bse_ticker == j:
                    i.cur_year = df.loc[df['company_name'] == j, 'cur_year'].iloc[0]
                    i.cur_quarter = df.loc[df['company_name'] == j, 'cur_quarter'].iloc[0]
                    i.a_year = eval(df.loc[df['company_name'] == j, 'a_year'].iloc[0])
                    i.a_quarter = eval(df.loc[df['company_name'] == j, 'a_quarter'].iloc[0])
                    i.save()



        self.stdout.write(self.style.SUCCESS('Successfully updated the database'))