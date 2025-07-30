import pytest
import os
from sheetiq.sheetiq import SheetIQ  # adjust to your module path
from sheetiq.sheetiq import SheetError
from dotenv import load_dotenv
load_dotenv()
# Setup shared sheet object
token = os.getenv("TOKEN")
sheet = SheetIQ({"token":token})
sheet.sheet = ["1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E", "Sheet1"]

def test_get_sheet_returns_array():
    data = sheet.get_sheet()
    assert isinstance(data, list)
   

def test_update_sheet_returns_object():
    data = sheet.get_sheet({"key":False})
    result = sheet.update_sheet({"data":data, "type":"update"})
    assert isinstance(result, (dict, list))  # depending on your return
    
def test_get_sheet_raises_on_empty_sheet_array():
    sheet.sheet = []
    with pytest.raises(SheetError, match="Sheet is not in right format"):
        sheet.get_sheet()

def test_get_sheet_raises_on_missing_sheet_name():
    sheet.sheet = ["fsdf"]
    with pytest.raises(SheetError, match="Sheet is not in right format"):
        sheet.get_sheet()

def test_get_sheet_raises_on_missing_token():
    sheet.token = ''
    with pytest.raises(ValueError, match="Bearer Token not defined"):
        sheet.get_sheet()