from retrieval.models import Company, Pdf_Data
from retrieval.bucket import download_blob
import pandas as pd
import os
from django.core.management.base import BaseCommand, CommandParser

class Command(BaseCommand):
    help = 'Data Updation'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file_name', type=str, help='path of the file containing pdf information')
        return super().add_arguments(parser)

    def handle(self, *args, **kwargs):

        filename = kwargs['file_name']

        df = pd.read_csv(filename)

        co = list(df['Security Id'])
    
        update_co = Company.objects.all()
        # update_pdf = Pdf_Data.objects.all()

        for i in update_co:
          for j in co:
              if i.bse_ticker == j:
                  try:
                      i.pdf_data_set.create(pdf1 = eval(df.loc[df['Security Id'] == j, 'pdf1'].iloc[0]),
                                            pdf2 = eval(df.loc[df['Security Id'] == j, 'pdf2'].iloc[0]),
                                            pdf3 = eval(df.loc[df['Security Id'] == j, 'pdf3'].iloc[0]),
                                            pdf4 = eval(df.loc[df['Security Id'] == j, 'pdf4'].iloc[0]))
                  except:
                      i.pdf_data_set.create(pdf1 = [],
                                            pdf2 = [],
                                            pdf3 = [],
                                            pdf4 = [])



        self.stdout.write(self.style.SUCCESS('Successfully updated the database'))