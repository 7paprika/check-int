# check-int 개발 환경 설정

## 1. 기본 요구사항
- Python 3.11+
- Linux 또는 Windows 개발 환경
- 폐쇄망 배포 대상은 Windows 10/11 64-bit 기준

## 2. 로컬 개발 환경 준비

프로젝트 루트에서:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
```

Windows PowerShell 예시:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -e '.[dev]'
```

## 3. 테스트 실행

기본 전체 테스트:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/pytest tests -q
```

개별 테스트 예시:

```bash
.venv/bin/pytest tests/unit/test_domain_models.py -v
.venv/bin/pytest tests/unit/test_comparator.py -v
.venv/bin/pytest tests/integration/test_mvp_flow.py -v
```

## 4. 앱 실행

Linux/headless 환경 예시:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m check_int.main
```

일반 데스크톱 환경:

```bash
.venv/bin/python -m check_int.main
```

Windows:

```powershell
.\.venv\Scripts\python -m check_int.main
```

## 5. 현재 구현된 범위
- 도메인 모델 및 정규화
- 무결성 비교 엔진
- EQ List / P&ID / Datasheet 정규화 서비스
- PySide6 데스크톱 UI 1차 셸
- Stub 기반 문서 처리 파이프라인 인터페이스
- 통합 use case
- Excel 리포트 1차 출력

## 6. 다음 고도화 우선순위
1. 실제 PDF rasterization 구현
2. YOLO 기반 영역 탐지 구현체 연결
3. PaddleOCR 실제 엔진 연결
4. sLLM/Ollama structured extraction 구현체 연결
5. UI에서 실제 파일 선택 -> 실행 -> 리포트 저장 전체 동선 완성
6. 이미지 삽입형 Punch List xlsx 구현
