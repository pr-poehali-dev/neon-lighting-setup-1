import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def handler(event: dict, context) -> dict:
    """Отправка сообщения из формы обратной связи JoyWorld на почту."""
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400',
            },
            'body': ''
        }

    body = json.loads(event.get('body') or '{}')
    name = body.get('name', '').strip()
    email = body.get('email', '').strip()
    message = body.get('message', '').strip()

    if not name or not email or not message:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Заполните все поля'})
        }

    smtp_host = os.environ.get('SMTP_HOST', 'smtp.yandex.ru')
    smtp_port = int(os.environ.get('SMTP_PORT', '465'))
    smtp_user = os.environ['SMTP_USER']
    smtp_password = os.environ['SMTP_PASSWORD']
    to_email = os.environ.get('CONTACT_EMAIL', smtp_user)

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'JoyWorld: новое сообщение от {name}'
    msg['From'] = smtp_user
    msg['To'] = to_email

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f9f9f9; border-radius: 12px;">
      <h2 style="color: #4a1c8f; margin-bottom: 16px;">Новое сообщение с сайта JoyWorld</h2>
      <table style="width: 100%; border-collapse: collapse;">
        <tr>
          <td style="padding: 8px 0; color: #666; width: 80px;"><strong>Имя:</strong></td>
          <td style="padding: 8px 0; color: #222;">{name}</td>
        </tr>
        <tr>
          <td style="padding: 8px 0; color: #666;"><strong>Email:</strong></td>
          <td style="padding: 8px 0; color: #222;"><a href="mailto:{email}" style="color: #4a1c8f;">{email}</a></td>
        </tr>
        <tr>
          <td style="padding: 8px 0; color: #666; vertical-align: top;"><strong>Текст:</strong></td>
          <td style="padding: 8px 0; color: #222; white-space: pre-wrap;">{message}</td>
        </tr>
      </table>
    </div>
    """
    msg.attach(MIMEText(html, 'html'))

    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, to_email, msg.as_string())

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'success': True})
    }
