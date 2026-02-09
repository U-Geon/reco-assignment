# 계근지 OCR 파싱 서비스 (Weighbridge OCR Parser)

## 배경 

계근지 (차량의 총중량 / 공차 / 실중량 등을 포함한 영수증 형태)의 OCR 결과 텍스트를 입력으로 받아, 업무에 필요한 필드를 정확하고 견고하게 파싱하여 구조화하는 프로젝트입니다.

## 1. 주요 기능

- **노이즈 강건성 (Robustness):** OCR 과정에서 발생하는 공백, 오탈자(`O`->`0`, `S`->`5`), 순서 뒤섞임(Interleaving) 등의 노이즈를 효과적으로 처리합니다.
- **하이브리드 파싱 전략:**
    - **Regex:** 정형화된 패턴(날짜, 시간, 차량번호, 무게) 추출
    - **spaCy NER:** 비정형 텍스트(업체명) 추출
    - **Heuristic:** 입/출고 시간 추론 및 중량 데이터 보정
- **데이터 검증 및 보정:** `총중량 - 공차중량 = 실중량` 공식을 이용한 논리적 정합성 검증(Cross-Validation)을 수행합니다.
- **표준화된 API 응답:** 성공/실패 여부와 에러 코드를 포함한 일관된 JSON 응답 포맷(`ApiResponse`)을 제공합니다.
- **Swagger 문서화:** 상세한 API 명세와 예시 데이터를 제공합니다.

---

## 2. 실행 방법 (로컬 환경)

### 필수 요구사항 (Prerequisites)
- **Python 3.10 ~ 3.12** (3.14는 호환성 문제로 권장하지 않음)
- **pip** (Python Package Installer)

### 설치 및 실행

1. **저장소 클론 및 이동**
   ```bash
   git clone https://github.com/U-Geon/reco-assignment.git
   cd reco-assignment
   ```

2. **가상환경 생성 및 활성화 (권장)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   # venv\Scripts\activate   # Windows
   ```

3. **의존성 설치**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

4. **spaCy 한국어 모델 다운로드**
   ```bash
   python3 -m spacy download ko_core_news_sm
   ```

5. **서버 실행**
   ```bash
   python3 -m app.main
   ```
   - 서버가 실행되면 `http://localhost:8000/docs` 에서 Swagger UI를 확인할 수 있습니다.

### 테스트 실행
```bash
python3 -m pytest
```

---

## 3. 기술 스택 및 환경

| 구분 | 기술 / 라이브러리 | 버전 | 용도 |
| --- | --- | --- | --- |
| **Language** | Python | 3.11+ | 주 개발 언어 |
| **Framework** | FastAPI | 0.109+ | 고성능 비동기 웹 프레임워크 |
| **NLP** | spaCy | 3.7.4+ | 자연어 처리 및 개체명 인식(NER) |
| **Validation** | Pydantic | 2.6.0+ | 데이터 유효성 검사 및 스키마 정의 |
| **Testing** | Pytest | 8.0.0+ | 유닛 및 통합 테스트 |

---

## 4. 설계 및 주요 가정

### 4.1. 아키텍처 (Layered Architecture)
- **Controller (`app/api`):** HTTP 요청 처리, DTO 변환, 응답 포맷팅 담당.
- **Service (`app/services`):** 핵심 파싱 로직 및 비즈니스 규칙(보정, 검증) 수행.
- **Domain Model (`app/models`):** 비즈니스 데이터 구조 정의.
- **Core (`app/core`):** 공통 에러 처리(Exception Filter), 로깅(Interceptor), 응답 포맷 정의.

### 4.2. 파싱 전략 (Parsing Strategy)
1.  **중량 추출 (Weight):**
    -   `총중량 : 11시 33분 14,080 kg` 처럼 라벨과 값 사이에 노이즈가 끼어드는 경우를 대비해 **Non-greedy Regex**를 사용합니다.
    -   단위(`kg`)를 앵커로 삼아 앞쪽의 숫자를 역추적하여 추출합니다.
2.  **차량 번호 (Vehicle No):**
    -   `차량번호` 키워드 뒤의 4자리 숫자를 우선 추출하고, 실패 시 `12가 3456` 형태의 전체 번호 패턴을 찾습니다.
3.  **업체명 (Company Name):**
    -   `상호 :` 라벨 검색 -> `(주)` 패턴 검색 -> `spaCy NER(ORG)` 순서로 시도하는 **하이브리드 방식**을 사용합니다.

### 4.3. 에러 처리 (Error Handling)
- **AOP 기반 처리:** 모든 예외는 `CustomException`으로 변환되거나 `GlobalExceptionHandler`에 의해 포착됩니다.
- **ErrorStatus Enum:** 에러 코드(`FILE_001`, `OCR_001` 등)와 메시지를 중앙에서 관리하여 일관성을 유지합니다.
