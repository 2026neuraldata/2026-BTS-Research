# E02 통합 인계 (2026-11-27)
- `condition_energy_mapping.csv`: D02 최신 Jar 24개 조건과 기존 입력 시나리오 ID의 연결표. D02 SHA-256: `557c98b75443bb493de8d3d70150bb0a10aa14d35f42e2957264078f3d7d3648`.
- 급속 100 rpm 1 min, 완속 30 rpm 30 min, HCl/NaOH stock 각 1 mol/L: 담당자 확인 공통조건. 개별 비커 투입 여부/부피와 실제 소비전력은 미확인.
- 8개 입력 행 및 11개 에너지 시나리오의 기존 수치 보존. 장비 모델·정격전력은 가정/사양값, 실제 소비전력 아님. 공용 모터 중복 합산 금지.
- M01 해결, M11 일부 해결(기록된 stock 질량 기준만). E01 계수와 active mass basis 확인 전 실제 탄소값 확정 불가.
- E01 원본 유지. C04/E04에서 실제 계산/검산.

## v2 인계
- D02 기준은 [GitHub jar_conditions.csv](https://github.com/2026neuraldata/2026-BTS-Research/blob/main/deliverables/D/D02/jar_conditions.csv)의 SHA-256 일치본임. `condition_energy_mapping.csv`의 `dose_input_id`/`rapid_input_id`/`slow_input_id`/`ph_input_id`/`pump_input_id`는 `energy_inputs.csv`의 `scenario_id` 참조임. 24개 조건의 공통 장비·교반 입력을 중복 합산하지 않음.
- E01/E02 시나리오 수치는 변경하지 않았음. 정격전력 시나리오의 E_device_kWh는 전체 장비값이며 비커별 E_mix_kWh와 구분해야 함. 실제 사용 비커 수 미확정.

## 2026-11-28 인계 보완
11개 시나리오는 가정별 절대량 예시이며 동일 목표를 만족한 기준/추천의 절감량 검증은 아님. C04/E04에서 동일 기능단위·경계·입력 기준의 두 조건을 비교하고 미확보 입력은 missing, 계산 가능한 항목은 부분합으로 표시. 동일 교반시간/rpm만으로 실제 전력 동일 또는 절감 0을 단정하지 않음. 동일 물리식 입력/전력 가정에 한해 동일 계산 결과를 보고. 0.5 L 결과의 단순 확대를 처리장 실측량으로 보고 금지. 최초 E02 ZIP과 초기 입력 CSV는 D01 메타데이터 출처로 원본 보존. 최신본과 별도 버전 관리.
