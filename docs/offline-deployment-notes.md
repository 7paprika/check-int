# check-int 오프라인 배포 메모

## 1. 목표
폐쇄망/망분리 환경의 Windows PC에서 인터넷 없이 LEDIC 실행 파일을 배포한다.

## 2. 패키징 대상
- Python 런타임
- 애플리케이션 코드 (`check_int`)
- Qt/PySide6 런타임
- OCR/Vision/LLM 로컬 모델 파일
- 필요 시 sample config / label map / prompt templates

## 3. 배포 자산 후보
- `best.pt` 또는 YOLO 계열 가중치
- PaddleOCR 모델 파일
- Ollama 모델 또는 대체 로컬 structured extraction 자산
- 아이콘/로고/기본 설정 파일
- 결과물 저장 폴더 정책

## 4. 오프라인 반입 체크리스트
1. Python wheel 사전 수집
2. GPU/CPU 모드별 의존성 분리
3. 모델 파일 해시 검증
4. 설치 후 인터넷 차단 상태 실행 검증
5. 문서 샘플로 smoke test 수행

## 5. PyInstaller 고려사항
- hidden imports: PySide6, pandas, openpyxl, 향후 paddle/ultralytics 포함
- 모델 파일과 설정 파일을 `--add-data`로 포함
- 출력 exe 크기 증가 예상
- 첫 실행 시 임시 압축 해제 경로 정책 확인 필요
- Linux에서 생성한 산출물은 ELF 실행파일이므로 Windows 배포물로 사용할 수 없음

### 빌드 프로파일
- 모델 미포함 빌드: 앱 코드와 기본 런타임만 묶고, `models/` 폴더는 현장 PC에 별도 배치한다. 초기 검증과 작은 배포 파일에 적합하다.
- 모델 포함 빌드: YOLO/PaddleOCR/structured extraction 자산을 PyInstaller `datas` 또는 배포 폴더에 포함한다. 폐쇄망 반입은 단순하지만 산출물 크기와 빌드 시간이 증가한다.
- Windows native build: 실제 `.exe`는 Windows 10/11 64-bit 환경 또는 Windows VM에서 PyInstaller를 실행해 생성한다.

## 6. 운영상 유의점
- 증빙 crop 이미지 캐시 저장 위치를 명확히 해야 함
- 문서 원본 저장 여부와 보존 주기를 정책화해야 함
- GPU 없는 환경에서의 fallback 속도 기준을 정의해야 함
- 엑셀 리포트 출력 경로와 파일명 규칙을 표준화해야 함

## 7. 다음 배포 전 준비 작업
- 실제 PDF 처리 라이브러리 확정
- YOLO/Paddle/Ollama 연결 완료
- Windows 환경 smoke test
- PyInstaller spec 파일 작성
- 샘플 문서 기준 사용자 가이드 작성
