# 데이터 인수인계 규격

- 담당: 김선우 작성, 허재영 구현 연결, 이건희 평가 수치 대조.
- 기준 원본: [Jar_Test_TS_VS_Data.xlsx](https://docs.google.com/spreadsheets/d/1YBOluRZW8hG1QDAmGNnKk65ANJPa0imD/edit?usp=drivesdk&ouid=100418307827053295745&rtpof=true&sd=true)임. SHA256은 `config.yaml`에 고정함.
- 10월 계획의 목표 dose와 실제 Excel의 투입량을 혼동하지 않음.
- 현행 인계본: [D01](../deliverables/D/D01) · [D02](../deliverables/D/D02). 11/27 E02 확인값을 추가 메타데이터로 반영함. 원본 Excel·11/23 분석 ZIP·TS/VS·기존 측정값은 그대로 유지함.

## jar_conditions.csv

| 필드 | 뜻·단위 | 규칙 |
|---|---|---|
| condition_id, source_row | 고유 조건·원본 행 | 원본 추적 가능해야 함 |
| site | Eonyang / Gulhwa | 지역 식별; 검증된 전이 가능성을 뜻하지 않음 |
| sample_date, experiment_date | 채수일·실험일 | 원문 없는 값은 빈칸; 폴더명으로 자동 채우지 않음 |
| target_ph, measured_ph | 목표/실측 pH | 서로 구분하고 없는 실측은 미기록 처리함 |
| coagulant, dose_actual_mg_L | FeCl3·실제 투입량 | 20.10 / 40.20 / 60.30 / 80.16 기준임 |
| volume_L | 비커 내 시료 부피 | 실제 기록 0.5L와 초기 계획 1L 구별함 |
| initial_ntu, ntu_5min, ntu_30min | 원수·5분·30분 탁도 | 같은 비커의 시간 측정임 |
| removal_5_pct, removal_30_pct | (initial−after)/initial×100 | 단위 %; 차이는 %p임 |
| rapid_rpm, rapid_min, slow_rpm, slow_min | 공통 확인 교반 조건 (rpm·min) | 24조건: 급속 100 rpm·1분, 완속 30 rpm·30분. 원본 Excel 미기록이며 11/27 실험 수행자 확인값임 |
| hcl_stock_concentration_mol_L, naoh_stock_concentration_mol_L | 산·염기 stock 농도 (mol/L) | 각각 1 M 공통 확인. 개별 비커 사용 여부·투입량을 의미하지 않음 |
| supplemental_metadata_source_id, supplemental_metadata_confirmed_date | 추가정보 출처·확인일 | E02_USER_20261127, 2026-11-27; 원본 source_id/hash와 구분 |
| acid_type, acid_amount, base_type, base_amount | pH 조정 약품·투입량 | 개별 비커 사용 여부·투입량은 미확인으로 공란 유지. 공통 stock 농도와 별개이며 누락은 0 아님 |
| observation_note, qc_flag | 부유물·흔들림 등 원본 메모 | 제외/포함 판단 근거 보존함 |
| source_id, source_sha256 | 원본 및 버전 | 모든 후속 표·그림과 연결함 |

## solids_exploratory.csv

- 굴화 원수2기록+처리12조건×독립 반복2회의 총26기록임.
- sample_id, condition_id, replicate_id, dish_g, dried_g, burned_g, volume_L, ts_g_L, vs_g_L, valid_mass_relation, source_row를 보존함.
- TS=(dried−dish)/volume_L, VS=(dried−burned)/volume_L로 원본 질량에 근거함.
- TS>0, VS≥0, TS≥VS를 통과한 비율만 별도 계산함. 5개 유효 비율을 나머지 21기록에 대입하지 않음.
- Jar 1개와 VS 반복2개는 동일 설계조건으로 연결되며 같은 비커의 직접 반복 매칭으로 간주하지 않음.

## 추천 규칙에 연결할 때

- 사용자가 선택한 지역·시점·보유 응집제·목표 탁도·실험 범위를 명시함. 조건을 만족하는 관측값 중 최소 dose를 선택하고 동률 규칙을 고정함.
- 원수 탁도 ±30%는 현재 구현의 휴리스틱 기준임. 이 폭이 과학적으로 검증된 유사성 기준이라는 주장은 하지 않음.
- 잔류 NTU 최소와 제거율 최대는 다른 목표임. 목표 설정에 따라 후보가 달라질 수 있음을 표시함.
- pH 조정 시약을 고려하지 않은 최소 dose는 최소 총비용·최소 총탄소를 의미하지 않음.
- 목표 미충족·지원하지 않는 응집제·새 원수 범위 밖 입력은 추가 Jar Test 필요로 처리함.
- VS/TS는 탐색 자료 화면에 두고 운영 추천 점수에 직접 포함하지 않는 안임.

## 결과물 구성

- 원본 24 Jar /26 solids 수, 원본 hash, 지역·dose·시점 조합, 결측 여부를 확인함.
- 그림은 실제 사용한 CSV와 일대일로 연결하고, 관측·회귀 예측·bootstrap을 표시함.
- 기준본 재분석을 반복 수행하기보다 앱과 평가에 동일한 수치가 전달되는지 우선 검증함. C02는 D02 실제 dose 소수점 정밀도를 유지하고 E02의 condition_id 매핑을 C04에서 연결함.

## 녹음에서 추가 확인한 연결 요구

- Excel/CSV를 읽기 쉬운 형태로 전달하면 되며 별도 SQL DB 구축을 필수로 요구하지 않음.
- 날짜별 조회·비교를 지원할 때 없는 날짜에는 자료 없음으로 응답함. 실제 날짜가 미기록인 행에 임의 날짜를 부여하지 않음.
- synthetic fixture는 테스트 전용으로 분리하고 UI·로그에 가상 데이터임을 표시함. 실측 분석·벤치마크 결과에 섞지 않음.
- 문헌 투입량을 보간하려면 원수·약품·pH·평가조건의 일치를 확인해야 함. 단순히 탁도만 가까운 서로 다른 연구의 값을 연결하지 않음.

## 11/27 기준 파일 연결

- `jar_conditions.csv` SHA-256: `557c98b75443bb493de8d3d70150bb0a10aa14d35f42e2957264078f3d7d3648`
- `data_dictionary.csv` SHA-256: `ddebc86e1e90684917fb9469e106a50359f7124b2f96e3289bdce0b3263ffb82`
- [E02 조건 매핑](../deliverables/E/E02/condition_energy_mapping.csv)으로 24개 조건의 에너지 입력 ID를 연결함. 실제 전력 및 개별 산·염기 투입량은 미확인임.
- 후보 LLM의 자료 접근 범위는 이 문서 전체가 아니라 [L02 corpus_manifest](../deliverables/L/L02/corpus_manifest.json)와 [접근 통제](EVALUATION_ACCESS_CONTROL.md)를 따름.
