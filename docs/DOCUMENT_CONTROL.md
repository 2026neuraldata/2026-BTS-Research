# 현행 문서 관리 기준 (2026-11-28 정비)

F01–F11 정비 이후 팀 내부 공유 정책을 반영한 현행 기준임. R01–R18 연구 범위, 업무 ID·담당·기간·의존관계 및 원본 데이터·평가문항·Gold·L03 결과는 그대로 유지함.

| 분야 | 기준 |
|---|---|
| 업무/제출/기한/상태 | [tasks.csv](../management/tasks.csv), [자동 생성 업무표](TEAM_TASKS.md) |
| 연구 설정 | [config.yaml](../config.yaml) |
| 평가 설계/실행 | [평가 규격](EVALUATION_PROTOCOL.md), [L02 설정](../deliverables/L/L02/evaluation_config.json), [허용자료](../deliverables/L/L02/corpus_manifest.json) |
| 채점 세부 | 팀 내부 rubric/Gold 열람 허용; 실제 채점 단계 및 개발 활용 제한; 공개 설정의 형식 규칙과 일치 |
| 에너지 | [E01 산식](../deliverables/E/E01/formulas.md), [계수](../deliverables/E/E01/energy_factors.csv), [해석 규격](ENERGY_SPEC.md) |
| 보안 | [평가 접근 통제](EVALUATION_ACCESS_CONTROL.md) |
| 변경 이력 | [과거 기록 목록](HISTORY_INDEX.md); 날짜별 manifest는 해당 배포 당시 증빙 |

- 업무 원장 먼저 수정, `config.yaml`의 기준일을 갱신하고 `python scripts/update_trackers.py`로 두 업무표 재생성. `python scripts/update_trackers.py --check`로 불일치 검출.
- `python scripts/check_plan.py` 및 `python scripts/check_release.py`를 저장소 루트에서 실행. 후자는 저장소 내부 링크/생성 문서/비공개 파일명·알려진 충돌 패턴·기준 데이터 해시를 점검함. 외부 접속 및 실제 API는 별도 검증함. `--release`는 이번 배포 변경 해시 검증에만 사용하며 이후 정상 변경에는 사용하지 않음. 자동 검사로 모든 의미상 모순이나 실제 접근통제를 보증하지 않음.
- 과거 문서/manifest는 현행 실행 지시 아님. C01 기준 코드는 역사적 구현이며 실행용 보안/에너지 수정은 C02–C04에서 실시.
- L05 독립 인간 채점·선정/검증 자료와 추가 비교 집계(미실행 사유 포함)를 확인하고 C05 실제 수동 프롬프트·모델 설정·루브릭·선정 근거·해시를 최종 답변 열람 전에 동결함. DSPy는 11/28 회의에서 제외 확정. C03/L04 실제 API·접근통제·형식 및 실제 개발 활용 검토 미통과 시 L06 실행 금지. L07은 L06의 동일 저장 응답만 사용함.
- 비공개 평가자료는 별도 공개 승인 전까지 평가 종료 후에도 보호. 팀 내부 단체방 및 회의는 열람 허용; 외부 공개 화면·회의록에는 집계 및 오류 유형만 제공. [팀 공유 정책](TEAM_SHARING_POLICY.md) 참조.
- 원본 수치나 평가문항은 이번 수정 범위 아님. 실제 API·접근 통제·독립 채점·계산 기능은 기존 후속 업무에서 검증.

- 현재 회의 결정: [11/28 회의록](../deliverables/G/G02/meeting_1128.md). `--release` 기본값은 [보완사항 배포 manifest](SUPPLEMENT_MANIFEST_20261128.json)이며 check_release.py·README 안내와 함께 갱신함. 과거 배포는 해당 시점 커밋에서 `--manifest`로 당시 manifest를 명시하여 검증. 최신 커밋에서 과거 manifest의 해시가 다른 것은 후속 수정에 따른 정상 이력일 수 있음. 담당자 내부 ZIP·scoring_rubric/split 원본은 이번 첨부에 없어 수정하지 않았으며 현재 수동 평가 지침과 동기화 필요.
