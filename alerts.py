
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

def send_email_smtp(host, port, user, password, to_addr, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = user
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        context = ssl.create_default_context()
        with smtplib.SMTP(host, port) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(user, to_addr, msg.as_string())
        return True, "Email sent."
    except Exception as e:
        return False, f"Email error: {e}"

def send_telegram_message(bot_token, chat_id, text):
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
        if r.status_code == 200:
            return True, "Telegram sent."
        return False, f"Telegram error: {r.text}"
    except Exception as e:
        return False, f"Telegram error: {e}"
