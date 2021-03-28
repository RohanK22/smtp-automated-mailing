from flask import Flask
import smtplib 
import re
import threading
import datetime
import time

gmailaddress = "rohan.kumar.smtp@gmail.com"
gmailpassword = "Smtp123456"
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

app = Flask(__name__)

@app.route("/wish/<string:email>", methods=['GET'])
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

@app.route("/add/<string:name>/<string:email>/<string:dob>", methods=['GET'])
def add(name, email, dob):
    file_object = open('contacts.txt', 'a')
    file_object.write("\n" + name + "|" + email + "|" + dob)
    file_object.close()
    return "Added successfully!"

@app.route("/start", methods=['GET'])
def start():
    print("Started Birthday Monitoring")
    setInterval(checkForBirthdays, 86400)
    return "Voila!"

@app.route("/registered", methods=['GET'])
def reg():
    names, emails, birthdaysWithMonth = get_contacts("contacts.txt")
    namesStr = ""
    for name in names:
        namesStr+= name + ","
    return namesStr

if __name__ == "__main__":
    app.run()
    
def get_contacts(filename):
    names = []
    emails = []
    birthdaysWithMonth = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split("|")[0])
            emails.append(a_contact.split("|")[1])
            birthdaysWithMonth.append(a_contact.split("|")[2])
    return names, emails, birthdaysWithMonth

def setInterval(func, time):
    e = threading.Event()
    while not e.wait(time):
        func()
        
def checkForBirthdays():
    dt = datetime.datetime.now()
    print("Checking for birthdays on ", dt)
    names, emails, birthdaysWithMonth = get_contacts("contacts.txt")
    for name, email, birthdayWithMonth in zip(names, emails, birthdaysWithMonth):
        if(dt.day == int(birthdayWithMonth.split("-")[0]) and dt.month == int(birthdayWithMonth.split("-")[1])):
            print("It's " + name + " 's birthday!")
            msg = "Happy birthday " + name +  "! Have a great day! - From Rohan"
            email_a_birthday_wish(email,msg)




