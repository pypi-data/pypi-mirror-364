import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from ecss_chat_client import Client

from .diagram import create_diagram
from .summary import generate_summary

load_dotenv()

DIAGRAM_NAME = f'{os.getenv("DIAGRAM_NAME", "chart")}.png'


def send_report(proto='https', port='3443',  ssl_verify: bool = False):
    current_dir = Path.cwd()
    report_dir = os.getenv('ALLURE_REPORT', 'allure_report')
    output_path = current_dir / report_dir / os.getenv('REPORT_DIAGRAM_NAME')
    create_diagram()
    client = Client(
        server=os.getenv('REPORT_ELPH_SERVER'),
        username=os.getenv('REPORT_ELPH_USER'),
        password=os.getenv('REPORT_ELPH_PASSWORD'),
        proto=proto,
        port=port,
        verify=ssl_verify,
    )

    # slave = Client(
    #     server=os.getenv('SERVER_IP'),
    #     username=os.getenv('ADMIN_USERNAME'),
    #     password=os.getenv('ADMIN_PASSWORD'),
    #     proto=proto,
    #     port=port,
    #     verify=ssl_verify,
    # )

    # version = slave.different.version()
    info_url = f'{proto}://{os.getenv("SERVER_IP")}:{port}/api/info'
    version = '0.0.0'
    try:
        version_response = requests.get(info_url, verify=False)
        version = version_response.json()['version']

    except requests.exceptions.RequestException:
        pass

    summary = generate_summary(
        project_name=os.getenv('REPORT_PROJECT_NAME', 'elph-chat-server'),
        version=version,
    )

    client.rooms.upload_file(
        room_id=os.getenv('REPORT_ELPH_ROOM_ID'),
        file_path=output_path,
        text=summary,
    )


if __name__ == '__main__':
    send_report()


__all__ = ['send_report']
