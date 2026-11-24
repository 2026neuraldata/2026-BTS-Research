# 저장소 사용법

## Git을 몰라도 사용하는 방법

1. README에서 PROGRESS와 TEAM_TASKS를 열어 자신의 ID·마감·산출물을 확인함.
2. 작업 후 결과 파일+사용 코드+입력 버전+해석을 Drive 작업 폴더에 저장함.
3. templates/HANDOFF.md를 복사하여 ID·완료 내용·검수 요청을 작성함.
4. 통합 담당이 파일 링크를 연결하고 tasks.csv 상태를 갱신함.
5. 검수 완료 전에는 완료 상태로 바꾸지 않음.

## 로컬에서 진행표 갱신

```bash
python scripts/check_plan.py
python scripts/update_trackers.py
```

- Python3 표준 라이브러리만 필요함. 이 두 명령은 앱이나 LLM을 실행하지 않음.
- 앱 실행 환경은 C01에서 확보해 `app/README.md`에 추가해야 함. 현재 저장소에 실제 앱 코드가 포함됐다고 가정하지 않음.
- tasks.csv는 UTF-8 BOM 형식이므로 Excel에서 확인 가능함. 날짜는 YYYY-MM-DD, 의존성은 세미콜론으로 유지함.
- 상태값은 planned / in_progress / review / done / blocked / conditional / deferred / artifact_present / reported임.
- artifact_present는 해당 산출물을 이번 검토에서 확인했다는 뜻임. reported는 보고서의 완료 보고만 확인했다는 뜻임.
- 자동 생성되는 PROGRESS.md·TEAM_TASKS.md를 직접 수정하기보다 tasks.csv를 수정함.
- 늦어진 작업은 기한만 지우지 말고 block 원인·다음 조치를 handoff와 회의록에 기록함.
