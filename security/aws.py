import boto3
import os
from dotenv import load_dotenv

load_dotenv()
aws_access_key = os.environ['AWS_ACCESS_KEY']
aws_secret_key = os.environ['AWS_SECRET_KEY']
aws_region = os.environ['AWS_REGION']

client = boto3.client('ses', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)


def aws_send_email(**kwargs):
    return client.send_email(
                Destination={
                    'ToAddresses': [
                        kwargs['recipient'],
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': kwargs['charset'],
                            'Data': kwargs['body_html'],
                        },
                        'Text': {
                            'Charset': kwargs['charset'],
                            'Data': kwargs['body_text'],
                        },
                    },
                    'Subject': {
                        'Charset': kwargs['charset'],
                        'Data': kwargs['subject'],
                    },
                },
                Source=kwargs['sender']
            )