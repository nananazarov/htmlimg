# main.py
# 2021/09/10
import imaplib
import email
from email.header import decode_header
import os
import base64
from bs4 import BeautifulSoup
import logging
from email import policy
import os
import yaml
import boto3
import uuid

configFile = os.path.join(os.path.abspath(os.getcwd()),'config.yaml')

logging.basicConfig(filename=os.path.join(os.path.abspath(os.getcwd()),'emltoimg.log'),
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')


class AWS():
    def __init__(self, accessKeyId, secretAccessKey, bucketName, folderName=""):
        self.accessKeyId = accessKeyId
        self.secretAccessKey = secretAccessKey
        self.bucketName = bucketName
        self.folderName = folderName
        self.session = boto3.Session(aws_access_key_id = self.accessKeyId, aws_secret_access_key = self.secretAccessKey)


    def put_file_tos3folder(self, fileName, data):
        if self.folderName != "":
            key = f'{self.folderName}/{fileName}'
        else: 
            key = fileName
        s3 = self.session.resource('s3')
        s3.Bucket(self.bucketName).put_object(Key = key, Body = data)


def write_to_file(string, path):
    f = open(path, 'w')
    f.write(string)
    f.close()


def check_config():
    this = True
    if not os.path.isfile(configFile):
        this = False
    else:
        f = read_yaml(configFile)
        for i in f['scriptSettings']:
            if f['scriptSettings'][i] == None or f['scriptSettings'][i] == '':
                this = False
        for i in f['awsSettings']:
            if f['awsSettings'][i] == None or f['awsSettings'][i] == '':
                this = False
        for i in f['emails']:
            for l in i:
                if i[l] == None or i[l] == '':
                    this = False
    return this


def read_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f.read())


def save_html_as_png(html, path, quality=80, zoom=0.8):
    temp = "temp.html"
    try:
      os.remove(temp)
    except:
      pass
    write_to_file(html, temp)
    os.system(f'xvfb-run wkhtmltoimage --quality {quality} --zoom {zoom} "{temp}" "{path}"')
    os.remove(temp)


def get_part_filename(part):
    filename = part.get_filename()
    if decode_header(filename)[0][1] is not None:
        filename = decode_header(filename)[0][0].decode(decode_header(filename)[0][1])
    return filename


def message_processing(msg, aws):
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1], policy=policy.default)

            subject = msg['Subject']
            From = msg['From']
            print("Subject:", subject)
            print("From:", From)

            if msg.get_content_type() == "text/html":
                dec = msg.get_content_charset()
                html = msg.get_payload(decode=True).decode(dec)
                save_html_as_png(html, 'temp.png')
                data = open('temp.png', 'rb')
                aws.put_file_tos3folder(uuid.uuid4().hex + '.png', data)
                os.remove('temp.png')

            if msg.is_multipart():
                html = ""
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        dec = part.get_content_charset()
                        html = part.get_payload(decode=True).decode(dec)
                
                if html != "":
                    soup = BeautifulSoup(html, 'html.parser')
                    for part in msg.walk():
                        if part.get_content_type() in ['image/jpeg', 'image/png']:
                            dat = f'data:{part.get_content_type()};base64,' + base64.b64encode(part.get_payload(decode=True)).decode('utf-8')
                            tag = soup.find('img', attrs = {'src' : 'cid:' + part.get('Content-ID')[1:-1]})

                            filename = get_part_filename(part)
                            if tag == None:
                                tag = soup.find('img', attrs = {'src' : 'cid:'+filename})
                            if tag == None:
                                tag = soup.find('img', attrs = {'src' : 'cid:' + os.path.splitext(filename)[0]})
                            if tag == None:
                                tag = soup.find('img', attrs = {'alt' : filename})
                            if tag == None:
                                tag = soup.find('img', attrs = {'alt' : os.path.splitext(filename)[0]})

                            if tag == None:
                                continue
                            tag['src'] = dat
                    save_html_as_png(str(soup),  'temp.png')
                    data = open('temp.png', 'rb')
                    aws.put_file_tos3folder(uuid.uuid4().hex + '.png', data)
                    os.remove('temp.png')   
                    

def main(): 
    logging.info('Start')
    if not check_config():
        print("\033[93m","The configuration file is missing or contains empty parameters. Try to run Init script first.")
        return False
    scrCon = read_yaml(configFile)['scriptSettings']
    aws = read_yaml(configFile)['awsSettings']
    emails = read_yaml(configFile)['emails']
    
    aws = AWS(aws['accessKeyId'], aws['secretAccessKey'], aws['bucketName'], aws['folderName'])
    for email in emails:
        imap = imaplib.IMAP4_SSL(email['imapServer'],email['imapPort'])
        try:
            imap.login(email['email'], email['password'])
            logging.info(f'Log in as {email["email"]}')
        except Exception as err:
            logging.error(f'Log in as {email["email"]} ({err})')
        imap.select(scrCon['folder'])
        status, messages = imap.uid('search', '(UNSEEN)')
        messages = messages[0].split()
        messages = messages[:scrCon['maxEmailsPerRun']]
        if scrCon['sort'] == "descending":
            messages = reversed(messages)
        for i in messages:
            res, msg = imap.uid('fetch', i, '(RFC822)')
            try:
                message_processing(msg, aws)
            except Exception as err:
                logging.error(f'Message ID{i} ({err})')
                imap.uid('STORE', i, '-FLAGS', '(\Seen)')
        imap.close()
        imap.logout()
        logging.info('End')


if __name__ == "__main__":
    main()