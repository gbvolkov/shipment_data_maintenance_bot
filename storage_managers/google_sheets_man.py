import os
from typing import List, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

# Add the parent directory to sys.path
if __name__ == '__main__':
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

import logging
logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self, credentials_file, spreadsheet_id, worksheet='Sheet1'):
        self.credentials_file = credentials_file
        self.spreadsheet_id = spreadsheet_id
        self.worksheet = worksheet
        self.service = self._create_service()

    def _create_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_file, 
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=creds)

    def append_row(self, values: List[Any]):
        sheet = self.service.spreadsheets()
        result = sheet.values().append(
            spreadsheetId=self.spreadsheet_id,
            range=self.worksheet,  # Adjust if your sheet has a different name
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [values]}
        ).execute()
        return result
    
    def get_headers(self) -> List[str]:
        sheet = self.service.spreadsheets()
        range_name = f"{self.worksheet}!1:1"
        values = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            majorDimension='ROWS'  # Ensures data is returned row-wise
        ).execute()
        headers = values.get('values', [])[0]
        return headers

    def append_row_from_json(self, data):
        headers = self.get_headers()
        values = [data.get(header, "") for header in headers]
        self.append_row(values)

# Создаем экземпляр GoogleSheetsManager с нужными параметрами
shipment_store = GoogleSheetsManager(credentials_file=config.GOOGLE_SHEETS_CRED, spreadsheet_id=config.SHIPMENTS_SHEET_ID, worksheet='shipments')
procurement_store = GoogleSheetsManager(credentials_file=config.GOOGLE_SHEETS_CRED, spreadsheet_id=config.PROCUREMENTS_SHEET_ID, worksheet='procurements')


def store_shipment(shipment_json):
    # Добавляем данные в таблицу
    
    shipment = json.loads(shipment_json)
    shipment_store.append_row_from_json(shipment)
    shipment_id = shipment['shipment_id']
    procurements = shipment['procurements']
    if procurements is None:
        return
    procurements = procurements if isinstance(procurements, list) else [procurements]
    for procurement in procurements:
        procurement['shipment_id'] = shipment_id
        procurement_store.append_row_from_json(procurement)


if __name__ == '__main__':
    shipment = """{
        "shipment_id": 1,
        "shipment_date": "07-11-2024",
        "shipment_time": "14:00",
        "customer_name": "Мастер Строй",
        "customer_address": "Ярославское шоссе, дом 114",
        "good": "Бетон марки 220",
        "good_volume": "1 куб",
        "good_price": "4850 руб.",
        "shipment_count": 1,
        "shipment_cost": "7000 руб.",
        "supplier": "Евробетон",
        "procurements": {
            "supplier": "Евробетон",
            "good": "Бетон марки 220",
            "good_price": "4850 руб."
        }
    }"""
    store_shipment(shipment)
