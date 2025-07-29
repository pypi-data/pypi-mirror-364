from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_accounts(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse account information from HTML.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        List of dictionaries containing account information
        
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        containers = soup.select('div.container')

        def safe_get_text(element, *args, **kwargs):
            if element is None:
                return ''
            return element.get_text(*args, **kwargs)

        accounts = []
        for c in containers:
            account = {}
            account['role'] = safe_get_text(c.select_one('td.cat5'), strip=True).replace('■', '')
            account['bank_name'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(1) td.data'), strip=True)
            if c.select_one('table:nth-of-type(5)') is not None:
                # For JP Bank
                account['branch_name'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(2) td.data'), strip=True)
                account['branch_code'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(3) td.data'), strip=True)
                account['branch_code_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                account['account_type'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(4) td.data'), strip=True)
                account['account'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(5) td.data'), strip=True)
                account['account_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                account['name'] = safe_get_text(c.select_one('table:nth-of-type(4) tr:nth-of-type(6) td.data'), strip=True).replace('\u3000', ' ')
                account['name_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True).replace('\u3000', ' ')
                account['amount'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                account['effective_from'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(2) td:nth-of-type(3)'), strip=True)
                account['effective_to'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(2) td:nth-of-type(5)'), strip=True)
                account['effective_method'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(3) td.data'), strip=True)
                account['payment_period'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(4) td.data'), strip=True)
                account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(5) td.data'), strip=True)
                account['notes'] = safe_get_text(c.select_one('table:nth-of-type(5) tr:nth-of-type(7) td.data'), strip=True)            
            elif c.select_one('table:nth-of-type(2) tr:nth-of-type(5)') is None:
                # For JP Bank Type 2
                account['branch_code_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                account['account_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                account['name_alias'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True).replace('\u3000', ' ')
                account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True)
            else:
                # For other banks
                account['branch_name'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(2) td.data'), strip=True)
                account['branch_code'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(3) td.data'), strip=True)
                account['account_type'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(4) td.data'), strip=True)
                account['account'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(5) td.data'), strip=True)
                account['name'] = safe_get_text(c.select_one('table:nth-of-type(2) tr:nth-of-type(6) td.data'), strip=True).replace('\u3000', ' ')
                account['amount'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(1) td.data2'), strip=True).replace('★', '')
                account['effective_from'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(3)'), strip=True)
                account['effective_to'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(2) td:nth-of-type(5)'), strip=True)
                account['effective_method'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(3) td.data'), strip=True)
                account['payment_period'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(4) td.data'), strip=True)
                account['suspend_date'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(5) td.data'), strip=True)
                account['notes'] = safe_get_text(c.select_one('table:nth-of-type(3) tr:nth-of-type(7) td.data'), strip=True)
            # Only add account if it has meaningful data
            if any(account.values()):
                accounts.append(account)

        logger.info(f"Parsed {len(accounts)} accounts from HTML")
        return accounts
    
    except Exception as e:
        logger.error(f"Error parsing accounts: {e}")
        return []
