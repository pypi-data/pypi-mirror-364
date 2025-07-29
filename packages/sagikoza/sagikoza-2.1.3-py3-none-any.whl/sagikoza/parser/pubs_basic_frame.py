from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


def parse_subject(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Parse subject information from HTML.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        List of dictionaries containing subject information
        
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        forms = soup.find_all('form', attrs={'name': 'list_form'})
        form_vals = [form.get('action').replace('./', '') for form in forms if form.has_attr('action')]

        inputs = soup.find_all('input', attrs={'name': 'r_no'})
        input_vals = [input.get('value').strip() for input in inputs if input.has_attr('value')]

        if len(form_vals) != len(input_vals):
            logger.warning(f"Form count ({len(form_vals)}) doesn't match input count ({len(input_vals)})")

        # Ensure we have unique pairs of form and input values
        unique_subjects = set((form, input) for form, input in zip(form_vals, input_vals) if form and input)
        subjects = [{'form': form, 'no': input} for form, input in unique_subjects]
        subjects.sort(key=lambda x: x['no'])

        logger.info(f"Parsed {len(subjects)} subjects from HTML")
        return subjects
    
    except Exception as e:
        logger.error(f"Error parsing subjects: {e}")
        return []

def create_pagination_list(soup: BeautifulSoup) -> List[int]:
    """
    Create a list of pagination parameters from the HTML.
    
    Args:
        soup: BeautifulSoup object containing the HTML
        
    Returns:
        List of integers representing pagination pages
    """
    try:
        # Find pagination links in table.con elements
        tables = soup.select('table.con')
        for table in tables:
            a_tags = table.select('a')
            pagesubmit_tags = [a for a in a_tags if a.get('href') and 'pageSubmit' in a.get('href')]
            
            if pagesubmit_tags:
                # Get the last pageSubmit link and extract the page number
                last_a = pagesubmit_tags[-1]
                href = last_a.get('href', '')
                match = re.search(r'pageSubmit\((\d+)\)', href)
                if match:
                    max_page = int(match.group(1))
                    return list(range(2, max_page + 1))
        
        logger.debug("No pagination links found")
        return []
    except Exception as e:
        logger.error(f"Error creating pagination list: {e}")
        return []