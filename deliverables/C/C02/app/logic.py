"""데이터 로딩, 추천 규칙, 문헌 검색, Claude 호출. UI는 app.py."""
import gzip
import hashlib
import itertools
import json
import re
from pathlib import Path

import anthropic
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "data"
JAR = DATA / "jar_conditions.csv"  # D02 인계본 (GitHub deliverables/D/D02)
JAR_SHA256 = "557c98b75443bb493de8d3d70150bb0a10aa14d35f42e2957264078f3d7d3648"  # docs/DATA_CONTRACT.md 11/27 기준
PAGES = HERE / "literature_pages.json.gz"  # data/*.pdf 쪽별 본문. PDF가 바뀌면 자동으로 다시 만든다.
MODEL = "claude-opus-5-5"
# shortcut: "비교 가능한 실험" = 원수 탁도 ±30% (디자인 그대로). 실험이 늘면 출처·수온 등으로 좁힐 것.
BAND = 0.3

COLS = {"condition_id": "cid", "site": "src", "experiment_date": "date", "initial_ntu": "ntu", "coagulant": "coag",
        "dose_actual_mg_L": "dose", "target_ph": "ph", "measured_ph": "ph_adj", "ntu_5min": "t5",
        "ntu_30min": "t30", "observation_note": "note", "qc_flag": "qc"}
LABELS = {"cid": "조건 ID", "src": "출처", "date": "실험일", "ntu": "원수 NTU", "dose": "주입량 mg/L",
          "ph": "목표 pH", "ph_adj": "조정 후 pH", "t5": "5분 NTU", "t30": "30분 NTU", "note": "특이사항",
          "qc": "QC"}


def jar_hash(path=JAR):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jar_tests(path=JAR):
    """D02 jar_conditions.csv → 조건 1개 = 1행. dose는 실제 투입량을 반올림 없이 쓴다 (명목 dose 사용 금지).
    qc_flag 행도 자동 제외하지 않는다 (DATA_CONTRACT). 실험일 공란은 미기록이며 채우지 않는다."""
    df = pd.read_csv(path, encoding="utf-8-sig")[list(COLS)].rename(columns=COLS)
    df["coag"] = df["coag"].str.strip()
    df["src"] = df["src"].replace({"Eonyang": "언양", "Gulhwa": "굴화"})  # 한국어 화면·질문용 표시명
    df[["date", "note"]] = df[["date", "note"]].fillna("")
    return df


def meets(rows, goal, times):
    """모든 시점에서 탁도가 목표 이하인지, 행별 True/False. goal은 숫자(times 모두 같은 목표)
    또는 시점별 목표 dict(예: {"t5": 5, "t30": 3}; 이때 times = list(goal))."""
    lim = goal if isinstance(goal, dict) else dict.fromkeys(times, goal)
    return (rows[list(lim)] <= pd.Series(lim)).all(axis=1)


def pareto(rows, times):
    """투입량과 선택 시점 최대 잔류 탁도가 둘 다 더 나은 다른 조건이 없는 행 (투입량 순)."""
    worst = rows[times].max(axis=1)
    keep = [i for i in rows.index if not ((rows.dose <= rows.dose[i]) & (worst <= worst[i])
                                          & ((rows.dose < rows.dose[i]) | (worst < worst[i]))).any()]
    return rows.loc[keep].sort_values(["dose", "cid"])


def common(df, goal, times, coag, ph0=None):
    """명시적으로 요청한 경우만: 모든 지역에서 같은 설계조건(목표 pH·명목 dose 수준, condition_id의 지역 뒤 부분)이
    목표를 충족하는 조건 중 최소 투입량. 원수 ±30%는 쓰지 않는다 (지역마다 자기 원수에서 한 실험).
    → (공통 충족 설계조건의 행들, 추천 설계조건 키 또는 None). 동률은 TIE_RULE과 같은 순서."""
    rows = df[df.coag == coag].dropna(subset=times)
    rows = rows.assign(_key=rows.cid.str.split("_", n=1).str[1], _ok=meets(rows, goal, times))
    g = rows.groupby("_key")
    good = g._ok.all() & (g.src.nunique() == df.src.nunique())
    both = rows[rows._key.map(good)].sort_values(["dose", "cid"])
    if both.empty or df.src.nunique() < 2:
        return both.drop(columns=["_ok"]), None
    k = both.assign(_worst=both[times].max(axis=1)).groupby("_key").agg(
        dose=("dose", "max"), ph=("ph", "first"), worst=("_worst", "max"))
    k = k.assign(_cur=(k.ph - ph0).abs() if ph0 is not None else 0, _ph7=(k.ph - 7).abs()).reset_index()
    best = k.sort_values(["dose", "_cur", "worst", "_ph7", "_key"]).iloc[0]["_key"]
    return both.drop(columns=["_ok"]), best


TIE_RULE = "같은 주입량이면 현재 pH에 가까운 목표 pH → 선택 시점 중 최대 잔류 탁도가 낮은 조건 → 목표 pH 7에 가까운 조건"


def recommend(df, raw, goal, times, coag, site=None, ph0=None):
    """같은 응집제·지역에서 원수 ±30% 범위로 한 실험 중, times 모든 시점 탁도가 goal(숫자 또는 시점별 dict) 이하인 최소 주입량 행.
    동률은 TIE_RULE(ph0 없으면 첫 단계 생략). 관측값 사이 보간은 하지 않는다.
    site=None은 두 지역 모두(교차 지역: 지역 간 전이 미검증). (비교 실험, 추천 행), 충족 없으면 추천 행은 None."""
    rows = df[(df.coag == coag) & ((df.ntu - raw).abs() <= raw * BAND)
              & (site is None or df.src == site)].dropna(subset=times)
    rows = rows.sort_values(["dose", "ph"])
    hit = rows[meets(rows, goal, times)]
    keys = {"_cur": (hit.ph - ph0).abs() if ph0 is not None else 0, "_worst": hit[times].max(axis=1),
            "_ph7": (hit.ph - 7).abs()}
    hit = hit.assign(**keys).sort_values(["dose", *keys, "cid"])  # cid: 끝까지 같아도 매번 같은 답
    return rows, (hit.iloc[0].drop(list(keys)) if len(hit) else None)


# 응집제 1 kg(주입량 기준 제품)당 탄소. PAC는 mainext Table 2. FeCl3·Alum은 INCOPA 평균 0.106 kgCO2eq/mol 금속을
# 무수물 몰질량으로 환산 — shortcut: 응집제 전체 평균이라 제조법별 차이(0.013–0.219)는 못 본다. 공급사 LCA가 있으면 교체.
CO2_PER_KG = {"FeCl3": 0.106 / 0.16220, "Alum": 0.106 * 2 / 0.34215, "PAC": 1.48}
CO2_PER_KWH = 0.4541  # 2024 국가 전력배출계수, 소비단 tCO2eq/MWh


def savings(cur, rec, flow, coag):
    """현재 → 추천 주입량(mg/L)으로 바꿀 때 하루 절감량. flow는 m³/일. mg/L × m³ = g."""
    kg = (cur - rec) * flow / 1000
    co2 = kg * CO2_PER_KG[coag]
    return {"kg": kg, "co2": co2, "kwh": co2 / CO2_PER_KWH}


# ---------- 문헌 ----------

def _pdf_signature():
    return [[p.name, p.stat().st_size] for p in sorted(DATA.glob("*.pdf"))]


def load_pages():
    """PDF 쪽별 본문. 처음 한 번만 PDF를 읽고(몇 분) 이후엔 캐시 파일을 쓴다."""
    if PAGES.exists():
        with gzip.open(PAGES, "rt", encoding="utf-8") as f:
            cached = json.load(f)
        if cached["sig"] == _pdf_signature():
            return cached["pages"]
    from pypdf import PdfReader

    pages = []
    for pdf in sorted(DATA.glob("*.pdf")):
        title = pdf.stem.split(" (")[0]
        for i, page in enumerate(PdfReader(pdf).pages, 1):
            try:
                text = page.extract_text() or ""
            except Exception:  # 깨진 쪽 하나 때문에 색인 전체를 잃지 않게
                text = ""
            pages.append({"title": title, "page": i, "text": text})
    with gzip.open(PAGES, "wt", encoding="utf-8") as f:
        json.dump({"sig": _pdf_signature(), "pages": pages}, f)
    return pages


def make_search(pages):
    """영어 검색어 → 관련 쪽 상위 k개 (TF-IDF). 교과서가 영어라 질문은 english_query로 먼저 바꾼다."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    vec = TfidfVectorizer(stop_words="english", sublinear_tf=True, ngram_range=(1, 2), min_df=2, max_df=0.5)
    m = vec.fit_transform(p["text"] for p in pages)

    def search(query, k=8):
        scores = (m @ vec.transform([query]).T).toarray().ravel()
        return [pages[i] for i in scores.argsort()[::-1][:k] if scores[i] > 0]

    return search


# ---------- Claude ----------

SYSTEM = ("너는 정수장 응집공정 운영자를 돕는 수처리 엔지니어다. 주어진 문헌 발췌와 실험 데이터만 근거로 "
          "한국어로 간결하게 답한다. 발췌에 없는 수치나 사실은 만들지 않고, 근거가 부족하면 부족하다고 말한다. "
          "운영자에게 보이는 글에서는 '발췌' 대신 '문헌'이라고 쓰고, 근거가 된 문장 뒤에 [발췌 번호]를 붙인다.")
POINT = {"type": "object", "additionalProperties": False, "required": ["ntu", "dose", "source"],
         "properties": {"ntu": {"type": "number"}, "dose": {"type": "number"}, "source": {"type": "integer"}}}
LIT_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["ph", "reason", "sources", "doses"],
              "properties": {"ph": {"type": "number"}, "reason": {"type": "string"},
                             "sources": {"type": "array", "items": {"type": "integer"}},
                             "doses": {"type": "array", "items": POINT}}}
QA_SCHEMA = {"type": "object", "additionalProperties": False, "required": ["answer", "sources"],
             "properties": {"answer": {"type": "string"},
                            "sources": {"type": "array", "items": {"type": "integer"}}}}


def _client():
    env = HERE / ".env"  # .env 형식이 "API key: sk-ant-..." 라서 키 모양만 찾아 쓴다
    m = re.search(r"sk-ant-[\w-]+", env.read_text(encoding="utf-8")) if env.exists() else None
    return anthropic.Anthropic(api_key=m.group(0) if m else None, timeout=120, max_retries=1)


def _ask(prompt, schema=None, effort="medium"):
    config = {"effort": effort}
    if schema:
        config["format"] = {"type": "json_schema", "schema": schema}
    r = _client().beta.messages.create(
        model=MODEL, max_tokens=16000, system=SYSTEM, output_config=config,
        betas=["server-side-fallback-2026-07-01"], fallbacks="default",  # 거절되면 서버가 다른 모델로 다시 시도
        messages=[{"role": "user", "content": prompt}],
    )
    if r.stop_reason == "refusal":
        raise RuntimeError("모델이 답변을 거절했습니다")
    text = "".join(b.text for b in r.content if b.type == "text")
    return json.loads(text) if schema else text.strip()


def english_queries(text):
    """한국어 → 짧은 영어 검색어 3개. 키워드가 많으면 TF-IDF 순위가 흐려지고(20개일 때 Davis p.267이 22위),
    검색어 하나는 표현에 따라 들쭉날쭉해서(같은 질문에 6위/19위) 표현을 달리한 3개를 함께 쓴다."""
    lines = _ask("다음 내용을 수처리 영어 교과서에서 찾기 위한 영어 검색어 3개를 만들어라. 한 줄에 하나씩, "
                 "각각 핵심 기술 용어 5~8개로, 교과서에 나올 법한 서로 다른 표현을 써라. 설명 없이 3줄만 써라.\n\n"
                 + text, effort="low").splitlines()
    return [q for q in (re.sub(r"^\s*(\d+[.)]|[-•*])\s*", "", line).strip() for line in lines) if q][:3]


def search_all(search, queries, k=10):
    """검색어별 결과를 번갈아 섞어 중복 없이 k쪽. 앞에 둔 검색어의 상위 쪽이 먼저 들어간다."""
    seen, out = set(), []
    for group in itertools.zip_longest(*(search(q) for q in queries)):
        for h in group:
            if h and (h["title"], h["page"]) not in seen:
                seen.add((h["title"], h["page"]))
                out.append(h)
    return out[:k]


def _excerpts(hits):
    return "\n\n".join(f"[{i}] {h['title']} — PDF p.{h['page']}\n{h['text']}" for i, h in enumerate(hits, 1))


def _cited(hits, nums):
    """모델이 고른 발췌 번호 → 해당 쪽. 번호(n)를 남겨 답변 속 [n] 표기와 출처 목록을 맞춘다."""
    return [dict(hits[n - 1], n=n) for n in dict.fromkeys(nums) if 1 <= n <= len(hits)]


COAG_EN = {"FeCl3": "ferric chloride ferric salts", "PAC": "polyaluminum chloride PACl", "Alum": "alum aluminum sulfate"}


def lit_dose(points, raw):
    """문헌 (원수 탁도, 주입량) 점들 → (주입량 또는 None, 설명). 원수 ±30% 안의 문헌값이 있으면 가장 가까운 값을 그대로.
    점 사이 보간·외삽은 하지 않는다: 점마다 pH·평가조건이 같은지 확인할 수 없어서 (DATA_CONTRACT, C02)."""
    pts = sorted((p for p in points if p["ntu"] > 0 and p["dose"] > 0), key=lambda p: p["ntu"])
    if not pts:
        return None, "문헌에 해당 조건의 주입량 없음"
    near = [p for p in pts if abs(p["ntu"] - raw) <= raw * BAND]
    if near:
        p = min(near, key=lambda p: abs(p["ntu"] - raw))
        return p["dose"], f"문헌값 (원수 {p['ntu']:g} NTU) [{p['source']}]"
    return None, (f"문헌 원수 {', '.join(f'{p['ntu']:g}' for p in pts)} NTU 중 ±30% 안의 값이 없음 "
                  "(조건이 다른 문헌값은 보간하지 않음)")


def suggest_lit(search, cond, coag, rows, raw):
    """문헌 기준 목표 pH와 주입량 → dict(ph, reason, cited, dose, dose_note). pH 근거가 없으면 ph=None,
    인용한 쪽이 하나도 없으면 ValueError."""
    # 조건 검색어만 쓰면 강우·수온 같은 말에 묻혀 응집제별 유효 pH 범위 쪽을 놓친다 → 고정 검색어를 맨 앞에 둔다
    en = COAG_EN.get(coag, coag)
    fixed = [f"{en} coagulation effective pH range", f"{en} dosage mg/L turbidity"]
    hits = search_all(search, fixed + english_queries(cond + "\n이 조건에서 응집 최적 pH와 응집제 주입량"))
    table = rows[list(LABELS)].rename(columns=LABELS).to_csv(index=False) if len(rows) else "(없음)"
    out = _ask(f"[운영 조건]\n{cond}\n\n[비교 가능한 Jar Test 결과]\n{table}\n[문헌 발췌]\n{_excerpts(hits)}\n\n"
               "운영 조건에 추천 주입량이 있으면 그 주입량과 함께 운전할 목표 pH 하나를, 없으면 이 조건에서 "
               "우선 검토할 목표 pH 하나를 문헌 발췌를 근거로 제안하라. 문헌 근거가 없으면 ph는 0으로 둬라. "
               "reason은 2~3문장: 왜 그 pH인지 쓰고, 실험 결과와 다르면 그 차이도 밝혀라. "
               f"doses에는 문헌 발췌에 원수 탁도(NTU)와 {coag} 주입량(mg/L)이 함께 적힌 사례만 넣고 "
               "source에 그 발췌 번호를 적어라. 운영 조건·Jar Test 표의 값, 단위가 다른 값, 짐작한 값은 넣지 말고 "
               "없으면 빈 배열로 둬라. "
               "sources에는 실제로 근거로 쓴 발췌 번호만 넣고, 근거가 되는 발췌가 없으면 빈 배열로 둬라.", LIT_SCHEMA)
    # 발췌 본문에 그 숫자가 실제로 있는 점만 쓴다 (실험 표 값을 문헌값으로 옮겨 적는 실수를 막는다)
    points = [p for p in out["doses"] if 1 <= p["source"] <= len(hits)
              and all(f"{v:g}" in hits[p["source"] - 1]["text"] for v in (p["ntu"], p["dose"]))]
    cited = _cited(hits, out["sources"] + [p["source"] for p in points])
    if not cited:
        raise ValueError("문헌에서 근거를 찾지 못했습니다")
    dose, note = lit_dose(points, raw)
    return dict(ph=out["ph"] if 0 < out["ph"] < 14 else None, reason=out["reason"], cited=cited,
                dose=dose, dose_note=note)


CITE = re.compile(r"\s*\[[\d\s,~–-]+\]")  # 답변 속 [1], [2, 3] 같은 발췌 번호


def _history(history):
    """최근 3턴 문답. 발췌 번호는 턴마다 새로 매기므로 이전 답의 [n]은 지운다 (이번 발췌 번호와 헷갈리지 않게)."""
    return "".join(f"질문: {q}\n답: {CITE.sub('', a)}\n\n" for q, a in history[-3:])


# 2026-11-13 / 2026.11.13 · 11/13 · 11월 13일. 연도 없는 "5.5"·"1.9"는 pH·탁도 숫자라 날짜로 보지 않는다.
DATE = re.compile(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})|(?<![\d./])()(\d{1,2})/(\d{1,2})(?![\d/])"
                  r"|()(\d{1,2})\s*월\s*(\d{1,2})\s*일")


def missing_dates(question, dates):
    """질문 속 날짜 중 실험일 기록에 없는 것. 연도가 없으면 월·일만 비교한다."""
    have = {d for d in dates if d}
    out = []
    for g in DATE.findall(question):
        y, m, d = next(g[i:i + 3] for i in (0, 3, 6) if g[i + 1])
        if not (1 <= int(m) <= 12 and 1 <= int(d) <= 31):
            continue
        md = f"-{int(m):02d}-{int(d):02d}"
        if not any(h.endswith(md) and (not y or h.startswith(y)) for h in have):
            out.append(f"{y + '-' if y else ''}{int(m)}-{int(d)}")
    return out


def ask_literature(search, df, question, history=()):
    """채팅 답변 → (답변, 인용한 쪽들). 문헌 발췌(RAG)와 Jar Test 전체를 근거로 쓴다.
    history: 이전 (질문, 답변) 쌍. '그럼 PAC는?' 같은 꼬리 질문도 찾도록 검색어를 만들 때 함께 넘긴다."""
    past = _history(history)
    hits = search_all(search, english_queries(f"[앞 대화 — 맥락으로만 참고]\n{past}[찾을 질문]\n{question}"
                                              if past else question))
    cols = {"coag": "응집제", **LABELS}  # 추천과 달리 응집제를 가리지 않고 전체 실험을 본다
    table = df[list(cols)].rename(columns=cols).to_csv(index=False)
    prev = f"[이전 대화]\n{past}" if past else ""
    gone = missing_dates(question, df.date)
    gone = (f"[날짜 확인] 질문의 날짜 {', '.join(gone)}는 Jar Test 실험일 기록에 없다. 그 날짜의 실험 자료는 "
            "없다고 답하라.\n\n") if gone else ""
    out = _ask(f"{prev}[질문]\n{question}\n\n{gone}[우리 Jar Test 실험 데이터 (비커 1개 = 1행)]\n{table}\n"
               f"[문헌 발췌]\n{_excerpts(hits)}\n\n"
               "이전 대화는 맥락으로만 참고하고, 실험 데이터와 문헌 발췌만 근거로 질문에 답하라. "
               "실험일이 빈 행은 날짜 미기록이다. 날짜를 짐작해 채우거나 다른 날짜의 행을 그 날짜 자료로 쓰지 마라. "
               "실험 데이터를 근거로 든 문장에는 '우리 Jar Test'라고 밝혀라. 둘 다로 답할 수 없으면 그렇다고 말하라. "
               "지금 원수에 넣을 주입량이나 목표 pH를 정해 달라는 질문이면 직접 정하지 말고, 관련 실험 결과를 보여 준 뒤 "
               "'원수 → 추천' 탭에서 확인하라고 안내하라. sources에는 실제로 근거로 쓴 발췌 번호만 넣어라.", QA_SCHEMA)
    return out["answer"], _cited(hits, out["sources"])


if __name__ == "__main__":  # python logic.py → 문헌 캐시를 미리 만들어 둔다
    print(len(load_pages()), "pages cached")
