import os
import google.generativeai as genai
import urllib, urllib.request
import re
from dotenv import load_dotenv
import smtplib
from  email.message import EmailMessage
import ssl

# Loads Gemini AI api and email api keys/passwords
load_dotenv()

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,

  # Gemini prompt instructions
  system_instruction="You will be given a string that contains a list of interests at the beggining of the string from the user followed by a list of titles summaries of scientific articles. Your task is to analyze the string containing the lists of interests and scientific article summaries and compare it to lists of interests provided to see how closely they match. After comparing, output the 15 article titles that match the best with the lists of interests provided and rank them from 1 to 15, 1 meaning it matches the best. Also, assign an accuracy rating to each of the top 15 articles from 100 to 0. 100 meaning the article is extremely accurate to the topics given, and 0 being that the article is completely unrelated.",
)

# Stores history of chat logs
history = []

# Input string given to Gemini containing list of topics that the user has interest in
input = "List of interests: Physics and algebra."

# ArXiv Section
# Searches for the most recent 50 articles on ArXiv database
url = 'http://export.arxiv.org/api/query?search_query=all&start=0&max_results=50'
data = urllib.request.urlopen(url)
dataTxt = data.read().decode('utf-8')
entries = re.findall(r'<entry.*?>.*?<title.*?>(.*?)</title>.*?<summary.*?>(.*?)</summary>.*?</entry>', dataTxt, re.DOTALL)

for i, (title, summary) in enumerate(entries, 1):
    input += f"Article {i} Title: {title.strip()}\n"
    input += f"Article {i} Summary: {summary.strip()}\n\n"

user_input = input

# Starts the chat with Gemini
chat_session = model.start_chat(
    history=history
)

response = chat_session.send_message(user_input)

model_response = response.text

print(f"Bot: {model_response}")

history.append({"role": "user", "parts": [user_input]})
history.append({"role": "model", "parts": [model_response]})

# Email Section 
# Sets the reciever, sender, password, body and subject of the email
email_sender = 'ryan811294@gmail.com'
email_password = os.environ.get("EMAIL_PASSWORD")
email_receiver = 'tard@vcu.edu'
subject = "New Scientific Articles"
body = f"{model_response}"

# Assigns values to the em object
em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

# Sends the email using smtplib
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())