"""Generate two Markdown views from management/tasks.csv using only stdlib."""
from pathlib import Path
import csv, json, collections

ROOT = Path(__file__).resolve().parents[1]
with (ROOT/'management/tasks.csv').open(encoding='utf-8-sig',newline='') as f:
    tasks = list(csv.DictReader(f))
cfg = json.loads((ROOT/'config.yaml').read_text(encoding='utf-8'))
labels = {'planned':'계획','in_progress':'진행','review':'검수 대기','done':'완료','blocked':'차단','conditional':'조건부','deferred':'보류','artifact_present':'산출물 확인','reported':'구현 보고'}
def esc(s): return str(s).replace('|','/').replace('\n',' ')
def table(items):
    rows=['| ID | 작업 | 담당 | 마감 | 상태 | 선행 작업 |','|---|---|---|---|---|---|']
    for t in items:
        rows.append('| '+' | '.join(esc(x) for x in [t['id'],t['title'],t['owner'],t['due'][5:],labels.get(t['status'],t['status']),t['dependencies'] or '—'])+' |')
    return '\n'.join(rows)
counts=collections.Counter(t['status'] for t in tasks)
text=['# 진행 현황','',f"- 기준일: {cfg['project']['as_of']}임. tasks.csv에서 생성한 문서이며 팀 합의가 확인되지 않은 세부 일정은 계획안임.",'- 기존 확정일: 11/28·29 회의, 12/6 포스터, 12/7–18 연구 중단, 12/29 발표임.','- 앱 기본 기능은 개발 보고서상 구현됨. 실제 앱 소스 확보·실제 모델 비교·공정 계산 검수가 다음 단계임.','', '## 상태','']
text += [f"- {labels[k]}: {v}건임." for k,v in counts.items()]
text += ['', '## 기존 성과', '', table([t for t in tasks if t['stream']=='기존 성과']), '', '## 후속 작업', '', table(sorted([t for t in tasks if t['stream']!='기존 성과'],key=lambda t:(t['due'],t['id']))), '', '## 차단 문제와 회의 결정','', '- 실제 앱 코드·배포 버전, 공정 입력·계수 기준, Gold 원문 검수와 비교 조건 확정이 필요함.','- 추가 실험·DSPy는 입력 확보에 따라 실행 여부를 결정함. 미완료 상태를 성과로 표시하지 않음.','- [결정 목록](docs/DECISIONS.md) · [인수인계](templates/HANDOFF.md) · [일일 기록](templates/DAILY_LOG.md)임.']
(ROOT/'PROGRESS.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
team=['# 담당별 작업·산출물','', '- 기존 담당 근거는 11/19 역할표임. 후속 마감·검수자·통합 담당은 이번 실행 계획안임.','- 책임 담당은 결과를 만들고 검수자는 완료 기준을 확인함. 한 사람이 구현을 모두 기다리지 않도록 각 담당이 CSV/JSON·수식·기대 결과를 함께 전달함.','']
for person in ['김선우','임수현','이건희','허재영','전원']:
    items=[t for t in tasks if t['owner']==person and t['stream']!='기존 성과']
    team += [f'## {person}', '', table(items),'']
team += ['## 작업별 정의','']
for t in tasks:
    if t['stream']=='기존 성과': continue
    team += [f"### {t['id']} · {t['title']}",'',f"- 담당: {t['owner']} / 검수: {t['reviewer']}임.",f"- 기간: {t['start']}–{t['due']} / 상태: {labels[t['status']]} / 우선순위: {t['priority']}임.",f"- 선행 작업: {t['dependencies'] or '없음'}임.",f"- 입력: {t['inputs'] or '관련 원문·현황 문서'}임.",f"- 산출물: {t['deliverables']}임.",f"- 완료 기준: {t['acceptance']}.",f"- 일정·배정 근거: {t['basis']}임.",'']
(ROOT/'docs/TEAM_TASKS.md').write_text('\n'.join(team)+'\n',encoding='utf-8')
print(f'Updated PROGRESS.md and docs/TEAM_TASKS.md from {len(tasks)} tasks.')
