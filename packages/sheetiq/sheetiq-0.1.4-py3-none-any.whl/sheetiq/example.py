from sheetiq import SheetIQ
from .types import SheetIQParam, SheetIQGetSheet, SheetIQUpdateSheet

sheet = SheetIQ({"token": "your_token_here"})

# Get as object list
data_obj = sheet.get_sheet({
    "id": "1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E",
    "range": "Sheet1",
    "key": True
})

# Append data
res = sheet.update_sheet({
    "id": "1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E",
    "range": "Sheet1",
    "type": "append",
    "data": [["example@gmail.com"]]
})