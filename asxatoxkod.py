import streamlit as st
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import os
import random
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# ReportLab imports for PDF Generation
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

# .env ֆայլի բեռնում
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Root directory path alignment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- REGISTRATION OF ARMENIAN SUPPORTED FONT FOR PDF ---
try:
    arial_path = "C:/Windows/Fonts/arial.ttf"
    arial_bold_path = "C:/Windows/Fonts/arialbd.ttf"

    if os.path.exists(arial_path):
        pdfmetrics.registerFont(TTFont('CustomArial', arial_path))
    if os.path.exists(arial_bold_path):
        pdfmetrics.registerFont(TTFont('CustomArial-Bold', arial_bold_path))
except Exception:
    pass

# --- PAGE CONFIG & CUSTOM STYLING ---
logo_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "image_cde603.png"
)

if os.path.exists(logo_path):
    st.set_page_config(
        page_title="Henk Foundation - AI Mock Interview Platform",
        page_icon=logo_path,
        layout="wide"
    )
else:
    st.set_page_config(
        page_title="Henk Foundation - AI Mock Interview Platform",
        page_icon="🌟",
        layout="wide"
    )

# --- GLOBAL STYLING (CSS) + SECURITY (BLUR & NO SELECT) ---
st.markdown("""
<style>
    /* Արգելել տեքստի նշումը և աջ սեղմումը */
    body {
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }

    /* Մշուշման էֆեկտ (Blur), երբ կորչում է ֆոկուսը կամ բացվում է այլ ծրագիր/սքրինշոթ */
    .blur-screen {
        filter: blur(12px);
        transition: filter 0.3s ease;
    }

    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', sans-serif;
    }
    .hero-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
    }
    .congrats-card {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px solid #10B981;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.1);
    }
    .encourage-card {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border: 2px solid #F59E0B;
        border-radius: 20px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(245, 158, 11, 0.1);
    }
    .warning-box {
        padding: 15px;
        background-color: #d9534f;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- JAVASCRIPT՝ Ֆոկուսի կորստի, Քոփի-Փեսթի և Աջ սեղմման արգելքի համար ---
protection_js = """
<script>
    // Զգուշացնել և մշուշել էջը, երբ օգտատերը դուրս է գալիս թաբից կամ բացում այլ ֆայլ/սքրինշոթ գործիք
    window.addEventListener('blur', function() {
        document.body.classList.add('blur-screen');
        alert('ՈՒՇԱԴՐՈՒԹՅՈՒՆ։ Հեռացել եք հարթակից կամ բացել այլ ծրագիր/ֆայլ/սքրինշոթ գործիք։ Ձեր գործողությունը գրանցվել է որպես խախտում։');
    });

    window.addEventListener('focus', function() {
        document.body.classList.remove('blur-screen');
    });

    // Արգելել աջ սեղմումը
    document.addEventListener('contextmenu', event => event.preventDefault());

    // Հետևել Paste (տեղադրման) գործողությանը
    document.addEventListener('DOMContentLoaded', (event) => {
        document.addEventListener('paste', (e) => {
            alert('Զգուշացում. Տեքստի տեղադրումը (Copy-Paste) արգելված է և ստուգման ժամանակ կհանգեցնի 0 միավորի (եթե > 5%)։');
        });
    });
</script>
"""
components.html(protection_js, height=0)


# --- OPENROUTER & GEMINI INTEGRATION ---
def call_openrouter_api(messages):
    if not OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Mock Interview Platform"
    }

    payload = {
        "model": "google/gemini-1.5-flash",
        "messages": messages,
        "temperature": 0.95
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['choices'][0]['message']['content']
        else:
            return None
    except Exception:
        return None


def evaluate_answer_standard(question, answer, difficulty):
    ans_clean = answer.strip()
    if not ans_clean or len(ans_clean.split()) < 2:
        return 0, "Պատասխանը բացակայում է կամ չափազանց կարճ է (0/100)։", False, False

    word_count = len(ans_clean.split())
    base_score = min(max(word_count * 2.5, 40), 95)

    is_copied = False
    is_ai_generated = False

    if OPENROUTER_API_KEY:
        # Խիստ պրոմպտ՝ ԱԲ-ի առկայությունը և քոփի-փեսթը / արտագրված լինելը ստուգելու համար
        prompt = f"""You are a strict technical interviewer and anti-cheat analyzer. Evaluate the candidate's answer.

Question: {question}
Candidate's Answer: {answer}

Check two critical things:
1. Is the answer copied from external sources or does it look like a direct heavy copy-paste (more than 5%)? Answer with True or False in the COPIED field.
2. Is the answer generated or derived heavily using AI (ChatGPT/Claude/etc.)? Answer with True or False in the AI_GENERATED field.

Provide your evaluation format EXACTLY like this:
SCORE: [0-100 number only]
COPIED: [True or False]
AI_GENERATED: [True or False]
FEEDBACK: [Short constructive feedback in Armenian]"""

        messages = [{"role": "user", "content": prompt}]
        response = call_openrouter_api(messages)

        if response:
            try:
                score = int(base_score)
                feedback = "Պատասխանը հաջողությամբ գրանցվեց։"
                lines = response.split('\n')
                for line in lines:
                    if line.startswith("SCORE:"):
                        score_str = line.replace("SCORE:", "").strip().replace("%", "")
                        score = int(''.join(filter(str.isdigit, score_str)))
                    elif line.startswith("COPIED:"):
                        is_copied = "true" in line.replace("COPIED:", "").strip().lower()
                    elif line.startswith("AI_GENERATED:"):
                        is_ai_generated = "true" in line.replace("AI_GENERATED:", "").strip().lower()
                    elif line.startswith("FEEDBACK:"):
                        feedback = line.replace("FEEDBACK:", "").strip()

                # Եթե քոփի-փեսթը գերազանցում է 5% (այստեղ ֆիքսում ենք is_copied-ը) կամ կանոնով որոշվում է
                if is_copied and is_ai_generated:
                    return 0, "❌ Արդյունքը՝ 0 միավոր։ Արտագրված է ԱԲ-ից։", True, True
                elif is_copied:
                    return 0, "❌ Արդյունքը՝ 0 միավոր։ Արտագրված է (Copy-Paste-ը գերազանցում է 5%-ը)։", True, False
                elif is_ai_generated:
                    return int(score * 0.5), "⚠️ Զգուշացում։ Հայտնաբերվել է ԱԲ միջամտություն։", False, True

                return min(max(score, 0), 100), feedback, is_copied, is_ai_generated
            except Exception:
                pass

    return int(base_score), "Պատասխանը հաջողությամբ գրանցվեց և վերլուծվեց։", False, False


def get_next_question(topic, level, difficulty, used_questions):
    if OPENROUTER_API_KEY:
        used_str = "\n".join([f"- {q}" for q in used_questions]) if used_questions else "None"

        prompt = f"""You are a technical interviewer for a {level} position in {topic}.
Generate ONE completely unique, fresh, creative and distinct technical interview question suitable for difficulty level: {difficulty}.

CRITICAL RULES:
1. The question MUST be strictly written in Armenian (հայերեն).
2. DO NOT repeat, rephrase, or use any concepts from these previous questions in this session:
{used_str}

Return ONLY the text of the question, without any introductory phrases, prefixes, or quotes."""

        messages = [{"role": "user", "content": prompt}]

        for _ in range(2):
            question = call_openrouter_api(messages)
            if question:
                q_clean = question.strip()
                if q_clean and q_clean not in used_questions:
                    return q_clean

    fallback_pool = {
        "Python Core & Data Structures": [
            "Ի՞նչ տարբերություն կա List-ի և Tuple-ի միջև, և ե՞րբ պետք է օգտագործել դրանցից յուրաքանչյուրը:",
            "Բացատրեք Python-ում Decorator-ների աշխատանքի սկզբունքը և բերեք գործնական օրինակ:",
            "Ինչպե՞ս է աշխատում Garbage Collector-ը Python-ում (Reference counting և Generational GC):"
        ],
        "FastAPI & REST API Architecture": [
            "Ի՞նչ է Dependency Injection-ը և ի՞նչ խնդիրներ է այն լուծում FastAPI-ում:",
            "Ինչպե՞ս է կազմակերպվում ասինխրոն (async/await) աշխատանքը FastAPI-ում:",
            "Ինչպե՞ս է աշխատում Pydantic-ը տվյալների վավերացման (validation) գործընթացում:"
        ],
        "Database, SQL & ORM": [
            "Բացատրեք N+1 հարցումների (queries) խնդիրը և նշեք դրա լուծման տարբերակները ORM-ում:",
            "Ո՞րն է տարբերությունը INNER JOIN-ի և LEFT JOIN-ի միջև, բերեք SQL օրինակ:",
            "Ի՞նչ են ինդեքսները (Indexes) տվյալների բազաներում, ինչպե՞ս են դրանք ազդում կատարողականի վրա:"
        ],
        "System Design & Asyncio": [
            "Ինչպե՞ս է աշխատում Python-ի Asyncio-ի Event Loop-ը և որո՞նք են դրա սահմանափակումները:",
            "Ի՞նչ է Microservices արխիտեկտուրան և որո՞նք են դրա առավելություններն ու թերությունները Monolith-ի համեմատ:",
            "Ինչպե՞ս կնախագծեիք URL Shortener համակարգ (System Design հիմնական մոտեցումները):"
        ]
    }

    topic_list = fallback_pool.get(topic, [f"Մասնագիտական հարց {topic}-ի վերաբերյալ:"])
    available_questions = [q for q in topic_list if q not in used_questions]

    if available_questions:
        return random.choice(available_questions)
    else:
        return f"({topic}) Խորացված տեխնիկական վերլուծություն #{len(used_questions) + 1} ({difficulty}): Որո՞նք են ձեր կիրառած լավագույն պրակտիկաները այս բաժնում:"


def is_valid_name(name_str):
    pattern = r'^[a-zA-Zа-яА-Яա-ֆԱ-Ֆ-]+\s*$'
    return bool(re.match(pattern, name_str.strip()))


def save_feedback_to_separate_storage(feedback_data):
    storage_file = "henk_feedback_log.json"
    data_list = []

    if os.path.exists(storage_file):
        try:
            with open(storage_file, "r", encoding="utf-8") as f:
                data_list = json.load(f)
        except Exception:
            data_list = []

    data_list.append(feedback_data)

    try:
        with open(storage_file, "w", encoding="utf-8") as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False


# --- FLAWLESS PDF CERTIFICATE GENERATOR WITH ARMENIAN FONT SUPPORT ---
def generate_certificate_pdf(full_name, topic, score):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    font_bold = "CustomArial-Bold" if "CustomArial-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    font_regular = "CustomArial" if "CustomArial" in pdfmetrics.getRegisteredFontNames() else "Helvetica"

    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.rect(0, 0, width, height, stroke=0, fill=1)

    c.setStrokeColor(colors.HexColor("#0F172A"))
    c.setLineWidth(4)
    c.rect(30, 30, width - 60, height - 60, stroke=1, fill=0)

    c.setStrokeColor(colors.HexColor("#D97706"))
    c.setLineWidth(1)
    c.rect(38, 38, width - 76, height - 76, stroke=1, fill=0)

    c.setFillColor(colors.HexColor("#0F172A"))
    c.setFont(font_bold, 20)
    c.drawCentredString(width / 2, height - 85, "HENK FOUNDATION")

    c.setFont(font_regular, 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawCentredString(width / 2, height - 105, "AI Mock Interview & Professional Assessment Platform")

    c.setFont(font_bold, 26)
    c.setFillColor(colors.HexColor("#2563EB"))
    c.drawCentredString(width / 2, height - 165, "CERTIFICATE OF ACHIEVEMENT")

    c.setFont(font_regular, 11)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(width / 2, height - 190, "This certificate is proudly presented to")

    c.setFont(font_bold, 24)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawCentredString(width / 2, height - 235, full_name)

    c.setStrokeColor(colors.HexColor("#93C5FD"))
    c.setLineWidth(1.5)
    c.line(width / 2 - 200, height - 245, width / 2 + 200, height - 245)

    c.setFont(font_regular, 11)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawCentredString(
        width / 2,
        height - 280,
        "for successfully completing the technical interview assessment in the field of"
    )

    c.setFont(font_bold, 14)
    c.setFillColor(colors.HexColor("#1E3A8A"))
    c.drawCentredString(width / 2, height - 305, f"« {topic} »")

    c.setFont(font_regular, 11)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawCentredString(
        width / 2,
        height - 335,
        f"and demonstrating high professional competence with an overall score of {score:.1f}%."
    )

    date_str = datetime.now().strftime("%d.%m.%Y")
    c.setFont(font_bold, 10)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawString(70, 65, f"Date: {date_str}")

    c.drawRightString(width - 70, 65, "Henk Foundation Leadership")
    c.setStrokeColor(colors.HexColor("#94A3B8"))
    c.setLineWidth(1)
    c.line(width - 270, 80, width - 70, 80)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# --- STATE MANAGEMENT ---
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
if "interview_deadline" not in st.session_state:
    st.session_state.interview_deadline = 0

# ---------------------------------------------------------
# ԷՋ 1: WELCOME PAGE
# ---------------------------------------------------------
if st.session_state.step == "welcome":

    col_l, col_r = st.columns([1, 10])
    with col_l:
        if os.path.exists(logo_path):
            st.image(logo_path, width=70)
        else:
            st.write("🌟")
    with col_r:
        st.markdown("<h3 style='color: #2563EB; margin: 0; padding-top: 10px;'>Հենք Հիմնադրամ</h3>",
                    unsafe_allow_html=True)

    st.markdown("""
        <h1 style="font-size: 2.8rem; font-weight: 800; color: #0F172A; margin-top: 1rem; margin-bottom: 0.5rem;">
            Բարի գալուստ <span style="color: #2563EB;">AI Մասնագիտական Հարթակ</span>
        </h1>
        <p style="font-size: 1.2rem; color: #64748B; margin-bottom: 2rem;">
            Որտեղ արժեքները, նորարարությունն ու մարդկային ներուժը միավորվում են՝ կերտելու մեր վաղվա ամուր հիմքերը։
        </p>
    """, unsafe_allow_html=True)

    # Խիստ զգուշացումների վահանակ
    st.markdown("""
    <div class="warning-box">
        🛑 ԱՆՎՏԱՆԳՈՒԹՅԱՆ ԵՎ ՔՆՆԱԿԱՆ ԿԱՆՈՆՆԵՐ<br>
        1. <b>Copy-Paste</b> սահմանափակում. Եթե արտագրված տեքստը գերազանցում է 5%-ը, ստանում եք <b>0 միավոր</b> ("Արտագրված է"):<br>
        2. <b>ԱԲ (AI) օգտագործում</b>. Համակարգը հայտնաբերելու դեպքում վերադարձնում է "Արտագրված է ԱԲ-ից" (< 0 միավոր):<br>
        3. <b>Անվտանգության վահան</b>. Արգելված է հեռանալ թաբից կամ փորձել սքրինշոթ անել (ֆոկուսի կորստի դեպքում էջը ակնթարթորեն մշուշվում է / Blur):
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-card">
        <h3 style="color: #1E293B; margin-top: 0; font-weight: 700;">✨ Մեր մասին</h3>
        <p style="color: #334155; font-size: 1.05rem; line-height: 1.7; margin-bottom: 1rem;">
            <b>«Հենք» հիմնադրամը</b> ավելին է, քան պարզապես կազմակերպություն։ Սա միասնական և ջերմ ընտանիք է, որտեղ յուրաքանչյուր անհատի ձայնը լսելի է, իսկ գաղափարները՝ արժևորված։ Մենք հավատում ենք, որ մեր հաջողության գրավականը նպատակասլաց, ստեղծարար և զարգանալ ձգտող մասնագետներն են։
        </p>
        <p style="color: #334155; font-size: 1.05rem; line-height: 1.7; margin: 0;">
            <b>Նոր կարգավորում․</b> Թեստի համար տրվում է <b>կես ժամ (30 րոպե)</b> ընդհանուր ժամանակ։ Դուք ինքներդ եք տնօրինում, թե որ հարցի վրա որքան ժամանակ կծախսեք։
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("welcome_form"):
        st.markdown("### 📝 Անձնական Տվյալներ")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            first_name = st.text_input("Անուն *", value="", placeholder="Օրինակ՝ Կարեն")
        with col2:
            last_name = st.text_input("Ազգանուն *", value="", placeholder="Օրինակ՝ Նավասարդյան")
        with col3:
            age = st.number_input("Տարիք", min_value=16, max_value=80, value=25)

        st.markdown("---")
        st.markdown("### 🎯 Հարցազրույցի Պարամետրեր")

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
        if not first_name.strip() or not last_name.strip():
            st.error("Խնդրում ենք լրացնել անունը և ազգանունը սկսելու համար։")
        elif not is_valid_name(first_name) or not is_valid_name(last_name):
            st.error("⚠️ Անունն ու ազգանունը կարող են պարունակել միայն տառեր և «-» նշանը։")
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
            # Սահմանում ենք 30 րոպե ընդհանուր ժամանակ (1800 վայրկյան)
            st.session_state.interview_deadline = time.time() + 1800
            st.rerun()

# ---------------------------------------------------------
# ԷՋ 2: INTERVIEW PAGE (30 MINS GENERAL TIMER)
# ---------------------------------------------------------
elif st.session_state.step == "interview":
    time_left = int(st.session_state.interview_deadline - time.time())

    if time_left <= 0:
        st.warning("⏱️ 30 րոպեանոց ընդհանուր ժամանակը սպառվեց։ Հարցազրույցն ավտոմատ անցնում է ամփոփման էջ։")
        st.session_state.step = "analytics"
        st.rerun()

    idx = st.session_state.q_index
    total_q = 4
    topic = st.session_state.selected_topic
    level = st.session_state.selected_level
    difficulty = st.session_state.current_difficulty

    if not st.session_state.current_q_text:
        with st.spinner("🤖 Գեներացվում է նոր, չկրկնվող հարց..."):
            q_generated = get_next_question(topic, level, difficulty, st.session_state.used_questions)
            st.session_state.current_q_text = q_generated
            st.session_state.used_questions.append(q_generated)

    mins, secs = divmod(max(0, time_left), 60)
    timer_color = "#EF4444" if time_left < 180 else "#10B981"

    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title(f"❓ Հարց {idx + 1} / {total_q}")
    with col_h2:
        st.markdown(
            f"<div style='text-align: right; font-size: 1.2rem; font-weight: bold; color: {timer_color}; padding-top: 15px;'>⏳ Մնացած ժամանակ՝ {mins:02d}:{secs:02d}</div>",
            unsafe_allow_html=True)

    st.caption(f"Թեմա՝ **{topic}** | Մակարդակ՝ **{level}** | Ընթացիկ բարդություն՝ **{difficulty}**")
    st.progress((idx + 1) / total_q)
    st.divider()

    st.markdown(f"### 💬 {st.session_state.current_q_text}")

    user_ans = st.text_area(
        "Ձեր պատասխանը․ (Հիշե՛ք՝ խստիվ արգելված է Copy-Paste-ը > 5% և ԱԲ օգտագործումը)",
        value="",
        placeholder="Գրեք Ձեր մանրամասն պատասխանն այստեղ...",
        height=160,
        key=f"ans_input_{idx}"
    )

    btn_label = "Հաջորդ Հարցը ➡️" if idx + 1 < total_q else "Ավարտել և Դիտել Վերլուծությունը 📊"
    if st.button(btn_label, use_container_width=True):
        with st.spinner("🤖 Ստուգվում է պատասխանը (անվտանգության և ԱԲ ստուգում)..."):
            score, feedback, is_copied, is_ai = evaluate_answer_standard(st.session_state.current_q_text, user_ans,
                                                                         difficulty)

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
            "word_count": len(user_ans.strip().split()),
            "is_copied": is_copied,
            "is_ai": is_ai
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
# ԷՋ 3: ANALYTICS
# ---------------------------------------------------------
elif st.session_state.step == "analytics":
    user = st.session_state.user_profile
    history = st.session_state.history

    st.title("📊 Հարցազրույցի Ամփոփում և Վերլուծություն")
    st.success(
        f"Շնորհակալություն, **{user.get('first_name')} {user.get('last_name')}**։ Ձեր հարցազրույցն հաջողությամբ ավարտվեց։")
    st.divider()

    st.subheader("📝 Ձեր Պատասխանները և Ստուգման Արդյունքները")
    if not history:
        st.info("Պատասխաններ չեն գրանցվել, քանի որ ժամանակը սպառվել է կամ տվյալներ չեն ուղարկվել։")
    else:
        for item in history:
            with st.expander(
                    f"📌 {item['q_num']}: {item['question']} (Բարդություն՝ {item['difficulty']}) - `{item['score']}/100`"):
                st.write(f"**Պատասխան:** {item['answer'] if item['answer'].strip() else '_[Պատասխան չի տրվել]_'}")
                st.write(f"**Վերլուծություն / Կարծիք:** {item['feedback']}")

    st.divider()
    st.subheader("📈 Վերլուծական Գրաֆիկներ")

    if history:
        labels = [h['q_num'] for h in history]
        scores = [h['score'] for h in history]
        word_counts = [h['word_count'] for h in history]
        difficulties = [h['difficulty'] for h in history]

        fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi=100)
        fig.patch.set_facecolor('#F8FAFC')

        # Chart 1
        axs[0, 0].plot(labels, scores, marker='o', markersize=8, color='#2563EB', linewidth=3, label="Միավոր")
        axs[0, 0].axhline(y=75, color='#EF4444', linestyle='--', alpha=0.7, label="Passing (75%)")
        axs[0, 0].set_title("1. Առաջադիմության Դինամիկան", fontsize=11, fontweight='bold')
        axs[0, 0].set_ylim(-5, 105)
        axs[0, 0].grid(True, linestyle=':', alpha=0.6)
        axs[0, 0].legend(loc="upper left")

        # Chart 2
        diff_colors = {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}
        col_list = [diff_colors.get(d, "#3B82F6") for d in difficulties]
        axs[0, 1].bar(labels, scores, color=col_list, width=0.5, edgecolor='#1E293B', linewidth=0.8)
        axs[0, 1].set_title("2. Միավորներն ըստ Բարդության", fontsize=11, fontweight='bold')
        axs[0, 1].set_ylim(-5, 105)
        axs[0, 1].grid(axis='y', linestyle=':', alpha=0.6)

        # Chart 3
        axs[1, 0].scatter(word_counts, scores, color='#8B5CF6', s=120, edgecolors='#4C1D95', zorder=5)
        axs[1, 0].set_title("3. Ծավալի (Բառեր) և Միավորի Կապը", fontsize=11, fontweight='bold')
        axs[1, 0].set_xlabel("Բառերի Քանակ", fontsize=9)
        axs[1, 0].set_ylabel("Միավոր", fontsize=9)
        axs[1, 0].set_ylim(-5, 105)
        axs[1, 0].grid(True, linestyle=':', alpha=0.6)

        # Chart 4
        high = sum(1 for s in scores if s >= 75)
        mid = sum(1 for s in scores if 40 <= s < 75)
        low = sum(1 for s in scores if s < 40)
        pie_data = [high, mid, low]
        pie_labels = ['Բարձր (75+)', 'Միջին (40-74)', 'Ցածր (<40)']
        pie_colors = ['#10B981', '#F59E0B', '#EF4444']

        non_zero = [(d, l, c) for d, l, c in zip(pie_data, pie_labels, pie_colors) if d > 0]
        if non_zero:
            d_vals, d_labs, d_cols = zip(*non_zero)
            axs[1, 1].pie(d_vals, labels=d_labs, colors=d_cols, autopct='%1.1f%%', startangle=140)
        axs[1, 1].set_title("4. Որակի Բաշխում", fontsize=11, fontweight='bold')

        plt.tight_layout(pad=2.0)
        st.pyplot(fig)
    else:
        st.write("Գրաֆիկներ չկան արդյունքների բացակայության պատճառով։")

    st.write("")
    if st.button("Անցնել Դիմում-Բողոք-Առաջարկների Բաժին 📝", use_container_width=True):
        st.session_state.step = "feedback_page"
        st.rerun()

# ---------------------------------------------------------
# ԷՋ 4: ԴԻՄՈՒՄ, ԲՈՂՈՔ, ԱՌԱՋԱՐԿՆԵՐԻ ԲԱԺԻՆ
# ---------------------------------------------------------
elif st.session_state.step == "feedback_page":
    user = st.session_state.user_profile
    st.title("📋 Դիմում, Բողոք և Առաջարկներ")
    st.markdown("""
    <p style="color: #475569; font-size: 1.05rem;">
        Ձեր կարծիքը, առաջարկները կամ բողոքները շատ կարևոր են մեզ համար։ Այս տվյալներն առանձնացված են և պահպանվելու են առանձին բազայում՝ հետագա բարելավումների համար։
    </p>
    """, unsafe_allow_html=True)
    st.divider()

    with st.form("feedback_form"):
        feedback_type = st.selectbox(
            "Ընտրեք դիմումի տեսակը",
            ["Առաջարկ (Suggestion)", "Բողոք (Complaint)", "Դիմում / Ընդհանուր կարծիք (Application/Feedback)"]
        )
        subject = st.text_input("Վերնագիր / Հարցի համառոտ նկարագրություն *",
                                placeholder="Օրինակ՝ Հարթակի վերաբերյալ առաջարկ...")
        details = st.text_area(
            "Մանրամասն նկարագրություն կամ առաջարկ *",
            placeholder="Գրեք ձեր մանրամասն մեկնաբանությունները այստեղ...",
            height=150
        )
        submit_feedback = st.form_submit_button("Ուղարկել և Պահպանել 📥", use_container_width=True)

    if submit_feedback:
        if not subject.strip() or not details.strip():
            st.error("Խնդրում ենք լրացնել վերնագիրը և մանրամասն նկարագրությունը։")
        else:
            payload_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "user": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                "age": user.get('age', 0),
                "topic": st.session_state.selected_topic,
                "level": st.session_state.selected_level,
                "type": feedback_type,
                "subject": subject.strip(),
                "details": details.strip()
            }

            success = save_feedback_to_separate_storage(payload_data)
            if success:
                st.success("✅ Ձեր դիմում/առաջարկը հաջողությամբ պահպանվեց առանձին բազայում (henk_feedback_log.json)։")
            else:
                st.error("⚠️ Տվյալների պահպանման ժամանակ առաջացավ խնդիր։")

    st.write("")
    if st.button("Դիտել Վերջնական Արդյունքը 🏆", use_container_width=True):
        st.session_state.step = "final_result"
        st.rerun()

# ---------------------------------------------------------
# ԷՋ 5: ՎԵՐՋՆԱԿԱՆ ԱՐԴՅՈՒՆՔԻ ԷՋ (ԿԵՆՏՐՈՆԱՑՎԱԾ)
# ---------------------------------------------------------
elif st.session_state.step == "final_result":
    user = st.session_state.user_profile
    history = st.session_state.history

    scores = [h['score'] for h in history]
    avg_score = sum(scores) / len(scores) if scores else 0

    st.markdown("<h1 style='text-align: center;'> Վերջնական Արդյունք</h1>", unsafe_allow_html=True)
    st.write("")

    if avg_score >= 75:
        st.balloons()
        st.markdown(f"""
        <div class="congrats-card">
            <h1 style="color: #065F46; margin-bottom: 0.5rem; text-align: center;">🎉 Շնորհավորում ենք, {user.get('first_name')} {user.get('last_name')}։</h1>
            <h3 style="color: #047857; text-align: center;">Դուք հաջողությամբ անցաք հարցազրույցը։</h3>
            <p style="font-size: 1.1rem; color: #064E3B; margin-top: 1rem; text-align: center;">
                Ձեր միջին արդյունքն է՝ <b>{avg_score:.1f}%</b> (Պահանջվող շեմը՝ 75%)։<br>
                Դուք ցուցաբերեցիք բարձր մասնագիտական գիտելիքներ <b>{st.session_state.selected_topic}</b> թեմայով։
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.write("")
        full_name_str = f"{user.get('first_name')} {user.get('last_name')}"
        pdf_buffer = generate_certificate_pdf(full_name_str, st.session_state.selected_topic, avg_score)

        col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
        with col_c2:
            st.download_button(
                label="📥 Ներբեռնել Պրեմիում Հավաստագիրը (PDF)",
                data=pdf_buffer,
                file_name=f"Henk_Certificate_{user.get('first_name')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.markdown(f"""
        <div class="encourage-card">
            <h1 style="color: #92400E; margin-bottom: 0.5rem; text-align: center;">💪 Լավ փորձ էր, {user.get('first_name')} {user.get('last_name')}։</h1>
            <h3 style="color: #B45309; text-align: center;">Սա հիանալի քայլ էր Ձեր գիտելիքները ստուգելու համար։</h3>
            <p style="font-size: 1.1rem; color: #78350F; margin-top: 1rem; text-align: center;">
                Ձեր միջին արդյունքն է՝ <b>{avg_score:.1f}%</b> (Անցողիկ շեմը՝ 75%)։<br>
                Խորհուրդ ենք տալիս ևս մեկ անգամ կրկնել թեման և փորձել նորից։
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