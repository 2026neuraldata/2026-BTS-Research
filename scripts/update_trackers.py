"""Build research task views from management/tasks.csv (stdlib only)."""
from pathlib import Path
import csv,json,collections
R=Path(__file__).resolve().parents[1]
with (R/'management/tasks.csv').open(encoding='utf-8-sig') as f:tasks=list(csv.DictReader(f))
colors={'H':'⚪','D':'🔵','E':'🟢','L':'🟣','C':'🟠','G':'🔴','P':'🟡'}
labels={'planned':'예정','in_progress':'진행 중','done':'완료','blocked':'진행 불가','conditional':'조건부','deferred':'보류','artifact_present':'산출물 확인','reported':'구현 보고'}
def badge(id):return colors[id[0]]+' **'+id+'**'
def deps(t):return ', '.join(badge(x) for x in t['dependencies'].split(';') if x) or '없음'
def period(t):return t['start'] if t['start'] == t['due'] else t['start']+'–'+t['due']
def key(t):return tuple(map(int,t['due'].split('/')))+(t['id'],)
def table(items):
 rows=['| 작업 ID | 해야 할 일 | 담당 | 기간 | 상태 |','|---|---|---|---|---|']
 for t in sorted(items,key=key):rows.append('| '+' | '.join([badge(t['id']),t['title'],t['owner'].replace(';','·'),period(t),labels[t['status']]])+' |')
 return '\n'.join(rows)
def team_table(items):
 from html import escape
 widths=[90,390,180,140,80]
 headers=['작업 ID','해야 할 일','담당','기간','상태']
 rows=['<table width="880">','<thead><tr>'+''.join(f'<th width="{w}">{h}</th>' for w,h in zip(widths,headers))+'</tr></thead>','<tbody>']
 for t in sorted(items,key=key):
  cells=[colors[t['id'][0]]+' <strong>'+escape(t['id'])+'</strong>',escape(t['title']),escape(t['owner'].replace(';','·')),escape(period(t)),escape(labels[t['status']])]
  rows.append('<tr>'+''.join(f'<td width="{w}">{v}</td>' for w,v in zip(widths,cells))+'</tr>')
 rows.extend(['</tbody>','</table>'])
 return '\n'.join(rows)
legend='🔵 D 데이터 · 🟢 E 에너지·탄소 · 🟣 L LLM 평가 · 🟠 C 앱 개발 · 🔴 G 전체 조율 · 🟡 P 포스터·발표 · ⚪ H 기존 성과'
active=[t for t in tasks if not t['id'].startswith('H')]
text=['# 연구 진행 현황','','- 기준일: 11/28. 연도: 2026.','- 현재: C01·D01·D02·E01·E02·L01·G01 산출물 검토 완료; L02 설계 완료; L03 잠정 선정 조건부. 실제 API·접근통제·독립 채점·에너지 계산 검산은 후속 업무.','- 12/6 포스터 완성 · 12/29 성과발표.','- 업무 배정 제외: 12/7–12/18 기말고사, 12/23–12/27 크리스마스 휴식.','',legend,'','## 전체 실행 업무','','완료는 산출물 검토 기준이며, 조건부 L03는 최종 심사위원 확정 전 상태임. L02 실행 검증은 후속 업무임.','',table(active),'','## 기존 성과','',table([t for t in tasks if t['id'].startswith('H')]),'','[담당별 상세 작업](docs/TEAM_TASKS.md) · [전체 일정](docs/ROADMAP.md) · [LLM 평가 설계](docs/EVALUATION_PROTOCOL.md)']
(R/'PROGRESS.md').write_text('\n'.join(text)+'\n')
team=['# 담당별 작업과 제출물','','- 기간 표기: 시작일–종료일(월/일). 연도: 2026.','- 12/7–12/18 및 12/23–12/27에는 작업을 배정하지 않음.',"- **공통 제출 규칙:** 일반 산출물은 해당 업무 기간 내 BTS 카카오톡 단체방에 제출함. 비공개 평가 자료는 승인된 평가 담당자·팀장 통제 경로로 제출하고 단체방에는 완료 안내만 게시함.","- **제출 형식 준수:** 각 업무에 명시된 제출 파일 형식(CSV, JSON, PDF, MD 등) 및 필수 제출물 구성을 반드시 준수해야 함.","- **진행 관리 규칙:** 김선우가 제출물의 형식 준수 여부 및 연구 진행 상황을 검토하고 GitHub를 업데이트함.","- **업무 의존성 유지:** 특정 팀원의 결과물이 후속 업무에 필요한 경우 기존 선행 작업 및 인계 관계를 유지함.","- **제출 대상자:** 일반 업무는 공통 제출 경로, 비공개 업무는 별도 통제 경로를 사용함.","- **11/28 상태 기준:** 완료는 해당 산출물 검토·인계 완료를 뜻함. L03 조건부는 후속 구현 착수 가능하나 최종 실행/선정 확정은 아님. 접근통제·실제 모델·심사 동결 미통과 시 L06 실행 보류. 회의 및 독립 업무는 예정대로 진행하고 미완료는 기록함.","- **비공개 자료 보호:** 문항 전체·정답·페이지 매핑·문항별 루브릭·채점/보정 자료·내부 로그는 승인된 평가 담당자·팀장 통제 환경으로 제한함. C05 구현 담당자는 승인된 보정/검증용 부분집합만 분리된 심사 환경에서 사용하며 최종 문항/Gold 접근은 금지함. 공개 GitHub와 후보 모델 검색·세션·파일 접근에서 제외함. [평가 접근 통제](EVALUATION_ACCESS_CONTROL.md) 준수. API 키 미포함.","","**핵심 운영 원칙:** 제출 기한 준수 · 제출 형식 엄수 · 제출 경로 일원화","",legend,'']
for name in ['김선우','임수현','이건희','허재영','전원']:
 team += ['## '+name,'',team_table([t for t in active if name in t['owner'].split(';')]),'']
team += ['## 작업별 상세 설명','']
for t in sorted(active,key=key):
 team += [f"### {colors[t['id'][0]]} {t['id']} · {t['title']}",'',f"- **담당:** {t['owner'].replace(';','·')}.",f"- **기간:** {period(t)}. **상태:** {labels[t['status']]}.",f"- **목적:** {t['purpose']}",f"- **먼저 필요한 작업:** {deps(t)}.",f"- **준비 자료:** {t['inputs'] or '관련 원문과 현황 보고서'}.",'','**실행 순서**','']
 team += [f'{i}. {s}.' for i,s in enumerate(t['steps'].split('|'),1)]
 team += ['',f"- **제출물:** {t['deliverables']}.",f"- **완료 기준:** {t['acceptance'].rstrip('.')}.",'']
(R/'docs/TEAM_TASKS.md').write_text('\n'.join(team)+'\n')
print('Generated task views:',len(tasks))

