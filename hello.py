from flask import Flask
import smtplib 
import re
import threading
import datetime

gmailaddress = "rohan.kumar.smtp@gmail.com"
gmailpassword = "Smtp123456"
regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'



app = Flask(__name__)

@app.route("/wish/<string:email>", methods=['GET'])
def email(email):
    if(re.search(regex, email)):
        print("Going to wish " + email)
    else:
        return "Invalid email"
    msg = "Happy birthday! Have a great day!"
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
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split("|")[0])
            emails.append(a_contact.split("|")[1])
            birthdaysWithMonth.append(a_contact.split("|")[2])
    return names, emails, birthdaysWithMonth

def setInterval(func, time, daysLimit):
    e = threading.Event()
    c = 0
    while not e.wait(time):
        func()
        if(daysLimit < c):
            print("Stopping server")
            break
        else:
            c+=1

def checkForBirthdays():
    dt = datetime.datetime.now();
    print("Checking for birthdays on ", dt)
    names, emails, birthdaysWithMonth = get_contacts("contacts.txt")
    for name, email, birthdayWithMonth in zip(names, emails, birthdaysWithMonth):
        if(dt.day == int(birthdayWithMonth.split("-")[0]) and dt.month == int(birthdayWithMonth.split("-")[1])):
            print("It's " + name + " 's birthday!")

setInterval(checkForBirthdays, 5, 5)

if __name__ == "__main__":
    app.run()