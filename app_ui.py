import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import os
from app.services.llm_service import LLMService
# Root directory path alignment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

llm_service = LLMService()

# 🌐 ԼԵԶՈՒՆԵՐԻ ԲԱՌԱՐԱՆ (TRANSLATIONS DICTIONARY)
T = {
    "AM": {
        "page_title": "🎯 AI Mock Interview Platform",
        "page_sub": "Պատրաստվեք ձեր ապագա հարցազրույցին արհեստական բանականության աջակցությամբ",
        "feat1_title": "Ադապտիվ Բարդություն",
        "feat1_desc": "Հարցերն ավտոմատ փոխվում են ըստ ձեր պատասխանների որակի",
        "feat2_title": "Թեմատիկ Հարցեր",
        "feat2_desc": "Ընտրեք հենց այն ուղղությունը, որը ցանկանում եք խորացնել",
        "feat3_title": "Խորացված Analytics",
        "feat3_desc": "Ստացեք 4 վերլուծական գրաֆիկներ ձեր պատասխաններից հետո",
        "p1_title1": "📝 1. Անձնական Տվյալներ",
        "p1_fn": "Անուն *",
        "p1_ln": "Ազգանուն *",
        "p1_fn_ph": "Օրինակ՝ Կարեն",
        "p1_ln_ph": "Օրինակ՝ Նավասարդյան",
        "p1_age": "Տարիք",
        "p1_title2": "🎯 2. Հարցազրույցի Պարամետրեր",
        "p1_topic": "Մասնագիտական Թեմա",
        "p1_level": "Ձեր Մասնագիտական Մակարդակը (Level)",
        "btn_start": "Սկսել Հարցազրույցը 🚀",
        "err_empty": "Խնդրում ենք լրացնել անունը և ազգանունը սկսելու համար։",
        "err_invalid": "⚠️ Անունն ու ազգանունը կարող են պարունակել միայն տառեր և «-» (գծիկ) նշանը։ Դրանք չեն կարող պարունակել թվեր, ստորակետեր, կետադրական կամ այլ հատուկ նշաններ։",
        "q_title": "❓ Հարց",
        "q_topic": "Թեմա՝",
        "q_level": "Մակարդակ՝",
        "q_diff": "Ընթացիկ բարդություն՝",
        "q_diff_short": "Բարդություն՝",
        "ans_label": "Ձեր պատասխանը․",
        "ans_ph": "Գրեք Ձեր պատասխանն այստեղ...",
        "btn_next": "Հաջորդ Հարցը ➡️",
        "btn_finish": "Ավարտել և Դիտել Վերլուծությունը 📊",
        "ana_title": "📊 Հարցազրույցի Ամփոփում և Վերլուծություն",
        "ana_thanks": "Շնորհակալություն, **{fname} {lname}**։ Ձեր հարցազրույցն ավարտված է։",
        "ana_sub": "📝 Ձեր Պատասխանները և Գնահատականները",
        "ana_ans": "Պատասխան:",
        "ana_no_ans": "_[Պատասխան չի տրվել]_",
        "ana_fb": "Գնահատական/Կարծիք:",
        "ana_charts": "📈 Վերլուծական 4 Բարձրորակ Գրաֆիկները",
        "ch1": "1. Առաջադիմության Դինամիկան",
        "ch1_leg": "Միավոր",
        "ch1_pass": " Passing Score (75%)",
        "ch2": "2. Միավորներն ըստ Բարդության",
        "ch3": "3. Իմաստային Ծավալի (Բառեր) և Միավորի Կապը",
        "ch3_x": "Բառերի Քանակ",
        "ch3_y": "Միավոր",
        "ch4": "4. Պատասխանների Որակի Բաշխում",
        "ch4_h": "Բարձր (75+)",
        "ch4_m": "Միջին (40-74)",
        "ch4_l": "Ցածր (<40)",
        "ch4_no": "Տվյալներ չկան",
        "btn_res": "Տեսնել Վերջնական Արդյունքը և Եզրակացությունը 🏆",
        "res_title": "🏆 Վերջնական Արդյունք",
        "res_win_title": "🎉 Շնորհավորում ենք, {fname} {lname}։",
        "res_win_sub": "Դուք հաջողությամբ անցաք Արհեստական Բանականության (AI) փուլը։",
        "res_win_p1": "Ձեր միջին արդյունքն է՝ <b>{score:.1f}%</b> (Պահանջվող շեմը՝ 75%)։",
        "res_win_p2": "Դուք ցուցաբերեցիք գերազանց մասնագիտական գիտելիքներ <b>{topic}</b> թեմայով։",
        "res_fail_title": "💪 Լավ փորձ էր, {fname} {lname}։",
        "res_fail_sub": "Մի՛ հանձնվեք, սա հիանալի քայլ էր Ձեր գիտելիքները ստուգելու համար։",
        "res_fail_p1": "Ձեր միջին արդյունքն է՝ <b>{score:.1f}%</b> (Անցողիկ շեմը՝ 75%)։",
        "res_fail_p2": "Խորհուրդ ենք տալիս ևս մեկ անգամ կրկնել <b>{topic}</b> թեմայի հիմնական հասկացությունները և փորձել նորից։",
        "btn_restart": "🔄 Սկսել Նոր Հարցազրույց",
        "q_e1": "({topic}) Որոնք են {topic}-ի հիմնական հասկացությունները:",
        "q_e2": "({topic}) Բացատրեք basic syntax-ը և կիրառության դեպքերը:",
        "q_m1": "({topic}) Ինչպե՞ս եք գործնականում լուծում {topic}-ի միջին բարդության խնդիրները:",
        "q_m2": "({topic}) Ինչպե՞ս են կառավարվում memory-ն և error handling-ը:",
        "q_h1": "({topic}) Նկարագրեք {topic}-ի ներքին մեխանիզմները և optimization-ը:",
        "q_h2": "({topic}) Ինչպե՞ս կլուծեք high-load և concurrency խնդիրները:",
        "q_extra": "({topic}) Լրացուցիչ խորացված հարց {count} ({diff}):",
        "eval_0": "Պատասխանը բացակայում է կամ անիմաստ է (0/100)։",
        "eval_low": "Պատասխանը թույլ է, չի պարունակում անհրաժեշտ տերմիններ և իմաստային խորություն։",
        "eval_mid": "Լավ պատասխան է, բայց կարելի է ավելի շատ մասնագիտական դետալներ ավելացնել։",
        "eval_high": "Գերազանց, իմաստալից և մասնագիտորեն հարուստ պատասխան։",
        "lvl_opt": ["Junior (0-1 տարի)", "Mid-level (2-4 տարի)", "Senior (5+ տարի)", "Lead / System Architect"]
    },
    "RU": {
        "page_title": "🎯 Платформа AI Интервью",
        "page_sub": "Подготовьтесь к будущему интервью с помощью искусственного интеллекта",
        "feat1_title": "Адаптивная Сложность",
        "feat1_desc": "Вопросы автоматически меняются в зависимости от качества ваших ответов",
        "feat2_title": "Тематические Вопросы",
        "feat2_desc": "Выберите именно то направление, которое хотите углубить",
        "feat3_title": "Углубленная Аналитика",
        "feat3_desc": "Получите 4 аналитических графика после ваших ответов",
        "p1_title1": "📝 1. Личные Данные",
        "p1_fn": "Имя *",
        "p1_ln": "Фамилия *",
        "p1_fn_ph": "Например: Иван",
        "p1_ln_ph": "Например: Иванов",
        "p1_age": "Возраст",
        "p1_title2": "🎯 2. Параметры Интервью",
        "p1_topic": "Профессиональная Тема",
        "p1_level": "Ваш Профессиональный Уровень",
        "btn_start": "Начать Интервью 🚀",
        "err_empty": "Пожалуйста, заполните имя и фамилию для начала.",
        "err_invalid": "⚠️ Имя и фамилия могут содержать только буквы и дефис («-»). Не допускаются цифры и другие символы.",
        "q_title": "❓ Вопрос",
        "q_topic": "Тема:",
        "q_level": "Уровень:",
        "q_diff": "Текущая сложность:",
        "q_diff_short": "Сложность:",
        "ans_label": "Ваш ответ:",
        "ans_ph": "Напишите ваш ответ здесь...",
        "btn_next": "Следующий Вопрос ➡️",
        "btn_finish": "Завершить и Посмотреть Аналитику 📊",
        "ana_title": "📊 Итоги и Аналитика Интервью",
        "ana_thanks": "Спасибо, **{fname} {lname}**. Ваше интервью завершено.",
        "ana_sub": "📝 Ваши Ответы и Оценки",
        "ana_ans": "Ответ:",
        "ana_no_ans": "_[Ответ не дан]_",
        "ana_fb": "Оценка/Отзыв:",
        "ana_charts": "📈 4 Аналитических Графика",
        "ch1": "1. Динамика Прогресса",
        "ch1_leg": "Балл",
        "ch1_pass": " Проходной Балл (75%)",
        "ch2": "2. Баллы по Сложности",
        "ch3": "3. Связь Объема (Слова) и Баллов",
        "ch3_x": "Количество Слов",
        "ch3_y": "Балл",
        "ch4": "4. Распределение Качества Ответов",
        "ch4_h": "Высокий (75+)",
        "ch4_m": "Средний (40-74)",
        "ch4_l": "Низкий (<40)",
        "ch4_no": "Нет данных",
        "btn_res": "Посмотреть Итоговый Результат 🏆",
        "res_title": "🏆 Итоговый Результат",
        "res_win_title": "🎉 Поздравляем, {fname} {lname}!",
        "res_win_sub": "Вы успешно прошли этап Искусственного Интеллекта (AI).",
        "res_win_p1": "Ваш средний результат: <b>{score:.1f}%</b> (Требуемый порог: 75%).",
        "res_win_p2": "Вы продемонстрировали отличные знания по теме <b>{topic}</b>.",
        "res_fail_title": "💪 Хорошая попытка, {fname} {lname}!",
        "res_fail_sub": "Не сдавайтесь, это был отличный шаг для проверки ваших знаний.",
        "res_fail_p1": "Ваш средний результат: <b>{score:.1f}%</b> (Проходной порог: 75%).",
        "res_fail_p2": "Рекомендуем еще раз повторить основные концепции темы <b>{topic}</b> и попробовать снова.",
        "btn_restart": "🔄 Начать Новое Интервью",
        "q_e1": "({topic}) Каковы основные концепции {topic}?",
        "q_e2": "({topic}) Объясните basic syntax и случаи использования:",
        "q_m1": "({topic}) Как вы на практике решаете задачи средней сложности в {topic}?",
        "q_m2": "({topic}) Как управляются memory и error handling?",
        "q_h1": "({topic}) Опишите внутренние механизмы и optimization {topic}:",
        "q_h2": "({topic}) Как вы решите проблемы high-load и concurrency?",
        "q_extra": "({topic}) Дополнительный углубленный вопрос {count} ({diff}):",
        "eval_0": "Ответ отсутствует или бессмысленен (0/100).",
        "eval_low": "Ответ слабый, не содержит необходимых терминов и смысловой глубины.",
        "eval_mid": "Хороший ответ, но можно добавить больше профессиональных деталей.",
        "eval_high": "Отличный, осмысленный и профессионально богатый ответ.",
        "lvl_opt": ["Junior (0-1 год)", "Mid-level (2-4 года)", "Senior (5+ лет)", "Lead / System Architect"]
    },
    "EN": {
        "page_title": "🎯 AI Mock Interview Platform",
        "page_sub": "Prepare for your future interview with the help of artificial intelligence",
        "feat1_title": "Adaptive Difficulty",
        "feat1_desc": "Questions automatically change based on the quality of your answers",
        "feat2_title": "Thematic Questions",
        "feat2_desc": "Choose exactly the direction you want to deepen",
        "feat3_title": "Advanced Analytics",
        "feat3_desc": "Get 4 analytical charts after your answers",
        "p1_title1": "📝 1. Personal Information",
        "p1_fn": "First Name *",
        "p1_ln": "Last Name *",
        "p1_fn_ph": "E.g., John",
        "p1_ln_ph": "E.g., Doe",
        "p1_age": "Age",
        "p1_title2": "🎯 2. Interview Parameters",
        "p1_topic": "Professional Topic",
        "p1_level": "Your Professional Level",
        "btn_start": "Start Interview 🚀",
        "err_empty": "Please fill in the first name and last name to start.",
        "err_invalid": "⚠️ First and last name can only contain letters and hyphens («-»). No numbers or special characters are allowed.",
        "q_title": "❓ Question",
        "q_topic": "Topic:",
        "q_level": "Level:",
        "q_diff": "Current difficulty:",
        "q_diff_short": "Difficulty:",
        "ans_label": "Your answer:",
        "ans_ph": "Write your answer here...",
        "btn_next": "Next Question ➡️",
        "btn_finish": "Finish & View Analytics 📊",
        "ana_title": "📊 Interview Summary and Analytics",
        "ana_thanks": "Thank you, **{fname} {lname}**. Your interview is complete.",
        "ana_sub": "📝 Your Answers and Scores",
        "ana_ans": "Answer:",
        "ana_no_ans": "_[No answer provided]_",
        "ana_fb": "Score/Feedback:",
        "ana_charts": "📈 4 High-Quality Analytical Charts",
        "ch1": "1. Progress Dynamics",
        "ch1_leg": "Score",
        "ch1_pass": " Passing Score (75%)",
        "ch2": "2. Scores by Difficulty",
        "ch3": "3. Semantic Volume (Words) vs Score",
        "ch3_x": "Word Count",
        "ch3_y": "Score",
        "ch4": "4. Answer Quality Distribution",
        "ch4_h": "High (75+)",
        "ch4_m": "Medium (40-74)",
        "ch4_l": "Low (<40)",
        "ch4_no": "No data",
        "btn_res": "View Final Result and Conclusion 🏆",
        "res_title": "🏆 Final Result",
        "res_win_title": "🎉 Congratulations, {fname} {lname}!",
        "res_win_sub": "You have successfully passed the Artificial Intelligence (AI) stage.",
        "res_win_p1": "Your average score is: <b>{score:.1f}%</b> (Required threshold: 75%).",
        "res_win_p2": "You demonstrated excellent professional knowledge in the topic of <b>{topic}</b>.",
        "res_fail_title": "💪 Good effort, {fname} {lname}!",
        "res_fail_sub": "Don't give up, this was a great step to test your knowledge.",
        "res_fail_p1": "Your average score is: <b>{score:.1f}%</b> (Passing threshold: 75%).",
        "res_fail_p2": "We recommend reviewing the core concepts of the <b>{topic}</b> topic and trying again.",
        "btn_restart": "🔄 Start New Interview",
        "q_e1": "({topic}) What are the main concepts of {topic}?",
        "q_e2": "({topic}) Explain basic syntax and use cases:",
        "q_m1": "({topic}) How do you practically solve medium-complexity tasks in {topic}?",
        "q_m2": "({topic}) How are memory and error handling managed?",
        "q_h1": "({topic}) Describe the internal mechanisms and optimization of {topic}:",
        "q_h2": "({topic}) How would you solve high-load and concurrency problems?",
        "q_extra": "({topic}) Additional advanced question {count} ({diff}):",
        "eval_0": "Answer is missing or meaningless (0/100).",
        "eval_low": "Answer is weak, lacks necessary terminology and semantic depth.",
        "eval_mid": "Good answer, but more professional details could be added.",
        "eval_high": "Excellent, meaningful, and professionally rich answer.",
        "lvl_opt": ["Junior (0-1 years)", "Mid-level (2-4 years)", "Senior (5+ years)", "Lead / System Architect"]
    }
}



# 🔥 ԱՆՎԱՆ ԵՎ ԱԶԳԱՆՎԱՆ ՍՏՈՒԳՄԱՆ ՖՈՒՆԿՑԻԱ (Միայն տառեր և -)
def is_valid_name(name_str):
    pattern = r'^[a-zA-Zа-яА-Яա-ֆԱ-Ֆ-]+\s*$'
    return bool(re.match(pattern, name_str.strip()))


st.set_page_config(page_title="AI Mock Interview Platform", page_icon="🤖", layout="wide")

# 🌍 ԼԵԶՎԻ ԸՆՏՐՈՒԹՅԱՆ ՀԱՄԱԿԱՐԳ
lang_map = {"Հայերեն": "AM", "Русский": "RU", "English": "EN"}
lang_keys = list(lang_map.keys())

if "lang" not in st.session_state:
    st.session_state.lang = "AM"

current_lang_idx = list(lang_map.values()).index(st.session_state.lang)

col_empty, col_lang = st.columns([9, 1])
with col_lang:
    selected_lang_name = st.selectbox(
        "🌐",
        lang_keys,
        index=current_lang_idx,
        label_visibility="collapsed"
    )
    st.session_state.lang = lang_map[selected_lang_name]

# Ստանում ենք ընթացիկ լեզվի բառարանը
t = T[st.session_state.lang]

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
# ԷՋ 1: WELCOME PAGE
# ---------------------------------------------------------
if st.session_state.step == "welcome":
    st.markdown(f'<div class="main-header">{t["page_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">{t["page_sub"]}</div>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div class="feature-card">
            <span style="font-size: 2rem;">🧠</span>
            <div class="feature-title">{t["feat1_title"]}</div>
            <div class="feature-desc">{t["feat1_desc"]}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="feature-card">
            <span style="font-size: 2rem;">🎯</span>
            <div class="feature-title">{t["feat2_title"]}</div>
            <div class="feature-desc">{t["feat2_desc"]}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div class="feature-card">
            <span style="font-size: 2rem;">📊</span>
            <div class="feature-title">{t["feat3_title"]}</div>
            <div class="feature-desc">{t["feat3_desc"]}</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    with st.form("welcome_form"):
        st.markdown(f"### {t['p1_title1']}")
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            first_name = st.text_input(t["p1_fn"], value="", placeholder=t["p1_fn_ph"])
        with col2:
            last_name = st.text_input(t["p1_ln"], value="", placeholder=t["p1_ln_ph"])
        with col3:
            age = st.number_input(t["p1_age"], min_value=16, max_value=80, value=25)

        st.markdown("---")
        st.markdown(f"### {t['p1_title2']}")

        col_topic, col_level = st.columns(2)
        with col_topic:
            topic = st.selectbox(
                t["p1_topic"],
                [
                    "Python Core & Data Structures",
                    "FastAPI & REST API Architecture",
                    "Database, SQL & ORM",
                    "System Design & Asyncio"
                ]
            )
        with col_level:
            user_level = st.selectbox(
                t["p1_level"],
                t["lvl_opt"]
            )

        st.write("")
        submit_welcome = st.form_submit_button(t["btn_start"], use_container_width=True)

    if submit_welcome:
        if not first_name.strip() or not last_name.strip():
            st.error(t["err_empty"])
        elif not is_valid_name(first_name) or not is_valid_name(last_name):
            st.error(t["err_invalid"])
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


elif st.session_state.step == "interview":
    idx = st.session_state.q_index
    total_q = 4
    topic = st.session_state.selected_topic
    level = st.session_state.selected_level
    difficulty = st.session_state.current_difficulty

    if not st.session_state.current_q_text:
            # Որպես question_id կարող ենք օգտագործել idx + 1 կամ used_questions-ի երկարությունը + 1
        current_q_id = len(st.session_state.used_questions) + 1

        q_generated = llm_service.generate_question(
            role=level,  # կամ level, կախված թե որն է role-ը քո մոտ
            difficulty=difficulty,
            topic=topic,
            question_id=current_q_id,
            lang = st.session_state.get("lang", "AM")
        )
        st.session_state.current_q_text = q_generated.question_text
        st.session_state.used_questions.append(q_generated.question_text)

    st.title(f"{t['q_title']} {idx + 1} / {total_q}")
    st.caption(f"{t['q_topic']} **{topic}** | {t['q_level']} **{level}** | {t['q_diff']} **{difficulty}**")
    st.progress((idx + 1) / total_q)
    st.divider()

    st.markdown(f"#### {st.session_state.current_q_text}")

    user_ans = st.text_area(
        t["ans_label"],
        value="",
        placeholder=t["ans_ph"],
        height=160,
        key=f"ans_input_{idx}"
    )

    btn_label = t["btn_next"] if idx + 1 < total_q else t["btn_finish"]
    if st.button(btn_label, use_container_width=True):

        evaluation = llm_service.evaluate_answer(
            question_text=st.session_state.current_q_text,
            user_answer=user_ans,
            role=level,
            difficulty=difficulty,
            topic=topic
        )

        score = evaluation.score
        feedback = evaluation.feedback

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

    st.title(t["ana_title"])
    st.success(t["ana_thanks"].format(fname=user.get('first_name'), lname=user.get('last_name')))
    st.caption(f"{t['q_topic']} **{st.session_state.selected_topic}** | {t['q_level']} **{st.session_state.selected_level}**")
    st.divider()

    st.subheader(t["ana_sub"])
    for item in history:
        with st.expander(
                f"📌 {item['q_num']}: {item['question']} ({t['q_diff_short']} {item['difficulty']}) - `{item['score']}/100`"):
            st.write(f"**{t['ana_ans']}** {item['answer'] if item['answer'].strip() else t['ana_no_ans']}")
            st.write(f"**{t['ana_fb']}** {item['feedback']}")

    st.divider()
    st.subheader(t["ana_charts"])

    labels = [h['q_num'] for h in history]
    scores = [h['score'] for h in history]
    word_counts = [h['word_count'] for h in history]
    difficulties = [h['difficulty'] for h in history]

    fig, axs = plt.subplots(2, 2, figsize=(13, 9), dpi=100)
    fig.patch.set_facecolor('#FFFFFF')

    # Chart 1: Line
    axs[0, 0].plot(labels, scores, marker='o', markersize=8, color='#2563EB', linewidth=3, label=t["ch1_leg"])
    axs[0, 0].axhline(y=75, color='#EF4444', linestyle='--', alpha=0.7, label=t["ch1_pass"])
    axs[0, 0].set_title(t["ch1"], fontsize=12, fontweight='bold', pad=10)
    axs[0, 0].set_ylim(-5, 105)
    axs[0, 0].grid(True, linestyle=':', alpha=0.6)
    axs[0, 0].legend(loc="upper left")

    # Chart 2: Bar
    diff_colors = {"Easy": "#10B981", "Medium": "#F59E0B", "Hard": "#EF4444"}
    colors = [diff_colors.get(d, "#3B82F6") for d in difficulties]
    bars = axs[0, 1].bar(labels, scores, color=colors, width=0.5, edgecolor='#1E293B', linewidth=0.8)
    axs[0, 1].set_title(t["ch2"], fontsize=12, fontweight='bold', pad=10)
    axs[0, 1].set_ylim(-5, 105)
    axs[0, 1].grid(axis='y', linestyle=':', alpha=0.6)
    for bar in bars:
        yval = bar.get_height()
        axs[0, 1].text(bar.get_x() + bar.get_width() / 2, yval + 3, f"{int(yval)}", ha='center', va='bottom',
                       fontweight='bold', fontsize=10)

    # Chart 3: Scatter
    axs[1, 0].scatter(word_counts, scores, color='#8B5CF6', s=120, edgecolors='#4C1D95', zorder=5)
    axs[1, 0].plot(word_counts, scores, linestyle=':', color='#A78BFA', alpha=0.7)
    axs[1, 0].set_title(t["ch3"], fontsize=12, fontweight='bold', pad=10)
    axs[1, 0].set_xlabel(t["ch3_x"], fontsize=10)
    axs[1, 0].set_ylabel(t["ch3_y"], fontsize=10)
    axs[1, 0].set_ylim(-5, 105)
    axs[1, 0].grid(True, linestyle=':', alpha=0.6)

    # Chart 4: Pie
    high = sum(1 for s in scores if s >= 75)
    mid = sum(1 for s in scores if 40 <= s < 75)
    low = sum(1 for s in scores if s < 40)

    pie_data = [high, mid, low]
    pie_labels = [t["ch4_h"], t["ch4_m"], t["ch4_l"]]
    pie_colors = ['#10B981', '#F59E0B', '#EF4444']

    non_zero = [(d, l, c) for d, l, c in zip(pie_data, pie_labels, pie_colors) if d > 0]
    if non_zero:
        d_vals, d_labs, d_cols = zip(*non_zero)
        axs[1, 1].pie(d_vals, labels=d_labs, colors=d_cols, autopct='%1.1f%%', startangle=140,
                      textprops=dict(color="black", fontweight='bold'))
    else:
        axs[1, 1].text(0.5, 0.5, t["ch4_no"], ha='center', va='center')
    axs[1, 1].set_title(t["ch4"], fontsize=12, fontweight='bold', pad=10)

    plt.tight_layout(pad=2.0)
    st.pyplot(fig)

    st.write("")
    if st.button(t["btn_res"], use_container_width=True):
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

    st.title(t["res_title"])
    st.write("")

    if avg_score >= 75:
        st.balloons()
        st.markdown(f"""
        <div class="congrats-card">
            <h1 style="color: #065F46; margin-bottom: 0.5rem;">{t["res_win_title"].format(fname=user.get('first_name'), lname=user.get('last_name'))}</h1>
            <h3 style="color: #047857;">{t["res_win_sub"]}</h3>
            <p style="font-size: 1.1rem; color: #064E3B; margin-top: 1rem;">
                {t["res_win_p1"].format(score=avg_score)}<br>
                {t["res_win_p2"].format(topic=st.session_state.selected_topic)}
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="encourage-card">
            <h1 style="color: #92400E; margin-bottom: 0.5rem;">{t["res_fail_title"].format(fname=user.get('first_name'), lname=user.get('last_name'))}</h1>
            <h3 style="color: #B45309;">{t["res_fail_sub"]}</h3>
            <p style="font-size: 1.1rem; color: #78350F; margin-top: 1rem;">
                {t["res_fail_p1"].format(score=avg_score)}<br>
                {t["res_fail_p2"].format(topic=st.session_state.selected_topic)}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    if st.button(t["btn_restart"], use_container_width=True):
        st.session_state.step = "welcome"
        st.session_state.q_index = 0
        st.session_state.history = []
        st.session_state.used_questions = []
        st.session_state.current_q_text = ""
        st.rerun()