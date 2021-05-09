from flask import Flask
import smtplib 
import re
import datetime
import os
import time
import threading
# https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask
from apscheduler.schedulers.background import BackgroundScheduler
import pymongo
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()
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
gmailpassword = "Maryhadalittlelamb"
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
   
# https://www.geeksforgeeks.org/how-to-create-a-new-thread-in-python/
class thread(threading.Thread): 
   def __init__(self, thread_name, thread_ID): 
      threading.Thread.__init__(self) 
      self.thread_name = thread_name 
      self.thread_ID = thread_ID 

   # helper function to execute the threads
   def run(self): 
         print(str(self.thread_name) +" "+ str(self.thread_ID));
         email_a_birthday_wish(gmailaddress, "Cron job started")
         # The cron job once every day
         scheduler  = BackgroundScheduler()
         scheduler.add_job(checkForBirthdays, trigger="interval", days=1, misfire_grace_time=60, coalesce=True)
         print(str(scheduler.get_jobs()))
         scheduler.start()
         print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

         try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while True:
               time.sleep(5)
         except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            scheduler.shutdown() 

#https://stackoverflow.com/questions/29223222/how-do-i-schedule-an-interval-job-with-apscheduler
@app.route("/start", methods=['GET'])
def start():
   # newThread = thread("Birthday hunting", 1000)
   # newThread.start()
   
   return "CRON started"


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
        
@sched.scheduled_job('cron',day_of_week='mon-fri', hour=17) # 5 PM every weekday 
def checkForBirthdays():
    dt = datetime.datetime.now()
    print("Checking for birthdays on ", dt)
    email_a_birthday_wish(gmailaddress,"Running cron job for the day")
    names, emails, birthdaysWithMonth = get_contacts("contacts.txt")
    for name, email, birthdayWithMonth in zip(names, emails, birthdaysWithMonth):
        if(dt.day == int(birthdayWithMonth.split("-")[0]) and dt.month == int(birthdayWithMonth.split("-")[1])):
            print("It's " + name + " 's birthday!")
            msg = "Happy birthday " + name +  "! Have a great day! - From Rohan"
            email_a_birthday_wish(email,msg)

if __name__ == '__main__':
   # Starting the cron job
   sched.start()
   app.run(debug=True)

