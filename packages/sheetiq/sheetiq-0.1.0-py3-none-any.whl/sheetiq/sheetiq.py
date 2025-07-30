import requests
from .types import SheetIQParam, SheetIQGetSheet, SheetIQUpdateSheet


class SheetIQ:
    def __init__(self, param: SheetIQParam):
        self.token = param["token"]
        self.base_url = "https://docapi.datafetchpro.com"

    def get_sheet(self, params: SheetIQGetSheet):
        """
        Fetch data from Google Sheet.

        Example:
        >>> sheet = SheetIQ({"token": "your_token"})
        >>> data = sheet.get_sheet({"id": "sheet_id", "range": "Sheet1"})
        """
        payload = {
            "id": params["id"],
            "range": params["range"],
            "key": params.get("key", True),
        }
        response = requests.post(
            f"{self.base_url}/api/v1/googlesheet/get",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json=payload
        )
        if response.status_code != 200:
            raise Exception("Failed to fetch sheet data")
        return response.json()

    def update_sheet(self, params: SheetIQUpdateSheet):
        """
        Update or Append data in Google Sheet.

        Example:
        >>> sheet.update_sheet({
        ...   "id": "sheet_id",
        ...   "range": "Sheet1",
        ...   "type": "append",
        ...   "data": [["example@gmail.com"]]
        ... })
        """
        response = requests.post(
            f"{self.base_url}/api/v1/googlesheet/get",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={
                "id": params["id"],
                "range": params["range"],
                "data": params["data"],
                "type": params["type"]
            }
        )
        if response.status_code != 200:
            raise Exception("Failed to update sheet")
        return response.json()