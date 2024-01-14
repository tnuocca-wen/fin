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
                e = 0
                try:
                    k = i.pdf_data_set.all()[0]
                    e = 1
                except:     
                    k = i.pdf_data_set.create(pdfs = [])
                                        # pdf2 = [],
                                        # pdf3 = [],
                                        # pdf4 = [])
                    e = 2
                if str(df.loc[df['Security Id'] == j, 'pdfs'].iloc[0]) != 'nan':
                    if e == 1:
                        if k.pdfs != eval(df.loc[df['Security Id'] == j, 'pdfs'].iloc[0]):
                            k.pdfs = eval(df.loc[df['Security Id'] == j, 'pdfs'].iloc[0])
                    elif e == 2:
                        k.pdfs = eval(df.loc[df['Security Id'] == j, 'pdfs'].iloc[0])
                else:
                    if e == 0:
                        k.pdfs = []
                # if str(df.loc[df['Security Id'] == j, 'pdf2'].iloc[0]) != 'nan':
                #     if e == 1:
                #         if k.pdf2 != eval(df.loc[df['Security Id'] == j, 'pdf2'].iloc[0]):
                #             k.pdf2 = eval(df.loc[df['Security Id'] == j, 'pdf2'].iloc[0])
                #     elif e == 2:
                #         k.pdf2 = eval(df.loc[df['Security Id'] == j, 'pdf2'].iloc[0])
                # else:
                #     if e == 0:
                #         k.pdf2 = []
                # if str(df.loc[df['Security Id'] == j, 'pdf3'].iloc[0]) != 'nan':
                #     if e == 1:
                #         if k.pdf3 != eval(df.loc[df['Security Id'] == j, 'pdf3'].iloc[0]):
                #             k.pdf3 = eval(df.loc[df['Security Id'] == j, 'pdf3'].iloc[0])
                #     elif e == 2:
                #         k.pdf3 = eval(df.loc[df['Security Id'] == j, 'pdf3'].iloc[0])
                # else:
                #     if e == 0:
                #         k.pdf3 = []
                # if str(df.loc[df['Security Id'] == j, 'pdf4'].iloc[0]) != 'nan':
                #     if e == 1:
                #         if k.pdf4 != eval(df.loc[df['Security Id'] == j, 'pdf4'].iloc[0]):
                #             k.pdf4 = eval(df.loc[df['Security Id'] == j, 'pdf4'].iloc[0])
                #     elif e == 2:
                #         k.pdf4 = eval(df.loc[df['Security Id'] == j, 'pdf4'].iloc[0])
                # else:
                #     if e == 0:
                #         k.pdf4 = []
                k.save()



        self.stdout.write(self.style.SUCCESS('Successfully updated the database'))