'''
Created on Mar 11, 2011

@author: yeho
'''
import imaplib, configparser, getpass,re,smtplib, time
from datetime import date
from email.mime.text import MIMEText


def read_keywords_from_config_File():
    global debug
    debug=True
    global hostname 
    global username
    global password
    global excluded_keywords
    global keywords
    global M #imap mailbox
    config = configparser.ConfigParser()
    ##debug  print o.readlines()
    config.read('config.txt')
    ##server address of the mailserver
    hostname= config.get('setup', 'mailserver')
    
    ##keywords to filter messages ie laptop/computer
    keywords= config.get('setup','keywords').split(', ')
    
    ## keywords that are not wanted ie doesn't work/broken
    excluded_keywords=config.get('setup','excluded_keywords').strip()
    excluded_keywords=excluded_keywords.split(', ');
    
    ##get username from config file.  
    username= config.get('setup','username');
    password= getpass.getpass()
    ## username is usually your email address
    if len(username)<2:
        raise StandardError('No Username')
    if len(keywords) < 2:
        
        raise StandardError('No keywords found in keywords.txt')
    
    for word in keywords:
        
        if len(word)<3:
            raise StandardError('keyword length too short')
    M = imaplib.IMAP4_SSL(hostname, 993)
    M.login(username, password)
        
def searchThroughUnreadMail():
    if (debug==True):
        print("Today's Date is " + str(date.today()))
        print( "Hostname is " + hostname)
        print( "The keywords are " + str(keywords))
        print( "The excluded keywords are " + str(excluded_keywords))
    M.select()
    searchstring = "(UNSEEN)"
    if len(keywords)<1:
        raise StandardError("no keywords")
    else:
        for word in keywords: 
            searchstring= searchstring + " (OR (BODY \"" + word.strip() + "\")"
        searchstring=searchstring + " (SEEN)"
        for word in keywords:
             searchstring=searchstring + ")" 
    
    if len(excluded_keywords) >1:
        
        for word in excluded_keywords:
            searchstring=searchstring + " (NOT (BODY \"" +word +"\"))"
    if (debug==True):    
        print( "The IMAP search string is " + searchstring)
        
    typ, searchResult = M.search(None, searchstring)
    if (debug==True):    
        print( "search result" + str(searchResult))
    if len(searchResult) >0:
        searchResult=searchResult[0].split()
    
    ##sample (UNSEEN) (OR (BODY "computer") (BODY "laptop"))

    for Id in searchResult:
        typ, wholeEmail = M.fetch(Id, '(BODY[HEADER.FIELDS (FROM SUBJECT)])')
        
        if len(wholeEmail)<0:
            raise StandardError("email header parsing failed")
        if (debug==True): 
            print( wholeEmail)
            print( wholeEmail[0][1])
        #  FROM: "Oliver Yeh" <oliver.k.yeh@gmail.com>
        #  FROM: oliver.k.yeh@gmail.com
        emailRegex= re.compile("([^<>\s]+@[^<>\s\r\\n]+)")
        subjectRegex= re.compile("Subject:([^\r\n]+)")
        subject=subjectRegex.findall(wholeEmail[0][1])
        sender=emailRegex.findall(wholeEmail[0][1])
        if len(subject)<1:
            raise StandardError("No subject")
        sendReply(sender[0],subject[0])
    
    
def sendReply(sender, subject):
    print( sender)
    print( subject)
    file=open("ReuseTemplate.txt")
    msg=MIMEText(file.read())
    file.close()
    print( msg)
    msg['Subject']=subject
    msg['From']= username
    msg['To']= sender
    server=smtplib.SMTP("smtp.gmail.com",587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username,password)
    server.sendmail(username, [sender], msg.as_string())
    #send an email to myself for recordkeeping
    server.sendmail(username, [username], msg.as_string())
    server.quit()
    
if __name__ == '__main__':
    read_keywords_from_config_File()
    while True:
        print( keywords)
        searchThroughUnreadMail()
        time.sleep(5)
        
    
