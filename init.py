# init.py
# 2021/09/10
import os
import yaml
import inquirer
import logging
import re

logging.basicConfig(filename=os.path.join(os.path.abspath(os.getcwd()),'emltoimg.log'),
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

configFile = os.path.join(os.path.abspath(os.getcwd()),'config.yaml')


def write_yaml(file_path, data):
    with open(file_path, 'w') as f:
        f.write(yaml.dump(data))


def int_validation(answers, current):
    if not re.match('^[+]?[0-9]+$', current):
        raise inquirer.errors.ValidationError('', reason='Must be positive integer')

    return True


def init():

    class C:
        H = '\033[95m'
        B = '\033[94m'
        C = '\033[96m'
        G = '\033[92m'
        W = '\033[93m'
        F = '\033[91m'
        E = '\033[0m'
        BLD = '\033[1m'
        U = '\033[4m'

    print('\n\n', C.W, 'Initialization process started.')

    if not inquirer.prompt({
            inquirer.Confirm(
                1, 
                message='The configuration file will be overwritten if it exists. Proceed?', 
                default=True
            )})[1]:
        return False

    print('\n', C.W, 'First script settings')
        
    scriptSettings = None
    scriptSettings = inquirer.prompt([
        inquirer.Text('maxEmailsPerRun', message='Input max of emails per account per run', default=200, validate=int_validation),
        inquirer.Text('folder', message='Input folder name', default="Inbox"),
        inquirer.List('sort', message='Choose sort type', choices=['descending', 'ascending'], default='descending')
        ])
    scriptSettings['maxEmailsPerRun']=int(scriptSettings['maxEmailsPerRun'])

    
    print('\n', C.W, 'Now enter your AWS credentials')
    
    aswSettings = None
    aswSettings = inquirer.prompt([
        inquirer.Text('accessKeyId', message='Input Access key ID'),
        inquirer.Text('secretAccessKey', message='Input Secret access key'),
        inquirer.Text('bucketName', message='Input Bucket name'),
        inquirer.Text('folderName', message='Input Folder name')
    ]) 

    print('\n', C.W, 'Finally add email (emails):')
    emails = []
    i = 1
    while i <= 10:
        email = {}
        email['email'] = inquirer.prompt({inquirer.Text(1, message=f'Input Email')})[1]
        email['password'] = inquirer.prompt({inquirer.Password(1, message=f'Input Password')})[1]
        email['imapServer'] = inquirer.prompt({inquirer.List(1, message=f'Choose IMAP server', choices=['imap.gmail.com', 'outlook.office365.com', 'imap.mail.yahoo.com', 'imap.mail.me.com', 'other'])})[1]
        if email['imapServer'] == 'other':
            email['imapServer'] = inquirer.prompt({inquirer.Text(1, message=f'Specify IMAP server')})[1]
            email['imapPort'] = int(inquirer.prompt({inquirer.Text(1, message=f'Input IMAP port')})[1])                 
        else:
            email['imapPort'] = 993
        emails.append(email)
        if i < 10:
            if not inquirer.prompt({
                inquirer.Confirm(
                    1, 
                    message=f'Add another email? ({10-i} more available)', 
                )})[1]:
                break
        i += 1
    
    temp = {
        "scriptSettings": scriptSettings,
        'awsSettings': aswSettings,
        'emails': emails
        }
    try:
        write_yaml(configFile, temp)
        print('\n', C.B, 'Config file written successfully','\n')
        logging.info('Config file written successfully')   
    except Exception as err:
        print('\n', C.E, 'An error has occured: ', err, '\n', 'Try one more time.' ,'\n')
        logging.error(f'Config file ({err})')
    


if __name__ == "__main__":
    init()