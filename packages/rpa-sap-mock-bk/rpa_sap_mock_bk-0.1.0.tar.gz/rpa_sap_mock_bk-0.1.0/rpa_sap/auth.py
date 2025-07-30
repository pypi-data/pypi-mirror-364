import json
import io

def load_sap_token_from_file(token_file_path: str) -> str:
    with io.open(token_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
        access_token = data.get("access_token")
        if not access_token:
            raise ValueError("access_token not found in token file.")
        return access_token
