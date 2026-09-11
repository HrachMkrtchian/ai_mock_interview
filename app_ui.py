import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import os

# Root directory path alignment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Backend services import
try:
    from app.services import get_next_question, evaluate_answer
except Exception:
    def get_next_question(topic, level, difficulty, used_questions):
        questions_pool = {
            "Easy": [
                f"({topic}) Որոնք են {topic}-ի հիմնական հասկացությունները:",
                f"({topic}) Բացատրեք basic syntax-ը և կիրառության դեպքերը:",
            ],
            "Medium": [
                f"({topic}) Ինչպե՞ս եք գործնականում լուծում {topic}-ի միջին բարդության խնդիրները:",
                f"({topic}) Ինչպե՞ս են կառավարվում memory-ն և error handling-ը:",
            ],
            "Hard": [
                f"({topic}) Նկարագրեք {topic}-ի ներքին մեխանիզմները և optimization-ը:",
                f"({topic}) Ինչպե՞ս կլուծեք high-load և concurrency խնդիրները:",
            ]
        }
        candidates = questions_pool.get(difficulty, questions_pool["Medium"])
        for q in candidates:
            if q not in used_questions:
                return q
        return f"({topic}) Լրացուցիչ խորացված հարց {len(used_questions) + 1} ({difficulty}):"


    def evaluate_answer(question, answer, difficulty):
        ans_clean = answer.strip().lower()
        words = ans_clean.split()
        word_count = len(words)

        if word_count < 3:
            return 0, "Պատասխանը բացակայում է կամ անիմաստ է (0/100)։"

        tech_keywords = [
            "class", "function", "async", "await", "sql", "query", "index",
            "memory", "process", "thread", "api", "rest", "orm", "database",
            "fastapi", "python", "object", "data", "performance", "optimization"
        ]
        found_keywords = [w for w in tech_keywords if w in ans_clean]

        base_score = min(60, len(found_keywords) * 20)

        if word_count >= 20:
            base_score += 30
        elif word_count >= 10:
            base_score += 15

        final_score = min(100, max(0, base_score))

        if final_score < 40:
            feedback = "Պատասխանը թույլ է, չի պարունակում անհրաժեշտ տերմիններ և իմաստային խորություն։"
        elif final_score < 75:
            feedback = "Լավ պատասխան է, բայց կարելի է ավելի շատ մասնագիտական դետալներ ավելացնել։"
        else:
            feedback = "Գերազանց, իմաստալից և մասնագիտորեն հարուստ պատասխան։"

        return final_score, feedback


# 🔥 ԱՆՎԱՆ ԵՎ ԱԶԳԱՆՎԱՆ ՍՏՈՒԳՄԱՆ ՖՈՒՆԿՑԻԱ (Միայն տառեր և -)
def is_valid_name(name_str):
    pattern = r'^[a-zA-Zа-яА-Яա-ֆԱ-Ֆ-]+\s*$'
    return bool(re.match(pattern, name_str.strip()))


st.set_page_config(page_title="AI Mock Interview Platform", page_icon="🤖", layout="wide")

# 🎨 CUSTOM STYLING
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .feature-title {
        font-weight: 600;
        color: #0F172A;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
    .feature-desc {
        font-size: 0.85rem;
        color: #475569;
    }
    .congrats-card {
        background-color: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }
    .encourage-card {
        background-color: #FFFBEB;
        border: 2px solid #F59E0B;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# State Management
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""
if "selected_level" not in st.session_state:
    st.session_state.selected_level = "Mid-level"
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Medium"
if "history" not in st.session_state:
    st.session_state.history = []
if "used_questions" not in st.session_state:
    st.session_state.used_questions = []
if "current_q_text" not in st.session_state:
    st.session_state.current_q_text = ""

# ---------------------------------------------------------
# ԷՋ 1: WELCOME PAGE (ԹԱՐՄԱՑՎԱԾ ՍՏՈՒԳՄԱՄԲ)
# ---------------------------------------------------------
if st.session_state.step == "welcome":
    st.markdown('<div class="main-header">🎯 AI Mock Interview Platform</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Պատրաստվեք ձեր ապագա հարցազրույցին արհեստական բանականության աջակցությամբ</div>',
        unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2rem;">🧠</span>
            <div class="feature-title">Ադապտիվ Բարդություն</div>
            <div class="feature-desc">Հարցերն ավտոմատ փոխվում են ըստ ձեր պատասխանների որակի</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2rem;">🎯</span>
            <div class="feature-title">Թեմատիկ Հարցեր</div>
            <div class="feature-desc">Ընտրեք հենց այն ուղղությունը, որը ցանկանում եք խորացնել</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="feature-card">
            <span style="font-size: 2rem;">📊</span>
            <div class="feature-title">Խորացված Analytics</div>
            <div class="feature-desc">Ստացեք 4 վերլուծական գրաֆիկներ ձեր պատասխաններից հետո</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    with st.form("welcome_form"):
        st.markdown("### 📝 1. Անձնական Տվյալներ")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            first_name = st.text_input("Անուն *", value="", placeholder="Օրինակ՝ Կարեն")
        with col2:
            last_name = st.text_input("Ազգանուն *", value="", placeholder="Օրինակ՝ Նավասարդյան")
        with col3:
            age = st.number_input("Տարիք", min_value=16, max_value=80, value=25)

        st.markdown("---")
        st.markdown("### 🎯 2. Հարցազրույցի Պարամետրեր")

        col_topic, col_level = st.columns(2)
        with col_topic:
            topic = st.selectbox(
                "Մասնագիտական Թեմա",
                [
                    "Python Core & Data Structures",
                    "FastAPI & REST API Architecture",
                    "Database, SQL & ORM",
                    "System Design & Asyncio"
                ]
            )
        with col_level:
            user_level = st.selectbox(
                "Ձեր Մասնագիտական Մակարդակը (Level)",
                [
                    "Junior (0-1 տարի)",
                    "Mid-level (2-4 տարի)",
                    "Senior (5+ տարի)",
                    "Lead / System Architect"
                ]
            )

        st.write("")
        submit_welcome = st.form_submit_button("Սկսել Հարցազրույցը 🚀", use_container_width=True)

    if submit_welcome:
        # 🔥 ՄԻԱՍՆԱԿԱՆ ՈՒՂՂՎԱԾ ՍՏՈՒԳՈՒՄ (ERROR MESSAGE)
        if not first_name.strip() or not last_name.strip():
            st.error("Խնդրում ենք լրացնել անունը և ազգանունը սկսելու համար։")
        elif not is_valid_name(first_name) or not is_valid_name(last_name):
            st.error(
                "⚠️ Անունն ու ազգանունը կարող են պարունակել միայն տառեր և «-» (գծիկ) նշանը։ Դրանք չեն կարող պարունակել թվեր, ստորակետեր, կետադրական կամ այլ հատուկ նշաններ։")
        else:
            initial_diff = "Easy" if "Junior" in user_level else (
                "Hard" if "Senior" in user_level or "Lead" in user_level else "Medium")
            st.session_state.user_profile = {"first_name": first_name.strip(), "last_name": last_name.strip(),
                                             "age": age}
            st.session_state.selected_topic = topic
            st.session_state.selected_level = user_level
            st.session_state.current_difficulty = initial_diff
            st.session_state.step = "interview"
            st.session_state.q_index = 0
            st.session_state.history = []
            st.session_state.used_questions = []
            st.session_state.current_q_text = ""
            st.rerun()

# ---------------------------------------------------------
# ԷՋ 2: INTERVIEW PAGE
# ---------------------------------------------------------
elif st.session_state.step == "interview":
    idx = st.session_state.q_index
    total_q = 4
    topic = st.session_state.selected_topic
    level = st.session_state.selected_level
    difficulty = st.session_state.current_difficulty

    if not st.session_state.current_q_text:
        q_generated = get_next_question(topic, level, difficulty, st.session_state.used_questions)
        st.session_state.current_q_text = q_generated
        st.session_state.used_questions.append(q_generated)

    st.title(f"❓ Հարց {idx + 1} / {total_q}")
    st.caption(f"Թեմա՝ **{topic}** | Մակարդակ՝ **{level}** | Ընթացիկ բարդություն՝ **{difficulty}**")
    st.progress((idx + 1) / total_q)
    st.divider()

    st.markdown(f"#### {st.session_state.current_q_text}")

    user_ans = st.text_area(
        "Ձեր պատասխանը․",
        value="",
        placeholder="Գրեք Ձեր պատասխանն այստեղ...",
        height=160,
        key=f"ans_input_{idx}"
    )

    btn_label = "Հաջորդ Հարցը ➡️" if idx + 1 < total_q else "Ավարտել և Դիտել Վերլուծությունը 📊"
    if st.button(btn_label, use_container_width=True):
        score, feedback = evaluate_answer(st.session_state.current_q_text, user_ans, difficulty)

        if score >= 75:
            next_diff = "Hard"
        elif score >= 40:
            next_diff = "Medium"
        else:
            next_diff = "Easy"

        st.session_state.history.append({
            "q_num": f"Q{idx + 1}",
            "question": st.session_state.current_q_text,
            "answer": user_ans,
            "difficulty": difficulty,
            "score": score,
            "feedback": feedback,
            "char_count": len(user_ans.strip()),
            "word_count": len(user_ans.strip().split())
        })

        st.session_state.current_q_text = ""

        if idx + 1 < total_q:
            st.session_state.q_index += 1
            st.session_state.current_difficulty = next_diff
            st.rerun()
        else:
            st.session_state.step = "analytics"
            st.rerun()

# ---------------------------------------------------------
# ԷՋ 3: ANALYTICS (ԳՐԱՖԻԿՆԵՐ)
# ---------------------------------------------------------
elif st.session_state.step == "analytics":
    user = st.session_state.user_profile
    history = st.session_state.history

    st.title("📊 Հարցազրույցի Ամփոփում և Վերլուծություն")
    st.success(f"Շնորհակալություն, **{user.get('first_name')} {user.get('last_name')}**։ Ձեր հարցազրույցն ավարտված է։")
    st.caption(f"Թեմա՝ **{st.session_state.selected_topic}** | Մակարդակ՝ **{st.session_state.selected_level}**")
    st.divider()

    st.subheader("📝 Ձեր Պատասխանները և Գնահատականները")
    for item in history:
        with st.expander(
                f"📌 {item['q_num']}: {item['question']} (Բարդություն՝ {item['difficulty']}) - `{item['score']}/100`"):
            st.write(f"**Պատասխան:** {item['answer'] if item['answer'].strip() else '_[Պատասխան չի տրվել]_'}")
            st.write(f"**Գնահատական/Կարծիք:** {item['feedback']}")

    st.divider()
    st.subheader("📈 Վերլուծական 4 Բարձրորակ Գրաֆիկները")

    labels = [h['q_num'] for h in history]
    scores = [h['score'] for h in history]
    word_counts = [h['word_count'] for h in history]
    difficulties = [h['difficulty'] for h in history]

    fig, axs = plt.subplots(2, 2, figsize=(13, 9), dpi=100)
    fig.patch.set_facecolor('#FFFFFF')

    # Chart 1: Line
    axs[0, 0].plot(labels, scores, marker='o', markersize=8, color='#2563EB', linewidth=3, label="Միավոր")
    axs[0, 0].axhline(y=75, color='#EF4444', linestyle='--', alpha=0.7, label=" Passing Score (75%)")
    axs[0, 0].set_title("1. Առաջադիմության Դինամիկան", fontsize=12, fontweight='bold', pad=10)
    axs[0, 0].set_ylim(-5, 105)
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend(loc="upper left")

    # Chart 2: Bar
    diff_colors = {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}
    colors = [diff_colors.get(d, "#3B82F6") for d in difficulties]
    bars = axs[0, 1].bar(labels, scores, color=colors, width=0.5, edgecolor='#1E293B', linewidth=0.8)
    axs[0, 1].set_title("2. Միավորներն ըստ Բարդության", fontsize=12, fontweight='bold', pad=10)
    axs[0, 1].set_ylim(-5, 105)
    axs[0, 1].grid(axis='y', linestyle=':', alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        axs[0, 1].text(bar.get_x() + bar.get_width() / 2, yval + 3, f"{int(yval)}", ha='center', va='bottom',
                       fontweight='bold', fontsize=10)

    # Chart 3: Scatter
    axs[1, 0].scatter(word_counts, scores, color='#8B5CF6', s=120, edgecolors='#4C1D95', zorder=5)
    axs[1, 0].plot(word_counts, scores, linestyle=':', color='#A78BFA', alpha=0.7)
    axs[1, 0].set_title("3. Իմաստային Ծավալի (Բառեր) և Միավորի Կապը", fontsize=12, fontweight='bold', pad=10)
    axs[1, 0].set_xlabel("Բառերի Քանակ", fontsize=10)
    axs[1, 0].set_ylabel("Միավոր", fontsize=10)
    axs[1, 0].set_ylim(-5, 105)
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Chart 4: Pie
    high = sum(1 for s in scores if s >= 75)
    mid = sum(1 for s in scores if 40 <= s < 75)
    low = sum(1 for s in scores if s < 40)

    pie_data = [high, mid, low]
    pie_labels = ['Բարձր (75+)', 'Միջին (40-74)', 'Ցածր (<40)']
    pie_colors = ['#10B981', '#F59E0B', '#EF4444']

    non_zero = [(d, l, c) for d, l, c in zip(pie_data, pie_labels, pie_colors) if d > 0]
    if non_zero:
        d_vals, d_labs, d_cols = zip(*non_zero)
        axs[1, 1].pie(d_vals, labels=d_labs, colors=d_cols, autopct='%1.1f%%', startangle=140,
                      textprops=dict(color="black", fontweight='bold'))
    else:
        axs[1, 1].text(0.5, 0.5, "Տվյալներ չկան", ha='center', va='center')
    axs[1, 1].set_title("4. Պատասխանների Որակի Բաշխում", fontsize=12, fontweight='bold', pad=10)

    plt.tight_layout(pad=2.0)
    st.pyplot(fig)

    st.write("")
    if st.button("Տեսնել Վերջնական Արդյունքը և Եզրակացությունը 🏆", use_container_width=True):
        st.session_state.step = "final_result"
        st.rerun()

# ---------------------------------------------------------
# ԷՋ 4: ՎԵՐՋՆԱԿԱՆ ԱՐԴՅՈՒՆՔԻ ԵՎ ՇՆՈՐՀԱՎՈՐԱՆՔԻ ԷՋ
# ---------------------------------------------------------
elif st.session_state.step == "final_result":
    user = st.session_state.user_profile
    history = st.session_state.history

    scores = [h['score'] for h in history]
    avg_score = sum(scores) / len(scores) if scores else 0

    st.title("🏆 Վերջնական Արդյունք")
    st.write("")

    if avg_score >= 75:
        st.balloons()
        st.markdown(f"""
        <div class="congrats-card">
            <h1 style="color: #065F46; margin-bottom: 0.5rem;">🎉 Շնորհավորում ենք, {user.get('first_name')} {user.get('last_name')}։</h1>
            <h3 style="color: #047857;">Դուք հաջողությամբ անցաք Արհեստական Բանականության (AI) փուլը։</h3>
            <p style="font-size: 1.1rem; color: #064E3B; margin-top: 1rem;">
                Ձեր միջին արդյունքն է՝ <b>{avg_score:.1f}%</b> (Պահանջվող շեմը՝ 75%)։<br>
                Դուք ցուցաբերեցիք գերազանց մասնագիտական գիտելիքներ <b>{st.session_state.selected_topic}</b> թեմայով։
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="encourage-card">
            <h1 style="color: #92400E; margin-bottom: 0.5rem;">💪 Լավ փորձ էր, {user.get('first_name')} {user.get('last_name')}։</h1>
            <h3 style="color: #B45309;">Մի՛ հանձնվեք, սա հիանալի քայլ էր Ձեր գիտելիքները ստուգելու համար։</h3>
            <p style="font-size: 1.1rem; color: #78350F; margin-top: 1rem;">
                Ձեր միջին արդյունքն է՝ <b>{avg_score:.1f}%</b> (Անցողիկ շեմը՝ 75%)։<br>
                Խորհուրդ ենք տալիս ևս մեկ անգամ կրկնել <b>{st.session_state.selected_topic}</b> թեմայի հիմնական հասկացությունները և փորձել նորից։
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button("🔄 Սկսել Նոր Հարցազրույց", use_container_width=True):
        st.session_state.step = "welcome"
        st.session_state.q_index = 0
        st.session_state.history = []
        st.session_state.used_questions = []
        st.session_state.current_q_text = ""
        st.rerun()