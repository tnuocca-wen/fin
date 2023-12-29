import os, json
from openai import OpenAI
import pdftotext
import re
import requests
from .bucket import upload_blob, file_exists
from django.shortcuts import HttpResponse


client = OpenAI()


def text_extraction(path):
  with open(path, "rb") as f:
      pdf = pdftotext.PDF(f)
  text = []
  # All pages
  for txt in pdf:
    text.append(txt)
  return text


def split_into_paragraphs(long_string):
    paragraphs = re.split(r'\n{1,}', long_string)
    return paragraphs

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
