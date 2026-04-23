# Windows Smoke Test Guide

## 목적
폐쇄망 Windows 환경에서 `check-int` 패키징 산출물이 최소 기능을 수행하는지 빠르게 확인합니다.

## 사전 준비
- `dist/check-int.exe` 또는 동등한 패키징 산출물
- 샘플 EQ List `.xlsx`
- 샘플 P&ID `.pdf`
- 샘플 Datasheet `.pdf`
- 모델 파일(해당 phase에서 실제 엔진 연결 시)
  - `models/detector.pt`
  - OCR/structured extraction 관련 로컬 자산

## 기본 확인 절차
1. Windows 10/11 64-bit PC에서 프로그램을 실행합니다.
2. 앱이 오류 없이 메인 창을 띄우는지 확인합니다.
3. EQ List / P&ID / Datasheet 파일을 각각 선택합니다.
4. 비교 실행 버튼을 눌러 결과 테이블이 채워지는지 확인합니다.
5. mismatch 행을 선택해 evidence 패널에 값/이미지가 보이는지 확인합니다.
6. 리포트 저장 버튼을 눌러 `.xlsx` 파일이 생성되는지 확인합니다.
7. 생성된 엑셀 파일에서
   - mismatch 셀 음영
   - evidence image embed(지원 시)
   - 기본 행 데이터
   가 정상인지 확인합니다.

## 실패 시 점검 항목
- 실행 직후 종료: 누락된 DLL / PySide6 runtime / hidden import 확인
- PDF 처리 실패: PyMuPDF 포함 여부 및 경로 확인
- 탐지 실패: 모델 파일 경로와 runtime checks 결과 확인
- OCR 실패: PaddleOCR 설치/모델 반입 여부 확인
- 저장 실패: 쓰기 권한 및 경로 문제 확인

## 합격 기준
- 앱 실행 성공
- 샘플 문서 1세트 비교 성공
- 결과 테이블 표시 성공
- 엑셀 저장 성공
- 치명적 예외 없이 종료/재실행 가능
