# sagikoza
![PyPI - Version](https://img.shields.io/pypi/v/sagikoza)

A Python library for automatically crawling and retrieving all public notices under Japan’s Furikome Sagi Relief Act. Supports both full and incremental data extraction, returning results as a list of dictionaries.

[日本語の説明はこちらを参照して下さい](https://note.com/newvillage/n/n6553ca45bd85)

---

## Features
- Automatically retrieves public notices under the Furikome Sagi Relief Act
- Supports fetching by year or for the latest 3 months
- Incremental (diff) data retrieval
- Returns data as a list of dictionaries

## Supported Environments
- Python 3.8 or later

## Installation
Install from PyPI:
```shell
python -m pip install sagikoza
```

Latest from GitHub:
```shell
git clone https://github.com/new-village/sagikoza
cd sagikoza
python setup.py install
```

## Usage
### Fetch notices for a specific year
Retrieve notices published since 2008 for a given year (e.g., '2025').
```python
import sagikoza
accounts = sagikoza.fetch('2025')
print(accounts)
# [{'doc_id': '12345', 'link': '/pubs_basic_frame.php?...', 'id': '...', ...}, ...]
```

### Fetch notices for the last 3 months
Call without arguments to get notices from the latest 3 months.
```python
import sagikoza
accounts = sagikoza.fetch()
print(accounts)
# [{'doc_id': '12345', 'link': '/pubs_basic_frame.php?...', 'id': '...', ...}, ...]
```

### Save data example
Save the retrieved data in Parquet format.
```python
import pandas as pd
import sagikoza
accounts = sagikoza.fetch()
df = pd.DataFrame(accounts)
df.to_parquet('accounts.parquet', index=False)
```

## Function Specification
- `fetch(year: str = "near3") -> list[dict]`
  - Specify a year (YYYY) or "near3" for the latest 3 months
  - Raises an exception on failure

## Internal Workflow
1. Fetch notice list (POST: sel_pubs.php)
2. Fetch notice details (POST: pubs_dispatcher.php)
3. Fetch basic info (GET: pubs_basic_frame.php)
4. Fetch account details (POST: k_pubstype_00_detail.php, etc.)

Parameters required for each step are extracted from the HTML and used for subsequent page transitions.

## Logging
Uses Python's standard `logging` module. For detailed logs:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
import sagikoza
sagikoza.fetch()
```
By default, only WARNING and above are shown. For more detail, set `level=logging.DEBUG`.

## Error Handling
- Network, HTTP, and timeout errors raise a `FetchError` exception
- If no records are found, a WARNING log is output

## Notes
- This library retrieves data from public sources. Changes to the source website may affect functionality
- Accuracy and completeness of retrieved data are not guaranteed. Please use together with official information

## License
Apache License 2.0
- BeautifulSoup (MIT License)

## Contribution
Bug reports, feature requests, and pull requests are welcome. Please use GitHub Issues or Pull Requests.

## Reference
- [Furikome Sagi Relief Act Notices](https://furikomesagi.dic.go.jp/index.php)

## Page Flow
The web pages to be scraped cannot be accessed directly by URL, but can be transitioned to the next page by making a POST request with a combination of parameters hidden within the page.
Note: pubs_basic_frame.php can exceptionally be accessed via GET.

The web page contents can be obtained by accessing `file` using `methods` and `payload`.
The contents include the payload's value, which is required for accessing other pages, in an element of `parameters`, which can be found using a `selector`.

| category   | file | method | payload | selector | parameters |
| - | - | - | - | - | - |
| notices | sel_pubs.php | POST | {"search_term": "near3", "search_no": "none", "search_pubs_type": "none", "sort_id": "5"} | `table.sel_pubs_list > tbody > input` | `<input type="hidden" name="doc_id" value="15362">` |
| submits | pubs_dispatcher.php | POST | {"head_line": "", "doc_id": "15362"} | `table:nth-child(9) > tbody > tr > td.6 > a` | `<a href="./pubs_basic_frame.php?inst_code=0153&amp;p_id=05&amp;pn=365597&amp;re=0">（別添）</a>` |
| subjects | pubs_basic_frame.php | GET | inst_code=0153&p_id=05&pn=365597&re=0 | `table:nth-child(12) > tbody > tr > td:nth-child(1) > input[type=submit]` | `<form method="POST" name="list_form" action="./k_pubstype_04_detail.php" target="_blank"></form><br><input type="submit" name="r_no" value=" 2420-0153-0007 ">` |
| accounts | k_pubstype_00_detail.php | POST | {"r_no":"+2420-0153-0007+", "pn": "365597", "r_no": "2420-0153-0007", "p_id": "05", "re": "0", "referer": "0"} | | |