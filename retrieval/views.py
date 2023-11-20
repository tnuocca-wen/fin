from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .models import Company
from.bucket import download_blob, file_exists
import json, os

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
        status = 0
        sel = json.loads(request.POST.get('selected'))
        # print("This is the request", type(sel))
        ticker = sel[0]
        qrtr = int(sel[1])
        srvc = int(sel[2])
        if srvc == 1:
            fn = "summaries"
            fp = f"static/documents/{ticker}/{qrtr}/{ticker}.txt"
            fp1 = fp[:-4]
        elif srvc == 2:
            fn = "sentiments"
            fp = f"static/documents/{ticker}/{qrtr}/{ticker}.txt"
            fp1 = fp[:-4]
        else:
            fn = "translations"
            fp = f"static/documents/{ticker}/{qrtr}/{ticker}.txt"
            fp1 = fp[:-4]
        
        if file_exists(f"{fn}/{ticker}/{qrtr}/{ticker}.txt") is False:
            return JsonResponse({'text': '', "ticker": '', "qrtr": '', "status": 404})
        if os.path.exists(fp) and file_exists(f"{fn}/{ticker}/{qrtr}/{ticker}.txt") is True:
            text = text_extract(fp)
        else:
            print(fp1)
            os.makedirs(f"static/documents/{ticker}/{qrtr}/")
            try:
                if file_exists(f"{fn}/{ticker}/{qrtr}/{ticker}.txt") is True:
                    download_blob(f"{fn}/{ticker}/{qrtr}/{ticker}.txt",f"{fp1}.txt")
                    if not os.path.exists(f"static/documents/{ticker}/{qrtr}/{ticker}.pdf"):
                        # print("hi")
                        download_blob(f"{fn}/{ticker}/{qrtr}/{ticker}.pdf",f"{fp1}.pdf")
                        status = 200
                        text = text_extract(fp)
                else:
                    raise Exception('File absent')
            except:
                text = ''
                ticker = ''
                status = 404

        return JsonResponse({'text': text, "ticker": ticker, "qrtr": qrtr, "status": status})

def text_extract(fp):
    with open(fp, 'r', encoding="utf8") as file:
        fc = file.read()
    return fc