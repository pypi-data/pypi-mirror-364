from robot.api.deco import keyword
from .sap_client import SAPClient
from .auth import load_sap_token_from_file
import json

class SAPKeywords:
    def __init__(self):
        self.client = None

    @keyword("Connect To SAP System")
    def connect_from_file(self, base_url: str, token_file_path: str, verify_ssl: bool = False):
        # access_token = load_sap_token_from_file(token_file_path)
        self.client = SAPClient(base_url, token_file_path)

    @keyword("Get Business Partner By ID")
    def get_business_partner(self, partner_id: str):
        return self.client.get_business_partner(partner_id)

    @keyword("Create Business Partner Address")
    def create_address(self, partner_id: str, json_data: str):
        data = json.loads(json_data)
        return self.client.create_address(partner_id, data)

    @keyword("Update Business Partner Address")
    def update_address(self, partner_id: str, address_id: str, json_data: str):
        data = json.loads(json_data)
        return self.client.update_address(partner_id, address_id, data)

    @keyword("Delete Business Partner Address")
    def delete_address(self, partner_id: str, address_id: str):
        return self.client.delete_address(partner_id, address_id)
