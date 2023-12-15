from retrieval.models import Company
import pandas as pd
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Data Updation'

    def handle(self, *args, **kwargs):

        df = pd.read_csv('static/documents/Names.csv')

        co = list(df['Security Id'])

        for i in range(len(co)):
            new_co = Company(company_name=df['Security Name'][i].title(), bse_ticker=df['Security Id'][i])
            new_co.save()


        self.stdout.write(self.style.SUCCESS('Successfully updated the database'))