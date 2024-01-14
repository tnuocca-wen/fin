import os, json
import openai
from openai import OpenAI
import pdftotext
import re
import requests
from .bucket import upload_blob, file_exists, download_blob, download_folder, upload_folder
from django.shortcuts import HttpResponse
import chromadb
from chromadb.utils import embedding_functions
import nltk
import tiktoken
import string
import pandas as pd

client = OpenAI()
openai.api_key = os.environ["OPENAI_API_KEY"]


def text_extraction(path):
  with open(path, "rb") as f:
      pdf = pdftotext.PDF(f)
  text = []
  # All pages
  for txt in pdf:
    text.append(txt)
  return text


def text_extractionTXT(path):
  with open (path, 'r') as f:
    txt = f.read()
  # for txt in pdf:
  return txt


def split_into_paragraphs(long_string):
    paragraphs = re.split(r'\n{1,}', long_string)
    return paragraphs

nltk.download('punkt')

def split_into_sentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

def num_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def remove_punct(input_string):
  return input_string.translate(str.maketrans('', '', string.punctuation)).lower()

def count_words(input_string):
    words = input_string.split()
    return len(words)

def namingFunc(pdf):
  parts = pdf.split('/')
  compID = parts[-4]
  qurtr = parts[-2]
  year = parts[-3]
  print(pdf)
  return [compID, year, qurtr]

def download_pdf(link, path):
  headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
  res = requests.get(link, headers=headers)
  print(res)
  # os.remove(path)
  if not os.path.exists('/'.join(path.split('/')[0:-1])):
     os.makedirs('/'.join(path.split('/')[0:-1]))
  with open(path, 'wb+') as pdf:
    pdf.write(res.content)
    pdf.close()
  if not file_exists(f"fin/{path.split('/')[-4]}/{path.split('/')[-3]}/{path.split('/')[-2]}/{path.split('/')[-4]}.pdf"):
    upload_blob(path, f"fin/{path.split('/')[-4]}/{path.split('/')[-3]}/{path.split('/')[-2]}/{path.split('/')[-4]}.pdf")
    create_vectors(path.split('/')[-4],path.split('/')[-3],path.split('/')[-4])

def upload_data(request):
   if request.method == 'POST':
      data = json.loads(request.POST.get('dat'))
      if int(data['sr']) == 1:
        finfl = "summary"
      else:
         finfl = "keytakeaways"
      if data['done'] == True:
        with open(f'static/documents/{data["tic"]}/{data["yr"]}/{data["qr"]}/{finfl}/{data["tic"]}.txt', "r+") as f:
          t = f.read()
          if t != '':
            upload_blob(f'static/documents/{data["tic"]}/{data["yr"]}/{data["qr"]}/{finfl}/{data["tic"]}.txt', f'fin/{data["tic"]}/{data["yr"]}/{data["qr"]}/{finfl}/{data["tic"]}.txt')
        return HttpResponse("Uploaded")
      return HttpResponse("Not Uploaded")


def summarize_stream(model, text_list, tic, yr, qr):
  summary = []
  for para in text_list:
    print('')
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a business analyst with expertise in summarizing business meeting transcripts."},
            {"role": "user", "content": f'''summarize the following paragraph with
            short simple sentences. If you encounter any difficulty, just don't say anything about it: "{para}"'''}
            ],
        temperature = 0,
        stream = True
        )
    collected_chunks = []
    collected_messages = []
    for chunk in completion:
        collected_chunks.append(chunk)
        chunk_message = chunk.choices[0].delta.content 
        collected_messages.append(chunk_message)
        # print(chunk_message, end='')
        yield chunk_message if chunk_message is not None else ''
    
    collected_messages = [m for m in collected_messages if m is not None]
    summary.append(''.join([m for m in collected_messages]))
    yield "<br><br>"
    
  summary = '\n\n'.join(summary)
  if not os.path.exists(f'static/documents/{tic}/{yr}/{qr}/summary/'):
      os.makedirs(f'static/documents/{tic}/{yr}/{qr}/summary/')
  with open(f'static/documents/{tic}/{yr}/{qr}/summary/{tic}.txt', 'w+', encoding='utf-8') as sum:
      sum.write(summary)
      sum.close()


def takeaways (model, text_list, tic, yr, qr):
  takeaways = ''
  full_summary = '\n\n'.join(text_list)

  completion = client.chat.completions.create(
      model=model,
      messages=[
          {"role": "system", "content": "You are a business analyst."},
          {"role": "user", "content": f'''list out key takeaways from the following text: "{full_summary}"'''}
          ],
      temperature=0,
      stream=True,)
  collected_chunks = []
  collected_messages = []
  for chunk in completion:
      collected_chunks.append(chunk)
      chunk_message = chunk.choices[0].delta.content 
      collected_messages.append(chunk_message)
      # print(chunk_message, end='')
      yield chunk_message if chunk_message is not None else ''
  
  collected_messages = [m for m in collected_messages if m is not None]
  takeaways = ''.join([m for m in collected_messages])
    
  if not os.path.exists(f'static/documents/{tic}/{yr}/{qr}/keytakeaways/'):
      os.makedirs(f'static/documents/{tic}/{yr}/{qr}/keytakeaways/')
  with open(f'static/documents/{tic}/{yr}/{qr}/keytakeaways/{tic}.txt', 'w+', encoding='utf-8') as tk:
      tk.write(takeaways)
      tk.close()
  elab_gen(tic, yr, qr, 5)

def create_vectors(ticker, year, qrtr):
  if file_exists(f"fin/{ticker}/{year}/{qrtr}/{ticker}.pdf") and not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf"):
    download_blob(f"fin/{ticker}/{year}/{qrtr}/{ticker}.pdf", f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf")
    pdf_path = f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf"
    if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/db"):
      os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/db")
    chclient = chromadb.PersistentClient(path=f"static/documents/{ticker}/{year}/{qrtr}/db")
  elif os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf"):
    pdf_path = f"static/documents/{ticker}/{year}/{qrtr}/{ticker}.pdf"
    if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/db"):
      os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/db")
    chclient = chromadb.PersistentClient(path=f"static/documents/{ticker}/{year}/{qrtr}/db")
  else:
    return
  texts = text_extraction(pdf_path)
  sentences = []
  for i in texts:
    sentences += split_into_sentences(i)

  #corpus
  corpus = []
  for i in range(len(texts) - 4):
    # Concatenate the current element with the next four elements and append to the new list
    concatenated_string = ' '.join(texts[i:i+5])
    corpus.append(concatenated_string)

  #cleaned corpus
  cleaned_corpus = []
  for doc in corpus:
    cleaned_doc = remove_punct(doc)
    cleaned_corpus.append(cleaned_doc)

  openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                  model_name="text-embedding-ada-002"
              )

  collection = chclient.get_or_create_collection(name="Sentences")

  embeddings = openai_ef([i for i in cleaned_corpus])
  print(embeddings)

  collection.add(
      embeddings = embeddings,
      documents = [i for i in cleaned_corpus],
      metadatas = [{"source":f"{i+1}"} for i, s in enumerate(cleaned_corpus)],
      ids = [f"id{i+1}" for i, s in enumerate(cleaned_corpus)]
  )

  if not file_exists(f"fin/{ticker}/{year}/{qrtr}/db/chroma.sqlite3"):
    upload_folder(f"static/documents/{ticker}/{year}/{qrtr}/db", f"fin/{ticker}/{year}/{qrtr}/db")
  else:
    pass


def kt_search(text, ticker, year, qrtr):
  print(text, ticker, year, qrtr)
  if file_exists(f"fin/{ticker}/{year}/{qrtr}/db/chroma.sqlite3"):

    if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/db/chroma.sqlite3"):
      download_folder(f"fin/{ticker}/{year}/{qrtr}/db", f"static/documents/{ticker}/{year}/{qrtr}/db")

    chclient = chromadb.PersistentClient(path=f"static/documents/{ticker}/{year}/{qrtr}/db")

    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                model_name="text-embedding-ada-002")
    collection = chclient.get_or_create_collection(name="Sentences", embedding_function=openai_ef)

    # print([i for i in ktaways])

    seres = collection.query(
    query_texts=[text],
    n_results=1)

    return seres["documents"][0][0]
  else:
    print("creating vector")
    create_vectors(ticker, year, qrtr)
    try:
      chclient = chromadb.PersistentClient(path=f"static/documents/{ticker}/{year}/{qrtr}/db")

      openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                  model_name="text-embedding-ada-002")
      collection = chclient.get_or_create_collection(name="Sentences", embedding_function=openai_ef)

      # print([i for i in ktaways])

      seres = collection.query(
      query_texts=[text],
      n_results=1)

      return seres["documents"][0][0]
    except:
      return ""
  

def elaborate(query, ticker, year, qrtr):
  data = kt_search(query, ticker, year, qrtr)
  if data != "":
    if num_tokens(data) > 2000:
      encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
      data = encoding.decode(encoding.encode(data)[:2000])
    print(num_tokens(data))
    message = f'''Elaborate this in short and simple setences - 
    `{query}`, 
    based on the following extracts (note to use Dates and other relevant information from the given extracts below and *not from the sentence which is to be elaborated)
    {data}'''

    messages = [
        {"role": "system", "content": "You are very good at efficiently elaborating small sentences based on the provided context."},
        {"role": "user", "content": message},
      ]

    response = client.chat.completions.create(
        model= "gpt-3.5-turbo",
        messages=messages,
        temperature=0
        )
    response = response.choices[0].message.content
    print(message)
    print(response)
    return response
  else:
    return ""
  

def elab_gen(ticker, year, qrtr, wq):
  if file_exists(f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt") and (not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt")):
    if not os.path.exists(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/"):
      os.makedirs(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways")
    download_blob(f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt", f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt")
    path = f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt"
  else:
    path = f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.txt"

  kttexts = text_extractionTXT(path)
  ktaways = []
  sent = kttexts.split('\n')
  for i in sent:
    if i != '':
      ktaways.append(i)

  print(kttexts)

  # tempkt = []
  indicators = ['key', 'takeaways', 'takeaways:']
  # for i in range(len(ktaways)):
  tkt = []
  for j in range(len(ktaways)):
    if j==0:
      split = ktaways[j].lower().split()
      try:
        for w in range(len(split)):
          if indicators[0] == split[w] and (indicators[1] == split[w+1] or indicators[2] == split[w+1]):
            tf = True
            break
          else :
            tf = False
      except IndexError:
        tf = False
    if (j==0 and tf): #or (ktaways[j]==''):
      pass# print(ktaways[j])
    else:
      x = ktaways[j].find(" ")
      tkt.append(ktaways[j][(x+1):])
  ktaways = tkt
  del tkt
  if wq == 0:
    df = pd.DataFrame()
    top1 = []
    top2 = []
    top3 = []
    for i in ktaways:
      top1.append(elaborate(i, ticker, year, qrtr))
      pyear = str(eval(year) - 1) if ((eval(qrtr)-2+4)%4)+1 == 4 else year
      if file_exists(f"fin/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt") and not os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        if not os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways"):
          os.makedirs(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways")
        download_blob(f"fin/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt", f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt")
        top2.append(elaborate(i, ticker, pyear, str(((eval(qrtr)-2+4)%4)+1)))
      elif os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        top2.append(elaborate(i, ticker, pyear, str(((eval(qrtr)-2+4)%4)+1)))
      ppyear = eval(year) - 1 if ((eval(qrtr)-3+4)%4)+1 == 3 or ((eval(qrtr)-3+4)%4)+1 == 4 else year
      if file_exists(f"fin/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt") and not os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        if not os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways"):
          os.makedirs(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways")
        download_blob(f"fin/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt", f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt")
        top3.append(elaborate(i, ticker, ppyear, str(((eval(qrtr)-3+4)%4)+1)))
      elif os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        top3.append(elaborate(i, ticker, ppyear, str(((eval(qrtr)-3+4)%4)+1)))
    if top1 != ["" for i in range(len(top1))] or top2 != ["" for i in range(len(top2))] or top3 != ["" for i in range(len(top3))]:
      df["takeaways"] = ktaways
      df["elaboration1"] = top1
      df["elaboration2"] = top2
      df["elaboration3"] = top3
      df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
  elif wq == 1:
    try:
      if not pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv").empty:
        n = 0
        df = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        n = 1
        df = pd.DataFrame()
    except:
      n = 1
      df = pd.DataFrame()
    top1 = []
    for i in ktaways:
      top1.append(elaborate(i, ticker, year, qrtr))
    if top1 != ["" for i in range(len(top1))]:
      if n == 1:
        df["takeaways"] = ktaways
        df["elaboration1"] = top1
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        df["elaboration1"] = top1
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", index = False)
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
  elif wq == 2:
    try:
      if not pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv").empty:
        n = 0
        df = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        n = 1
        df = pd.DataFrame()
    except:
      n = 1
      df = pd.DataFrame()
    top2 = []
    for i in ktaways:
      pyear = str(eval(year) - 1) if ((eval(qrtr)-2+4)%4)+1 == 4 else year
      if file_exists(f"fin/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt") and not os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        if not os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways"):
          os.makedirs(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways")
        download_blob(f"fin/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt", f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt")
        top2.append(elaborate(i, ticker, pyear, str(((eval(qrtr)-2+4)%4)+1)))
      elif os.path.exists(f"static/documents/{ticker}/{pyear}/{str(((eval(qrtr)-2+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        top2.append(elaborate(i, ticker, pyear, str(((eval(qrtr)-2+4)%4)+1)))
    if top2 != []:
      if n == 1:
        df["takeaways"] = ktaways
        df["elaboration2"] = top2
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        df["elaboration2"] = top2
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", index=False)
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
  elif wq == 3:
    try:
      if not pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv").empty:
        n = 0
        df = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        n = 1
        df = pd.DataFrame()
    except:
      n = 1
      df = pd.DataFrame()
    top3 = []
    for i in ktaways:
      ppyear = eval(year) - 1 if ((eval(qrtr)-3+4)%4)+1 == 3 or ((eval(qrtr)-3+4)%4)+1 == 4 else year
      if file_exists(f"fin/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt") and not os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        if not os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways"):
          os.makedirs(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways")
        download_blob(f"fin/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt", f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt")
        top3.append(elaborate(i, ticker, ppyear, str(((eval(qrtr)-3+4)%4)+1)))
      elif os.path.exists(f"static/documents/{ticker}/{ppyear}/{str(((eval(qrtr)-3+4)%4)+1)}/keytakeaways/{ticker}.txt"):
        top3.append(elaborate(i, ticker, ppyear, str(((eval(qrtr)-3+4)%4)+1)))
    if top3 != []:
      if n == 1:
        df["takeaways"] = ktaways
        df["elaboration3"] = top3
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        df["elaboration3"] = top3
        df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", index=False)
        upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
  elif wq==5:
    try:
      if not pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv").empty:
        n = 0
        df = pd.read_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")
      else:
        n = 1
        df = pd.DataFrame()
    except:
      n = 1
      df = pd.DataFrame()
    print("yoyo")
    df["takeaways"] = ktaways
    df["elaboration1"] = ["" for i in range(len(ktaways))]
    df["elaboration2"] = ["" for i in range(len(ktaways))]
    df["elaboration3"] = ["" for i in range(len(ktaways))]
    df.to_csv(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", index=False)
    upload_blob(f"static/documents/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv", f"fin/{ticker}/{year}/{qrtr}/keytakeaways/{ticker}.csv")