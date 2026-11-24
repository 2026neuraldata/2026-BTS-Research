"""Build research task views from management/tasks.csv (stdlib only)."""
from pathlib import Path
import csv,json,collections
R=Path(__file__).resolve().parents[1]
with (R/'management/tasks.csv').open(encoding='utf-8-sig') as f:tasks=list(csv.DictReader(f))
colors={'H':'⚪','D':'🔵','E':'🟢','L':'🟣','C':'🟠','G':'🔴','P':'🟡'}
labels={'planned':'예정','in_progress':'진행 중','review':'검수 대기','done':'완료','blocked':'진행 불가','conditional':'조건부','deferred':'보류','artifact_present':'산출물 확인','reported':'구현 보고'}
def badge(id):return colors[id[0]]+' **'+id+'**'
def deps(t):return ', '.join(badge(x) for x in t['dependencies'].split(';') if x) or '없음'
def key(t):return tuple(map(int,t['due'].split('/')))+(t['id'],)
def table(items):
 rows=['| 작업 ID | 해야 할 일 | 담당 | 마감 | 상태 |','|---|---|---|---|---|']
 for t in sorted(items,key=key):rows.append('| '+' | '.join([badge(t['id']),t['title'],t['owner'],t['due'],labels[t['status']]])+' |')
 return '\n'.join(rows)
legend='🔵 D 데이터 · 🟢 E 에너지·탄소 · 🟣 L LLM 평가 · 🟠 C 앱 개발 · 🔴 G 전체 조율 · 🟡 P 포스터·발표 · ⚪ H 기존 성과'
active=[t for t in tasks if not t['id'].startswith('H')]
text=['# 연구 진행 현황','','- 기준일: 11/24. 연도: 2026.','- 현재: 데이터 분석 산출물 확보, 앱 기본 기능 구현 보고. 실제 모델 평가와 에너지 계산 검증은 수행 예정.','- 12/6 포스터 완성 · 12/7–12/18 연구 중단 · 12/29 성과발표.','',legend,'','## 남은 작업','',table(active),'','## 기존 성과','',table([t for t in tasks if t['id'].startswith('H')]),'','[담당별 상세 작업](docs/TEAM_TASKS.md) · [전체 일정](docs/ROADMAP.md) · [LLM 평가 설계](docs/EVALUATION_PROTOCOL.md)']
(R/'PROGRESS.md').write_text('\n'.join(text)+'\n')
team=['# 담당별 작업과 제출물','','- 기간 표기: 월/일. 연도: 2026.','- 담당자는 작업 결과를 만들고, 검수자는 아래 완료 기준을 확인함.','',legend,'']
for name in ['김선우','임수현','이건희','허재영','전원']:
 team += ['## '+name,'',table([t for t in active if t['owner']==name]),'']
team += ['## 작업별 상세 설명','']
for t in sorted(active,key=key):
 team += [f"### {colors[t['id'][0]]} {t['id']} · {t['title']}",'',f"- **담당 / 검수:** {t['owner']} / {t['reviewer']}.",f"- **기간:** {t['start']}–{t['due']}. **상태:** {labels[t['status']]}.",f"- **목적:** {t['purpose']}",f"- **먼저 필요한 작업:** {deps(t)}.",f"- **준비 자료:** {t['inputs'] or '관련 원문과 현황 보고서'}.",'','**실행 순서**','']
 team += [f'{i}. {s}.' for i,s in enumerate(t['steps'].split('|'),1)]
 team += ['',f"- **제출물:** {t['deliverables']}.",f"- **완료 기준:** {t['acceptance'].rstrip('.')}.",'']
(R/'docs/TEAM_TASKS.md').write_text('\n'.join(team)+'\n')
print('Generated task views:',len(tasks))
