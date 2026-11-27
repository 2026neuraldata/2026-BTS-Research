"""Build research task views from management/tasks.csv (stdlib only)."""
from pathlib import Path
import csv,json,collections,sys
R=Path(__file__).resolve().parents[1]
with (R/'management/tasks.csv').open(encoding='utf-8-sig') as f:tasks=list(csv.DictReader(f))
cfg=json.loads((R/'config.yaml').read_text(encoding='utf-8'))
year=cfg['project']['year']; as_of=cfg['project']['as_of']; dates=cfg['dates']
pauses=', '.join(x['start']+'–'+x['end']+' '+x['reason'] for x in dates['non_working_periods'])
def write_view(path, content):
 if '--check' in sys.argv:
  if not path.exists() or path.read_bytes()!=content.encode('utf-8'): raise SystemExit('OUTDATED: '+str(path))
 else: path.write_text(content,encoding='utf-8')
colors={'H':'⚪','D':'🔵','E':'🟢','L':'🟣','C':'🟠','G':'🔴','P':'🟡'}
labels={'planned':'예정','in_progress':'진행 중','done':'완료','blocked':'진행 불가','conditional':'조건부','deferred':'보류','artifact_present':'산출물 확인','reported':'구현 보고','review':'검토 중'}
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
counts=collections.Counter(t['status'] for t in active)
summary=' · '.join(labels[k]+' '+str(v)+'개' for k,v in sorted(counts.items()) if v)
statusline='- 현재: '+summary+' (기존 성과 제외). 실행 승인 조건은 평가 규격 및 업무별 완료 기준 참조.'
text=['# 연구 진행 현황','',f'- 기준일: {as_of}. 연도: {year}.',statusline,f"- {dates['poster_final']} 포스터 완성 · {dates['presentation']} 성과발표.",'- 업무 배정 제외: '+pauses+'.','',legend,'','## 전체 실행 업무','','완료는 해당 업무의 완료 기준 충족을 뜻하며 후속 실행 승인과 별개임. 조건부 업무의 상세 조건은 업무 원장 참조.','',table(active),'','## 기존 성과','',table([t for t in tasks if t['id'].startswith('H')]),'','[담당별 상세 작업](docs/TEAM_TASKS.md) · [전체 일정](docs/ROADMAP.md) · [LLM 평가 설계](docs/EVALUATION_PROTOCOL.md)']
write_view(R/'PROGRESS.md','\n'.join(text)+'\n')
team=['# 담당별 작업과 제출물','',f'- 기간 표기: 시작일–종료일(월/일). 연도: {year}.','- 업무 배정 제외: '+pauses+'.',"- **공통 제출 규칙:** 모든 산출물(비공개 평가자료 포함)은 해당 업무 기간 내 BTS 카카오톡 단체방에 공유함.","- **제출 형식 준수:** 각 업무에 명시된 제출 파일 형식(CSV, JSON, PDF, MD 등) 및 필수 제출물 구성을 반드시 준수해야 함.","- **진행 관리 규칙:** 김선우가 제출물의 형식 준수 여부 및 연구 진행 상황을 검토하고 GitHub를 업데이트함.","- **업무 의존성 유지:** 특정 팀원의 결과물이 후속 업무에 필요한 경우 기존 선행 작업 및 인계 관계를 유지함.","- **제출 대상자:** 모든 팀원이 연구 이해 및 설계 검토를 위해 자료를 열람할 수 있음.",f"- **{as_of} 상태 기준:** {summary}. 완료 및 조건부의 의미는 각 업무의 완료 기준을 따름. 최종 평가 실행 승인 조건은 평가 규격 참조. 회의 및 독립 업무는 예정대로 진행하고 미완료는 기록함.","- **비공개 자료 보호:** 평가자료는 연구 이해 및 평가 설계 검토 목적으로 팀원이 자유롭게 열람할 수 있으나, 최종 평가문항 및 정답자료를 평가 대상 LLM의 개발·최적화·성능 개선에 사용하지 않음. 공개 GitHub·후보 LLM/RAG에 비공개 자료 입력 금지. C05 실행은 승인된 보정/검증 자료만 사용. [공유 주의사항](TEAM_SHARING_POLICY.md) 및 [평가 접근 통제](EVALUATION_ACCESS_CONTROL.md) 준수. API 키 미포함.","","**핵심 운영 원칙:** 제출 기한 준수 · 제출 형식 엄수 · 제출 경로 일원화","",legend,'']
for name in ['김선우','임수현','이건희','허재영','전원']:
 team += ['## '+name,'',team_table([t for t in active if name in t['owner'].split(';')]),'']
team += ['## 작업별 상세 설명','']
for t in sorted(active,key=key):
 team += [f"### {colors[t['id'][0]]} {t['id']} · {t['title']}",'',f"- **담당:** {t['owner'].replace(';','·')}.",f"- **기간:** {period(t)}. **상태:** {labels[t['status']]}.",f"- **목적:** {t['purpose']}",f"- **먼저 필요한 작업:** {deps(t)}.",f"- **준비 자료:** {t['inputs'] or '관련 원문과 현황 보고서'}.",'','**실행 순서**','']
 team += [f'{i}. {s}.' for i,s in enumerate(t['steps'].split('|'),1)]
 team += ['',f"- **제출물:** {t['deliverables']}.",f"- **완료 기준:** {t['acceptance'].rstrip('.')}.",'']
write_view(R/'docs/TEAM_TASKS.md','\n'.join(team)+'\n')
print('Generated task views:',len(tasks))

