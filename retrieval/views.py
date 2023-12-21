from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .models import Company
from.bucket import download_blob, file_exists
import json, os
import pandas as pd
from django.db.models import Q

# Create your views here.
def index(request):
    return render(request, "retrieval/index.html")

@csrf_exempt
def retrieve(request):
    if request.method == 'POST':
        text = ''
        ktdata = []
        status = 0
        sel = json.loads(request.POST.get('selected'))
        # print("This is the request", type(sel))
        ticker = sel[0]
        try: 
            year = int(sel[1])
        except ValueError:
            year = None
        try: 
            qrtr = int(sel[2])
        except:
            qrtr = None
        srvc = int(sel[3]) if sel[3] != '' else 0

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
            try:
                c = Company.objects.get(pk=ticker).pdf_data_set.all()[0]
            except:
                c = None
            if c is not None:
                wrkarr = [c.pdf1,c.pdf2,c.pdf3,c.pdf4]
                for i in wrkarr:
                    if i != []:
                        if i[1] == year and i[2] == qrtr:
                            pdf = i[0] #if c.pdf1 != [] else ''
                            yr = i[1] # if c.pdf1 != [] else ''
                            qr = i[2] # if c.pdf1 != [] else ''
                            break
                        else:
                            yr = ''
                            qr = ''
                            pdf = ''
                    else:
                        yr = ''
                        qr = ''
                        pdf = ''
                    # pdf2 = c.pdf2[0] if c.pdf2 != [] else ''
                    # pdf3 = c.pdf3[0] if c.pdf3 != [] else ''
                    # pdf4 = c.pdf4[0] if c.pdf4 != [] else ''
                return JsonResponse({'text': '', "ticker": '', "year": yr, "qrtr": qr, "status": 207, "pdf": pdf}) 
            else:
                return JsonResponse({'text': '', "ticker": '', "year": '', "qrtr": '', "status": 404, "pdf": []})

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
        try: 
            year = int(sel[1])
        except ValueError:
            year = None
        try: 
            qrtr = int(sel[2])
        except:
            qrtr = None
        fn = "sentiment"
        fp = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_POS.txt"
        fpn = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEG.txt"
        fpe = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_NEU.txt"
        fps = f"static/documents/{ticker}/{year}/{qrtr}/{fn}/{ticker}_SCO.txt"
        if file_exists(f"fin/{ticker}/{year}/{qrtr}/{fn}/{ticker}_POS.txt") is True:
            if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/{fn}/"):
                os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/{fn}/")
            if os.path.exists(fp) is False:
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
    
start = 0
@csrf_exempt
def auto_complete(request):
    global start
    # print("\n",1)
    start = 1
    if request.method == 'POST':
        val = request.POST.get('nameval') 
        if len(val) == 1:
            c = Company.objects.filter(Q(company_name__istartswith=val) | Q(bse_ticker__istartswith=val))[:10]
        elif len(val) > 4:
            c = Company.objects.filter(Q(company_name__icontains=val) | Q(bse_ticker__istartswith=val))[:10]
        else:
            c = Company.objects.filter(Q(company_name__istartswith=val) | Q(bse_ticker__istartswith=val))[:10]
        # print(c)
        cdict = []
        tickers = None
        tickers = c.values_list('bse_ticker', flat=True)
        for i in range(len(tickers)):
            if start == 1:
                n = c[i].company_name
                t = tickers[i]
                cy = c[i].cur_year
                cq = c[i].cur_quarter
                ay = c[i].a_year
                aq = c[i].a_quarter
                j = c[i].pdf_data_set.all()[0]
                # print(j)
                # print(ay,j.pdf1, j.pdf2, j.pdf3, j.pdf4)
                if ay == [] and (j.pdf1 != [] or j.pdf2 != [] or j.pdf3 != [] or j.pdf4 != []):
                    for k in ay:
                        if j.pdf1[1] == k:
                            continue
                        else:
                            ay.append(j.pdf1[1])
                        if j.pdf2[1] == k:
                            continue
                        else:
                            ay.append(j.pdf2[1])
                        if j.pdf3[1] == k:
                            continue
                        else:
                            ay.append(j.pdf3[1])
                        if j.pdf4[1] == k:
                            continue
                        else:
                            ay.append(j.pdf4[1])
                    cy = j.pdf1[1]
                    # ay.append(j.pdf1[1])
                    try:
                        ay.append(j.pdf2[1])
                    except:
                        pass
                    try:
                        ay.append(j.pdf3[1])
                    except:
                        pass
                    try:
                        ay.append(j.pdf4[1])
                    except:
                        pass
                    # cq = j.pdf1[2]
                    # print(j.pdf1[1],j.pdf1[2])
                cdict.append([n, t, cy, cq, ay, aq])
        start = 0
        return JsonResponse({"cdict":cdict})
