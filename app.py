from flask import Flask
import smtplib 
import re
import datetime
import os
# https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask
from apscheduler.schedulers.background import BackgroundScheduler
import pymongo
import pprint

app = Flask(__name__)
mongo_uri = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(mongo_uri)
db = client.test

# Getting the collection birthdays
birthdays = None
if(not db.collection_names().__contains__('birthdays')):
   birthdays = db.create_collection('birthdays')
else:
   birthdays = db.birthdays
gmailaddress = "rohan.kumar.smtp@gmail.com"
gmailpassword = "Smtp123456"
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

@app.route("/", methods=['GET'])
def home():
    str = "<html><body><h1>Automated Birthday Wish API Usage:</h1><p>Adding person to birthday list: BaseURL/add/name/email/dob('dd-mm')</p><p>Seeing registerd birthdays: BaseURL/registered</p></body></html>"
    return str

@app.route("/add/<string:name>/<string:email>/<string:dob>", methods=['GET'])
def add(name, email, dob):
   reg = re.compile(regex)
   if(not reg.match(email)):
      return "Invalid Email"
   bday = {
      "name": name,
      "email": email,
      "dob": dob
   }
   if(birthdays.find({"name": name}).count() != 0):
      return "Person already in the database"
   result = birthdays.insert_one(bday)
   res = {
      "result": result.__str__()
   }
   return res

@app.route("/registered", methods=['GET'])
def reg():
   results = birthdays.find()
   l = list(results)
   d = {}
   n = 0
   for i in l:
      i["_id"] = n
      i["email"] = "Hidden"
      d[str(n)] = i
      n+=1
   return d
    


def email_a_birthday_wish(email, msg):
    if(re.search(regex, email)):
        print("Going to wish " + email)
    else:
        return "Invalid email"
    mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
    mailServer.starttls()
    mailServer.login(gmailaddress , gmailpassword)
    mailServer.sendmail(gmailaddress, email , msg)
    mailServer.quit()
    print("Success!")
    return "Wished " + email + "!"

    
def get_contacts(filename):
   names = []
   emails = []
   birthdaysWithMonth = []
   res = birthdays.find()
   l = list(res)
   for item in l:
      names.append(item["name"])
      emails.append(item["email"])
      birthdaysWithMonth.append(item["dob"])
   return names, emails, birthdaysWithMonth
        
def checkForBirthdays():
    dt = datetime.datetime.now()
    print("Checking for birthdays on ", dt)
    names, emails, birthdaysWithMonth = get_contacts("contacts.txt")
    for name, email, birthdayWithMonth in zip(names, emails, birthdaysWithMonth):
        if(dt.day == int(birthdayWithMonth.split("-")[0]) and dt.month == int(birthdayWithMonth.split("-")[1])):
            print("It's " + name + " 's birthday!")
            msg = "Happy birthday " + name +  "! Have a great day! - From Rohan"
            email_a_birthday_wish(email,msg)

# The cron job once every day
scheduler  = BackgroundScheduler()
scheduler.add_job(func=checkForBirthdays, trigger="interval", seconds=86400)
scheduler.start()

if __name__ == '__main__':
   app.run(debug=True)

