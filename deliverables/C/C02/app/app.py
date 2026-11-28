import datetime as dt

import anthropic
import streamlit as st

import logic

st.set_page_config(page_title="BTS 응집공정")


@st.cache_resource(show_spinner="문헌 색인을 준비하는 중… (처음 한 번)")
def library():
    return logic.make_search(logic.load_pages())


def why(e):
    if isinstance(e, anthropic.AuthenticationError):
        return "API 키 인증에 실패했습니다. .env의 키를 확인하세요."
    if isinstance(e, anthropic.APIConnectionError):
        return "Claude API에 연결하지 못했습니다. 인터넷 연결을 확인하세요."
    return f"{type(e).__name__}: {e}"


def md(text):
    # Streamlit 마크다운은 $…$를 수식, ~…~를 취소선으로 그려서 "pH 4~9 … 5.5~7" 같은 범위가 깨진다
    return text.replace("$", r"\$").replace("~", r"\~")


def source_lines(pages):
    return "\n".join(f"- [{p['n']}] {p['title']} — PDF p.{p['page']}" for p in pages)


df = logic.load_jar_tests()
TNAME = {"t5": "5분", "t30": "30분"}

st.title("응집공정 추천")
if logic.jar_hash() != logic.JAR_SHA256:
    st.warning("data/jar_conditions.csv가 D02 기준본(SHA-256 557c98…)과 다릅니다. 결과를 평가·보고에 쓰지 마세요.")
st.caption("Jar Test 실험 데이터와 수처리 문헌을 근거로 응집제 주입량과 목표 pH를 제안합니다.")
# 흰 입력창(#fff)과 배경(#f4f6f7)의 대비가 1.08:1이라 칸이 잘 안 보인다 → 테두리만 진하게.
# #7d8b93은 배경 대비 3.2:1, 입력창 대비 3.5:1 (WCAG 비텍스트 3:1). 테마 색은 그대로 둔다.
st.markdown("<style>[data-baseweb='input'], [data-baseweb='select'] > div, [data-baseweb='textarea']"
            "{border-color:#7d8b93 !important}"
            # 세그먼트 버튼 좌우 여백을 줄여 칸 안에 들어가게 (Streamlit 1.66 button kind 기준)
            "button[kind^='segmented_control']{padding-left:.7rem;padding-right:.7rem}</style>",
            unsafe_allow_html=True)
rec_tab, ask_tab = st.tabs(["원수 → 추천", "문헌 질문"])

with rec_tab:
    # st.form이 아니라 테두리 칸: 폼 안 위젯은 제출 전까지 다시 그려지지 않아, 지역을 바꿔도
    # '두 지역 공통 조건' 체크박스를 바로 켜고 끌 수 없다. 추천·문헌 호출은 여전히 버튼을 눌렀을 때만.
    with st.container(border=True):
        # 필수(①②) → 선택(③④) 순. 같은 성격끼리 한 행, 라벨은 "항목 (단위)", 긴 설명은 ⓘ 툴팁으로.
        st.markdown("**① 원수와 목표** :primary-badge[필수]")
        a, b, c = st.columns(3)
        raw = a.number_input("원수 탁도 (NTU)", min_value=0.1, value=33.0, step=1.0, format="%g")
        goals = {"t5": b.number_input("5분 목표 (NTU 이하)", min_value=0.1, value=None, step=0.5, format="%g",
                                      placeholder="비우면 평가 안 함",
                                      help="5분·30분 중 하나 이상 넣으세요. 넣은 시점을 모두 충족해야 추천합니다."),
                 "t30": c.number_input("30분 목표 (NTU 이하)", min_value=0.1, value=3.0, step=0.5, format="%g",
                                       placeholder="비우면 평가 안 함",
                                       help="5분·30분 중 하나 이상 넣으세요. 넣은 시점을 모두 충족해야 추천합니다.")}

        st.markdown("**② 비교할 Jar Test** :primary-badge[필수]")
        # 선택지가 적은 단일 선택 → 둘 다 세그먼트 (required: 선택 해제로 빈 값이 되지 않게).
        # 지역은 버튼 3개라 1/3 칸에서 넘쳐 가로 스크롤(오른쪽 페이드)이 생겼다 → 칸을 넓히고 wrap=True로
        # 그래도 좁은 화면(태블릿 세로)에서는 잘리지 않고 다음 줄로 넘긴다.
        a, b, _ = st.columns([2, 1, 1])
        site = a.segmented_control("지역", ["언양", "굴화", "두 지역 모두"], default="언양", required=True, wrap=True,
                                   help="다른 지역 실험 결과가 이 원수에 맞는지는 검증되지 않았습니다.")
        both_sites = site == "두 지역 모두"
        # 지역 바로 아래: 두 지역을 볼 때만 의미가 있어 그 외에는 비활성화
        want_common = a.checkbox("두 지역 공통 조건도 찾기", disabled=not both_sites,
                                 help="'두 지역 모두'를 고르면 쓸 수 있습니다. 언양·굴화 모두에서 목표를 충족한 같은 "
                                      "설계조건(목표 pH·투입량 수준)을 찾습니다. 각 지역 자기 원수 실험 기준이며 "
                                      "원수 ±30%는 쓰지 않습니다.") and both_sites  # 체크한 채 지역을 바꿔도 무시
        coag = b.segmented_control("응집제", sorted(df.coag.unique()), default=sorted(df.coag.unique())[0],
                                   required=True, wrap=True,  # 응집제가 데이터에 추가되면 버튼이 늘어난다 (PAC, Alum 등)
                                   help="Jar Test를 한 응집제만 고를 수 있습니다. 다른 응집제는 추가 Jar Test가 필요합니다.")

        st.markdown("**③ 절감 계산** :gray-badge[선택]")
        a, b, _ = st.columns(3)
        cur = a.number_input("현재 운전 주입량 (mg/L)", min_value=0.0, value=None, step=1.0, format="%g",
                             placeholder="예: 60",  # 숫자만 쓰면 입력한 값처럼 보여 비운 채 제출하게 된다
                             help="넣으면 추천 주입량과 비교해 약품·탄소 절감량을 계산합니다.")
        flow = b.number_input("처리유량 (m³/일)", min_value=1.0, value=10000.0, step=1000.0, format="%g")

        st.markdown("**④ 참고 정보** :gray-badge[선택]")
        a, b, c = st.columns([1, 1, 2])
        ph0 = a.number_input("현재 pH", min_value=0.0, max_value=14.0, value=None, step=0.1, format="%g",
                             placeholder="7.2", help="같은 주입량 조건이 여럿이면 이 pH에 가까운 목표 pH를 고릅니다. "
                                                     "문헌 검색에도 씁니다.")
        temp = b.number_input("수온 (℃)", value=None, step=1.0, format="%g", placeholder="18",
                              help="문헌 검색과 설명에만 씁니다.")
        memo = c.text_input("특이사항", placeholder="강우 직후, 조류 발생기", help="문헌 검색과 설명에만 씁니다.")
        submitted = st.button("추천 받기", type="primary", width="stretch")

    goal = {t: v for t, v in goals.items() if v is not None}
    if submitted and not goal:
        st.error("5분 또는 30분 목표 탁도를 하나 이상 넣으세요.")
    elif submitted:
        times = list(goal)
        when = " · ".join(f"{TNAME[t]} ≤ {v:g}" for t, v in goal.items()) + " NTU"
        rows, best = logic.recommend(df, raw, goal, times, coag, None if site == "두 지역 모두" else site, ph0)
        com = logic.common(df, goal, times, coag, ph0) if want_common else None
        cond = ", ".join(filter(None, [
            f"원수 탁도 {raw:g} NTU", f"목표 탁도 {when} (침전 후)", f"응집제 {coag}",
            best is not None and f"추천 주입량 {best.dose:g} mg/L",
            ph0 is not None and f"현재 pH {ph0:g}", temp is not None and f"수온 {temp:g}℃",
            memo.strip() and f"특이사항: {memo.strip()}"]))
        st.session_state.rec = dict(raw=raw, goal=goal, times=times, when=when, coag=coag, site=site, rows=rows,
                                    best=best, cond=cond, cur=cur, flow=flow, com=com)
        st.session_state.decision = None  # 새 추천이면 이전 판단은 지운다

    r = st.session_state.get("rec")
    if r:
        rows, best, times, cur = r["rows"], r["best"], r["times"], r["cur"]
        n = len(rows)
        if r["site"] == "두 지역 모두":
            st.warning("두 지역 실험을 함께 봅니다. 지역 간 전이 가능성은 검증되지 않았으므로 참고용으로만 쓰세요.")
        s = (logic.savings(cur, best.dose, r["flow"], r["coag"])
             if best is not None and cur is not None and cur > best.dose else None)
        a, b = st.columns(2)
        with a.container(border=True):  # 실험 쪽은 로컬 계산이라 문헌 답을 기다리지 않고 먼저 보인다
            st.markdown("**우리 실험 데이터**")
            st.metric("추천 주입량", f"{best.dose:g} mg/L" if best is not None else "—")
            st.caption(f"{best.src} · {r['coag']} · 탁도 실측 "
                       + " · ".join(f"{TNAME[t]} {best[t]:g}" for t in times) + " NTU"
                       if best is not None
                       else f"실험 최대 {rows.dose.max():g} mg/L로도 미달" if n else "비교 실험 없음")
            st.metric("목표 pH", f"{best.ph:.1f}" if best is not None else "—")
            st.caption(f"조정 후 실측 {best.ph_adj:g}" if best is not None else "추천 실험 없음")
        if best is not None:  # 절감 효과도 로컬 계산이라 문헌 칸(b)보다 먼저 그린다. 화면에서는 두 카드 바로 아래
            with st.container(border=True):  # 계산할 수 없어도 칸은 남긴다. 위 카드처럼 —와 이유를 보인다
                st.markdown("**추천대로 조정하면 · 하루 기준**" + (
                    f" ({cur:g} → {best.dose:g} mg/L, {r['flow']:,.0f} m³/일)" if s else ""))
                m1, m2, m3 = st.columns(3)  # a·b는 위 카드 칸이라 다른 이름을 쓴다
                m1.metric("약품 절감", f"{s['kg']:,.1f} kg" if s else "—")
                m2.metric("탄소 절감 (CO₂eq)", f"{s['co2']:,.1f} kg" if s else "—")  # 값에 kgCO₂eq를 다 쓰면 칸에서 잘린다
                m3.metric("전력 환산", f"{s['kwh']:,.0f} kWh" if s else "—")
                st.caption(f"연간 탄소 {s['co2'] * 365 / 1000:,.1f} t · 전력 환산은 같은 탄소를 내는 전력량 · "
                           "계산 방법은 아래 근거 보기" if s
                           else f"현재 주입량 {cur:g} mg/L가 이미 추천({best.dose:g} mg/L) 이하라 줄일 약품이 없습니다."
                           if cur is not None else "위에 현재 운전 주입량을 넣으면 계산합니다.")
        with b.container(border=True):
            st.markdown("**문헌 기준**")
            if "lit" not in r:
                with st.spinner("문헌에서 주입량과 목표 pH를 찾는 중…"):
                    try:
                        r["lit"] = logic.suggest_lit(library(), r["cond"], r["coag"], rows, r["raw"])
                    except Exception as e:  # 인터넷·API가 안 돼도 왼쪽 실험 값은 그대로 보인다
                        r["lit"], r["err"] = None, why(e)
            lit = r["lit"]
            st.metric("주입량", f"{lit['dose']:g} mg/L" if lit and lit["dose"] is not None else "—")
            st.caption(lit["dose_note"] if lit else f"문헌 확인 실패: {r['err']}")
            st.metric("목표 pH", f"{lit['ph']:.1f}" if lit and lit["ph"] is not None else "—")
            st.caption(("문헌 근거" if lit["ph"] is not None else "문헌에 pH 근거 없음") if lit
                       else f"문헌 확인 실패: {r['err']}")

        if not n:
            have = df[(df.coag == r["coag"]) & ((r["site"] == "두 지역 모두") | (df.src == r["site"]))]
            st.error(f"원수 {r['raw']:g} NTU와 비교 가능한 {r['site']} {r['coag']} 실험이 없습니다. " + (
                f"보유 {r['coag']} 실험의 원수 범위는 {have.ntu.min():g}–{have.ntu.max():g} NTU입니다." if len(have)
                else f"보유 실험의 응집제는 {', '.join(df.coag.unique())}뿐입니다.") + " 추가 Jar Test가 필요합니다.")
        elif best is None:
            st.error(f"비교 실험 {n}건 중 목표({r['when']})를 만족한 조건이 없습니다. "
                     "추가 Jar Test가 필요합니다.")
        else:
            k = int(logic.meets(rows, r["goal"], times).sum())
            st.success(f"비교 실험 {n}건 중 {k}건이 목표({r['when']})를 충족했고, 그중 가장 적은 주입량입니다. "
                       f"({logic.TIE_RULE}) · 최소 주입량은 pH 조정 약품을 뺀 기준이라 최소 총비용·탄소를 뜻하지 않습니다.")
            choice = st.segmented_control(
                "운전 판단", ["현재 조건 유지", "추천대로 조정"], key="decision",
                on_change=lambda: st.session_state.update(decided_at=dt.datetime.now().strftime("%H:%M")))
            if choice:
                st.caption(f"✓ {choice} · {st.session_state.decided_at}")

        if r.get("com") is not None:
            both, key = r["com"]
            with st.container(border=True):
                st.markdown("**두 지역 공통 조건** · 각 지역 자기 원수 실험 기준 (지역 간 전이 미검증)")
                if key is None:
                    st.error(f"언양·굴화 모두에서 목표({r['when']})를 충족한 같은 설계조건이 없습니다. 추가 Jar Test가 필요합니다.")
                else:
                    pick = both[both._key == key]
                    st.metric("공통 최소 주입량", f"{pick.dose.max():g} mg/L")
                    st.caption(f"목표 pH {pick.ph.iloc[0]:g} · " + " · ".join(
                        f"{x.src} " + "/".join(f"{TNAME[t]} {x[t]:g}" for t in times) for _, x in pick.iterrows())
                               + " NTU")
                    st.dataframe(both[list(logic.LABELS)].rename(columns=logic.LABELS), hide_index=True)

        if n or lit:
            with st.expander(f"근거 보기 · 실험 {n}건 · 문헌 {len(lit['cited']) if lit else 0}쪽"
                             + (" · 절감 계산" if s else "")):
                if n:
                    lo, hi = r["raw"] * (1 - logic.BAND), r["raw"] * (1 + logic.BAND)
                    st.markdown(f"**Jar Test** · {r['site']} · {r['coag']}, 원수 {lo:.1f}–{hi:.1f} NTU "
                                "(±30%: 검증되지 않은 휴리스틱 기준)")
                    tbl = rows[list(logic.LABELS)].rename(columns=logic.LABELS)
                    ok = logic.meets(rows, r["goal"], times)
                    tbl.insert(9, "판정", ["충족 · 추천" if best is not None and i == best.name
                                         else "충족" if v else "미달" for i, v in ok.items()])
                    st.dataframe(tbl, hide_index=True)
                    par = logic.pareto(rows, times)
                    st.markdown(f"**투입량–잔류 탁도 Pareto** · 위 실험 중 투입량과 최대 잔류 탁도({'·'.join(TNAME[t] for t in times)}"
                                " 중 큰 값)가 둘 다 더 나은 조건이 없는 것 · 목표 충족 여부와 별개")
                    st.dataframe(par[["cid", "src", "dose", "ph", *times]].assign(
                        최대잔류=par[times].max(axis=1)).rename(columns=logic.LABELS), hide_index=True)
                if lit:
                    st.markdown("**문헌**")
                    st.markdown(md(lit["reason"]))
                    st.markdown(source_lines(lit["cited"]))
                if s:
                    st.markdown("**절감 계산** · 약품 제조 탄소만 셉니다 (슬러지·운송 제외)")
                    st.markdown(
                        f"- 약품: ({cur:g} − {best.dose:g}) mg/L × {r['flow']:,.0f} m³/일 = {s['kg']:,.1f} kg/일\n"
                        f"- 탄소: × {logic.CO2_PER_KG[r['coag']]:.4g} kgCO₂eq/kg ({r['coag']}) = {s['co2']:,.1f} kgCO₂eq/일\n"
                        f"- 전력 환산: ÷ {logic.CO2_PER_KWH} kgCO₂eq/kWh = {s['kwh']:,.0f} kWh/일")
                    st.caption("계수 출처 — PAC 1.48 kgCO₂eq/kg: mainext Table 2 · FeCl₃·Alum: INCOPA 응집제 평균 "
                               "0.106 kgCO₂eq/mol(Fe³⁺·Al³⁺)을 무수물 몰질량으로 환산 · "
                               "전력 0.4541 kgCO₂eq/kWh: 2024 국가 전력배출계수(소비단)")

with ask_tab:
    chat = st.session_state.setdefault("chat", [])
    log = st.container(height=450)  # 높이가 고정이라 새 말풍선이 생기면 맨 아래로 스크롤된다
    if q := (st.chat_input("문헌·실험 데이터에 질문 (예: 탁도가 높을 때 FeCl₃의 최적 pH 범위는?)") or "").strip():
        chat.append({"q": q})
    with log:  # 입력창이 탭 안이라 화면 하단에 고정되지 않고 이 칸 바로 아래에 붙는다
        st.chat_message("assistant").markdown("응집공정 문헌과 우리 Jar Test 실험 데이터를 근거로 답합니다. "
                                              "앞 질문에 이어서 물어도 됩니다.")
        for i, m in enumerate(chat):
            st.chat_message("user").markdown(md(m["q"]))
            with st.chat_message("assistant"):
                if "answer" not in m and "err" not in m:  # 새 질문만 묻는다. 이전 턴은 저장한 답을 다시 그린다
                    with st.spinner("문헌과 실험 데이터를 찾는 중…"):
                        try:
                            past = [(p["q"], p["answer"]) for p in chat[:i] if "answer" in p]  # 실패한 턴은 뺀다
                            m["answer"], m["pages"] = logic.ask_literature(library(), df, m["q"], past)
                        except Exception as e:
                            m["err"] = why(e)
                if "err" in m:
                    st.error(f"답변을 만들지 못했습니다. {m['err']}")
                else:
                    st.markdown(md(m["answer"]))
                    st.markdown(source_lines(m["pages"]) or "인용한 문헌 쪽이 없습니다.")
