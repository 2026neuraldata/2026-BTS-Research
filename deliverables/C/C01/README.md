# C01 · 현재 앱 코드와 실행 버전

응집 실험 조건 추천과 문헌 검색 Streamlit 앱입니다.

> **C01 최초 제출자의 기준 환경: localhost (http://localhost:8503).** 당시 평가·시연·발표에 localhost만 사용한다는 제출자 기록임. 통합 기준안의 평가 환경은 localhost/C03 runner이며, 최종 발표 환경 및 C07 범위는 팀 확인 사항임.

2026-11-27에 허재영 PC에서 실행되던 코드를 그대로 묶었습니다. 이 버전은 초기 기준 버전이고, 최종 평가 버전은 L06 전에 따로 고정합니다.

## 구성 (app/)
| 파일 | 내용 |
|---|---|
| app.py | Streamlit 화면: 실험 조건 추천, 절감량, 문헌 질의응답 |
| logic.py | 추천 규칙, 절감량 계산, TF-IDF 문헌 검색, Claude API 호출 |
| literature_pages.json.gz | data/*.pdf 쪽별 본문 캐시 |
| data/ | Jar Test 엑셀(24개 조건)과 문헌 PDF |
| .streamlit/config.toml | 테마, 포트 8503, 127.0.0.1에서만 접속 |
| start_app.bat | 더블클릭하면 실행하고 브라우저를 엽니다 |

## 실행
1. Python 3.14 설치 후 `pip install -r requirements.txt`
2. app/ 폴더에 `.env` 파일을 만들고 `API key: sk-ant-...` 형식으로 Claude API 키를 넣습니다. 키는 제출물에 넣지 않았습니다.
3. `start_app.bat`을 실행하거나 `python -X utf8 -m streamlit run app.py`를 실행한 뒤 http://localhost:8503 에 접속합니다.

## 주의
- data/의 PDF 파일 이름이나 크기가 달라지면, 앱이 처음 시작할 때 문헌 캐시를 다시 만듭니다(몇 분 걸림). PDF를 빼면 문헌 검색 결과가 비어 있게 됩니다.
- 모델 ID와 API 설정은 app_version.csv에 적었습니다.
- 배포 URL(Sites, https://ph-control-bts-1121.jaey1371.chatgpt.site/)은 이 코드와 다른 별도 구현입니다(정적 HTML + 서버 API). 개별 비교 사례는 내부 검증 기록에만 보관함. Sites에는 절감량·CO₂ 계산이 없고, 문헌 규모가 3,516쪽으로 이 버전(4,078쪽)과 다릅니다. Sites 서버 코드와 모델 ID는 확인하지 못했습니다. Sites는 초기 제출자 기준에서 사용하지 않는 대조 환경임. 최종 발표 환경은 팀 확인 사항임.


## 2026-11-27 통합 인계
기존 코드 및 버전 기록은 기준본 그대로 보존함. `evaluation_handoff.json`의 평가 목표 설정은 C02/C03/C04 구현 전 계획이며 현재 코드에 적용된 상태가 아님. 평가 기준 데이터는 GitHub D02 최신본, 문헌은 L02 허용 목록(S021/S022)만 사용. 기존 계산값을 최종 성과로 사용 금지. localhost 기준 평가를 제안하되 실제 API 및 발표 환경은 팀 확인 필요.

## 공개 저장소 배포 제한
공개본은 초기 확보 운영 코드 및 일부 공개용으로 편집된 버전 기록·인계 문서만 포함함. 원본 버전 기록과 테스트 코드는 내부 보존함. PDF 원문, Excel 사본, 문헌 캐시, 검색 평가 정답, 평가 실행 코드(eval_search.py), 예상 결과를 포함한 테스트 코드(test_logic.py)는 미포함. 따라서 공개본만으로 전체 앱 또는 테스트를 실행할 수 없음. 팀 내부에서 허가된 원문 및 기존 baseline 입력을 별도 제공받아야 함. 현재 코드에 C02/C03/C04 변경은 반영되지 않았음. 시험용 구현은 L02 허용 목록과 최신 D02를 기준으로 작성함.

## v2 인계 및 파일 위치
- [최신 D02](https://github.com/2026neuraldata/2026-BTS-Research/tree/main/deliverables/D/D02), [E01](https://github.com/2026neuraldata/2026-BTS-Research/tree/main/deliverables/E/E01), [E02](https://github.com/2026neuraldata/2026-BTS-Research/tree/main/deliverables/E/E02), [L02 공개 설정](https://github.com/2026neuraldata/2026-BTS-Research/tree/main/deliverables/L/L02)은 GitHub 반영 후 해당 경로에서 확보함. 공개본/담당자별 ZIP에 다른 업무 폴더가 없는 것은 의도된 구성임.
- C03은 비공개 Gold/채점자료 없이 개발용 별도 문항으로 실행기를 검증하고, 최종 문항은 평가 담당자가 통제된 실행에 제공함.

## 2026-11-28 인계 보완
개발 보관용 ZIP과 실제 평가용 실행 환경을 분리함. 정답 포함 테스트·검색 평가·기존 캐시·미승인 자료는 평가 실행 경계 밖에 보존. C02/C03은 일반화된 다중 조건 조회·추천·계산 기능을 별도 개발 fixture로 확인하고 승인 원자료 및 현재 입력만으로 실행함.

- 2026-11-28 문서 정비: C01은 초기 구현/개발 보관용이며 실제 평가용 실행 환경이 아님. G03 결정에 따라 로컬 또는 외부 URL로 시연하고, 외부 QR 사용이 승인된 경우에만 QR을 확인함. [현행 업무](https://github.com/2026neuraldata/2026-BTS-Research/blob/main/docs/TEAM_TASKS.md) 우선.
