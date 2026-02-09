import pytest
from fastapi.testclient import TestClient
from app.main import app
import json
import os
import csv
import io

client = TestClient(app)
SAMPLE_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/sample_03.json")

def test_export_csv_success():
    """[POST] /api/v1/ocr/export/csv 성공 테스트 (파일 업로드)"""
    if not os.path.exists(SAMPLE_FILE_PATH):
        pytest.skip(f"Sample file not found at {SAMPLE_FILE_PATH}")

    with open(SAMPLE_FILE_PATH, "rb") as f:
        response = client.post(
            "/api/v1/ocr/export/csv", 
            files={"file": ("sample.json", f, "application/json")}
        )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment; filename=weighbridge_ticket.csv" in response.headers["content-disposition"]
    
    # CSV 내용 검증
    content = response.text
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["vehicle_number"] == "5405"
    assert rows[0]["total_weight"] == "14080"

def test_export_json_success():
    """[POST] /api/v1/ocr/export/json 성공 테스트 (파일 업로드)"""
    if not os.path.exists(SAMPLE_FILE_PATH):
        pytest.skip(f"Sample file not found at {SAMPLE_FILE_PATH}")

    with open(SAMPLE_FILE_PATH, "rb") as f:
        response = client.post(
            "/api/v1/ocr/export/json", 
            files={"file": ("sample.json", f, "application/json")}
        )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment; filename=weighbridge_ticket.json" in response.headers["content-disposition"]
    
    # JSON 내용 검증
    res_json = response.json()
    assert res_json["vehicle_number"] == "5405"
    assert res_json["total_weight"] == 14080
