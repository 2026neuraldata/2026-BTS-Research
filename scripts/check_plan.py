"""Validate the research plan's dates, dependency graph, and source coverage."""
from pathlib import Path
from datetime import date,datetime
import csv,json,sys,re

ROOT=Path(__file__).resolve().parents[1]
def read_csv(p):
    with (ROOT/p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
tasks=read_csv('management/tasks.csv'); by_id={t['id']:t for t in tasks}
cfg=json.loads((ROOT/'config.yaml').read_text(encoding='utf-8'))
errors=[]
def parse_date(s):return datetime.strptime('2026/'+s,'%Y/%m/%d').date()
if len(by_id)!=len(tasks):errors.append('Duplicate task ID')
pause0=parse_date(cfg['dates']['pause_start']);pause1=parse_date(cfg['dates']['pause_end'])
statuses={'planned','in_progress','review','done','blocked','conditional','deferred','artifact_present','reported'}
for t in tasks:
    try: start,end=map(parse_date,[t['start'],t['due']])
    except ValueError: errors.append(f"{t['id']}: invalid date");continue
    if start>end:errors.append(f"{t['id']}: reversed dates")
    if start<=pause1 and end>=pause0:errors.append(f"{t['id']}: overlaps exam pause")
    if t['status'] not in statuses:errors.append(f"{t['id']}: unknown status")
    for k in ['owner','reviewer','deliverables','acceptance','basis']:
        if not t[k].strip():errors.append(f"{t['id']}: missing {k}")
    for dep in filter(None,t['dependencies'].split(';')):
        if dep not in by_id:errors.append(f"{t['id']}: unknown dependency {dep}")
        elif parse_date(by_id[dep]['due'])>parse_date(t['due']):errors.append(f"{t['id']}: dependency due after dependent")
seen=set();active=set()
def visit(id):
    if id in active:errors.append('Dependency cycle: '+id);return
    if id in seen:return
    active.add(id)
    for dep in filter(None,by_id[id]['dependencies'].split(';')):
        if dep in by_id:visit(dep)
    active.remove(id);seen.add(id)
for id in by_id:visit(id)
manifest=read_csv('management/source_manifest.csv')
drive=[x for x in manifest if x['item_type']=='Drive file']
extras=[x for x in manifest if x['item_type']=='ZIP-only file']
if len(drive)!=289 or len(extras)!=4:errors.append('Source coverage differs from 289 Drive + 4 ZIP-only files')
if len({x['drive_file_id'] for x in drive})!=289:errors.append('Duplicate Drive source ID')
if len({x['sha256'] for x in drive})!=253:errors.append('Distinct-byte count differs from 253')
for x in manifest:
    if not re.fullmatch(r'[a-f0-9]{64}',x['sha256']):errors.append('Invalid source hash: '+x['audit_id'])
if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(tasks)} tasks; acyclic dependencies; no exam-period work; 289 Drive + 4 ZIP-only source records.')
