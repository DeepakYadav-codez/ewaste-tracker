import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from app.config import Config

EMAIL_ADDRESS = Config.EMAIL_ADDRESS
EMAIL_PASSWORD = Config.EMAIL_PASSWORD

# Load templates from app/templates/emails folder
env = Environment(loader=FileSystemLoader("app/templates/emails"))

def send_email_html(to_email, subject, template_name, context):
    try:
        # Load template
        template = env.get_template(template_name)
        html_content = template.render(context)

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        server.quit()
        print("sending to",to_email)
        print("HTML Email sent successfully!")
        return True

    except Exception as e:
        print("Error sending HTML email:", e)
        return False