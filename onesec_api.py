import requests
import json
import random
import string
import lxml.html as HT 

#comment

class Mailbox:
    """Main operation with 1secmail.com api:
    'get' - get all mail in box
    'read' - read message in box (need message id)
    'del' - clear mailbox, all messages be removed!
    """
    
    def __init__(self,mail_name):
        """Constructor"""
        self.API = 'https://www.1secmail.com/api/v1/'
        self.s = requests.Session()
        
        if mail_name == '':
            self._mailbox_ = self.rand_pass()
            #print(f'use mailbox: {self._mailbox_}@1secmail.com')
        else:
           self._mailbox_ = mail_name #change to your own test mailbox
        
    def rand_pass(password=False):
        """Generate a random password or random mail"""
        
        if password:
            special = string.punctuation
        else:
            special = "abcdefghijklmnopqrstuvwxyz1234567890"
        
        randomSource = string.ascii_letters + string.digits
        password = ""
        for i in range(9):
            password += random.choice(randomSource)

        return password

    def rand_pass_for(password=False):
        """Generate a random password or random mail"""
        
        if password:
            special = string.punctuation
        else:
            special = "abcdefghijklmnopqrstuvwxyz1234567890"
        
        randomSource = string.ascii_letters + string.digits
        password = ""
        n = random.randint(8, 24)
        for i in range(n):
            password += random.choice(randomSource)

        return password


    def mailjobs (self, action, id=None):
        """Main operation with 1secmail.com api:
        'get' - get all mail in box
        'read' - read message in box (need message id)
        'del' - clear mailbox, all messages be removed!
        """
        
        mail_list = 'error'
        
        act_ilst = ['getMessages','deleteMailbox','readMessage']
        act_dict = {
            'get':act_ilst[0],
            'del':act_ilst[1],
            'read':act_ilst[2]
        }
            
        if action in ['read', 'readMessage'] and id is None:
            print ('Need message id for reading')
            return mail_list
        
        if action in act_dict:
            action = act_dict[action]
        elif action in act_ilst:
            pass
        else:
            print (f'Wrong action: {action}')
            return mail_list
        
        if action == 'readMessage':
            mail_list = self.s.get(self.API,
                    params={'action':action, 
                        'login':self._mailbox_,
                        'domain':'1secmail.com',
                        'id':id
                        }
                    )
        if action == 'deleteMailbox':
            mail_list = self.s.post('https://www.1secmail.com/mailbox/',
                    data={'action':action, 
                        'login':self._mailbox_,
                        'domain':'1secmail.com'
                        }
                    )
        if action == 'getMessages':
            mail_list = self.s.get(self.API,
                    params={'action':action, 
                        'login':self._mailbox_,
                        'domain':'1secmail.com'
                        }
                    )
                    
        return mail_list


    def filtred_mail (self, domain=True, subject=True, id=True, date=True):
        """Simpled mail filter, all params optional"""
            
        ma = self.mailjobs('get')
        out_mail = []
        if ma != 'error':
            #print(ma.url)
            list_ma = ma.json()
            for i in list_ma:
                if id != True:
                    id_find = i['id'].find(id) != -1
                else:
                    id_find = id
                if date != True:
                    dat_find = i['date'].find(date) != -1
                else: 
                    dat_find = date
                if domain != True:
                    dom_find = i['from'].lower().find(domain.lower()) != -1
                else:
                    dom_find = domain
                if subject != True:     
                    sub_find = i['subject'].lower().find(subject.lower()) != -1
                else:
                    sub_find = subject
                if sub_find and dom_find and id_find and dat_find:
                    out_mail.append(i['id'])
            
            if len(out_mail) >0:
                return out_mail
            else:
                return 'not found'
        else:
            return ma


    def clear_box(self, domain, subject, clear=True):
        """Clear mail box if we find some message"""

        ma = self.filtred_mail(domain, subject)
        if isinstance(ma, list):
            ma = self.mailjobs('read', ma[0])
            if ma != 'error': 
                if clear: print('clear mailbox')
                if clear: x = self.mailjobs ('del')
                return ma
            else:
                return ma
        else:
            return ma


    def get_link(self, domain, subject, x_path='//a', clear=True): 
        """Find link inside html mail body by x-path and return link"""

        ma = self.clear_box(domain, subject, clear)
        if ma != 'error' and ma != 'not found':
            mail_body = ma.json()['body']
        else:
            return ma    
        #try:
        web_body = HT.fromstring(mail_body)   
        #except Type_of_Exception:
        #    print("except")
        child = web_body.xpath(x_path)[0]
        return child.attrib['href']
    
    
if __name__ == "__main__":
    """Easy test"""
    #random box
    ma = Mailbox('')
    #user box
    ma = Mailbox('api.test')
    mb = ma.filtred_mail()
    print('all mail id: ', mb)
    
    if isinstance(mb, list):
        print(mb[0])
        mf = ma.mailjobs('read',mb[0])
        print('first mail: ',mf.json()['body'])
    else:
        mf = 'not found'
   
    print ("if email from gmail.com contain 'Restore password' subject - return restore link and clear mailbox")
    rl = ma.get_link('gmail.com', 'Restore password')
    print ('return link:', rl)
    
