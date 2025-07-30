<div align="center">
    <img src="https://docapi.datafetchpro.com/featured_google_api.png" width="60%" />
    <br />
    <a href="https://discord.gg/ZkMMxZQf"><img src="https://img.shields.io/discord/1397785576253423616?color=5865F2&logo=discord&logoColor=white" alt="support server" /></a>
    <a href="https://www.npmjs.com/package/sheetiq"><img src="https://img.shields.io/npm/v/sheetiq?maxAge=3600" alt="npm version" /></a>
    <a href="https://www.npmjs.com/package/sheetiq"><img src="https://img.shields.io/npm/dt/sheetiq?maxAge=3600" alt="npm downloads" /></a>
   <a href="https://pypi.org/project/sheetiq/"><img src="https://img.shields.io/pypi/dm/sheetiq.svg" alt="PyPI downloads" /></a>
</div>

# SheetIQ

> Python SDK for reading and writing to Google Sheets using [docapi.datafetchpro.com](https://docapi.datafetchpro.com)

## 🚀 Installation

```bash
pip install sheetiq
```

##  Initlization

```py
from sheetiq.sheetiq import SheetIQ
sheet=SheetIQ({"token":"YOUR_BEARER_TOKEN"})
```

## Get Sheet Data

```py
sheet.get_sheet({"id":"1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E","range":"Sheet1"})
```

## Append Data on Sheet

```py
res = sheet.update_sheet({
    "id": "1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E",
    "range": "Sheet1",
    "type": "append",
    "data": [["example@gmail.com"]]
})
```

## Update Data on Sheet

```py
res = sheet.update_sheet({
    "id": "1jNPCbbYGT49dlXCeWkAoutazh3Cp2awsJyXnWyAKZ8E",
    "range": "Sheet1",
    "type": "update",
    "data": [["example@gmail.com"]]
})
```

