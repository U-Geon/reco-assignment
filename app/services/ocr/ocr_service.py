import re
import spacy
from typing import Optional, List, Tuple
from loguru import logger
from app.models.ocr.models import OCRInput, WeighbridgeTicket

class OCRParserService:
    def __init__(self):
        try:
            # 한국어 모델 로드
            self.nlp = spacy.load("ko_core_news_sm")
            logger.info("Loaded spaCy model: ko_core_news_sm")
        except OSError:
            logger.warning("spaCy model 'ko_core_news_sm' not found. NER capabilities will be limited.")
            self.nlp = None

    def parse(self, ocr_input: OCRInput) -> WeighbridgeTicket:
        text = ocr_input.text
        logger.debug(f"Parsing text length: {len(text)}")

        # 1. 중량 데이터 추출 (정규표현식 기반 패턴 매칭)
        # 다양한 라벨 변형을 고려하여 키워드 확장
        total_weight = self._extract_weight(text, ["총중량", "총량", "총"])
        empty_weight = self._extract_weight(text, ["공차중량", "공차", "차중량", "차량중량"])
        net_weight = self._extract_weight(text, ["실중량", "순중량", "실량"])

        # 라벨 기반 추출 실패 시, Fallback 로직: kg 단위 숫자들을 크기순으로 할당
        if not (total_weight and empty_weight and net_weight):
            logger.info("Label-based weight extraction incomplete. Trying fallback logic.")
            weights = self._extract_all_weights(text)
            if len(weights) >= 2:
                # 내림차순 정렬: [큰값, 중간값, 작은값] -> [총중량, 공차중량, 실중량]
                weights.sort(reverse=True)
                if not total_weight: total_weight = weights[0]
                if not empty_weight: empty_weight = weights[1]
                if not net_weight and len(weights) >= 3: net_weight = weights[2]

        # 2. 날짜 및 시간 추출
        date = self._extract_date(text)
        times = self._extract_times(text)
        
        # 입/출고 시간 추론 (휴리스틱)
        in_time = None
        out_time = None
        if len(times) >= 1:
            in_time = times[0]
        if len(times) >= 2:
            out_time = times[-1]

        # 3. 차량 번호 추출
        vehicle_number = self._extract_vehicle_number(text)

        # 4. 회사명 및 품목명 추출 (하이브리드 방식: Regex + spaCy NER)
        company_name = self._extract_company(text)
        product_name = self._extract_product(text)

        # 5. 데이터 검증 및 보정 (Cross-Validation)
        # 논리적 검증: 총중량 - 공차중량 = 실중량
        if total_weight and empty_weight and net_weight:
            calc_net = total_weight - empty_weight
            if abs(calc_net - net_weight) > 50:
                logger.warning(f"Weight mismatch: Total({total_weight}) - Empty({empty_weight}) = {calc_net} != Net({net_weight})")
                net_weight = calc_net
        
        # 누락된 중량 데이터 역산 채우기
        if total_weight and empty_weight and not net_weight:
            net_weight = total_weight - empty_weight
        if total_weight and net_weight and not empty_weight:
            empty_weight = total_weight - net_weight
        if empty_weight and net_weight and not total_weight:
            total_weight = empty_weight + net_weight

        return WeighbridgeTicket(
            company_name=company_name,
            product_name=product_name,
            vehicle_number=vehicle_number,
            date=date,
            in_time=in_time,
            out_time=out_time,
            total_weight=total_weight,
            empty_weight=empty_weight,
            net_weight=net_weight,
            confidence_score=ocr_input.confidence,
            uncertain=False, 
            original_text=text
        )

    def _normalize_number_text(self, text: str) -> str:
        """
        OCR 과정에서 흔히 발생하는 숫자 오인식 문자를 교정
        """
        text = text.replace('O', '0').replace('o', '0')
        text = text.replace('I', '1').replace('l', '1')
        text = text.replace('S', '5').replace('s', '5')
        text = text.replace('B', '8')
        return text

    def _make_spaced_regex(self, keyword: str) -> str:
        """
        키워드 글자 사이에 공백이 있어도 매칭되도록 정규식 생성
        """
        return r"\s*".join(list(keyword))

    def _extract_weight(self, text: str, keywords: List[str]) -> Optional[int]:
        """
        라벨 기반 무게 추출
        """
        unit_regex = r"(?:[kK]\s*[gG]|[kK][oO])"
        
        for keyword in keywords:
            spaced_kw = self._make_spaced_regex(keyword)
            # [\d,OISBl. ]+ : 숫자, 콤마, 점, 오타 문자, 그리고 공백 포함 (13 460 케이스 대응)
            pattern = f"{spaced_kw}.*?([\\d,OISBl. ]+)\\s*{unit_regex}"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            
            if match:
                num_str = match.group(1)
                val = self._parse_weight_string(num_str)
                if val: return val
        return None

    def _extract_all_weights(self, text: str) -> List[int]:
        """
        텍스트 내의 모든 'kg' 단위 앞의 숫자를 추출 (Fallback용)
        """
        unit_regex = r"(?:[kK]\s*[gG]|[kK][oO])"
        # 라벨 없이 숫자+단위 패턴만 찾음
        # 시간 패턴(HH:MM:SS)과 혼동되지 않도록 주의해야 함.
        # 하지만 보통 시간 뒤에는 kg가 붙지 않으므로 kg 앵커가 강력함.
        pattern = f"([\\d,OISBl. ]+)\\s*{unit_regex}"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

        weights = []
        for num_str in matches:
            val = self._parse_weight_string(num_str)
            if val: weights.append(val)

        # 중복 제거 및 정렬
        return sorted(list(set(weights)), reverse=True)

    def _parse_weight_string(self, num_str: str) -> Optional[int]:
        """
        문자열을 정수 무게 값으로 변환
        """
        # 숫자 정제
        num_str = self._normalize_number_text(num_str)
        # 공백 제거 (13 460 -> 13460)
        num_str = num_str.replace(" ", "")
        # 콤마 제거
        num_str = num_str.replace(",", "")

        if not num_str: return None

        # 천단위 구분기호(.) 처리
        if "." in num_str:
            parts = num_str.split(".")
            if len(parts) > 1 and len(parts[-1]) == 3:
                num_str = num_str.replace(".", "")
            else:
                try:
                    return int(float(num_str))
                except ValueError:
                    pass

        try:
            return int(num_str)
        except ValueError:
            return None

    def _extract_date(self, text: str) -> Optional[str]:
        # YYYY-MM-DD
        match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if match: return match.group(1)
        # YYYY/MM/DD
        match = re.search(r"(\d{4}/\d{2}/\d{2})", text)
        if match: return match.group(1).replace("/", "-")
        # YYYY.MM.DD
        match = re.search(r"(\d{4}\.\d{2}\.\d{2})", text)
        if match: return match.group(1).replace(".", "-")
        return None

    def _extract_times(self, text: str) -> List[str]:
        times = []
        # Pattern 1: HH:MM:SS (또는 HH:MM) - 콜론 사이 공백 허용 (\s*)
        matches = re.findall(r"(\d{1,2})\s*:\s*(\d{2})(?:\s*:\s*(\d{2}))?", text)
        for h, m, s in matches:
            if not s: s = "00"
            times.append(f"{h.zfill(2)}:{m.zfill(2)}:{s.zfill(2)}")
        
        # Pattern 2: HH시 MM분
        matches_kr = re.findall(r"(\d{1,2})시\s*(\d{1,2})분", text)
        for h, m in matches_kr:
            times.append(f"{h.zfill(2)}:{m.zfill(2)}:00")
            
        return sorted(list(set(times)))

    def _extract_vehicle_number(self, text: str) -> Optional[str]:
        kw_regex = self._make_spaced_regex("차량번호")
        
        # Strategy 1: 키워드 뒤 4자리 숫자
        match = re.search(f"{kw_regex}.*?(\\d{{4}})", text)
        if match: return match.group(1)
            
        # Strategy 2: 전체 번호 패턴 (숫자2~3 + 한글 + 숫자4)
        match = re.search(r"(\d{2,3}\s*[가-힣]\s*\d{4})", text)
        if match: return match.group(1).replace(" ", "")
            
        return None

    def _extract_company(self, text: str) -> Optional[str]:
        # 1. Label Search
        kw_regex = r"(?:상호|회사명|공급자|거래처)" # 거래처 추가
        match = re.search(f"{kw_regex}.*?[:]\s*([^\n]+)", text)
        if match:
            val = match.group(1).strip()
            if val and len(val) > 1: return val

        # 2. Regex Pattern Search
        match = re.search(r"\(주\)[ ]*([가-힣a-zA-Z0-9]+)", text)
        if match: return f"(주) {match.group(1)}"

        match = re.search(r"([가-힣a-zA-Z0-9]+)[ ]*\(주\)", text)
        if match: return f"{match.group(1)} (주)"

        # 3. spaCy NER Fallback
        if self.nlp:
            doc = self.nlp(text)
            org_candidates = []
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    if len(ent.text) > 1 and not ent.text.isdigit():
                        org_candidates.append(ent.text)
            if org_candidates:
                return org_candidates[0]
        return None

    def _extract_product(self, text: str) -> Optional[str]:
        kw_regex = r"(?:품명|제품명)"
        match = re.search(f"{kw_regex}.*?[:]\s*([^\n]+)", text)
        if match:
            val = match.group(1).strip()
            if not val or val == ":": return None
            return val
        return None
