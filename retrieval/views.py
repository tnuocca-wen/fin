from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .models import Company
from.bucket import download_blob, file_exists
import json, os
import pandas as pd

# Create your views here.
def index(request):
    c = Company.objects.all()
    cdict = {}
    tickers = c.values_list('bse_ticker', flat=True)
    for i in range(len(tickers)):
        cdict[tickers[i]] = c.get(pk=tickers[i]).company_name
    return render(request, "retrieval/index.html", {'cdict':cdict})

@csrf_exempt
def retrieve(request):
    if request.method == 'POST':
        text = ''
        ktdata = []
        status = 0
        sel = json.loads(request.POST.get('selected'))
        # print("This is the request", type(sel))
        ticker = sel[0]
        year = int(sel[1])
        qrtr = int(sel[2])
        srvc = int(sel[3])

        if srvc == 1:
            fn = "summary"
            fp = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}.txt"
        else:
            fn = "keytakeaways"
            fp = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}.txt"
    


        if file_exists(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}.txt") is True:    
            if os.path.exists(fp) is True:
                status = 200
                text = text_extract(fp)
                if srvc != 1:
                    ktdata = elaborate_fetch(ticker, year, qrtr)
                    print("The type of ktdata is:", type(ktdata))
            else:
                fp1 = fp[:-4]
                print(fp1)
                os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/{fn}")
                download_blob(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}.txt",f"{fp}")
                if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf"):
                    # print("hi")
                    download_blob(f"fin/{ticker}/{year}/{qrtr}/{ticker}.pdf",f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf")
                
                if srvc != 1:
                    ktdata = elaborate_fetch(ticker, year, qrtr)

                status = 200
                text = text_extract(fp)

            return JsonResponse({'text': text, "ticker": ticker, "year": year, "qrtr": qrtr, "status": status, "ktr": 1 if srvc != 1 else 0, "ktdata": ktdata})
        else:
            return JsonResponse({'text': '', "ticker": '', "qrtr": '', "status": 404})

def text_extract(fp):
    with open(fp, 'r', encoding="utf8") as file:
        fc = file.read()
    return fc

def elaborate_fetch(ticker, year, qrtr):
    if os.path.exists("static/documents/kt_elaborated.csv"):
        ktdf = pd.read_csv('static/documents/kt_elaborated.csv')
        filtered = ktdf[(ktdf['company'] == ticker) & (ktdf['year'] == year) & (ktdf['quarter'] == qrtr)]
        filtered = filtered.reset_index(drop=True)
        return eval(filtered['kt_elaborated'][0])
    else:
        download_blob(f"fin/kt_elaborated.csv",f"static/documents/kt_elaborated.csv")
        ktdf = pd.read_csv('static/documents/kt_elaborated.csv')
        filtered = ktdf[(ktdf['company'] == ticker) & (ktdf['year'] == year) & (ktdf['quarter'] == qrtr)]
        filtered = filtered.reset_index(drop=True)
        return eval(filtered['kt_elaborated'][0])

@csrf_exempt
def sentiment(request):
    if request.method == 'POST':
        sel = json.loads(request.POST.get('selected'))
        ticker = sel[0]
        year = int(sel[1])
        qrtr = int(sel[2])
        fn = "sentiment"
        fp = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_POS.txt"
        fpn = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEG.txt"
        fpe = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEU.txt"
        fps = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_SCO.txt"
        if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/{fn}/"):
            os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/{fn}/")
        if file_exists(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_POS.txt") is True and os.path.exists(fp) is False:
            status = 0
            download_blob(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_POS.txt",f"{fp}")
            download_blob(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEG.txt",f"{fpn}")
            download_blob(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEU.txt",f"{fpe}")
            download_blob(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_SCO.txt",f"{fps}")

        score = ''
        pos = ''
        neg = ''
        neu = ''
        if os.path.exists(fps):
            score = text_extract(fps)
        else:
            return JsonResponse({"score": None, "pos": None, "neg": None, "neu": None, "ticker": None, "year": None, "qrtr": None, "status": 404})
        if score:
            pos = text_extract(fp)
            neg = text_extract(fpn)
            neu = text_extract(fpe)
        return JsonResponse({"score": score, "pos": pos, "neg": neg, "neu": neu, "ticker": ticker, "year": year, "qrtr": qrtr, "status": 200})
