import requests

class SAPClient:
    def __init__(self, base_url: str, access_token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

    def get_business_partner(self, partner_id: str = ''):
        url = f"{self.base_url}/business-partner"
        if partner_id:
            url += f"/{partner_id}"
        response = requests.get(url, headers=self.headers, verify=False)
        response.raise_for_status()
        return response.json()

    def create_address(self, partner_id: str, data: dict):
        url = f"{self.base_url}/business-partner/{partner_id}/address"
        response = requests.post(url, headers=self.headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()

    def update_address(self, partner_id: str, address_id: str, data: dict):
        url = f"{self.base_url}/business-partner/{partner_id}/Address/{address_id}"
        response = requests.put(url, headers=self.headers, json=data, verify=False)
        response.raise_for_status()
        return response.json()

    def delete_address(self, partner_id: str, address_id: str):
        url = f"{self.base_url}/business-partner/{partner_id}/address/{address_id}"
        response = requests.delete(url, headers=self.headers, verify=False)
        response.raise_for_status()
        return response.text
