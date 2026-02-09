## [ADR] 에러 처리 및 응답 구조 표준화

### 1. 배경
FastAPI의 기본 `HTTPException`을 사용하면 에러 응답 포맷이 일관되지 않고, 프론트엔드나 클라이언트가 에러 원인을 파악하기 위해 매번 다른 필드를 확인해야 하는 문제가 있었습니다. 또한, 비즈니스 로직 곳곳에 에러 메시지가 하드코딩되어 관리가 어려웠습니다.

### 2. 대안 분석
1.  **개별 try-except 처리:**
    -   모든 엔드포인트마다 예외 처리를 반복해야 함. 코드 중복 심화.
2.  **Middleware 활용:**
    -   요청 전후 처리는 좋으나, 구체적인 예외 타입에 따른 세밀한 응답 제어가 복잡함.
3.  **AOP 기반 Global Exception Handler & Custom Exception:**
    -   예외 발생 시 중앙에서 가로채어 처리.

### 3. 결정
**AOP 기반의 Global Exception Handler와 Custom Exception**을 도입했습니다.
- **`ApiResponse` 클래스:** 성공/실패 여부(`success`), 상태 코드(`code`), 메시지(`message`), 데이터(`data`)를 포함하는 통일된 JSON 구조 정의.
- **`ErrorStatus` Enum:** 모든 에러 코드와 메시지를 한 곳에서 관리.
- **Exception Filter:** `CustomException`뿐만 아니라 프레임워크 내부 에러(`HTTPException`, `Validation Error`)까지 모두 잡아내어 공통 포맷으로 변환.

### 4. 결론
- **장점:** 클라이언트는 항상 동일한 구조의 응답을 받으므로 예외 처리가 단순해짐. 개발자는 비즈니스 로직에만 집중할 수 있음 (`raise CustomException(...)`).
- **단점:** 초기 설정 코드가 다소 늘어남.