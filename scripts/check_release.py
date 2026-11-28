"""Static checks for the public repository. No network or private evaluation data required.
Run from the complete checkout; --inventory is for an explicitly partial review copy.
--release validates the selected manifest (defaults to the 11/28 C02 submission).
"""
import argparse,csv,fnmatch,hashlib,json,posixpath,re,subprocess,sys
from pathlib import Path
from urllib.parse import unquote,urlsplit
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--release',action='store_true');ap.add_argument('--manifest',default='docs/C02_MANIFEST_20261128.json');ap.add_argument('--inventory',type=Path,help='verified remote path inventory for partial review only');a=ap.parse_args()
errors=[]
def fail(msg):errors.append(msg)
def read(p):return (ROOT/p).read_text(encoding='utf-8-sig')
def jsonfile(p):return json.loads(read(p))
files={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '__pycache__' not in p.relative_to(ROOT).parts}
# On a real checkout inspect tracked files, not local untracked private development files.
if (ROOT/'.git').exists():
 files=set(subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().strip('\0').split('\0'))
 if a.inventory:ap.error('--inventory is only for a partial review copy')
inventory=files|set(json.loads(a.inventory.read_text())) if a.inventory else files
for path in sorted(files):
 name=posixpath.basename(path)
 bad=['questions.jsonl','gold.jsonl','source_page_mapping.csv','scoring_rubric.md','split_manifest.csv','calibration_data.jsonl','calibration_split.csv','*responses.jsonl','*judge_scores.csv','human_scores.csv','human_judge_comparison.csv','pairwise_results.csv','judge_selection_data.jsonl','judge_selection_questions.jsonl','candidate_judge_outputs.jsonl','approved_reference_scores.csv','judge_blind.jsonl','judge_run_log.csv','response_score_differences.csv','run_logs.jsonl','access_control_check.csv','pilot_errors.csv','error_analysis.csv','judge_prompt*.md','judge_comparison.csv','L03_judge_packet_*.md','L03_judge_prompt.md','selection_gold*.md','selection_questions*.md','search_eval.json','eval_search.py','test_logic.py','literature_pages.json.gz','*.zip','*.pem','*.key']
 if any(fnmatch.fnmatchcase(name,x) for x in bad) or (name.startswith('.env') and name!='.env.example') or {'private','raw_sources'}&set(path.split('/')):fail('private/secret candidate path: '+path)
 if path.endswith(('.md','.csv','.json','.yaml','.py','.txt','.toml','.bat')):
  try:s=read(path)
  except (UnicodeError,OSError):fail('unreadable text: '+path);continue
  if re.search(r'(?:sk-ant-[A-Za-z0-9_-]{25,}|sk-proj-[A-Za-z0-9_-]{25,}|AIza[0-9A-Za-z_-]{35})',s):fail('possible credential: '+path)
 if not path.endswith('.md'):continue
 for m in re.finditer(r'\]\(([^\s)]+)\)',s):
  link=m.group(1);u=urlsplit(link);p=unquote(u.path)
  prefix='/2026neuraldata/2026-BTS-Research/'
  if u.netloc=='github.com' and p.startswith(prefix):
   pp=p[len(prefix):].split('/',2)
   if len(pp)<3 or pp[0] not in ('blob','tree') or pp[1]!='main':continue # immutable refs checked separately by release review
   target=pp[2].rstrip('/')
  elif u.scheme or u.netloc or not p:continue
  else:target=posixpath.normpath(posixpath.join(posixpath.dirname(path),p))
  if target not in inventory and not any(x.startswith(target+'/') for x in inventory):fail(f'broken repository link: {path} -> {target}')
# Current instructions: targeted regressions, not an exhaustive semantic proof.
checks={
 'management/tasks.csv':['단체방에는 완료 안내만','팀장 통제 경로로 제출','팀장 전용'],
 'docs/TEAM_TASKS.md':['단체방에는 완료 안내만','비공개 업무는 별도 통제 경로'],
 'docs/EVALUATION_ACCESS_CONTROL.md':['단체방에는 완료 안내','팀장만 비공개 최종 자료 접근'],
 'docs/EVALUATION_PROTOCOL.md':['단체방은 비공개 산출물 완료 안내만','후보/개발자에게 전달 금지','정답이나 근거 누락/오류 1점'],
 'deliverables/L/L01/README.md':['팀장 전용'],
 'deliverables/E/E01/formulas.md':['교반 절감 0(동일 조건 확인 시)','제조량·농도는 다음 주 확인한다.'],
 'deliverables/L/L01/submission_manifest.json':['to public GitHub before evaluation','authorized_evaluation_custodians_only'],
 'deliverables/C/C01/evaluation_handoff.json':['confirm localhost-only presentation']}
for p,phrases in checks.items():
 for phrase in phrases:
  if phrase in read(p):fail('known obsolete instruction: '+p)
# Current meeting instructions only; dated history and immutable manifests excluded.
current_paths=['README.md','config.yaml','management/tasks.csv','docs/TEAM_TASKS.md','docs/ROADMAP.md','docs/DECISIONS.md','docs/DOCUMENT_CONTROL.md','docs/EVALUATION_PROTOCOL.md','docs/PDF_EVIDENCE_SPEC.md','docs/POSTER_PLAN.md','deliverables/C/C01/evaluation_handoff.json','deliverables/L/L02/evaluation_config.json','deliverables/L/L03/judge_config.json']
obsolete=['조건부 DSPy','optional DSPy','optionally optimize with DSPy','DSPy 적용 시','외부 QR 사용 결정 시','QR 사용 여부','직접/간접 활용 조건 확정']
for path in current_paths:
 for phrase in obsolete:
  if phrase in read(path):fail('obsolete meeting instruction: '+path+' : '+phrase)
# Date/dependency validation on current source ledger, works in review copy too.
from datetime import datetime
cfg=jsonfile('config.yaml');year=cfg['project']['year'];tasks=list(csv.DictReader(read('management/tasks.csv').splitlines()));by={t['id']:t for t in tasks}
def dt(s):return datetime.strptime(f'{year}/{s}','%Y/%m/%d').date()
if len(by)!=len(tasks):fail('duplicate task IDs')
allowed={'planned','in_progress','review','done','blocked','conditional','deferred','artifact_present','reported'}
for t in tasks:
 try:
  start,end=dt(t['start']),dt(t['due'])
  if start>end:fail('reversed date: '+t['id'])
  if any(start<=dt(x['end']) and end>=dt(x['start']) for x in cfg['dates']['non_working_periods']):fail('pause overlap: '+t['id'])
  if t['status'] not in allowed:fail('unknown task status: '+t['id'])
  for dep in filter(None,t['dependencies'].split(';')):
   if dep not in by:fail('missing dependency: '+dep)
   elif dt(by[dep]['due'])>end:fail('dependency deadline after task: '+t['id'])
 except (ValueError,KeyError) as e:fail(str(e))
seen=set();visiting=set()
def visit(k):
 if k in visiting:fail('cycle: '+k);return
 if k in seen:return
 visiting.add(k)
 for dep in filter(None,by[k]['dependencies'].split(';')):
  if dep in by:visit(dep)
 visiting.remove(k);seen.add(k)
for k in by:visit(k)
try:subprocess.run([sys.executable,str(ROOT/'scripts/update_trackers.py'),'--check'],check=True)
except subprocess.CalledProcessError:fail('generated task views out of sync')
# Baseline dataset integrity; exact repository paths from current config
for k in ['jar','dictionary']:
 p=cfg['data'][k+'_path'];expected=cfg['data'][k+'_sha256']
 if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=expected:fail('data hash mismatch: '+p)
# Only public corpus paths are accessible here; textbooks checked in authorized internal copies.
corpus=jsonfile('deliverables/L/L02/corpus_manifest.json')
# Actual config has private evaluation file pointers; never demand their presence in public repo.
eval_cfg=jsonfile('deliverables/L/L02/evaluation_config.json')
if cfg['evaluation'].get('dspy_enabled') is not False:fail('DSPy must remain excluded')
if not isinstance(eval_cfg['ready_for_final_run'],bool):fail('invalid execution gate flag')
if a.release:
 m=jsonfile(a.manifest)
 for x in m['replace_files']:
  p=ROOT/x['path']
  if not p.is_file():fail('release file missing: '+x['path']);continue
  b=p.read_bytes();git=hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
  if git!=x['new_git_blob_sha1'] or hashlib.sha256(b).hexdigest()!=x['new_sha256']:fail('release hash mismatch: '+x['path'])
if errors:print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(tasks)} task rows; generated views match; {len(files)} local files inspected; {len(inventory)} repository paths resolved; known conflict and private filename checks passed.')
if a.inventory:print('PARTIAL COPY: missing unchanged remote contents were not scanned locally; inventory validates destinations only.')
print('Static checks only; actual API, permissions, semantic answer leakage, third-party URLs and candidate runtime require separate verification.')
