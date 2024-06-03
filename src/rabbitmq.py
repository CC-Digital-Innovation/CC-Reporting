import json
import os
import ssl

import certifi
from dotenv import load_dotenv
import pika
import requests


# Load environment variables.
load_dotenv()
RABBITMQ_HOSTNAME = os.getenv('RABBITMQ_HOSTNAME')
RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')


# Global variables.
RABBITMQ_CREDENTIALS = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
RABBITMQ_SSL_OPTIONS = pika.SSLOptions(ssl.create_default_context(cafile=certifi.where()))
CUSTOMER_NAME = "Test Customer"
NOCO_DB_API_TOKEN = "16U2jvYgpD0WFeXfIWRKf-XwKLbe_xrzWCkP_YiY"
NOCO_DB_TEST_CUSTOMER_BASE_ID = "plfr4je0dtov3tl"
NOCO_DB_TEST_ALERTS_TABLE_ID = "maejeyyk5wmikzn"


def get_alerts():
    with open("./fake_payloads/fake_alert_payload.json") as alerts_file:
        alerts = json.load(alerts_file)
        return alerts


#Function to run when message has been received
#  Even though they may not be used, I believe the "basic_consume" function is set
#  up to call callback like this so the ch, method, and properties values can
#  be referenced and are required in the function definition
def callback(ch, method, properties, body):
    bodystr = str(body, 'UTF-8') # Converts message to string
    # WORK WE WANT TO DO BASED ON MESSAGE
    if CUSTOMER_NAME in bodystr:
        alerts = get_alerts()
        nocodb_response = requests.post(
            url=f"https://k3sdev.quokka.ninja/nocodb/api/v2/tables/{NOCO_DB_TEST_ALERTS_TABLE_ID}/records",
            headers={"Content-Type": "application/json", "xc-token": NOCO_DB_API_TOKEN},
            json=alerts
        )
        print("Data has been sent to NocoDB!")

    print(f"I got a message from the rabbitmq queue: {bodystr}")


if __name__ == "__main__":
    # Establish connection to the RabbitMQ instance in Kubernetes.
    rabbitmq_connection = pika.BlockingConnection(pika.ConnectionParameters(
          host=RABBITMQ_HOSTNAME,
          port=RABBITMQ_PORT,
          credentials=RABBITMQ_CREDENTIALS,
          ssl_options=RABBITMQ_SSL_OPTIONS
    ))
    rabbitmq_channel = rabbitmq_connection.channel()

    # Sets this up as a consumer of the QUEUE in RabbitMQ. Also defines function to run on callback.
    rabbitmq_channel.basic_consume(queue='test_queue', on_message_callback=callback, auto_ack=True)
    rabbitmq_channel.start_consuming()  # Endless looping function that will wait for a message, execute callback, and then wait for more messages.

    # url = "https://k3sdev.quokka.ninja/nocodb/api/v2/tables/maejeyyk5wmikzn/records"

    # querystring = {"offset":"0","limit":"25","where":"","viewId":"vwx0zsn0t2ouhdsp"}

    # headers = {"xc-auth": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6ImFudGhvbnkuZmFyaW5hQGNvbXB1dGFjZW50ZXIuY29tIiwiaWQiOiJ1c3l5cHlnbTFtY3N1ZG4zIiwicm9sZXMiOnsib3JnLWxldmVsLWNyZWF0b3IiOnRydWV9LCJ0b2tlbl92ZXJzaW9uIjoiNWQzMDQ1MWMzMzc3Y2IzZDM2NGUyZmY0NWQ0YTYzYzAxNjFiOThjODYwNmFiODU1ZTlmODc2MDc0YjliMzIxMWQ0NThmZDI1ODJhYTU0MzgiLCJpYXQiOjE3MTMzNjkwOTIsImV4cCI6MTcxMzQwNTA5Mn0.QYWWS5xjdkkR3ZR6ptFCrBR6TxoPYCAPcIsocv7kiEc"}

    # response = requests.request("GET", url, headers=headers, params=querystring)

    # print(response.text)
