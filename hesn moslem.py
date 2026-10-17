
import json
import html
import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================
# إعدادات التطبيق
# =========================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

QURAN_API = "https://api.alquran.cloud/v1"

ADHKAR_SOURCES = [
    "https://raw.githubusercontent.com/nawafalqari/azkar-api/main/azkar.json",
    "https://raw.githubusercontent.com/rn0x/Adhkar-json/master/adhkar.json",
    "https://www.hisnmuslim.com/api/ar/husn_ar.json",
]

RECITERS = {
    "مشاري العفاسي": "ar.alafasy",
    "عبدالرحمن السديس": "ar.abdurrahmaansudais",
    "محمود خليل الحصري": "ar.husary",
    "محمد صديق المنشاوي": "ar.minshawi",
    "عبدالباسط عبدالصمد": "ar.abdulbasitmurattal",
    "أبو بكر الشاطري": "ar.shaatree",
    "ماهر المعيقلي": "ar.mahermuaiqly",
}

# =========================
# التصميم
# =========================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    direction: rtl;
    text-align: right;
}
[data-testid="stSidebar"] {
    direction: rtl;
}
.main-title {
    text-align: center;
    color: #15966b;
    font-size: 32px;
    font-weight: bold;
    margin-top: 15px;
}
.subtitle {
    text-align: center;
    color: #d4af37;
    margin-bottom: 25px;
}
.ayah {
    background: rgba(20,130,90,.08);
    border: 1px solid rgba(20,130,90,.25);
    border-radius: 14px;
    padding: 18px;
    margin: 12px 0;
    font-size: 24px;
    line-height: 2.1;
    text-align: center;
}
.dhikr-card {
    background: rgba(20,130,90,.08);
    border: 1px solid rgba(20,130,90,.25);
    border-radius: 16px;
    padding: 20px;
    margin: 10px 0;
    font-size: 21px;
    line-height: 2;
    text-align: center;
}
.watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%,-50%);
    opacity: .10;
    font-size: 27px;
    font-weight: bold;
    letter-spacing: 4px;
    pointer-events: none;
    z-index: 0;
    white-space: nowrap;
}
div.st-key-adhkar_float button {
    position: fixed;
    right: 22px;
    bottom: 25px;
    z-index: 999999;
    width: 88px;
    height: 88px;
    border-radius: 50%;
    background: linear-gradient(145deg,#15966b,#064e3b);
    color: white;
    border: 4px solid #d4af37;
    box-shadow: 0 5px 18px rgba(0,0,0,.3);
    font-size: 16px;
    font-weight: bold;
}
div.st-key-adhkar_float button:hover {
    background: #087f5b;
    color: white;
}
.stButton button {
    border-radius: 10px;
}
</style>

<div class="watermark">★<br>OMAR MELIGY</div>
<div class="main-title">القرآن الكريم وحصن المسلم</div>
<div class="subtitle">﴿ أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ ﴾</div>
""", unsafe_allow_html=True)

# =========================
# تحميل السور
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_surah_list():
    r = requests.get(f"{QURAN_API}/surah", timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        raise ValueError("تعذر تحميل قائمة السور")
    return data["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def get_surah(number, edition):
    r = requests.get(
        f"{QURAN_API}/surah/{number}/{edition}",
        timeout=30
    )
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 200:
        raise ValueError("تعذر تحميل السورة")
    return data["data"]


# =========================
# قراءة JSON بطريقة تدعم UTF-8 BOM
# =========================
def response_json_utf8(response):
    response.raise_for_status()
    # utf-8-sig يحذف BOM إن وُجدت في بداية الملف
    content = response.content.decode("utf-8-sig")
    return json.loads(content)


# =========================
# استخراج الأذكار من مصادر مختلفة
# =========================
def normalize_adhkar(data):
    records = []

    def add_record(category, text, count=1, reference=""):
        if isinstance(text, str) and text.strip():
            records.append({
                "category": str(category or "أذكار متنوعة"),
                "text": text.strip(),
                "count": count if count not in (None, "") else 1,
                "reference": reference or "",
            })

    def walk(obj, category="أذكار متنوعة"):
        if isinstance(obj, list):
            for item in obj:
                walk(item, category)
            return

        if not isinstance(obj, dict):
            return

        title = (
            obj.get("category")
            or obj.get("title")
            or obj.get("TITLE")
            or obj.get("name")
            or category
        )

        # تنسيق: category / array / text
        if isinstance(obj.get("array"), list):
            for item in obj["array"]:
                if isinstance(item, dict):
                    text = (
                        item.get("text")
                        or item.get("zekr")
                        or item.get("ARABIC_TEXT")
                        or item.get("TEXT")
                        or item.get("content")
                    )
                    add_record(
                        title,
                        text,
                        item.get("count", item.get("repeat", 1)),
                        item.get("reference", item.get("REFERENCE", "")),
                    )
                elif isinstance(item, str):
                    add_record(title, item)
            return

        # تنسيق: title / content / zekr
        if isinstance(obj.get("content"), list):
            for item in obj["content"]:
                if isinstance(item, dict):
                    text = (
                        item.get("zekr")
                        or item.get("text")
                        or item.get("ARABIC_TEXT")
                        or item.get("content")
                    )
                    add_record(
                        title,
                        text,
                        item.get("count", item.get("repeat", 1)),
                        item.get("reference", ""),
                    )
                elif isinstance(item, str):
                    add_record(title, item)
            return

        # نص مباشر داخل العنصر
        text = (
            obj.get("text")
            or obj.get("zekr")
            or obj.get("ARABIC_TEXT")
            or obj.get("arabic_text")
            or obj.get("TEXT")
        )

        if isinstance(text, str):
            add_record(
                title,
                text,
                obj.get("count", obj.get("repeat", obj.get("REPEAT", 1))),
                obj.get("reference", obj.get("REFERENCE", "")),
            )

        # التعامل مع الملفات ذات البنية المتداخلة
        ignored = {
            "text", "zekr", "ARABIC_TEXT", "arabic_text", "TEXT",
            "count", "repeat", "REPEAT", "reference", "REFERENCE",
        }
        for key, value in obj.items():
            if key not in ignored and isinstance(value, (dict, list)):
                walk(value, str(title))

    walk(data)

    # حذف التكرارات
    unique = []
    seen = set()
    for item in records:
        key = (item["category"], item["text"])
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique


@st.cache_data(ttl=3600, show_spinner=False)
def get_adhkar():
    errors = []

    for url in ADHKAR_SOURCES:
        try:
            response = requests.get(
                url,
                timeout=25,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            data = response_json_utf8(response)
            records = normalize_adhkar(data)

            if records:
                return records

            errors.append(f"لم أجد أذكارًا في المصدر: {url}")

        except Exception as exc:
            errors.append(f"{url}: {exc}")

    raise RuntimeError(
        "تعذر تحميل الأذكار من المصادر المتاحة.\n"
        + "\n".join(errors)
    )


# =========================
# حالة التنقل
# =========================
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "show_adhkar" not in st.session_state:
    st.session_state.show_adhkar = False

# الزر الدائري الثابت
if st.button("📿\nالأذكار", key="adhkar_float"):
    if st.session_state.page == "الأذكار":
        st.session_state.page = "الرئيسية"
        st.session_state.show_adhkar = False
    else:
        st.session_state.page = "الأذكار"
        st.session_state.show_adhkar = True
    st.rerun()

# أزرار التنقل
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🏠 الرئيسية", use_container_width=True):
        st.session_state.page = "الرئيسية"
        st.session_state.show_adhkar = False
        st.rerun()

with c2:
    if st.button("📖 القرآن الكريم", use_container_width=True):
        st.session_state.page = "القرآن الكريم"
        st.session_state.show_adhkar = False
        st.rerun()

with c3:
    if st.button("📿 حصن المسلم", use_container_width=True):
        st.session_state.page = "الأذكار"
        st.session_state.show_adhkar = True
        st.rerun()

st.divider()

# =========================
# الرئيسية
# =========================
if st.session_state.page == "الرئيسية":
    st.markdown("### أهلاً بك في تطبيق القرآن الكريم وحصن المسلم")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📖 القرآن الكريم")
        st.write("اقرأ القرآن واستمع إلى تلاوات القرّاء.")
        if st.button("افتح القرآن الكريم", use_container_width=True):
            st.session_state.page = "القرآن الكريم"
            st.rerun()

    with col2:
        st.markdown("#### 📿 حصن المسلم")
        st.write("أذكار الصباح والمساء والنوم والصلاة وغيرها.")
        if st.button("افتح جميع الأذكار", use_container_width=True):
            st.session_state.page = "الأذكار"
            st.session_state.show_adhkar = True
            st.rerun()

    st.info("اضغط على الزر الدائري أسفل الصفحة لفتح الأذكار.")

# =========================
# القرآن الكريم
# =========================
elif st.session_state.page == "القرآن الكريم":
    st.subheader("📖 القرآن الكريم")

    try:
        surahs = get_surah_list()
    except Exception as exc:
        st.error(f"تعذر تحميل السور: {exc}")
        st.stop()

    names = [f'{s["number"]}. {s["name"]}' for s in surahs]
    selected_name = st.selectbox("اختر السورة", names)
    surah_number = names.index(selected_name) + 1
    reciter_name = st.selectbox("اختر القارئ", list(RECITERS.keys()))
    edition = RECITERS[reciter_name]

    if st.button("تحميل السورة", type="primary", use_container_width=True):
        st.session_state.loaded_surah = surah_number
        st.session_state.loaded_reciter = edition

    if (
        st.session_state.get("loaded_surah") == surah_number
        and st.session_state.get("loaded_reciter") == edition
    ):
        try:
            surah = get_surah(surah_number, edition)
            st.markdown(f"### سورة {surah['name']}")
            ayahs = surah.get("ayahs", [])

            for ayah in ayahs:
                verse = html.escape(ayah.get("text", ""))
                number = ayah.get("numberInSurah", "")
                st.markdown(
                    f'<div class="ayah">{verse}'
                    f'<br><small>﴿ {number} ﴾</small></div>',
                    unsafe_allow_html=True
                )

            audio_urls = [
                ayah.get("audio")
                for ayah in ayahs
                if ayah.get("audio")
            ]

            if audio_urls:
                urls_json = json.dumps(audio_urls)
                components.html(
                    f"""
                    <div dir="rtl" style="text-align:center;padding:10px">
                      <h3>🎧 استمع إلى السورة كاملة</h3>
                      <audio id="player" controls
                             style="width:100%;max-width:600px"></audio>
                      <p id="status">اضغط تشغيل لبدء التلاوة</p>
                    </div>
                    <script>
                    const urls = {urls_json};
                    const player = document.getElementById('player');
                    const status = document.getElementById('status');
                    let current = 0;
                    player.src = urls[0];
                    player.addEventListener('ended', function() {{
                        current++;
                        if (current < urls.length) {{
                            player.src = urls[current];
                            status.textContent =
                                'الآية ' + (current + 1) + ' من ' + urls.length;
                            player.play().catch(() => {{}});
                        }} else {{
                            status.textContent = 'انتهت السورة';
                        }}
                    }});
                    </script>
                    """,
                    height=150
                )

        except Exception as exc:
            st.error(f"تعذر تحميل السورة: {exc}")

# =========================
# حصن المسلم والأذكار
# =========================
elif st.session_state.page == "الأذكار":
    st.subheader("📿 حصن المسلم — الأذكار")

    try:
        with st.spinner("جاري تحميل الأذكار..."):
            adhkar = get_adhkar()

        categories = sorted(set(item["category"] for item in adhkar))

        selected_category = st.selectbox(
            "اختر قسم الأذكار",
            ["كل الأذكار"] + categories
        )

        search = st.text_input(
            "🔎 ابحث في الأذكار",
            placeholder="ابحث عن الصباح أو المساء أو النوم..."
        )

        filtered = adhkar

        if selected_category != "كل الأذكار":
            filtered = [
                item for item in filtered
                if item["category"] == selected_category
            ]

        if search.strip():
            query = search.strip()
            filtered = [
                item for item in filtered
                if query in item["text"] or query in item["category"]
            ]

        st.caption(f"عدد الأذكار: {len(filtered)}")

        if not filtered:
            st.warning("لا توجد أذكار مطابقة للبحث.")
        else:
            page_size = 15
            total_pages = (len(filtered) - 1) // page_size + 1

            page_num = st.number_input(
                "رقم الصفحة",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1
            )

            start = (int(page_num) - 1) * page_size

            for i, item in enumerate(
                filtered[start:start + page_size],
                start=start + 1
            ):
                st.markdown(f"#### {i}. {html.escape(item['category'])}")
                st.markdown(
                    f'<div class="dhikr-card">'
                    f'{html.escape(item["text"])}</div>',
                    unsafe_allow_html=True
                )

                count = item.get("count", 1)
                if str(count) not in ("1", "None", ""):
                    st.caption(f"عدد التكرار: {count}")

                if item.get("reference"):
                    st.caption(f"المرجع: {item['reference']}")

                st.divider()

            st.caption(f"صفحة {int(page_num)} من {total_pages}")

    except Exception as exc:
        st.error("تعذر تحميل الأذكار.")
        st.code(str(exc))
        st.info(
            "تأكد من اتصال الإنترنت. جرّب إعادة تشغيل التطبيق، "
            "وإذا استمر الخطأ أرسل صورة الرسالة."
        )

# =========================
# التذييل
# =========================
st.markdown("""
<div style="text-align:center;color:#d4af37;padding:25px 0;">
    ★ OMAR MELIGY ★
</div>
""", unsafe_allow_html=True)
