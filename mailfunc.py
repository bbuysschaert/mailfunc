import getpass

import email
import imaplib

import os

def connect_to_inbox(server_, user_, passw_, **kwargs):
    """
    Connect to the email client through IMAP
    """
    conn_ = imaplib.IMAP4_SSL(server_)
    conn_.login(user_, passw_)
    conn_.select()
    return conn_

def switch_inbox(conn_, inbox_, **kwargs):
    """
    Switch the IMAP connection to a different inbox (= inbox folder)
    """
    conn_.select(inbox_)
    return conn_

def get_emailids_inbox(conn_, inbox_=None, **kwargs):
    """
    Get all email ids from a specified inbox.  Otherwise using the current inbox
    """

    if inbox_:
        conn_ = switch_inbox(conn_, inbox_)

    _, data_ = conn_.search(None, 'ALL')

    return data_[0].split()

def get_emailids_query(conn_, query_='', qtype_='from', qexplicit_=False, **kwargs):
    """
    Get all email ids from the emails after a simple query.  Accepts explicit queries or one structures through query_ and qtype_

    (Dev note: should be created more robust for future use!)
    """
    assert qtype_.upper() in ['FROM', 'SUBJECT'], 'query type not developed!'

    # Construct the query when not an explicit query
    if not qexplicit_:
            query_ = 'HEADER ' + qtype_.upper() + ' \"' + query_ + '\"'

    # Make the search
    _, data_ = conn_.search(None, query_)

    return data_[0].split()

def get_emailbody(conn_, mailid_, **kwargs):
    """
    Get the email message
    """
    resp_, data_ = conn_.fetch(mailid_, '(BODY.PEEK[])')
    assert resp_ == 'OK', f'Invalid response when fetching {mailid_}'

    # Get the mailbody (always this index) -- Should be more robust in the future
    mailbody_ = data_[0][1]

    # Translate the binary content with the email module
    mail_ = email.message_from_bytes(mailbody_)

    return mail_

def download_attachments_email(mail_, outputdir_, **kwargs):
    """
    Download the attachment of the email and write it (binary) at outputdir
    """

    # Check the content type to be multipart (= has attachment)
    if mail_.get_content_maintype() != 'multipart':
        print('No attachements in email received from {}'.format(mail_['From']))
        return
    else:
        for pp in mail_.walk():
            if pp.get_content_maintype() != 'multipart' and pp.get('Content-Disposition') is not None:
                filename_ = outputdir_ + '/' + pp.get_filename()
                print(f'Downloading {pp.get_filename()}')
                with open(filename_, 'wb') as file_:
                    file_.write(pp.get_payload(decode=True))
    return

if __name__ == 'main':
    # Get the user and password from a dynamic entry
    username = getpass.getuser()
    password = getpass.getpass()
    host = 'outlook.office365.com'

    # Create the connection, test it and close it
    with connect_to_inbox(host, username, password) as conn:
        mailids = get_emailids(conn)
        print('Retrieved the ids for {} emails'.format(len(mailids)))
