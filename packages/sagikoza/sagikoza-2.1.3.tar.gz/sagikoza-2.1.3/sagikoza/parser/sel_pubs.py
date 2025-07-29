from bs4 import BeautifulSoup
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def parse_notices(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    BeautifulSoupオブジェクトからbutton.button_whiteまたはbutton.button_blueのテキスト内容と
    input[name='doc_id']のvalueを抽出し、リスト辞書形式で返す。

    Args:
        soup: BeautifulSoupオブジェクト

    Returns:
        List[Dict[str, Any]]: 抽出結果のリスト。各要素は{'label': ボタンテキスト, 'doc_id': ドキュメントID}
    
    Raises:
        ValueError: HTMLパースエラーの場合
    """
    try:
        notices: List[Dict[str, Any]] = []

        # ボタン要素を取得
        buttons = soup.find_all('button', class_=['button_white', 'button_blue'])
        # 対応するinput[name='doc_id']を取得
        inputs = soup.find_all('input', attrs={'name': 'doc_id'})

        if len(buttons) != len(inputs):
            logger.warning(f"Button count ({len(buttons)}) doesn't match input count ({len(inputs)})")
        
        for btn, inp in zip(buttons, inputs):
            # ボタン内の文字列を結合
            label = ' '.join(btn.stripped_strings).replace('\u3000', ' ').strip()
            doc_id = inp.get('value', '')
            if label and doc_id:
                notices.append({'label': label, 'doc_id': doc_id})

        logger.info(f"Parsed {len(notices)} notices from HTML")
        return notices
    
    except Exception as e:
        logger.error(f"Error parsing notices: {e}")
        return []