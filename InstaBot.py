"""
@Author: Demerak
@Date: 06/11/2021
@Description: This is a quick script that will store all your follower 
              and following account. Based on that information it will 
              unfollow a certain amount of accounts if they haven't followed 
              you back within 5 days. Following that step, it will follow 
              new accounts based on a specific hashtag to grow your account.
"""

# Core Pkgs
import time
import config
from datetime import datetime

# Data Analysis Pkgs
import pandas as pd

# Web scraping Pkgs
from bs4 import BeautifulSoup

## Database Pkgs
import sqlite3
from sqlite3 import Error

## Selenium Pkgs (Browser automation Pkgs) 
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

class InstaBot:
    def __init__(self, hashtag, account_username, db_file, FOLLOWER_TABLE, FOLLOWING_TABLE, UNFOLLOW_TABLE, FOLLOWERS_HISTORY_TABLE, FOLLOWING_HISTORY_TABLE, UNFOLLOW_HISTORY_TABLE):
        self.hashtag = hashtag
        self.account_username = account_username
        self.db_file = db_file

        self.FOLLOWER_TABLE = FOLLOWER_TABLE
        self.FOLLOWING_TABLE = FOLLOWING_TABLE
        self.UNFOLLOW_TABLE = UNFOLLOW_TABLE

        self.FOLLOWERS_HISTORY_TABLE = FOLLOWERS_HISTORY_TABLE
        self.FOLLOWING_HISTORY_TABLE = FOLLOWING_HISTORY_TABLE
        self.UNFOLLOW_HISTORY_TABLE = UNFOLLOW_HISTORY_TABLE

    @staticmethod
    def create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return conn: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file, 
                                detect_types=sqlite3.PARSE_DECLTYPES |
                                                sqlite3.PARSE_COLNAMES)
            print("Connection Successful")
            return conn
        except Error as e:
            print(e)

        return conn

    @staticmethod
    def create_table(conn, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
            print("Table Created")
        except Error as e:
            print(e)

    def add_f(self, conn, table_name, f_info):
        """ add followers/following account info (f_info)
            a table in the database 
        :param conn: Connection object
        :param table_name: Name of the table 
        :param f_info: followers/following info
        :return c.lastrowid: data of the added followers/following
        """
        if table_name == self.FOLLOWER_TABLE or table_name == self.UNFOLLOW_TABLE:
            sql = """ INSERT INTO {} (url)
                VALUES(?) """.format(table_name)
        elif table_name == FOLLOWING_TABLE:
            sql = """ INSERT INTO {} (url, follow_date)
                VALUES(?,?) """.format(table_name)
        c = conn.cursor()
        c.execute(sql, f_info)
        conn.commit()
        print("Commit Successful")
        return c.lastrowid 

    @staticmethod
    def delete_f(conn, table_name, f_info):
        """ delete followers/following account info (f_info)
            a table in the database 
        :param conn: Connection object
        :param table_name: Name of the table 
        :param f_info: followers/following info
        """
        sql = """ DELETE from {} where url = ? """.format(table_name)
        c = conn.cursor()
        c.execute(sql ,f_info)
        conn.commit()

    def chrome_options(self):
        """ setup chrome options
        """
        option = Options()

        option.add_argument("--disable-infobars")
        option.add_argument("start-maximized")
        option.add_argument("--disable-extensions")

        # Pass the argument 1 to allow and 2 to block
        option.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.notifications": 1 })

        # CHANGE THE executable_path 
        self.driver = webdriver.Chrome(options = option, 
                                        executable_path = "chromedriver\chromedriver.exe")

        # MAXIMIZE THE CHROME PAGE TO FIT THE SCREEN
        self.driver.maximize_window()

        # AMOUNT OF TIME, IN SECONDS, TO WAIT FOR A PAGE LOAD TO COMPLETE BEFORE THROWING AN ERROR
        self.driver.set_page_load_timeout(10) 

        # TIMEOUT, IN SECONDS, TO IMPLICITLY WAIT FOR AN ELEMENT TO BE FOUND, OR A COMMAND TO COMPLETE
        self.driver.implicitly_wait(10)

    def login(self):
        """ login to the instagram account
        """   
        ## REQUEST AND OPEN MAXIMIZE THE INSTAGRAM LOGIN PAGE 
        self.driver.get("https://www.instagram.com/accounts/login/?hl=en&source=auth_switcher")

        ## FIND AND CLEAR THE USERNAME AND PASSWORD FIELD 
        email_box = self.driver.find_element_by_name("username")
        email_box.clear()
        pwd_box = self.driver.find_element_by_name("password")
        pwd_box.clear()

        ## GET THE EMAIL ADDRESS AND PASSWORD FORM THE CONFIG.PY FILE 
        email = config.EMAIL      
        pwd = config.PASSWORD 

        ## SEND THE INSTAGRAM ACCOUNT EMAIL ADDRESS AND PWD TO THE USERNAME AND PWD FIELD
        email_box.send_keys(email)
        pwd_box.send_keys(pwd)

        ## LOCATE THE LOGIN BTN AND CLICK
        try :
            login_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            login_btn.click() 
        except :
            print("Oops! Something went wrong")

        # SLEEP FOR 5 SECONDS
        time.sleep(5) 
    
    def get_user_pff(self):
        """ get the user account post btn, followers btn, following btn  
        :return post_btn, followers_btn, following_btn: the three button 
        """
        ## GO ON USER PROFIL TO UPDATE ACCOUNT DATA
        self.driver.get("https://www.instagram.com/" + self.account_username)

        # SLEEP FOR 2 SECONDS
        time.sleep(2)
        
        account_info = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "-nal3")))
        print([pff.text for pff in account_info])

        post_btn, followers_btn, following_btn = account_info[0], account_info[1], account_info[2]
        
        return post_btn, followers_btn, following_btn

    def get_f_list(self, btn, num):
        """ get all the followers/following into a list 
        :param bnt: either the followers_btn or following_btn from get_users_pff
        :param num: either the # of followers or following (int)
        :return f_list: the list of followers/following 
        """
        
        btn.click()

        # SLEEP FOR 2 SECONDS
        time.sleep(2)
        
        f_list = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "FPmhX.notranslate._0imsa"))) 

        count = 0
        while len(f_list) < num:
            time.sleep(1)
            self.driver.execute_script("arguments[0].scrollIntoView();", f_list[-1])
            time.sleep(1)
            f_list = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "FPmhX.notranslate._0imsa"))) 
            print("Number of followers or following found: {}".format(len(f_list)))
            if count == len(f_list): break
            count = len(f_list)

        f_list = [f.get_attribute('href') for f in f_list]
        print("Total Following: {}".format(len(f_list)))
        return f_list 

    def get_table_urls_list(self, table, table_name, f_num):
        """ get all the followers/following from the database into a list 
        :param table: table
        :param table_name: table name
        :param f_num: followers/following #
        :return database_list: database_list or False
        """
        conn = self.create_connection(self.db_file)
        self.create_table(conn, table)

        cur = conn.cursor()
        
        sqlite_select_query = """SELECT url from {}""".format(table_name)
        cur.execute(sqlite_select_query)

        data = cur.fetchall()
        
        conn.close()

        if len(data) != f_num or data == []:
            print("THE # OF FOLLOWERS/FOLLOWING ISN'T ACCURATELY REPRESENTING WHAT WE CURRENTLY HAVE IN THE DATABASE. THE DATABASE NEEDS TO BE UPDATED")
            
            df = pd.DataFrame(data, columns = ["url"])
            database_list = df["url"].tolist() 
        
            return database_list
        else:
            return False

    def update_database(self, database_list, f_num, f_list, table_name):
        """ If # of followers and following isn't the same as what the database
            has, the database is updated. 
        :param database_list: list of followers/following from the database
        :param f_num: # of followers/following from the user account
        :param f_list: list of followers/following from the user account
        :param table_name: name of the table
        """
        print(database_list)
        
        ## IF NUM OF FOLLOWER/FOLLOWING HAS INCREASE
        if len(f_list) > len(database_list):

            url_not_in_database = [url for url in f_list if url not in database_list]

            print(url_not_in_database)

            conn = self.create_connection(self.db_file)
            for url in url_not_in_database:
                if table_name == self.FOLLOWER_TABLE:
                    follow_info = ((url,));
                elif table_name == self.FOLLOWING_TABLE:
                    follow_info = (url, datetime.now());
                self.add_f(conn, table_name, follow_info)
            conn.close()
        
        ## IF NUM OF FOLLOWER/FOLLOWING HAS DECREASE
        elif len(f_list) < len(database_list):
            url_not_in_f_list = [url for url in database_list if url not in f_list]

            print("THE FOLLOWING ACCOUNTS ARE NO LONGER IN THE FOLLOWERS/FOLLOWING LIST: {}".format(url_not_in_f_list))
            
            conn = self.create_connection(self.db_file)
            for url in url_not_in_f_list:
                follow_info = ((url,));
                self.delete_f(conn, table_name, follow_info)
            conn.close()

    def update_user_info(self):
        """ main method that calls other methods to check and 
            update the tables in the databases 
        """
        ## GET USER ACCOUNT INFO BTN (POST BTN, FOLLOWERS BTN, FOLLOWING BTN)    
        post_btn, followers_btn, following_btn = self.get_user_pff()

        followers_num = int(followers_btn.text.replace(' followers', ''))
        following_num = int(following_btn.text.replace(' following', ''))

        followers_database_list = self.get_table_urls_list(self.FOLLOWERS_HISTORY_TABLE, self.FOLLOWER_TABLE, followers_num)
        following_database_list = self.get_table_urls_list(self.FOLLOWING_HISTORY_TABLE, self.FOLLOWING_TABLE, following_num)

        if following_database_list != False:
            
            following_list = self.get_f_list(following_btn, following_num)

            print(following_list)
            
            self.update_database(following_database_list, following_num, following_list, self.FOLLOWING_TABLE)
            
        if followers_database_list != False:
            ## GET USER ACCOUNT INFO BTN (POST BTN, FOLLOWERS BTN, FOLLOWING BTN)  
            post_btn, followers_btn, following_btn = self.get_user_pff()
        
            followers_list = self.get_f_list(followers_btn, followers_num)
            
            close_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "wpO6b")))
            close_btn[-1].click()
            
            print(followers_list)
            
            self.update_database(followers_database_list, followers_num, followers_list, self.FOLLOWER_TABLE)

    def unfollow(self, conn):
        """ delete followers/following account info (f_info)
            a table in the database 
        :param conn: Connection object
        :return list_of_account_not_following: list of account
        """
    
        ## FIND ACCOUNT THAT ARE NOT FOLLOWERS IN THE FOLLOWING LIST 
        sql = """ SELECT * FROM {} WHERE url NOT IN (SELECT url FROM {}) """.format(self.FOLLOWING_TABLE, self.FOLLOWER_TABLE)
        
        ## GET THE FULL LIST OF ACCOUNT THAT AREN'T FOLLOWING BACK
        list_of_account_not_following = conn.execute(sql).fetchall()   
        
        ## ITERATE OVER THE LIST AND KEEP ONLY THE URL OF THE ACCOUNTS THAT HAVEN'T FOLLOW BACK FOR MORE THAN 5 DAYS 
        list_of_account_not_following = [l[1] for l in list_of_account_not_following if (datetime.now() - l[2]).days > 5]
        
        ## TAKES THE FIRST HALF OF THE LIST
        half_list_of_account_not_following = list_of_account_not_following[len(list_of_account_not_following)//2:]
        print(half_list_of_account_not_following)
        
        conn = self.create_connection(self.db_file)  
        self.create_table(conn, self.UNFOLLOW_HISTORY_TABLE)
        
        ## ITERATE OVER THE URLS TO UNFOLLOW THEM 
        for url in half_list_of_account_not_following:
            self.driver.get(url)    
            time.sleep(1)
            ## FIND THE FIRST FOLLOW BUTTON 
            try:
                first_unfollow_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sqdOP.L3NKy._8A5w5")))
                first_unfollow_btn[-1].click()
            except: 
                first_unfollow_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "sqdOP.L3NKy.y3zKF")))
                first_unfollow_btn[-1].click()

            time.sleep(1)
            
            second_unfollow_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "aOOlW.-Cab_")))  
            second_unfollow_btn.click()
            
            follow_info = ((url,));
            self.add_f(conn, self.UNFOLLOW_TABLE, follow_info)
            
        return list_of_account_not_following

    def follow_new_account(self):
        """ main method that gets the url of all the first few accounts found when
            searching a  particular hashtag
        """
        
        ## BEFORE FOLLOWING NEW ACCOUNT, WE NEED TO UNFOLLOW A FEW
        conn = self.create_connection(self.db_file)
        list_of_account_not_following = self.unfollow(conn)
        print(len(list_of_account_not_following))
        print(list_of_account_not_following)

        ## REQUEST THE TOP NEW POST WITH THE REQUESTED HASHTAG
        self.driver.get("https://www.instagram.com/explore/tags/" + self.hashtag + "/")

        # SLEEP FOR 2 SECONDS
        time.sleep(2)

        ## FIND ALL THE PICTURES ELEMENTS AND STORE THEM IN A LIST 
        pictures = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "_9AhH0")))

        ## ITERATE OVER THE LIST OF PICTURES AND CLICK ON EACH OF THEM 
        url_list = []
        for picture in pictures:    
            ## CLICK ON THE PICTURE
            picture.click()
            
            ## FIND THE NAME OF THE PROFILE 
            profil = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "sqdOP.yWX7d._8A5w5.ZIAjV")))
            
            ## FIND THE URL OF THAT PROFILE AND APPEND THE URL TO THE URL_LIST
            url = profil.get_attribute('href')
            url_list.append(url)   
            
            ## CLOSE THE PICTURE TO CLICK ON THE NEXT ONE 
            close_btn = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "wpO6b")))
            
            ## MULTILE ELEMENT HAVE THE SAME CLASS NAMES BUT THE CLOSE BTN IS ALWAYS THE LAST ONE IN THE LIST
            close_btn[-1].click()
            
        print(url_list)

        conn = self.create_connection(self.db_file)

        self.create_table(conn, self.FOLLOWING_HISTORY_TABLE)

        c = conn.cursor()

        for url in url_list:
            try:
                ## REQUEST THE ACCOUNT INSTAGRAM PAGE 
                self.driver.get(url)
                page = self.driver.page_source
                soup = BeautifulSoup(page, 'lxml')
                
                # pff --> post, followers, followings
                ## FIND THE ACCOUNT POSTS, FOLLOWERS, FOLLOWING
                ppf_list = []
                for ppf_data in soup.find_all('span', {'class': 'g47SY'}):
                    ppf_list.append(ppf_data.text)
                
                print(ppf_list)
                ## REMOVE THE COMMA AND REPLACE K OR M BY 1000 AND 1000000
                ppf_list = [ppf.replace(",", "") for ppf in ppf_list]
                ppf_list = [int(1000*float(ppf.replace('k', ''))) if 'k' in ppf else int(ppf) for ppf in ppf_list]
                #ppf_list = [int(1000000*float(ppf.replace('M', ''))) if 'k' in ppf else int(ppf) for ppf in ppf_list]

                print(ppf_list)
                
                ## ADD EACH ELEMENTS OF THE PPF_LIST TO INDIVIDUAL VARIABLE
                posts, followers, following = ppf_list[0], ppf_list[1], ppf_list[2]
                
                sql = """ SELECT url FROM {} WHERE url = ? """.format(UNFOLLOW_TABLE)
                
                c.execute(sql, (url,))
                
                previously_f = c.fetchall()
                
                ## CHECK IF THE ACCOUNT AS ENOUGH FOLLOWERS
                if followers > 1000 and len(previously_f)==0 and following > 500: 
                    try:
                        try:
                            ## TRY TO FIND THE FOLLOW BUTTON IF FIND CLICK 
                            follow_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sqdOP.L3NKy.y3zKF")))
                            follow_btn.click()
                        except: 
                            ## TRY TO FIND THE FOLLOW BUTTON IF FIND CLICK 
                            follow_btn = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "_5f5mN.jIbKX._6VtSN.yZn4P")))
                            follow_btn.click()
                              
                        follow_info = (url, datetime.now());

                        self.add_f(conn, self.FOLLOWING_TABLE, follow_info)

                        print("Follow!")
                    except:
                        ## IF FOLLOW BUTTON NOT FOUND, IT'S BECAUSE THE ACCOUNT IS ALREADY FOLLOW
                        print("Already Following")
                else:
                    print("Not enough followers/following or previously unfollow")

            except Exception as e: 
                print(e)
            
if __name__ == "__main__":
    print("###################################################################")
    print("#                         |INSTAGRAM BOT|                         #")
    print("#                                                                 #")
    print("# This is a quick script that will store all your follower        #")
    print("# and following account. Based on that information it will        #")  
    print("# unfollow a certain amount of accounts if they haven't followed  #")      
    print("# you back within 5 days. Following that step, it will follow     #")  
    print("# new accounts based on a specific hashtag to grow your account   #") 
    print("###################################################################")

    ## CHANGE THE HASHTAG, ACCOUNT_USERNAME     
    HASHTAG = "cars"
    ACCOUNT_USERNAME = "samuel__leblanc"
    DB_FILE = ACCOUNT_USERNAME + ".db"

    FOLLOWER_TABLE = "followers_history"
    FOLLOWING_TABLE = "follow_history"
    UNFOLLOW_TABLE = "unfollow_history"

    FOLLOWERS_HISTORY_TABLE = """ CREATE TABLE IF NOT EXISTS {} (
                                            id integer PRIMARY KEY,
                                            url text NOT NULL
                                        ); """.format(FOLLOWER_TABLE)  

    FOLLOWING_HISTORY_TABLE = """ CREATE TABLE IF NOT EXISTS {} (
                                            id integer PRIMARY KEY,
                                            url text NOT NULL,
                                            follow_date timestamp
                                        ); """.format(FOLLOWING_TABLE)   

    UNFOLLOW_HISTORY_TABLE = """ CREATE TABLE IF NOT EXISTS {} (
                                            id integer PRIMARY KEY,
                                            url text NOT NULL
                                        ); """.format(UNFOLLOW_TABLE) 

    sambot = InstaBot(
        HASHTAG, 
        ACCOUNT_USERNAME, 
        DB_FILE, 
        FOLLOWER_TABLE,
        FOLLOWING_TABLE,
        UNFOLLOW_TABLE,
        FOLLOWERS_HISTORY_TABLE,
        FOLLOWING_HISTORY_TABLE,
        UNFOLLOW_HISTORY_TABLE
    )
    sambot.chrome_options()
    sambot.login()
    sambot.update_user_info()
    sambot.follow_new_account()

    


