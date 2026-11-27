# E01 — 응집 공정 에너지·탄소 계산 규격

- 담당: 임수현 | 작성 기준일: 2026-11-27
- 상태: 계산식 확정안 / 배출계수 조건부 제안(실제 시약·제조 경로 확인 전)
- 연계: `energy_factors.csv`, `energy_references.csv`, E02 입력 파일
- 근거: [BTS_ENERGY_SPEC](https://github.com/2026neuraldata/2026-BTS-Research/blob/main/docs/ENERGY_SPEC.md). 아래 source_id는 문헌 CSV와 연결한다.

## 1. 산정 경계 및 기능 단위

| 항목 | 포함 여부 | 출력 |
|---|---|---|
| 급속·완속교반 | 기본 포함 | kWh/batch 또는 kWh/day |
| 응집 관련 이송·주입 펌프 | 실제 사용 확인 시 포함 | kWh/batch 또는 kWh/day |
| FeCl3 제조 | 기본 포함 | kgCO2e/batch 또는 day |
| pH 조절용 NaOH 및 HCl 제조 | 기본 포함 (각 1 mol/L 용액 사용) | kgCO2e/batch 또는 day |
| 응집보조제 제조 | 미사용 확인: 배출량 0 | kgCO2e/batch 또는 day |
| 약품 제조공장 이후 운송, 슬러지·후속처리, 직접 CH4/N2O, 설비 건설 | 기본 산정 제외 | 별도 확장 모듈 |

기능 단위는 동일 처리 목표를 충족하는 폐수 1 m³로 정규화한다. 원자료는 batch 또는 day 단위로 보존하며 두 단위를 섞지 않는다. 본 산정은 응집 단계 부분 배출량이며 전체 하수처리장 탄소발자국이나 인증용 LCA가 아니다. 실제 장치 미사용 확인 시에만 0; 범위 밖은 excluded; 미기록은 missing.

## 2. 단위 및 기호

| 변수 | 의미 | 입력 단위 |
|---|---|---|
| Q_m3 | 해당 기간에 처리한 폐수량 | m³/batch 또는 m³/day |
| V_m3 | 실제 교반조 내 액체 부피 | m³ |
| dose_mg_L | 약품 투입농도(질량 기준 명시) | mg/L |
| P_el_W | 장비의 유효 전기 입력 전력 | W |
| P_fluid_W | 유체에 전달되는 이론 동력 | W |
| mu | 동점성이 아닌 동적 점성계수 | Pa·s |
| G | 속도경사 | s⁻¹ |
| Np | 장비 및 유동 조건에 맞는 동력수 | 무차원 |
| rho | 유체 밀도 | kg/m³ |
| n | 임펠러 회전수 | s⁻¹ (rpm/60) |
| D | 임펠러 직경 | m |
| t_h | 해당 장치 실제 작동 시간 | h |
| eta | 전기 입력 대비 유효 전달동력 효율 | 0 < eta ≤ 1 |
| q | 펌프 운전 중 유량 | m³/s |
| H | 펌프 전양정 | m |
| w | 제품 또는 용액의 유효성분 질량분율 | kg/kg |
| EF_grid | 소비 전력 배출계수 | kgCO2e/kWh |
| EF_i | 약품 제조 배출계수 | kgCO2e/kg (질량 기준 일치) |

변환: L/1000=m³; min/60=h; s/3600=h; m³/h/3600=m³/s; W/1000=kW; tCO2e/MWh=kgCO2e/kWh(수치 동일).

## 3. 산식

### F01. 약품 사용량

`M_kg = dose_mg_L * Q_m3 / 1000`

batch 부피가 L이면 `M_kg = dose_mg_L * volume_L / 1e6`. 제품 농도와 활성성분 농도를 구별한다. 용액을 직접 계량하면 `M_solution_kg = volume_mL * density_kg_L / 1000`; `M_active_kg = M_solution_kg * w`. 활성성분에서 제품량을 역산하면 `M_product_kg = M_active_kg / w`. 희석 stock의 투입량을 구매 원제품으로 환산할 때에는 stock과 구매품 각각의 농도를 적용하고 희석수 질량은 원제품으로 계산하지 않는다. 산·염기 농도가 mol/L로 기록된 경우 `M_active_kg = molarity_mol_L * volume_L * molar_mass_kg_mol`.

**실험 확인 조건 (2026-11-27, 담당자 확인):** pH 상승은 NaOH 1 mol/L, pH 하강은 HCl 1 mol/L 용액을 사용한다. 응집보조제는 사용하지 않는다.

- `M_NaOH_active_kg = V_NaOH_L * 0.04000`
- `M_HCl_active_kg = V_HCl_L * 0.03646`
- 투입량이 mL이면 L로 변환(/1000) 후 적용한다. 투입 부피는 E02에서 확인하며, 사용량 미기록은 missing으로 유지한다.
- `M_aid_kg = 0`, `C_aid = 0` (미사용 확인). 배출계수 자체를 0으로 설정하지 않는다.

FeCl3 무수물 몰질량 162.204 g/mol, Fe 55.845 g/mol, FeCl3·6H2O 270.294 g/mol(순수 물질 기준). `M_active_FeCl3 = M_hydrate * purity * 162.204 / 270.294`; Fe 기준이면 `M_active_FeCl3 = M_Fe * 162.204 / 55.845`. 순도·형태가 불명확하면 변환하지 않는다. 실험 확인 사항(2026-11-27): FeCl3는 수화물로 추정되나 형태·수화수는 미확정이다. Stock 용액 제조 시 질량 기준을 보정했으며, 기록상 기준(무수 FeCl3 또는 수화물), 제조량·농도는 다음 주 확인한다. 이미 무수 FeCl3 기준으로 보정된 투입량은 재환산하지 않는다. 제품 배출계수는 미확정으로 유지한다. 수화물에서 무수물 질량으로 변환할 수 있어도 고체 제조 배출계수와 용액 제조계수가 동일해지는 것은 아니다.

### F02. 교반 전력 (급속 및 완속 각각)

우선순위: ① 전력계에서 측정한 kWh ② 측정한 평균 유효 전력 × 작동시간 ③ 물리식 추정.

- 실측 전기 입력: `E_stage = P_el_W * t_h / 1000` (효율을 다시 나누지 않음).
- G 기반: `P_fluid_W = mu * V_m3 * G**2`.
- 임펠러 기반: `P_fluid_W = Np * rho * (rpm/60)**3 * D**5`.
- 추정 전력: `E_stage = P_fluid_W * t_h / (1000 * eta)`.
- `E_mix = sum(E_stage)`; 시간에 따라 변하는 경우 구간별 합산 또는 전력 적분.

G식과 Np식은 대안이며 동일 단계에 합산하지 않는다. Np는 임펠러 기하 및 Reynolds 수(`rho*n*D**2/mu`)에 맞는 값이 필요하다. 장비별 rpm-G 보정곡선 또는 기하·동력수가 없으면 rpm만으로 산정하지 않는다. 정격 모터 동력은 실제 소비전력이 아니다. 다구 jar tester의 공용 모터 전력은 전체 장치에서 한 번만 집계하고, 개별 jar 배분 시 근거를 남긴다. batch의 교반조 부피와 하루 처리유량은 다르며 연속조는 실제 운전시간으로 계산한다. [EPA_NUTRIENT_CONTROL_2010, OHA_COAGULATION]

실제 실험 조건(2026-11-27 확인)
- 급속교반: 100 rpm, 1분
- 완속교반: 30 rpm, 30분
- Jar tester: C-JT-1 추정
- 장비 사양: 220 V, 30 W, 6구

장비 모델은 추후 확인하며, 정격전력 30 W는 실제 소비전력이 아닌 시나리오 계산에만 사용한다.

### F03. 펌프 전력

`P_el_W = rho * 9.80665 * q * H / eta_total`

`eta_total = eta_pump * eta_motor * eta_transmission` (인버터 손실이 있다면 해당 효율도 포함). `E_pump = sum(P_el_W * t_h / 1000)`. 실측 전력/kWh 우선. q는 폐수 하루 평균 유량이 아니라 해당 펌프의 운전 유량이며 약품 주입펌프에는 약품 유량·밀도·양정을 사용한다. 수동 주입은 펌프 미사용 확인 시 0. 정적 혼화기 압력손실이 이미 펌프 양정에 포함되면 혼화 에너지와 중복 합산하지 않는다. [EECA_PUMP_AUDIT]

### F04. 공정 전력 및 전력 배출량

`E_grid = E_mix + sum(E_pump_included)`

`C_grid = E_grid * EF_grid`

연구 비교 기본 권장: `GRID_KR_2023 = 0.4173 kgCO2e/kWh` (2023년 국가통계, 2025-12 공표). 0.4541은 2020–2022 평균으로 구버전 재현에만 사용한다. 2026 실측 계수가 아니며 법정 보고에는 해당 보고기간의 적용지침을 따른다. [GIR_KR_GRID_2023]

### F05. 약품 제조 배출량

`C_i = M_i * EF_i`; `C_chemical = sum(C_i)`.

INCOPA Table D-1의 제품 철 함량은 0.138 kg/kg. 무수 FeCl3 환산 질량분율 `w_ref = 0.138 * 162.204 / 55.845 = 0.400826`.

| 제조 경로 | kgCO2e/kg 문헌 제품 | kgCO2e/kg active FeCl3 환산 | kgCO2e/mol Fe (원문) |
|---|---:|---:|---:|
| Pickling acids | 0.135 | 0.336804 | 0.055 |
| Iron oxide | 0.395 | 0.985464 | 0.160 |

제품 기준과 active 기준 중 하나만 선택한다. 환산값은 동일 경로 제품의 활성성분당 배출량일 뿐 무수 고체 또는 수화물 제조의 독립 검증 계수가 아니다. 몰 기준도 대안이며 제품·몰 값의 반올림 차이가 있다. 제조 경로를 모르면 두 시나리오를 별도로 표시하고 평균값을 실제 계수로 지정하지 않는다. 이 두 값은 전 세계 최대·최소를 의미하지 않는다. `FE_LEGACY = 0.6535`는 여러 응집제 평균 0.106 kgCO2e/mol-metal의 환산값이므로 신규 계산 금지. 국내 공급품의 제품탄소발자국/EPD가 확보되면 경계·농도·연도 검증 후 우선 적용. [INCOPA_LCA_2014]

산·염기 보조 시나리오: HCl 30% 용액 0.735, NaOH 50% 용액 1.010 kgCO2e/kg 제품. Tucson 보고서의 WEF 2013 2차 인용이므로 실제 시약 제조국 및 경로 검증 전 기본계수로 사용하지 않는다. 다른 농도 또는 고체는 직접 적용 금지. 1 M 실험용액에 제품 기준 계수를 직접 곱하지 않는다. 문헌과 같은 원제품을 희석한 것으로 가정하는 시나리오에 한해 `C_HCl = (M_HCl_active_kg / 0.30) * 0.735`, `C_NaOH = (M_NaOH_active_kg / 0.50) * 1.010`을 적용할 수 있다. 이는 원제품 일치 가정이며 실제 구매품 계수는 미확정이다. 원제품 형태·농도와 공급 경로 확인 전 확정값으로 사용하지 않는다. [TUCSON_GHG_2021]

### F06. 부분 탄소배출량 및 원단위

`C_total = C_grid + C_chemical`; `C_intensity = C_total / Q_m3`; `E_intensity = E_grid / Q_m3`.

약품 제조에 사용된 전력은 제조 배출계수에 이미 반영되므로 현장 사용전력에 다시 더하지 않는다. 전력 간접배출과 약품 상류 제조를 분리하여 표시한다. 서로 다른 GWP 버전·지역의 계수로 계산한 결과는 탐색적 추정으로 명시한다. 포함 항목에 누락이 있으면 전체 합계는 missing; 확보 항목만 합산한 값은 명시적으로 partial subtotal로 표시한다.

### F07. 변화량 및 전력 환산량

`delta_E = E_baseline - E_recommended`; `delta_C = C_baseline - C_recommended`; `reduction_pct = 100 * delta_C / C_baseline` (기준량이 양수일 때만).

`E_equivalent = delta_C / EF_grid`는 탄소 감소량의 전력 등가값(kWh-equivalent)이며 실제 교반·펌프 전력 절감량이 아니다. 계수 동일·양수 조건에서 선택 출력. 음수는 증가로 표시한다. 동일 지역, 원수 범위, 목표 탁도, 침전 시간, 처리량, 산정 경계, 계수 및 가정 조건에서만 비교한다. 단순 dose 감소로 실제 전력 감소를 주장하지 않는다. 기준과 추천의 교반 조건이 동일하면 교반 절감 0(동일 조건 확인 시); 조건 미확인 시 missing. Jar 결과는 현장 실증이 아니다.

## 4. 앱 구현·입력 검증

- `factor_id`로 명시 선택하고 `status`가 recommended_default인 전력만 기본 사용. scenario_only는 사용자 선택과 가정 표시 필요. legacy_only는 구버전 재현, deprecated 및 missing은 신규 산정 금지.
- 입력 단위, 질량 기준, 제품 농도·순도, 제조경로와 source_id를 보존. 숫자는 유한값, 질량·시간·동력·유량은 음수 금지, 효율/분율은 0 초과 1 이하. 원단위 계산은 처리량 양수. 전력 계수는 양수.
- 미사용이 확인된 항목만 0. `missing`과 `excluded` 구분; NaN을 0으로 대체하지 않음. E02에서 입력 상태 및 원본 기록 확인.
- 정수처리 OHA 자료는 혼화 원리 및 기하 참고에 한정; 폐수 US EPA 설계 범위도 jar 장치의 실측값이 아님. 점성·G·Np·효율의 가정값은 실측과 분리.
- 결과 필드 제안: `energy_mix_kWh`, `energy_pump_kWh`, `energy_grid_kWh`, `chemical_mass_kg`, `carbon_grid_kgCO2e`, `carbon_chemical_kgCO2e`, `carbon_total_kgCO2e`, `carbon_intensity_kgCO2e_m3`, `delta_energy_kWh`, `delta_carbon_kgCO2e`, `carbon_equivalent_kWh`, `factor_ids`, `basis`, `status`, `excluded_items`, `missing_items`.

## 5. 산식 검산 예시 (가상 입력, 실제 실험 결과 아님)

동일한 1 m³에 active FeCl3 투입량 50→40 mg/L, 급속교반 100 W 0.1 h, 완속교반 20 W 0.5 h(전기 입력), 펌프 미사용, pH 조절약품 투입량 0인 가상 비교 조건을 가정한다(실제 실험에서 NaOH/HCl 사용 확인, 투입 부피는 미확인). 응집보조제는 실제 미사용이다.

- 약품량 0.050→0.040 kg active; 감소 0.010 kg.
- 전력 0.020 kWh로 동일, 전력 절감 0 kWh. 전력 탄소 각 0.008346 kgCO2e.
- 산세 폐액 시나리오: 약품 감소 탄소 0.003368 kgCO2e; 산화철 시나리오: 0.009855 kgCO2e.
- 탄소 감소의 전력 등가값은 각각 0.008071, 0.023615 kWh-equivalent. 실측 전력 절감량과 다름.

### pH 조절약품 검산 (가상 투입량)

각 1 M 용액을 10 mL 투입하는 경우 NaOH 유효성분 0.0004000 kg, HCl 유효성분 0.0003646 kg이다. 위 문헌 원제품 희석 가정 시 각각 0.0008080 및 0.00089327 kgCO2e이다. 실제 사용량·배출량이 아니다.

## 6. E02 인계 및 확인 필요 사항

시약 제품명/SDS/CoA, 무수·수화물·용액 여부, stock 및 원제품 농도·순도, 제조사·국가·경로, NaOH/HCl 원제품 정보와 실제 1 M 용액 투입 부피 (응집보조제 미사용 확인 완료), 실제 교반 시간·전력 또는 장비 기하/G·점성·효율, 펌프 사용 여부 및 유량·양정·효율 확인. 내부 Energy_Usage PDF는 접근 제한으로 직접 대조하지 못했으며 공개 GitHub 규격과 문헌 원문으로 작성했다. 따라서 실제 공급품 배출계수는 미확정이며, 경로별 문헌 시나리오만 구현 가능하다. 담당자 및 팀 검토 후 채택. 미확인 시약 정보와 stock 제조 기록은 다음 주 확인 예정(2026-11-30 주간).
