# Automated Birthday Wishing Bot via e-mail
I made use of a flask server and MongoDB to keep track of peoples birthdays and mail them a personal greeting on their birthdays by running a simple cron job on the server. 

The server also has a few API end points for adding and displaying existing users.

# Usage
Look at the pre-registered users: https://birthday-wisher-rohan.herokuapp.com/registered
Add a person to the mailing list using: https://birthday-wisher-rohan.herokuapp.com/add/<name>/<email>/<birthday(in format('dd-mm'))
