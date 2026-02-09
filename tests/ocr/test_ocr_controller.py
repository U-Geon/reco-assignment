import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
import csv
import io

client = TestClient(app)

# 테스트용 샘플 파일 경로
SAMPLE_FILE_PATH = os.path.join(os.path.dirname(__file__), "../../data/sample_03.json")

def test_upload_ocr_file_success():
    """[POST] /api/v1/ocr/upload-ocr 파일 업로드 성공 테스트"""
    if not os.path.exists(SAMPLE_FILE_PATH):
        pytest.skip(f"Sample file not found at {SAMPLE_FILE_PATH}")

    with open(SAMPLE_FILE_PATH, "rb") as f:
        response = client.post(
            "/api/v1/ocr/upload-ocr", 
            files={"file": ("sample.json", f, "application/json")}
        )
    
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["status_code"] == "SUCCESS"
    
    data = res_json["data"]
    assert data["vehicle_number"] == "5405"
    assert data["total_weight"] == 14080

def test_upload_ocr_invalid_extension():
    """[POST] /api/v1/ocr/upload-ocr 잘못된 확장자 테스트"""
    response = client.post(
        "/api/v1/ocr/upload-ocr", 
        files={"file": ("test.txt", b"dummy", "text/plain")}
    )
    
    assert response.status_code == 400
    res_json = response.json()
    assert res_json["success"] is False
    assert res_json["status_code"] == "FILE_001"

def test_upload_ocr_invalid_json_content():
    """[POST] /api/v1/ocr/upload-ocr 잘못된 JSON 내용 테스트"""
    # .json 확장자지만 내용은 JSON이 아님
    response = client.post(
        "/api/v1/ocr/upload-ocr", 
        files={"file": ("test.json", b"invalid json content", "application/json")}
    )
    
    assert response.status_code == 400
    res_json = response.json()
    assert res_json["success"] is False
    assert res_json["status_code"] == "FILE_002"

def test_export_csv_success():
    """[POST] /api/v1/ocr/export/csv 성공 테스트"""
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
    """[POST] /api/v1/ocr/export/json 성공 테스트"""
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
