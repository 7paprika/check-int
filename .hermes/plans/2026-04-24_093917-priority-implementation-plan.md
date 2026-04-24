# check-int 추천 우선순위 실행 계획

> For Hermes: 이 문서를 기준으로 위에서 아래 순서대로 자율 구현합니다. 각 phase는 TDD로 진행하고, phase 완료/검증 후 커밋합니다.

## 목표
현재 테스트 가능한 MVP 골격을 실제 사용 가능한 데스크톱 검증 흐름으로 끌어올립니다. 우선순위는 즉시 품질게이트를 깨는 항목, GUI 실행 경로, 증빙 데이터 흐름, Tag No 매칭 신뢰성 순서입니다.

## 현재 확인 상태
- Repo: `/root/check-int`
- 전체 테스트: `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q` 기준 40 passed
- Ruff: 미사용 import 1건으로 실패
- GUI: `MainWindowController`에 `use_case`가 주입되지 않아 버튼 실행이 실제 비교로 이어지지 않음
- Evidence: crop/evidence 정보가 pipeline 결과에서 `EquipmentRecord.evidence`까지 전달되지 않음
- Comparator: EQ List master만 순회하므로 target-only tag와 duplicate tag 검출이 약함

## 진행 로그

- 2026-04-24: Phase 1 완료 — Ruff 통과, pytest 기본 Qt offscreen 환경화, 41개 테스트 통과
- 2026-04-24: Phase 2 완료 — MainWindow에 use case 주입, main 기본 use case factory 연결, UI 오류 로그 처리, 43개 테스트 통과
- 2026-04-24: Phase 3 완료 — pipeline/mapper/formatter evidence metadata 전달, 43개 테스트 통과
- 2026-04-24: Phase 4 완료 — target-only Tag No 및 duplicate Tag No 검출, 45개 테스트 통과
- 2026-04-24: Phase 5 완료 — Excel Summary, mismatch-only export, evidence image headers/size 보강, 46개 테스트 통과
- 2026-04-24: Phase 6 완료 — Linux ELF/Windows native build 구분 및 모델 포함/미포함 배포 프로파일 문서화, 47개 테스트 통과

## Phase 1. 품질게이트 안정화

### 목표
Ruff와 Qt 테스트 실행 안정성을 먼저 확보합니다.

### 작업
1. `tests/unit/test_ocr_engine_real.py`의 미사용 `Path` import 제거
2. 테스트 실행 시 `QT_QPA_PLATFORM=offscreen` 기본 적용
   - 우선 `tests/conftest.py`에서 `os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")` 적용
3. README/문서 명령과 실제 테스트 명령 불일치 여부 확인

### 예상 변경 파일
- `tests/unit/test_ocr_engine_real.py`
- `tests/conftest.py` 또는 `pyproject.toml`

### 검증
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m pytest -q`
- `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q`

### 완료 기준
- Ruff 통과
- Qt 환경변수를 외부에서 주지 않아도 pytest가 abort 없이 통과

## Phase 2. GUI 비교 실행 경로 연결

### 목표
사용자가 GUI에서 파일 선택 후 “비교 실행”을 누르면 실제 use case가 실행되고 결과 테이블이 채워지게 합니다.

### 작업
1. 테스트로 `MainWindow` 또는 controller가 use case를 주입받아 실행 결과를 테이블에 반영하는지 확인
2. `main.py`에서 앱 설정과 use case factory를 구성
3. 모델/실제 엔진이 없는 환경을 위해 demo/stub fallback 또는 명확한 production factory 분리
4. 실행 실패 시 status log에 사용자 친화 메시지 출력

### 예상 변경 파일
- `src/check_int/main.py`
- `src/check_int/ui/main_window.py`
- `src/check_int/app/controller.py`
- `src/check_int/app/use_cases.py` 또는 factory 모듈
- `tests/unit/test_main_window_flow.py`

### 검증
- controller 단위 테스트
- offscreen window smoke
- 전체 pytest

### 완료 기준
- GUI button path가 “use case 없음”에서 멈추지 않음
- 테스트 fixture/dummy use case로 결과 row가 UI에 표시됨

## Phase 3. Pipeline evidence metadata 연결

### 목표
PDF/YOLO/OCR pipeline에서 생성되는 page, bbox, crop_ref, raw_text가 비교 결과와 UI/Excel까지 전달되게 합니다.

### 작업
1. `DocumentProcessingResult.structured_rows`에 evidence metadata 포함 테스트 작성
2. `record_mapper`가 metadata를 `DocumentEvidence`로 변환하도록 테스트 작성
3. `result_formatter`가 image path 외 page/bbox/raw_text까지 필요한 row 필드로 전달
4. EvidencePanel 표시 항목 보강

### 예상 변경 파일
- `src/check_int/services/pipeline.py`
- `src/check_int/services/record_mapper.py`
- `src/check_int/services/result_formatter.py`
- `src/check_int/ui/evidence_panel.py`
- `tests/unit/test_pipeline_interfaces.py`
- `tests/unit/test_record_mapper.py`
- `tests/unit/test_evidence_panel.py`

### 검증
- pipeline/mapper/formatter/evidence panel 단위 테스트
- integration flow
- 전체 pytest

### 완료 기준
- mismatch row 선택 시 P&ID/Datasheet image_path 기반 증빙 표시가 가능한 데이터 구조 확보

## Phase 4. Tag No 매칭 신뢰성 강화

### 목표
Tag No가 문서 매칭 key라는 원칙을 코드에 명확히 반영합니다. target-only tag와 duplicate tag를 놓치지 않습니다.

### 작업
1. P&ID/Datasheet에만 있는 Tag No가 결과에 표시되는 테스트 작성
2. 동일 문서 내 duplicate Tag No가 warning/mismatch row로 표시되는 테스트 작성
3. comparator를 단일 dict가 아닌 tag별 grouping 기반으로 변경
4. UI/Excel status label 보강 필요 여부 확인

### 예상 변경 파일
- `src/check_int/domain/enums.py`
- `src/check_int/services/comparator.py`
- `src/check_int/services/result_formatter.py`
- `src/check_int/ui/result_table.py`
- `src/check_int/services/excel_exporter.py`
- `tests/unit/test_comparator.py`

### 검증
- comparator 단위 테스트
- result table/export label 테스트
- 전체 pytest

### 완료 기준
- EQ List, P&ID, Datasheet 간 Tag No 누락/초과/중복이 모두 검토 대상 row로 나타남

## Phase 5. Excel Punch List 실사용성 보강

### 목표
증빙 이미지와 검토용 summary를 포함한 Excel 보고서로 고도화합니다.

### 작업
1. Evidence image header 추가
2. mismatch only export 옵션 추가
3. row height/column width 자동 조정
4. summary sheet 추가

### 예상 변경 파일
- `src/check_int/services/excel_exporter.py`
- `tests/unit/test_excel_exporter.py`
- `tests/unit/test_excel_exporter_with_images.py`

### 검증
- openpyxl 기반 workbook 구조 검증
- 전체 pytest

## Phase 6. Windows 패키징 검증 준비

### 목표
Linux에서 가능한 spec 검증과 Windows에서 수행할 smoke 절차를 구분해 배포 준비를 명확히 합니다.

### 작업
1. Linux PyInstaller 결과는 ELF임을 문서화
2. Windows native build 절차 추가
3. 모델 포함/미포함 빌드 프로파일 정리

### 예상 변경 파일
- `docs/windows-smoke-test.md`
- `docs/offline-deployment-notes.md`
- `packaging/check_int.spec`

### 검증
- 문서 체크 테스트 또는 packaging asset 테스트
- 전체 pytest
