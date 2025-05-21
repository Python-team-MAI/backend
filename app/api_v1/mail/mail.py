from fastapi_mail import FastMail, ConnectionConfig, MessageType, MessageSchema
from app.core.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME = settings.mail.MAIL_USERNAME,
    MAIL_PASSWORD = settings.mail.MAIL_PASSWORD,
    MAIL_FROM = settings.mail.MAIL_FROM,
    MAIL_PORT = settings.mail.MAIL_PORT,
    MAIL_SERVER = settings.mail.MAIL_SERVER,
    MAIL_FROM_NAME = settings.mail.MAIL_FROM_NAME,
    MAIL_STARTTLS = settings.mail.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.mail.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.mail.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.mail.VALIDATE_CERTS,
    TEMPLATE_FOLDER= settings.mail.TEMPLATE_FOLDER
)

mail = FastMail(config=conf)


def create_message(recipients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body, 
        subtype=MessageType.html
    )
    return message
    

# @app.post("/email")
# async def send_with_template(email: EmailSchema) -> JSONResponse:

#     message = MessageSchema(
#         subject="Fastapi-Mail module",
#         recipients=email.dict().get("email"),
#         template_body=email.dict().get("body"),
#         subtype=MessageType.html,
#         )

#     fm = FastMail(conf)
#     await fm.send_message(message, template_name="email_template.html") 
#     return JSONResponse(status_code=200, content={"message": "email has been sent"})