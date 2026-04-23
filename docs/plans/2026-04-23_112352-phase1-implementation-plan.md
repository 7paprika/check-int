# LEDIC 1차 구현 계획서

> For Hermes: 이후 구현 단계에서는 이 계획을 기준으로 작은 단위로 끊어 순차 구현합니다.

목표: 오프라인 환경에서 P&ID / Datasheet / EQ List를 불러오고, 문서별 추출 데이터를 공통 스키마로 정규화한 뒤, 불일치 항목을 테이블로 표시하는 1차 실행 가능한 데스크톱 MVP를 만든다.

아키텍처 요약:
- 1차 구현은 "완성형 AI 정확도"보다 "흐름이 끊기지 않는 오프라인 검증 파이프라인" 확보에 집중한다.
- 따라서 PDF 입력, 이미지 변환, 문서 타입별 추출 어댑터, 정규화 스키마, mismatch 비교 엔진, PySide6 결과 테이블을 먼저 연결한다.
- YOLO / PaddleOCR / sLLM은 모두 추후 고도화 가능하도록 인터페이스 기반으로 분리하고, 1차에서는 일부 Mock/Fallback 경로를 허용한다.

기술 스택:
- Python 3.11+
- PySide6
- pandas
- Pillow / openpyxl
- pytest / pytest-qt
- 추후 연결: ultralytics, paddleocr, ollama

---

## 1. 1차 구현 범위

이번 1차 구현에서는 아래만 완료 대상으로 본다.

1. 로컬 파일 선택 UI
   - EQ List Excel 파일 선택
   - P&ID PDF 파일 선택
   - Datasheet PDF 파일 선택

2. 문서 입력 파이프라인 골격
   - PDF -> 페이지 이미지 변환 인터페이스
   - 영역 탐지 인터페이스
   - OCR 인터페이스
   - 정규화 인터페이스

3. 공통 데이터 모델 정의
   - EquipmentRecord
   - DocumentEvidence
   - FieldComparisonResult
   - IntegrityCheckResult

4. mismatch 비교 엔진 구현
   - Tag No 기준 정렬/매칭
   - 주요 필드 비교
   - mismatch / missing / matched 상태 계산

5. 결과 시각화 1차
   - 메인 테이블 표시
   - mismatch 셀 음영 처리
   - 행 선택 시 증빙 패널 영역 표시

6. 엑셀 보고서 1차
   - 테이블 중심 리포트 저장
   - 1차에서는 이미지 삽입 대신 이미지 경로/자리표시자 허용

이번 1차 범위에서 제외:
- YOLO 전이학습 파이프라인 구현
- 실제 고정밀 OCR 성능 튜닝
- sLLM 프롬프트 튜닝 자동화
- 이미지가 삽입된 완성형 Punch List 산출물
- Windows exe 패키징 최적화 마감

---

## 2. 현재 프로젝트 기준 전제

현재 이미 존재하는 파일:
- `LEDIC_Project_Plan.md`
- `README.md`
- `pyproject.toml`
- `src/check_int/main.py`
- `src/check_int/ui/main_window.py`
- `tests/test_smoke.py`

따라서 1차 구현은 기존 최소 스캐폴드 위에 아래 계층을 추가하는 방식으로 진행한다.

권장 디렉터리 구조:
- `src/check_int/app/`
- `src/check_int/domain/`
- `src/check_int/services/`
- `src/check_int/adapters/`
- `src/check_int/ui/`
- `tests/unit/`
- `tests/integration/`
- `docs/plans/`

---

## 3. 단계별 구현 계획

### Phase 1. 도메인 모델과 비교 규칙 확정

목적:
비교 엔진과 UI가 흔들리지 않도록 공통 데이터 구조를 먼저 확정한다.

생성/수정 파일:
- Create: `src/check_int/domain/models.py`
- Create: `src/check_int/domain/enums.py`
- Create: `src/check_int/domain/normalization.py`
- Create: `tests/unit/test_domain_models.py`

구현 내용:
- 문서 종류 enum 정의: `EQ_LIST`, `PID`, `DATASHEET`
- 비교 상태 enum 정의: `MATCHED`, `MISMATCH`, `MISSING_SOURCE`, `MISSING_TARGET`, `UNREVIEWED`
- 핵심 데이터 클래스 정의
  - `DocumentEvidence`
  - `FieldValue`
  - `EquipmentRecord`
  - `FieldComparisonResult`
  - `IntegrityCheckResult`
- 문자열 정규화 규칙 정의
  - 공백 제거/다중 공백 축약
  - 대소문자 통일
  - 단위 문자열 normalize 훅 제공

완료 기준:
- Tag No와 핵심 필드셋을 표현할 수 있음
- 비교 결과를 UI/엑셀 양쪽에서 공통 사용 가능
- 단위 테스트 통과

세부 작업:
1. dataclass 기반 도메인 모델 작성
2. 필드 정규화 유틸리티 작성
3. 최소 샘플 객체 생성 테스트 작성
4. normalize 동작 테스트 작성

검증:
- `pytest tests/unit/test_domain_models.py -v`

---

### Phase 2. 문서 입력 파이프라인 인터페이스 분리

목적:
실제 AI 엔진이 없어도 앱 흐름이 동작하도록 입력 파이프라인을 추상화한다.

생성/수정 파일:
- Create: `src/check_int/adapters/pdf_loader.py`
- Create: `src/check_int/adapters/vision_detector.py`
- Create: `src/check_int/adapters/ocr_engine.py`
- Create: `src/check_int/adapters/structured_extractor.py`
- Create: `src/check_int/services/pipeline.py`
- Create: `tests/unit/test_pipeline_interfaces.py`

구현 내용:
- PDF 페이지를 이미지 리스트로 바꾸는 loader 인터페이스 정의
- 이미지에서 후보 영역을 반환하는 detector 인터페이스 정의
- crop에서 문자열을 추출하는 OCR 인터페이스 정의
- 비정형 텍스트를 구조화 데이터로 바꾸는 extractor 인터페이스 정의
- 1차에서는 실제 모델 대신 더미/Mock 구현 포함

권장 인터페이스:
- `load_pdf(path) -> list[PageImage]`
- `detect_regions(page_image) -> list[DetectedRegion]`
- `extract_text(image_or_crop) -> str`
- `to_structured_fields(text, document_type) -> dict[str, str]`

완료 기준:
- 실제 AI 모델 미연동 상태에서도 end-to-end stub 실행 가능
- 각 인터페이스가 서비스 계층과 분리됨

검증:
- `pytest tests/unit/test_pipeline_interfaces.py -v`

---

### Phase 3. EQ List / P&ID / Datasheet 정규화 서비스 작성

목적:
서로 다른 입력 형태를 공통 `EquipmentRecord` 리스트로 변환한다.

생성/수정 파일:
- Create: `src/check_int/services/eq_list_parser.py`
- Create: `src/check_int/services/pid_parser.py`
- Create: `src/check_int/services/datasheet_parser.py`
- Create: `src/check_int/services/record_mapper.py`
- Create: `tests/unit/test_eq_list_parser.py`
- Create: `tests/unit/test_record_mapper.py`

구현 내용:
- EQ List는 pandas 기반으로 Excel 읽기
- P&ID / Datasheet는 1차에서 stub OCR 결과 또는 샘플 JSON을 매퍼에 공급
- 공통 필드 예시
  - tag_no
  - equipment_name
  - service
  - size
  - rating
  - material
  - design_pressure
  - design_temperature

완료 기준:
- 서로 다른 입력 원천이 동일한 `EquipmentRecord` 구조로 정규화됨
- 최소 샘플 데이터셋으로 비교 엔진 투입 가능

검증:
- `pytest tests/unit/test_eq_list_parser.py tests/unit/test_record_mapper.py -v`

---

### Phase 4. 무결성 비교 엔진 구현

목적:
마스터 EQ List 기준으로 문서 간 불일치 탐지를 수행한다.

생성/수정 파일:
- Create: `src/check_int/services/comparator.py`
- Create: `src/check_int/services/result_formatter.py`
- Create: `tests/unit/test_comparator.py`

구현 내용:
- EQ List를 기준 master로 사용
- Tag No 기준 병합
- 필드별 값 비교
- 상태 산정 규칙
  - 둘 다 있고 normalize 후 동일 -> MATCHED
  - 둘 다 있으나 상이 -> MISMATCH
  - 한쪽 누락 -> MISSING_*
- 화면용 평탄화 결과 생성

핵심 출력 예시:
- 장비별 비교 결과 리스트
- 필드별 상태 맵
- mismatch 개수 요약

완료 기준:
- 최소 샘플 입력에서 mismatch가 정확히 계산됨
- UI 테이블에서 바로 사용할 결과 형태 확보

검증:
- `pytest tests/unit/test_comparator.py -v`

---

### Phase 5. PySide6 UI 1차 구현

목적:
엔지니어가 실제로 파일을 열고 결과를 확인할 수 있는 화면을 구성한다.

생성/수정 파일:
- Modify: `src/check_int/ui/main_window.py`
- Create: `src/check_int/ui/file_panel.py`
- Create: `src/check_int/ui/result_table.py`
- Create: `src/check_int/ui/evidence_panel.py`
- Create: `src/check_int/app/controller.py`
- Create: `tests/unit/test_result_table_model.py`

화면 구성:
- 상단: 파일 선택 패널
- 중앙: 결과 테이블
- 하단: 선택 항목 증빙 패널(side-by-side placeholder)
- 우측 또는 하단: 로그/상태 메시지

구현 내용:
- 세 문서 파일 경로 선택 버튼
- 실행 버튼
- 결과 테이블 바인딩
- mismatch 셀 배경색 강조
- 행 선택 시 증빙 패널 업데이트
- 1차에서는 실제 crop 이미지 없을 경우 placeholder 텍스트 표시 허용

완료 기준:
- 사용자가 파일을 지정하고 비교 실행 가능
- 결과 테이블에 mismatch 음영 표시 가능
- 선택 이벤트에 따라 증빙 패널 내용 변경

검증:
- `pytest tests/unit/test_result_table_model.py -v`
- 수동 실행: `python -m check_int.main`

---

### Phase 6. 통합 서비스 연결

목적:
UI, 파서, 비교 엔진을 한 흐름으로 묶는다.

생성/수정 파일:
- Create: `src/check_int/app/use_cases.py`
- Modify: `src/check_int/main.py`
- Create: `tests/integration/test_mvp_flow.py`

구현 내용:
- 입력 파일 경로 검증
- EQ List 로딩
- P&ID / Datasheet 파이프라인 호출
- 정규화 후 비교 엔진 호출
- UI에 결과 전달

완료 기준:
- 샘플 파일 기반으로 앱 전 과정이 예외 없이 실행됨
- 통합 테스트 1개 이상 통과

검증:
- `pytest tests/integration/test_mvp_flow.py -v`

---

### Phase 7. Excel 리포트 1차 구현

목적:
비교 결과를 오프라인 보고용 파일로 저장한다.

생성/수정 파일:
- Create: `src/check_int/services/excel_exporter.py`
- Create: `tests/unit/test_excel_exporter.py`

구현 내용:
- 결과 테이블을 엑셀로 저장
- 상태별 셀 색상 반영
- 이미지 삽입 예정 칼럼/시트 구조 미리 확보
- 1차에서는 evidence 이미지 경로 또는 note 컬럼 저장 허용

완료 기준:
- mismatch 셀 서식이 반영된 xlsx 저장 가능
- 오프라인 검토용 기본 Punch List 확보

검증:
- `pytest tests/unit/test_excel_exporter.py -v`

---

### Phase 8. 개발 환경 문서화 및 실행 가이드 보강

목적:
다음 구현 단계에서 혼선이 없도록 개발/테스트/오프라인 배포 준비 문서를 정리한다.

생성/수정 파일:
- Modify: `README.md`
- Create: `docs/development-setup.md`
- Create: `docs/offline-deployment-notes.md`

구현 내용:
- 로컬 개발 절차
- optional AI dependency 설치 주의점
- Windows 폐쇄망 반입 시 필요한 wheel/model 관리 항목 정리
- 향후 PyInstaller 포함 자산 목록 정리

완료 기준:
- 신규 엔지니어가 프로젝트 구조와 실행 순서를 바로 이해 가능

---

## 4. 제안 파일 맵

우선 생성 권장 파일 목록:
- `src/check_int/domain/models.py`
- `src/check_int/domain/enums.py`
- `src/check_int/domain/normalization.py`
- `src/check_int/adapters/pdf_loader.py`
- `src/check_int/adapters/vision_detector.py`
- `src/check_int/adapters/ocr_engine.py`
- `src/check_int/adapters/structured_extractor.py`
- `src/check_int/services/pipeline.py`
- `src/check_int/services/eq_list_parser.py`
- `src/check_int/services/pid_parser.py`
- `src/check_int/services/datasheet_parser.py`
- `src/check_int/services/record_mapper.py`
- `src/check_int/services/comparator.py`
- `src/check_int/services/result_formatter.py`
- `src/check_int/services/excel_exporter.py`
- `src/check_int/app/controller.py`
- `src/check_int/app/use_cases.py`
- `src/check_int/ui/file_panel.py`
- `src/check_int/ui/result_table.py`
- `src/check_int/ui/evidence_panel.py`
- `tests/unit/test_domain_models.py`
- `tests/unit/test_pipeline_interfaces.py`
- `tests/unit/test_eq_list_parser.py`
- `tests/unit/test_record_mapper.py`
- `tests/unit/test_comparator.py`
- `tests/unit/test_result_table_model.py`
- `tests/unit/test_excel_exporter.py`
- `tests/integration/test_mvp_flow.py`

---

## 5. 데이터 모델 초안

### EquipmentRecord
필수 필드 초안:
- `document_type: DocumentType`
- `tag_no: str`
- `equipment_name: str | None`
- `service: str | None`
- `size: str | None`
- `rating: str | None`
- `material: str | None`
- `design_pressure: str | None`
- `design_temperature: str | None`
- `source_file: str`
- `page_no: int | None`
- `evidence: list[DocumentEvidence]`

### DocumentEvidence
- `page_no: int`
- `bbox: tuple[int, int, int, int] | None`
- `image_path: str | None`
- `raw_text: str | None`
- `note: str | None`

### FieldComparisonResult
- `field_name: str`
- `master_value: str | None`
- `pid_value: str | None`
- `datasheet_value: str | None`
- `status: ComparisonStatus`
- `master_evidence: DocumentEvidence | None`
- `pid_evidence: DocumentEvidence | None`
- `datasheet_evidence: DocumentEvidence | None`

---

## 6. 테스트 전략

테스트 우선순위:
1. 도메인 모델 / 정규화 유닛 테스트
2. 비교 엔진 유닛 테스트
3. EQ List 파싱 유닛 테스트
4. UI 테이블 모델 테스트
5. end-to-end 통합 테스트

핵심 원칙:
- 실제 AI 모델 추론을 기본 테스트에 넣지 않는다.
- 1차는 deterministic fixture 중심으로 간다.
- OCR/YOLO/LLM은 mock adapter로 고정된 결과를 반환하게 한다.

권장 테스트 데이터:
- `tests/fixtures/eq_list_sample.xlsx`
- `tests/fixtures/pid_stub.json`
- `tests/fixtures/datasheet_stub.json`
- `tests/fixtures/expected_comparison.json`

전체 검증 커맨드 후보:
- `pytest -q`
- `python -m check_int.main`

---

## 7. 리스크와 대응

리스크 1: PDF 처리 라이브러리 선택 지연
- 대응: 1차는 loader 인터페이스만 고정하고 구현체는 후속 확정

리스크 2: OCR 결과 품질 불안정
- 대응: 비교 엔진과 UI는 OCR 품질과 독립적으로 먼저 개발

리스크 3: sLLM 구조화 품질 편차
- 대응: 정규화 계층 앞단에 rule-based mapper fallback 제공

리스크 4: Windows 폐쇄망 배포 복잡성
- 대응: 의존성/모델/런타임 자산을 문서화하고 1차부터 packaging input 목록 관리

리스크 5: 이미지 증빙 저장 용량 증가
- 대응: 1차는 원본 crop 저장 정책과 임시 캐시 정책을 분리해 설계

---

## 8. 1차 구현 완료 정의

다음 조건을 만족하면 1차 구현 완료로 본다.

- 사용자가 EQ List / P&ID / Datasheet 파일을 선택할 수 있다.
- 앱이 세 문서를 공통 데이터 구조로 변환할 수 있다.
- Tag No 기준 비교 결과를 테이블에 표시할 수 있다.
- mismatch 셀에 색상 표시가 된다.
- 선택한 행의 증빙 영역을 하단 패널에서 확인할 수 있다.
- 결과를 xlsx로 저장할 수 있다.
- 핵심 유닛 테스트와 최소 통합 테스트가 통과한다.

---

## 9. 바로 다음 실행 권장 순서

실행 우선순위는 아래 순서를 권장한다.

1. Phase 1: 도메인 모델 + enum + normalization
2. Phase 4: comparator 먼저 구현
3. Phase 3: EQ List parser 작성
4. Phase 5: 결과 테이블 UI 연결
5. Phase 2: 파이프라인 인터페이스 추가
6. Phase 6: 통합 연결
7. Phase 7: Excel exporter
8. Phase 8: 문서화

이 순서를 권장하는 이유:
- 비교 엔진과 데이터 모델이 먼저 안정되어야 UI와 추출 엔진이 흔들리지 않음
- 실제 AI 추론이 늦어져도 MVP 데모가 가능함
- 오프라인 환경에서 가장 빨리 검증 가치를 보여줄 수 있음
