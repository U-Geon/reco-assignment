import csv
import io
from typing import Any, Dict, List

def dict_to_csv(data: Dict[str, Any]) -> str:
    """
    단일 딕셔너리 데이터를 CSV 문자열로 변환합니다.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data.keys())
    writer.writeheader()
    writer.writerow(data)
    return output.getvalue()

def list_of_dicts_to_csv(data_list: List[Dict[str, Any]]) -> str:
    """
    딕셔너리 리스트를 CSV 문자열로 변환합니다.
    """
    if not data_list:
        return ""
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data_list[0].keys())
    writer.writeheader()
    writer.writerows(data_list)
    return output.getvalue()
