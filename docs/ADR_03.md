## [ADR] 계층형 아키텍처 (Layered Architecture) 및 DTO 도입

### 1. 배경

초기에는 도메인 모델(`Pydantic Model`)을 API 요청/응답에 그대로 사용했습니다. 

하지만 API 스펙이 변경될 때마다 내부 로직까지 영향을 받거나, 반대로 내부 로직 변경이 API 스펙을 깨뜨리는 문제가 우려되었습니다. 

또한, `app/models`에 모든 로직이 섞여 있어 유지보수가 어려웠습니다.

### 2. 대안 분석

1. **단일 모듈 구조:**
    - 작은 프로젝트에는 적합하나, 기능이 늘어날수록 스파게티 코드가 될 위험이 큼.
2. **MVC 패턴:**
    - Web App에 적합하나, API 서버 특성상 View가 없음.
3. **Controller-Service-Repository (Layered) 패턴:**
    - 관심사의 분리가 명확함

### 3. 결정

**Layered Architecture**를 적용하고 **DTO(Data Transfer Object)** 를 도입했습니다.

- **Controller:** API 요청을 받아 DTO로 변환하고 Service를 호출.
- **Service:** 비즈니스 로직 수행 (도메인 모델 사용).
- **DTO:** API 계층의 데이터 교환 전용 객체 (`OCRRequest`, `WeighbridgeResponse`).
- **Domain Model:** 내부 비즈니스 데이터 객체 (`OCRInput`, `WeighbridgeTicket`).

### 4. 결과

- **장점:** API 스펙 변경이 내부 로직에 영향을 주지 않음 (Decoupling). 각 계층의 역할이 명확하여 테스트 코드 작성이 용이해짐.
- **단점:** DTO와 도메인 모델 간의 변환 로직(Mapping)이 추가되어 보일러플레이트 코드가 발생함.
