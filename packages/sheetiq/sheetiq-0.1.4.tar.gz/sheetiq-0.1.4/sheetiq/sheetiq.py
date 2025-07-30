import requests
from .types import SheetIQParam, SheetIQGetSheet, SheetIQUpdateSheet

class SheetError(Exception):
    pass
class SheetIQ:
    def __init__(self, param: SheetIQParam):
        self.token = param["token"]
        self.base_url = "https://docapi.datafetchpro.com"
        self.sheet=[]
    def checkParameter(self):
        if(not self.token): raise ValueError("Bearer Token not defined")
        if(len(self.sheet)) < 2 : raise SheetError("Sheet is not in right format")
        
    def get_sheet(self, params: SheetIQGetSheet | None ={}):
        """
        Fetch data from Google Sheet.

        Example:
        >>> sheet = SheetIQ({"token": "your_token"})
        >>> sheet.sheet=["SHEET_ID","SHEET_NAME"]
        >>> data = sheet.get_sheet()
        """
        self.checkParameter()
        payload = {
            "id":self.sheet[0],
            "range":self.sheet[1],
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
        ...   "type": "append",
        ...   "data": [["example@gmail.com"]]
        ... })
        """
        self.checkParameter()
        response = requests.post(
            f"{self.base_url}/api/v1/googlesheet/get",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            json={
             "id":self.sheet[0],
            "range":self.sheet[1],
                "data": params["data"],
                "type": params["type"]
            }
        )
        if response.status_code != 200:
            raise Exception("Failed to update sheet")
        return response.json()