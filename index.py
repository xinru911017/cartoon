import requests
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__)

@app.route("/cartoon")
def cartoon():
  url = "https://acgsecrets.hk/bangumi/202210/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result = sp.select(".CV-search")

  for item in result:
    id = item.find("a").get("href").replace("/","").replace("#bangumi_anime_","")
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="anime_name").text
    today = item.find("div", class_="day").text
    today = "每週" + item.find("div", class_="day").text  
    time =  item.find("div", class_="time").text
    link = "https://acgsecrets.hk/bangumi/202210" +item.find("a").get("href").replace("/","")
    doc = {
      "title": title,
      "picture": picture,
      "today": today,
      "time" : time,
      "link": link
    }

    doc_ref = db.collection("動漫卡片").document(id)
    doc_ref.set(doc)

@app.route("/webhook", methods=["POST"])
def webhook():
  req = request.get_json(force=True)
  action =  req.get("queryResult").get("action")
  if (action == "cartoonChoice"):
    date =  req.get("queryResult").get("parameters").get("date")
    info = "您選擇的星期天數是：" + date + "，相關動漫：\n"

    collection_ref = db.collection("動漫卡片")
    docs = collection_ref.get()
    result = ""
    for doc in docs:
        dict = doc.to_dict()
        if date in dict["date"]:
          result += "片名：" + dict["title"] + "\n"
          result += "介紹：" + dict["link"] + "\n\n"
    info += result
  return make_response(jsonify({"fulfillmentText": info}))

@app.route("/")
def index():
    homepage = "<a href=/cartoon target = _blank>動漫查詢</a><br>"
    homepage += "<a href=/webhook target = _blank>對話機器人</a><br>"
    return homepage

if __name__ == "__main__":
    app.run()
