import smtplib
from feedbackanalysis.settings import EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from django.template import loader, Context


def send_email(toaddr, subject, context, template):
    fromaddr = EMAIL_HOST_USER
    pswd = EMAIL_HOST_PASSWORD
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject

    c = context
    t = loader.get_template(template)
    body = t.render(c)

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(fromaddr, pswd)
        text = msg.as_string()
        try:
            server.sendmail(fromaddr, toaddr, text)
            print 'Email Sent!'
        except Exception, e:
            print e
        server.quit()
    except Exception, e:
        print e


def mail_daily_report(toaddr):

    context = Context({
        'name': 'Sachiv',
    })
    send_email(toaddr, 'FA - Daily Report', context, 'ggemail/daily-report.html')
