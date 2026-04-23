# check-int

온프레미스 엔지니어링 문서 무결성 검증 데스크톱 앱(LEDIC) 개발용 프로젝트입니다.

## 프로젝트 목적
- EQ List, P&ID, Datasheet 사이의 핵심 장비/설계 데이터 불일치를 오프라인 환경에서 자동 검출합니다.
- 폐쇄망/망분리 환경을 전제로 외부 API 없이 로컬에서만 처리합니다.
- 최종적으로 Windows 데스크톱 앱(.exe) 배포를 목표로 합니다.

## 현재 구현 상태
완료된 1차 범위:
- 기획서 저장
- 도메인 모델 및 정규화 규칙
- 무결성 비교 엔진
- EQ List / P&ID / Datasheet 정규화 서비스
- Stub 기반 문서 처리 파이프라인 인터페이스
- PySide6 UI 1차 셸
- 통합 use case
- Excel 리포트 1차 출력

## 디렉터리 구조
- `LEDIC_Project_Plan.md`: 사용자 제공 기획서
- `docs/plans/`: 구현 계획 문서
- `docs/development-setup.md`: 개발 환경 설정 가이드
- `docs/offline-deployment-notes.md`: 폐쇄망 배포 메모
- `src/check_int/domain/`: 도메인 모델과 enum
- `src/check_int/services/`: 비교, 파싱, export 서비스
- `src/check_int/adapters/`: PDF/OCR/Vision/structured extraction 인터페이스 및 stub
- `src/check_int/app/`: use case 및 controller
- `src/check_int/ui/`: 데스크톱 UI
- `tests/`: 단위/통합 테스트

## 빠른 시작
```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install -e '.[dev]'
QT_QPA_PLATFORM=offscreen .venv/bin/pytest tests -q
.venv/bin/python -m check_int.main
```

Windows PowerShell 예시:
```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -e '.[dev]'
.\.venv\Scripts\pytest tests -q
.\.venv\Scripts\python -m check_int.main
```

## 현재 테스트 상태
현재 구현 기준 검증 커맨드:
```bash
QT_QPA_PLATFORM=offscreen .venv/bin/pytest tests -q
```

## 다음 개발 우선순위
1. 실제 PDF -> 이미지 변환 구현
2. YOLO 기반 영역 탐지 구현체 연결
3. PaddleOCR 실제 엔진 연결
4. structured extraction 고도화
5. UI에서 파일 선택부터 리포트 저장까지 완전 연결
6. 이미지 삽입형 Excel Punch List 구현
7. Windows용 PyInstaller 패키징
