# 공정 에너지·탄소 계산 규격

- 담당: 임수현 산식·계수·입력 확보, 허재영 구현, 선우 원본 조건 대조.
- 근거: [Energy_Usage_임수현.pdf](https://drive.google.com/file/d/13_P8N2nwInXZqbeVw2PwCMmkdxmX8ZBG/view?usp=drivesdk) 및 [Dev_Status_Features_허재영.pdf](https://drive.google.com/file/d/1UctLqjikQwz9aCi_4hPZ3Ef4RUAcu-s1/view?usp=drivesdk)임. 아래는 현재 자료에서 확인한 계산 문제를 정리한 구현 요구사항임.

## 구분해서 보여줄 출력

| 출력 | 단위 | 뜻 |
|---|---|---|
| 공정 전력 | kWh/batch 또는 kWh/day | 급속·완속교반·포함하기로 한 펌프의 전력 사용량임 |
| 약품 사용량 | kg/batch 또는 kg/day | 질량 기준이 명확한 FeCl3·산·염기 사용량임 |
| 공정 전력 배출량 | kgCO2e | 전력×해당 연도·지역·방법의 계수임 |
| 약품 제조 배출량 | kgCO2e | 약품 질량×같은 질량 기준의 제조계수임 |
| 전력 환산량(선택) | kWh-equivalent | 탄소량/전력계수의 등가값이며 실제 절감 전력이 아님 |

## 계산식과 단위

- 약품 질량: `M_kg = D_mg_L × Q_m3 / 1000`임. active FeCl3, 수화물, 제품용액의 질량 기준을 별도 필드로 관리함.
- 유체에 전달되는 혼합 동력: `P_W = μ × V × G²` 또는 `P_W = Np × ρ × N³ × D⁵`임. N은 회전수/s이며 rpm은 60으로 나눔. 두 식은 대안이며 더하지 않음.
- 유체 동력으로부터 전기 입력을 추정하면 `E_kWh = Σ(P_W × t_h)/(1000×η)`임. 이미 전기 입력 전력을 실측했다면 η로 다시 나누지 않음.
- 펌프는 포함 범위를 먼저 정하고 `P_W = ρgQH/η`로 산정함. 이 식의 Q는 m³/s임.
- `C_total = E_grid × EF_grid + Σ(M_i × EF_i)`임. 약품계수에 포함된 전력 배출을 다시 더하지 않음.
- 변화량은 같은 경계·유량·목표·시간 기준에서 `baseline − recommended`로 계산함. 음수면 증가임; 절감처럼 표시하지 않음.

## 현재 계산의 수정 우선순위

1. 개발 보고서의 `탄소 절감 / 0.4541`은 전력 환산량으로 이름을 바꿔야 함. 교반 에너지 절감 카드와 분리함.
2. FeCl3의0.6535는 INCOPA 응집제 전체 평균0.106kgCO2e/mol-metal을 무수 FeCl3 몰질량으로 나눈 값임. FeCl3 제품별 검증 계수처럼 사용하지 않음.
3. INCOPA의 FeCl3 제조 경로별 값과 실제 시약 형태·금속 함량·농도 기준을 맞춰야 함. 서로 다른 kg 기준 값을 바로 교체하거나 평균내지 않음.
4. 현재 원본의 실제 교반 속도·시간, 장비/기하, 산·염기 사용량 등의 공백을 확보함. 미확보는 0이 아니라 missing임.
5. 물리적으로 동등한 처리 성능을 달성하는 기준/추천 조건을 정의함. dose 감소만으로 공정 전력이 줄었다고 추론하지 않음.

## 필요한 입력 파일

- energy_inputs.csv: scenario_id, site, basis(batch/day), measured_or_assumed, volume_L/flow_m3_day, mixing_method, stage, power_W 또는 μ/V/G/Np/ρ/N/D, time_h, efficiency, acid/base mass·concentration, source_id, uncertainty_note임.
- energy_factors.csv: substance, factor_value, unit, mass_basis, concentration, geography, year, boundary, manufacturing_route, source_id, page/table, assumption, reviewer임.
- 문헌별 식별자는 DOI/제목 기반으로 고정함. PPT의1–10과 보고서의R01–R15 번호만으로 연결하지 않음.

## 검수 예시와 범위

- 60→40.2mg/L, 10,000m³/day 조건의 약품 차이는198kg/day임. 이 예시는 수식 검수용 시나리오이며 실험으로 관측한 현장 절감량이 아님.
- 0.6535를 가정한129.393kgCO2e/day는 해당 가정의 산술 결과이며, 올바른 제품 계수 확보와 별개임.
- 입력 근거가 없으면 ‘현재 계산 불가’와 필요한 입력을 표시함. 가정 시나리오를 제공할 때는 측정값과 구분함.
- AI 추론 전력, 전체 하수처리장의 생물공정 배출, 슬러지 처분·자원화는 이번 기본 경계 밖임. 필요하면 별도 경계로 연구함.
- E04에서 CBAM·RE100·ISO별 증빙 활용 조건과 PDF 예시를 작성하고 C06에 인계. [PDF 증빙 설계](PDF_EVIDENCE_SPEC.md) 참조. 추천 시나리오와 실제 보고기간의 배출 실적은 분리하고, 제도별 요구 원자료와 외부 검증 결과를 연결.
