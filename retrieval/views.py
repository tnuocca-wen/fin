from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt,csrf_protect
from .models import Company
from .bucket import download_blob, file_exists
from .generate import text_extraction, split_into_paragraphs, count_words, summarize_stream, download_pdf, takeaways, elab_gen
import json, os
import pandas as pd
from django.db.models import Q
from django.http import StreamingHttpResponse

# Create your views here.
def index(request):
    return render(request, "retrieval/index.html")

# @csrf_exempt
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
                    try:
                        ktdata = elaborate_fetch(ticker, year, qrtr)
                    except:
                        srvc = 1
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
                wrkarr = c.pdfs
                if wrkarr != []:
                    for i in wrkarr:
                        # if i != []:
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
                # print({'text': '', "ticker": ticker, "year": yr, "qrtr": qr, "status": 207, "pdf": pdf})
                return JsonResponse({'text': '', "ticker": ticker, "year": yr, "qrtr": qr, "status": 207, "pdf": pdf}) 
            else:
                return JsonResponse({'text': '', "ticker": '', "year": '', "qrtr": '', "status": 404, "pdf": []})

def text_extract(fp):
    with open(fp, 'r', encoding="utf8") as file:
        fc = file.read()
    return fc

def elaborate_fetch(ticker, year, qrtr):
    if os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv"):
        ktdf = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        ktdf = ktdf.reset_index(drop=True)
        elab1 = list(ktdf['elaboration1']) if not ktdf['elaboration1'].isnull().all() else []
        elab2 = list(ktdf['elaboration2']) if not ktdf['elaboration2'].isnull().all() else []
        elab3 = list(ktdf['elaboration3']) if not ktdf['elaboration3'].isnull().all() else []
        return [elab1, elab2, elab3]
    elif file_exists(f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv"):
        download_blob(f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        ktdf = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        ktdf = ktdf.reset_index(drop=True)
        elab1 = list(ktdf['elaboration1']) if not ktdf['elaboration1'].isnull().all() else []
        elab2 = list(ktdf['elaboration2']) if not ktdf['elaboration2'].isnull().all() else []
        elab3 = list(ktdf['elaboration3']) if not ktdf['elaboration3'].isnull().all() else []
        return [elab1, elab2, elab3]
    else:
        elab_gen(ticker, year, qrtr, 5)
        ktdf = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        ktdf = ktdf.reset_index(drop=True)
        elab1 = list(ktdf['elaboration1']) if not ktdf['elaboration1'].isnull().all() else []
        elab2 = list(ktdf['elaboration2']) if not ktdf['elaboration2'].isnull().all() else []
        elab3 = list(ktdf['elaboration3']) if not ktdf['elaboration3'].isnull().all() else []
        return [elab1, elab2, elab3]

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
# @csrf_exempt
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
        print(c)
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
                print(ay)
                # print(j.pdfs)
                i = 0
                if j.pdfs != []:
                    if ay != []:
                        tmp = []
                        for k in ay:
                            print("eneres")
                            for l in j.pdfs:
                                # print(l[1])
                                if l[1] == int(k):
                                    continue
                                else:
                                    if l[1] in tmp:
                                        pass
                                    else:
                                        tmp.append(l[1])
                            print(tmp)
                        for i in tmp:
                            ay.append(i)
                    else:
                        for l in j.pdfs:
                            ay.append(l[1])
                    # for l in ay:
                    cy = j.pdfs[0][1]
                        # try:
                        #     ay.append(l[1])
                        # except:
                        #     pass
                    cq = j.pdfs[0][2]
                cdict.append([n, t, cy, cq, ay, aq])
        start = 0
        print(ay)
        return JsonResponse({"cdict":cdict})
    

def gen_content(request):
  if request.method == 'POST':
    link = request.POST.get('link')
    tic = request.POST.get('ticker')
    yr = request.POST.get('year')
    qr = request.POST.get('quarter')
    sr = int(request.POST.get('service'))
    pdf_path = f"static/documents/{tic}/{yr}/{qr}/{tic}.pdf"
    if not (file_exists(f"fin/{tic}/{yr}/{qr}/{tic}.pdf") and os.path.exists(f"static/documents/{tic}/{yr}/{qr}/{tic}.pdf")):
        download_pdf(link, pdf_path)
    if sr == 1:
        texts = text_extraction(pdf_path)
        textss = '\n'.join(texts)
        paras = split_into_paragraphs(textss)
        # for text in texts:
            # names = namingFunc(pdf_path)
        para_list = []
        for i,item in enumerate(paras):
            if count_words(item)> 700:
                para_list.append(item)
            elif i == len(paras)-1:
                para_list.append(item)
            else:
                paras[i+1]= item + ' ' + paras[i+1]
        response = StreamingHttpResponse(summarize_stream("gpt-3.5-turbo", para_list, tic, yr, qr))
        response['Content-Type'] = 'text/plain'
    else:
        if file_exists(f"fin/{tic}/{yr}/{qr}/summary/{tic}.txt") == True:
            if os.path.exists(f"static/documents/{tic}/{yr}/{qr}/summary/{tic}.txt"):
                with open(f"static/documents/{tic}/{yr}/{qr}/summary/{tic}.txt", "r") as f:
                    sum = f.read()
                    f.close()
                sum_lst = sum.split("\n\n")
            else:
                download_blob(f"fin/{tic}/{yr}/{qr}/summary/{tic}.txt", f"static/documents/{tic}/{yr}/{qr}/summary/{tic}.txt")
                with open(f"static/documents/{tic}/{yr}/{qr}/summary/{tic}.txt", "r") as f:
                    sum = f.read()
                    f.close()
                sum_lst = sum.split("\n\n")
            response = StreamingHttpResponse(takeaways("gpt-3.5-turbo", sum_lst, tic, yr, qr))
            response['Content-Type'] = 'text/plain'
        else:
            response = HttpResponse('<p>Summary <strong>not</strong> Generated, <strong>Generate the summary first.</strong></p>', content_type='text/html')
            response.status_code = 210
    print(response)
    return response #HttpResponse("hi")
 

def strtktelab(request):
    if request.method == 'POST':
        elab_gen(request.POST.get("ticker"), request.POST.get("year"), request.POST.get("qrtr"), int(request.POST.get("wq")))
        return HttpResponse()