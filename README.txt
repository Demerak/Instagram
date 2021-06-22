# Instagram Bot 

- :boom: Disclaimer: This is just a quick project I did for fun. There is definitively room for improvements regarding optimization and code best practices. Please keep in mind that if Instagram changed one element class name within the HTML the script won't work, hence those names might need to be changed if this is the case. Anyhow, please read below for more technical details regarding the bot's functionalities. 

- :closed_book: Description: This is a quick script that will store all your follower and following account. Based on that information it will unfollow a certain amount of accounts if they haven't followed you back within 5 days. Following that step, it will follow new accounts based on a specific hashtag to grow your account.

- :blue_book: More information: All of the data is store inside a SQLite database with three tables. The first table is for all the follower's accounts, the second table is for all the following accounts and the third table is for accounts previously unfollow (to make sure the bot doesn't follow them again). The following table also contains the date when the accounts were followed to make sure to unfollow after a few days if they haven't followed back. 

## Configuration 

- Create a config.py file within the same folder and add the email and password of your Instagram account

	    EMAIL = "WRITE_THE_EMAIL_HERE"
	    PASSWORD = "WRITE_THE_PWD_HERE"

- Download the chrome driver that corresponds to the chrome version on your device. Once downloaded, extract the file inside a folder named chrome driver within your working directory. 

- Change the HASHTAG variable to the hashtag you would like the bot to search for and the ACCOUNT_USERNAME variable to your Instagram account username (it will initialize the database with your account name). These two variables can be found at the bottom of the script. 