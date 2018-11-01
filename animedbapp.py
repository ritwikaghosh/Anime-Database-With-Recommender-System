import sqlite3
import csv
from math import sqrt
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import string

conn = sqlite3.connect('animedatabase.db')

fromad = "" #put your gmail address within the quotes
msg = MIMEMultipart()
sub = "Anime Database App password reset"
msg['From'] = fromad
msg['Subject'] = sub

def pass_generator(size = 10, chars = string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class AutoVivification(dict):
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def mainfn(recuser):
    dataset = AutoVivification()
    filename = 'out.csv'
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            r0 = int(row[0])
            r1 = int(row[1])
            r2 = int(row[2])
            dataset[r0][r1] = r2

    def pearson(p1,p2):
        both={}
        for item in dataset[p1]:
            if item in dataset[p2]:
                both[item] = 1
        num_rating = len(both)
        if num_rating == 0 :
            return 0
        p1_ssq = sum([pow(int(dataset[p1][item]),2) for item in both])
        p1_sp = sum([int(dataset[p1][item]) for item in both])
        p1_s =  p1_ssq-(pow(p1_sp,2)/num_rating)
        p2_ssq = sum([pow(int(dataset[p2][item]),2) for item in both])
        p2_sp = sum([int(dataset[p2][item]) for item in both])
        p2_s =  p2_ssq-(pow(p2_sp,2)/num_rating)
        denom = sqrt(p1_s * p2_s)
        prod_both = sum([int(dataset[p1][item]) * int(dataset[p2][item]) for item in both])
        num = prod_both - ((p1_sp * p2_sp)/num_rating)
        if denom == 0 :
            return 0
        else:
            r = num/denom
            return r

    def recommend(per):
        total = {}
        sim_sum = {}
        for other in dataset :
            if other == per:
                continue
            sim = pearson(per,other)
            if sim <= 0 :
                continue
            for item in dataset[other]:
                if item not in dataset[per] or dataset[per][item] == 0 :
                    total.setdefault(item,0)
                    total[item] += int(dataset[other][item])*sim
                    sim_sum.setdefault(item,0)
                    sim_sum[item] += sim
        rank = [(tot/sim_sum[item],item) for item,tot in total.items()]
        rank.sort()
        rank.reverse()
        recom_list = [recommend_item for recommend_item,recommend_item in rank]
        if not recom_list :
            return 0
        return recom_list[0:5]

    umax = conn.execute("SELECT max(userid) FROM user_ratings;")
    for r in umax:
        if recuser > r[0]:
            print("This user has not rated any anime. Please rate some anime to get recommendations.")
        else:
            n1 = int(recuser)
            animelist = recommend(n1)
            if(animelist == 0):
                print("\nNo recommendation! Please try rating some animes.")
            else:
            #print(animelist)
                cursor = conn.execute("SELECT animeid, animename FROM anime_details;")
                cursor2 = conn.execute("SELECT userid, username FROM user;")
                for j in cursor2:
                    for k in j:
                        if(k == n1):
                            print("\nRecommendations for User {} : ".format(j[1]))
                            print("---------------------------------------\n")
                for row1 in cursor:
                    for i in animelist:
                        if(i == row1[0]):
                            if row1[0] < 10 :
                                print("{0}  | {1}".format(row1[0], row1[1]))
                            else:
                                print("{0} | {1}".format(row1[0], row1[1]))

def insertcsv():
    cs = conn.execute("SELECT * FROM user_ratings;")
    file = open('out.csv', 'w+')
    for row2 in cs:
        for col in row2:
            file.write("%d, "%col)
        file.write('\n')
    file.close()
    print("\nDone!")

print("\n          ------------------")
print("          ANIME DATABSE APP")
print("          ------------------\n")
while True:
    print("\n1. User login")
    print("2. User sign up")
    print("3. Admin login")
    print("4. Forgot password?")
    print("5. Exit")
    lch = input("\nEnter your login choice : ")
    if int(lch) < 1 or int(lch) > 5:
        print("\nInvalid choice! Enter again!")
    else :
        if int(lch) == 5 :
            print("\nBye! See you again!\n")
            conn.close()
            break
        if int(lch) == 1:
            login = conn.execute("SELECT emailid, password, userid FROM login_info;")
            print("\nPlease log in to your account\n")
            emailid = input("Email ID : ")
            x = -1
            y = 0
            for row in login:
                if row[0] == emailid:
                    x = 0
                    break
            if x == -1:
                print("\nThis email ID does not exist in the database!\n")
                break
            while True:
                password = getpass.getpass(prompt='Password', stream = None)
                if(password == row[1]):
                    print("\nWelcome!!\n")
                    y = row[2]
                    break;
                else:
                    print("Wrong password!!")
                    print("Please re-enter your password")
            anime = conn.execute("SELECT * FROM anime_details;")
            print("Here is a list of all the anime in the database\n")
            lx = conn.execute("SELECT max(length(animename)) FROM anime_details;")
            lg = 0
            for i in lx :
                lg = i[0]
            print("|"+("-"*int(lg*1.2))+ "|")
            for r1 in anime:
                if(r1[0] < 10):
                    print(" {0}  | {1}".format(r1[0], r1[1]))
                    print("|"+("-"*int(lg*1.2))+ "|")
                else :
                    print(" {0} | {1}".format(r1[0], r1[1]))
                    print("|"+("-"*int(lg*1.2))+ "|")

            while True:
                print("\n CHOICES:\n")
                print("1. Get anime recommendation")
                print("2. Select anime ID to view anime details")
                print("3. Rate an anime")
                print("4. Remove rating of an anime")
                print("5. Update personal details")
                print("6. Logout")
                ch = input("\nEnter your choice: ")
                if(int(ch) > 6 or int(ch) < 1):
                    print("Invalid Choice! Please choose again")
                else:
                    if(ch == '2'):
                        id = input("Enter anime id: ")
                        anime = conn.execute("SELECT * FROM anime_details;")
                        ratings = conn.execute("SELECT animeid, avg(rating) FROM user_ratings GROUP BY animeid;")
                        genres = conn.execute("SELECT genrename FROM genre WHERE animeid = %s" % int(id))
                        crt = conn.execute("SELECT creatorname FROM creators WHERE animeid = %s" % int(id))
                        print("----" * 29)
                        for r1 in anime:
                            if r1[0] == int(id):
                                print(r1[1])
                                print("\nNO. OF EPISODES = {}".format(r1[2]))
                                print("\nAGE LIMIT = {}".format(r1[3]))
                                for r2 in ratings:
                                    if(r2[0] == int(id)):
                                        print("\nAVERAGE RATING = %.2f" % r2[1])
                                print("\nGENRES :")
                                for r2 in genres:
                                    print(r2[0])
                                print("\nCREATORS :")
                                for r2 in crt:
                                    print(r2[0])
                                print("\nSUMMARY :")
                                print(r1[4])
                                print("----" * 29)
                                break
                
                    if(ch == '1'):
                        mainfn(row[2])
                    
                    if ch == '5' :
                        print("\n1. Update name")
                        print("2. Update location")
                        print("3. Update email address")
                        print("4. Update password")
                        nuch = input("Enter your choice : ")
                        uch = int(nuch)
                        if uch < 1 or uch > 4:
                            print("\nInvalid Choice!\n")
                        else:
                            if uch == 1:
                                nm = input("Enter new name : ")
                                conn.execute("UPDATE user SET username = ? WHERE userid = ?" , (nm, y))
                                conn.commit()
                                print("\nDone!")

                            if uch == 2:
                                nl = input("Enter new location : ")
                                conn.execute("UPDATE user SET location = ? WHERE userid = ?" , (nl, y))
                                conn.commit()
                                print("\nDone!!")
                                    
                            if uch == 3:
                                nem = input("Enter new email address : ")
                                rx = conn.execute("SELECT emailid FROM login_info;")
                                x = -1
                                for rxw in rx:
                                    if(rxw[0] == nem):
                                        x = 0
                                        print("This email address already exists!")
                                        break
                                if x == -1 :
                                    conn.execute("UPDATE login_info SET emailid = ? WHERE userid = ?" , (nem, y))
                                    conn.commit()
                                    print("\nDone!")
                                    
                            if uch == 4:
                                op = input("\nEnter old password : ")
                                xnp = conn.execute("SELECT password FROM login_info WHERE userid = %s" % (y))
                                for rxnp in xnp:
                                    if rxnp[0] == op:
                                        np = input("Enter new password : ")
                                        np2 = input("Re-enter new password : ")
                                        if np != np2 :
                                            print("\nPasswords do not match!")
                                        else :
                                            conn.execute("UPDATE login_info SET password = ? WHERE userid = ?" , (np2, y))
                                            conn.commit()
                                            print("\nDone!")
                                    else:
                                        print("\nIncorrect password!")
                    
                    if(ch == '6'):
                        print("\nThank you for using the app! Bye.\n")
                        break
                    
                    if ch == '4' :
                        aid = input("Please enter the anime ID of the anime you want to unrate : ")
                        naid = int(aid)
                        rx = conn.execute("SELECT animeid FROM anime_details;")
                        x = -1
                        for rxw in rx:
                            if rxw[0] == naid:
                                x = 0
                                break
                        if x == -1:
                            print("This anime ID does not exist!!")
                            break
                        rw1 = conn.execute("SELECT animeid FROM user_ratings WHERE userid = %s" % (y))
                        x = -1
                        for rxw1 in rw1:
                            if rxw1[0] == naid:
                                x = 0
                                conn.execute("DELETE FROM user_ratings WHERE userid = %s AND animeid = %s" % (y, naid))
                                conn.commit()
                                insertcsv()
                                break
                        if x == -1:
                            print("You have not rated this anime yet!")

                    if(ch == '3'):
                        rid = input("Enter the ID of the anime you want to rate: ")
                        rid1 = int(rid)
                        r = conn.execute("SELECT animeid, rating FROM user_ratings WHERE userid = %s"%(y))
                        z = -1
                        for r3 in r:
                            if r3[0] == rid1 :
                                z = 0
                                print("You have already rated this anime.")
                                print("Do you want to rate it again?")
                                print("1 : Yes\n2 : No\n")
                                ch2 = input("Enter : ")
                                if int(ch2) < 1 or int(ch2) > 2 :
                                    print("Invalid choice!")
                                else:
                                    if int(ch2) == 2 :
                                        print("Okay!")
                                        break
                                    else:
                                        while True:
                                            rate = input("Enter new rating : ")
                                            rate1 = float(rate)
                                            if rate1 < 1 or rate1 > 5 :
                                                print("Invalid rating! Please rate again.")
                                            else:
                                                conn.execute("UPDATE user_ratings SET rating = %s WHERE userid = %s AND animeid = %s" % (rate1, y, rid1))
                                                conn.commit()
                                                insertcsv()
                                                break
                        if z == -1:
                            while True:
                                print("This is an unrated anime!")
                                rate2 = input("Enter the rating : ")
                                rate3 = float(rate2)
                                if rate3 < 1 or rate3 > 5 :
                                    print("Invalid rating! Please rate again.")
                                else:
                                    conn.execute("INSERT INTO user_ratings VALUES(%s,%s,%s)" % (y, rid1, rate3))
                                    conn.commit()
                                    insertcsv()
                                    break
                                        
        if int(lch) == 2 :
            print("Hello new user!")
            name = input("Please enter your name : ")
            muid = conn.execute("SELECT max(userid) FROM user;")
            uid = 0
            for row in muid :
                uid = row[0] + 1
            loc = input("Please enter your location : ")
            login = conn.execute("SELECT emailid, password, userid FROM login_info;")
            emid = input("Please enter your email ID : ")
            x = -1
            for row in login :
                if row[0] == emid :
                    x = 0
                    print("This email ID is already in use! Please enter a different one")
                    break
            if x == -1 :
                while True:
                    pas = input("Please enter your password : ")
                    pas1 = input("Please re-enter your password : ")
                    if pas == pas1 :
                        break
                    else :
                        print("Password does not match!! Please enter your password again!!")
            conn.execute("INSERT INTO user(userid, username, location) VALUES (?, ?, ?)" , (uid, name, loc))
            conn.execute("INSERT INTO login_info VALUES (?, ?, ?)" , (uid, emid, pas1))
            conn.commit()
            print("Please login to your new account")

        if int(lch) == 3 :
            login = conn.execute("SELECT * FROM admin;")
            print("\nPlease log in to your account")
            emailid = input("\nEmail ID : ")
            x = -1
            y = 0
            for row in login:
                if row[1] == emailid:
                    x = 0
                    break
            if x == -1:
                print("This email ID does not exist in the database!")
                break
            while True:
                password = getpass.getpass(prompt='Password', stream = None)
                if(password == row[2]):
                    print("\nWelcome Admin!!\n")
                    y = row[0]
                    break;
                else:
                    print("Wrong password!!")
                    print("Please re-enter your password")

            while True:
                print("\n1. Add an anime")
                print("2. Delete an anime")
                print("3. View user details")
                print("4. Update login details")
                print("5. Logout")
            
                adch = input("\nEnter your choice : ")
                if int(adch) < 1 or int(adch) > 5 :
                    print("Invalid choice! Please enter again.")
                else :
                    if int(adch) == 5 :
                        print("\nThank you for using the app! Bye.\n")
                        break
                    
                    if int(adch) == 4:
                        print("\n1. Update email ID\n2. Update password")
                        nuch = input("\nEnter your choice : ")
                        uch = int(nuch)
                        if uch < 1 or uch > 2:
                            print("Invalid choice")
                            break
                        else:
                            if uch == 1:
                                aem = input("\nEnter email ID : ")
                                xem = conn.execute("SELECT adminemail FROM admin;")
                                x = -1
                                for rxem in xem:
                                    if rxem[0] == aem :
                                        x = 0
                                        print("\nThis email ID already exists!")
                                        break
                                if x == -1:
                                    conn.execute("UPDATE admin SET adminemail = ? WHERE adminid = ?",(aem,y))
                                    conn.commit()
                                    print("\nDone!")

                            if uch == 2:
                                npo = input("\nEnter old password : ")
                                xnpo = conn.execute("SELECT adminpassword FROM admin WHERE adminid = %s" % (y))
                                for rxnp in xnpo:
                                    if rxnp[0] == npo:
                                        npn = input("\nEnter new password : ")
                                        rnpn = input("Re-enter new password : ")
                                        if npn == rnpn:
                                            conn.execute("UPDATE admin SET adminpassword = ? WHERE adminid = ?", (rnpn, y))
                                            conn.commit()
                                            print("\nDone!")
                                        else:
                                            print("\nPassword does not match")
                                    else:
                                        print("\nIncorrect password!")

                    if int(adch) == 1 :
                        aid = conn.execute("SELECT max(animeid) FROM anime_details;")
                        naid = 0
                        for r in aid:
                            naid = r[0] + 1
                        aname = input("Please enter anime name : ")

                        agl = input("Please enter age limit : ")
                        nofep = input("Please enter number of episodes : ")
                        summ = input("Please enter summary : ")
                        conn.execute("INSERT INTO anime_details VALUES(?, ?, ?, ?, ?)", (naid, aname, nofep, agl, summ))
                        ngn = input("Enter the number of genres : ")
                        for i in range(int(ngn)):
                            gn = input("Please enter genre name : ")
                            conn.execute("INSERT INTO genre VALUES(?,?)", (gn, naid))
                        ncr = input("Enter the number of creators : ")
                        for i in range(int(ncr)):
                            crnm = ""
                            crid = input("Please enter creator ID : ")
                            m = conn.execute("SELECT creatorid, creatorname FROM creators;")
                            x = -1
                            for rw in m:
                                if(rw[0] == int(crid)):
                                    x = 0
                                    crnm = rw[1]
                                    break
                            if x == -1 :
                                crnm = input("Enter creator name : ")
                            conn.execute("INSERT INTO creators VALUES(?,?,?)", (crid, crnm, naid))
                        conn.commit()
                        print("Entered!")
                
                    if int(adch) == 2 :
                        nanid = input("Please enter anime ID of the anime to be deleted : ")
                        anid = int(nanid)
                        m = conn.execute("SELECT animeid FROM anime_details;")
                        x = -1
                        for r in m:
                            if anid == r[0]:
                                x = 0
                                break
                        if x == -1 :
                            print("Anime ID does not exist!")
                        else :
                            conn.execute("DELETE FROM anime_details WHERE animeid = %s" % (anid))
                            conn.execute("DELETE FROM genre WHERE animeid = %s" % (anid))
                            conn.execute("DELETE FROM creators WHERE animeid = %s" % (anid))
                            conn.execute("DELETE FROM user_ratings WHERE animeid = %s" % (anid))
                            conn.commit()
                            insertcsv()
                
                    if int(adch) == 3 :
                        nuid = input("Enter user ID : ")
                        uid = int(nuid)
                        x = -1
                        m = conn.execute("SELECT userid FROM user;")
                        for r in m:
                            if uid == r[0]:
                                x = 0;
                                break
                        if x == -1 :
                            print("User ID does not exist!")
                        else :
                            y = conn.execute("SELECT user.userid, username, location, emailid FROM user, login_info WHERE user.userid = %s AND user.userid = login_info.userid;" % (uid))
                            for row in y:
                                print("\nUser name : {}".format(row[1]))
                                print("Location : {}".format(row[2]))
                                print("Email Address : {}".format(row[3]))
        if int(lch) == 4:
            while True:
                print("Are you an admin or user?\n1. Admin\n2. User\n3. Go to main page")
                npch = input("\nEnter your choice : ")
                pch = int(npch)
                if pch < 0 or pch > 3:
                    print("\nInvalid choice. Please enter again\n")
                else:
                    if pch == 3:
                        print("\nMain page\n")
                        break
                    if pch == 1:
                        aem = input("Please enter your admin email ID : ")
                        xem = conn.execute("SELECT adminemail FROM admin;")
                        x = -1
                        for i in xem:
                            if i[0] == aem:
                                x = 0
                                r = pass_generator()
                                msg['To'] = aem
                                body = "Your new password is "+r+". Please use this password to login to your account and reset your password."
                                msg.attach(MIMEText(body,'plain'))
                                server = smtplib.SMTP('smtp.gmail.com', 587)
                                server.ehlo()
                                server.starttls()
                                server.ehlo()
                                server.login("ritwikaghosh48@gmail.com","cphe-b39p-39fl")
                                text = msg.as_string()
                                server.sendmail(fromad, aem, text)
                                conn.execute("UPDATE admin SET adminpassword = ? WHERE adminemail= ?" , (r, aem))
                                conn.commit()
                                server.quit()
                                print("\nPlease check your registered email ID for your new password.\n")
                                break
                        if x == -1:
                            print("\nThis email ID does not exist in our database")
                            break
                    if pch == 2:
                        uem = input("\nPlease enter your email ID : ")
                        xem = conn.execute("SELECT emailid FROM login_info;")
                        x = -1
                        for i in xem:
                            if i[0] == uem:
                                x = 0
                                r = pass_generator()
                                msg['To'] = uem
                                body = "Your new password is "+r+". Please use this password to login to your account and reset your password."
                                msg.attach(MIMEText(body,'plain'))
                                server = smtplib.SMTP('smtp.gmail.com', 587)
                                server.ehlo()
                                server.starttls()
                                server.ehlo()
                                #SMTP login might fail because Google blocks sign-in attempts from apps which do not use modern security standards.
                                #Turn off this safety feature by going to this link -
                                #https://myaccount.google.com/lesssecureapps
                                server.login("youremail@gmail.com","yourpassword") #put your gmail address and password
                                text = msg.as_string()
                                server.sendmail(fromad, uem, text)
                                conn.execute("UPDATE login_info SET password = ? WHERE emailid = ?" , (r, uem))
                                conn.commit()
                                server.quit()
                                print("\nPlease check your registered email ID for your new password.\n")
                                break
                        if x == -1:
                            print("\nThis email ID does not exist in our database")
                            break