# 시간순 연구 진행과 해석

> 과거 기록(11/24까지의 검토): 현행 실행 지시가 아님. [현행 업무](TEAM_TASKS.md)와 [문서 관리 기준](DOCUMENT_CONTROL.md)을 따름. [수정 전 원문](https://github.com/2026neuraldata/2026-BTS-Research/blob/df4fe3a6b15af486149f908c79f95811bb5c6119/docs/RESEARCH_HISTORY.md)은 그대로 보존.


- 폴더명·문서 본문·버전 차이를 연결하여 재구성함. Drive 업로드 날짜는 연구 수행 날짜와 다르므로 연대 판단에 단독 사용하지 않음.
- 10월의 template/idea/reference는 당시 선택 전 아이디어를 포함함. 현재 구현이나 완료 결과와 구분함.

| 시점 | 확인한 진행 | 이전 상태에서 바뀐 점 | 현재 판단 |
|---|---|---|---|
| 10/29 자료 | 응집 pH·dose, 문헌/수치 DB, Router, LLM 평가, DSPy 심사위원 계획 | 초기 ESG·공급망 템플릿에서 폐수 응집 주제로 구체화 | Local LLM·Vector DB·DSPy는 계획과 구현을 나눠 표기해야 함 |
| 11/13 기록 | 언양·굴화 Jar 24조건, 굴화 TS/VS 26기록 | 실제 비커 500mL, 실제 투입량 약20.1/40.2/60.3/80.16mg/L 확보 | 10월 계획의 1L·20/22.5/25/27.5mg/L와 다름; 전체 실험일 확정 불가 |
| 11/19 | 선우 분석·지도 / 수현 에너지 / 건희 평가문항 / 재영 코딩 | 역할 구체화, 교과서 기반·속도 개선·공개 시연·탄소 연계 논의 | 이 역할을 유지해 후속 작업 배분함 |
| 11/20 | 5단계 분석·15개 그림·해설·코드, MCQ 후보은행 140개, 에너지 문헌 | 수치 품질·회귀·Pareto·내부 검증까지 확대 | TS/VS 불일치와 Jar 반복 부족을 발견한 분석임 |
| 11/21 | 실험10+교재10의 평가문항 20개 | 후보은행에서 실제 평가안 구성 | 모델 성능 측정 완료가 아님 |
| 11/22 | 발표와 약56분 피드백 녹음·요약 | 제거율 그림, Pareto 선정 설명, 과도한 해석·민감도 정의 개선 요청 | 실험 추가 여부는 조건부 논의임 |
| 11/23 | 원본 보존 재분석, VS 중심 탐색, 실제 입력 민감도, 에너지 확장, 평가문항 개정, 39슬라이드 통합 | TS 목적함수 제외; 문헌10문항을 교재4+논문6으로 수정 | 최신 분석본을 기준으로 사용함 |
| 11/24 | 4개 담당 현황 보고와 일정·기능 계획 통합 | 공정 에너지 확정; AI 추론 에너지는 검토; PDF·지역 비교 UX 제안 | 통합·실제 평가·결과 동결 단계로 이동해야 함 |

## 분석 버전 간 차이

| 항목 | 11/20 | 11/23 기준본 |
|---|---|---|
| TS/VS 표현 | TS·VS 모두 탐색 그림과 목적 조합에 포함 | TS 성능 목적 제외; VS도 탐색적 한계 유지 |
| VS/TS | 질량 일관성 문제 진단 | 물리 조건을 통과한 5/26 기록만 비율 표시; 일반화·역산 금지 |
| Fig07 | 반응표면 | 지역별 색척도 분리; 회귀 추정과 관측 구별 |
| Fig08/09 | 잔류 NTU·ΔNTU 중심 | 제거율·제거율 변화량으로 재표현 |
| Pareto | TS 포함 추가 조합 존재 | dose+NTU, dose+removal, 탐색적 dose+NTU+VS |
| Fig15 | 반복 재표집의 최저 VS 선택 빈도 | pH ±0.2 / dose ±10%의 모델 입력 민감도; bootstrap은 보조 결과 |

- 11/24 분석 이력 보고서에는 가상 재구성 시나리오를 검토했다가 원본 기준으로 돌아온 과정이 기록되어 있음. 해당 중간 시나리오 ZIP은 현재 Drive 목록에 없으므로 그 파일 자체를 검토했다고 주장하지 않음.
- 현재 3개 Excel 사본의 SHA256은 동일하며 원본 값을 수정한 자료를 분석 기준으로 삼지 않음.
- bootstrap의 이전 약62.9%와 새63.69%는 seed가 다르며, 실제 최적조건일 확률이 아닌 표본 재선택 빈도임.

## 현재 사용할 수 있는 관찰 결과

| 관찰 | 수치/범위 | 반드시 함께 제시할 제한 |
|---|---|---|
| 잔류 탁도 최소 | 언양 pH5/80.16mg/L: 0.50NTU; 굴화 pH7/80.16mg/L: 2.30NTU | 관측한 12조건 내 최소이며 Jar 독립 반복 없음 |
| 평균 30분 제거율 | 언양93.72%, 굴화90.27% | 초기 원수 차이로 지역 원인 효과 해석 불가 |
| 30분 탁도 재상승 | 언양0/12, 굴화7/12 | 평균 ΔNTU는 각각−0.300, −0.192로 둘 다 음수임 |
| VS/TS 물리 일관성 | VS>TS 21/26; TS<0 2건은 21건에 포함 | 오류 원인·VS 자체 정확성 미확정 |
| VS 반복 변동 | CV 중앙27.8%, 최대78.6% | 조건당 n=2의 기술통계임 |
| 2목적 Pareto | 지역별 비지배조건4개 | 단일 검증된 최적값이 아닌 관측 후보 집합임 |
| LOOCV 최저 MAE | 언양 quadratic0.412NTU / 굴화 linear1.436NTU | 같은 데이터 내 모델 비교이며 독립 채수일 검증 아님 |

## 구현 상태의 표현

- 현재 개발 보고서의 구조는 Claude API + TF-IDF 검색 + 로컬 규칙 추천임. Local LLM·dense Vector DB·DSPy 적용 완료로 표현할 근거는 없음.
- 검색 평가 13/15=0.87은 recall@10의 보고값임. 20문항 LLM 정답률이나 추천 정확도로 바꿔 쓰지 않음.
- 코드 자체와 실제 API 평가 로그는 현재 폴더에 없음. 보고된 mock 테스트 통과와 독립 실행 검증은 구별함.
- 공정 에너지·약품탄소 계산의 일부 식은 준비됨. 실제 교반전력·산염기량·약품 규격 등 입력 확보가 남아 있음.

근거: [Data_Analysis_김선우.pdf](https://drive.google.com/file/d/1o2OGKhoRQ7n2b7n3AzS1_2XJzwqjdA3K/view?usp=drivesdk) · [BTS_VS_Original_Reanalysis_1123.zip](https://drive.google.com/file/d/1VRyarPqxo694Dz2hN_xKQUfOpadlfUXa/view?usp=drivesdk) · [feedback_from presentation_instruction.txt](https://drive.google.com/file/d/1w4KNAAqX8Uvb0CIOdeRG4dxH8YD9bfI6/view?usp=drivesdk) · [LLM_Validation_이건희.pdf](https://drive.google.com/file/d/15_HNCQfPAqK64jPsemyXN-WTXxzN6_GV/view?usp=drivesdk) · [Energy_Usage_임수현.pdf](https://drive.google.com/file/d/13_P8N2nwInXZqbeVw2PwCMmkdxmX8ZBG/view?usp=drivesdk) · [Dev_Status_Features_허재영.pdf](https://drive.google.com/file/d/1UctLqjikQwz9aCi_4hPZ3Ef4RUAcu-s1/view?usp=drivesdk)임.
