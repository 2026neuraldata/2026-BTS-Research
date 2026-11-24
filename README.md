# 2026 BTS Research

**응집 공정의 최적화를 위한 LLM 프레임워크 설계 — 연구 운영 계획안**

- 기준일: 2026-11-24, Asia/Seoul임.
- 계정/저장소: `2026neuraldata/2026-BTS-Research`, 비공개 운영 기본임.
- 현재 제공물은 일정·역할·검증 규칙을 담은 관리 저장소임. 실제 앱 코드는 C01에서 담당자가 연결해야 함.
- 기존 담당과 주요 일정은 원문에 근거함. 새 세부 마감·검수 기준은 이번 검토에서 제안한 실행 기준이며, 팀 합의가 완료됐다는 뜻은 아님.

## 바로 확인할 문서

| 필요한 내용 | 문서 |
|---|---|
| 현재 완료/미완료·다음 마감 | [PROGRESS.md](PROGRESS.md) |
| 각자 무엇을 언제까지 수행하는지 | [TEAM_TASKS.md](docs/TEAM_TASKS.md) |
| 전체 일정·중단 기간·연결 순서 | [ROADMAP.md](docs/ROADMAP.md) |
| 모든 파일을 바탕으로 한 연구 진행 이력 | [RESEARCH_HISTORY.md](docs/RESEARCH_HISTORY.md) |
| 파일별 검토 목록·출처·제약 | [SOURCE_AUDIT.md](docs/SOURCE_AUDIT.md), [전체 목록 CSV](management/source_manifest.csv) |
| 회의에서 확정할 사항 | [DECISIONS.md](docs/DECISIONS.md) |
| 데이터 / 에너지 / LLM 검증 규격 | [DATA_CONTRACT](docs/DATA_CONTRACT.md) · [ENERGY_SPEC](docs/ENERGY_SPEC.md) · [EVALUATION_PROTOCOL](docs/EVALUATION_PROTOCOL.md) |
| GitHub 초보자 사용법 | [SETUP.md](docs/SETUP.md) |

## 연구 질문과 현재 답할 수 있는 범위

1. 측정한 pH·투입량 조건에서 탁도와 약품 사용량의 절충관계가 어떻게 나타나는지 탐색함.
2. 실험 조회·문헌 검색·단위가 명확한 계산을 연결한 시스템이 동일 정보의 기준 모델과 비교해 더 정확하고 근거 있는 답을 내는지 평가함.
3. 명시한 공정 경계와 가정 아래 추천 조건의 에너지·약품 제조 탄소를 계산할 수 있는지 검증함.

- 관측 범위의 추천과 의사결정 지원이 핵심임. 현장 최적 운전이나 실제 탄소감축이 이미 입증된 상태는 아님.
- 5단계 데이터 분석은 산출물 완료임. 앱 기본 기능은 개발 보고서상 구현됨. 실제 모델 비교·공정 에너지 통합·외부 검증은 남은 단계임.
- TS/VS 26건 중 21건의 물리적 불일치가 남아 있으며, VS만 분리해도 품질 검증 완료로 바뀌지 않음.

## 운영 규칙

- `management/tasks.csv`를 업무 상태의 기준 파일로 사용함. `python scripts/update_trackers.py`로 진행표·개인별 역할표를 함께 갱신함.
- `python scripts/check_plan.py`로 날짜·의존관계·시험기간·출처 목록을 점검함.
- 완료는 결과 파일, 코드/조건, 검수자 확인이 있을 때 기록함. 구현 보고만 받은 항목은 `reported`로 유지함.
- 매 작업 종료 시 담당자가 handoff를 작성하고, 김선우가 문서·결과를 통합하며 허재영이 앱 코드를 통합하는 운영안을 제안함.
- 팀원이 Git에 익숙하지 않으면 Drive로 결과+코드+설명을 전달하고 통합 담당이 커밋하는 방식으로 운영 가능함.
- 교재 PDF·녹음 원본·API 키·평가 정답은 저장소 공개 자료로 올리지 않음. 원문은 권한이 있는 Drive에서 참조함.

## 근거

- [role assignment_1119.txt](https://drive.google.com/file/d/1DGi5E37JYE18Wr_DRV5RLyWTm_iIhzf-/view?usp=drivesdk) / [schedule.txt](https://drive.google.com/file/d/1huuMd6EX_6p7StmoCFlwfwobfDZNVdOj/view?usp=drivesdk) / [LLM_Plan.txt](https://drive.google.com/file/d/12YLJMCVnvSyM98ORx-a2-SZkMeBGhrcd/view?usp=drivesdk)
- 현황: [Data_Analysis_김선우.pdf](https://drive.google.com/file/d/1o2OGKhoRQ7n2b7n3AzS1_2XJzwqjdA3K/view?usp=drivesdk) · [Energy_Usage_임수현.pdf](https://drive.google.com/file/d/13_P8N2nwInXZqbeVw2PwCMmkdxmX8ZBG/view?usp=drivesdk) · [LLM_Validation_이건희.pdf](https://drive.google.com/file/d/15_HNCQfPAqK64jPsemyXN-WTXxzN6_GV/view?usp=drivesdk) · [Dev_Status_Features_허재영.pdf](https://drive.google.com/file/d/1UctLqjikQwz9aCi_4hPZ3Ef4RUAcu-s1/view?usp=drivesdk)
- 참고 관리 구조: [AI-based-Neural-Data-Science](https://github.com/jimmytrn154/AI-based-Neural-Data-Science)임. README·PROGRESS·TEAM_TASKS·공통 설정·인수인계 구조를 참고하고, 타 연구의 내용·역할은 복사하지 않음.
