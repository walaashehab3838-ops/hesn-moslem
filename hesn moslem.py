
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
ADHKAR_API = "https://www.hisnmuslim.com/api/ar/husn_ar.json"

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
# تنسيق الصفحة
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
    color: #16845b;
    font-size: 34px;
    font-weight: bold;
    margin-top: 12px;
}
.subtitle {
    text-align: center;
    color: #b89430;
    font-size: 17px;
    margin-bottom: 24px;
}
.ayah {
    background: rgba(20, 130, 90, 0.08);
    border: 1px solid rgba(20, 130, 90, 0.25);
    border-radius: 14px;
    padding: 18px;
    margin: 12px 0;
    font-size: 24px;
    line-height: 2.1;
    text-align: center;
}
.dhikr-card {
    background: rgba(20, 130, 90, 0.08);
    border: 1px solid rgba(20, 130, 90, 0.25);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    font-size: 21px;
    line-height: 2;
    text-align: center;
}
.watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    opacity: 0.12;
    font-size: 28px;
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
    background: linear-gradient(145deg, #12835d, #064e3b);
    color: white;
    border: 3px solid #d4af37;
    box-shadow: 0 5px 18px rgba(0,0,0,.3);
    font-size: 16px;
    font-weight: bold;
}
div.st-key-adhkar_float button:hover {
    background: #15966b;
    color: white;
    border-color: #f2d36b;
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
# تحميل بيانات القرآن
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_surah_list():
    response = requests.get(
        f"{QURAN_API}/surah",
        timeout=20
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise ValueError("تعذر تحميل قائمة السور")
    return data["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def get_surah(number, edition):
    response = requests.get(
        f"{QURAN_API}/surah/{number}/{edition}",
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise ValueError("تعذر تحميل السورة")
    return data["data"]


# =========================
# تحميل الأذكار
# =========================
@st.cache_data(ttl=3600, show_spinner=False)
def get_adhkar():
    errors = []

    # المصدر الأساسي
    for url in [
        ADHKAR_API,
        "https://www.hisnmuslim.com/api/ar/husn_ar.json",
    ]:
        try:
            response = requests.get(
                url,
                timeout=25,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()
            data = response.json()
            records = []

            # يدعم صيغ JSON المختلفة
            def walk(obj, category="أذكار متنوعة"):
                if isinstance(obj, list):
                    for item in obj:
                        walk(item, category)
                    return

                if not isinstance(obj, dict):
                    return

                title = (
                    obj.get("category")
                    or obj.get("TITLE")
                    or obj.get("title")
                    or obj.get("ARABIC_TITLE")
                    or obj.get("name")
                    or category
                )

                # الصيغة الشائعة: category + array
                if isinstance(obj.get("array"), list):
                    for item in obj["array"]:
                        if isinstance(item, dict):
                            text = (
                                item.get("text")
                                or item.get("ARABIC_TEXT")
                                or item.get("TEXT")
                                or item.get("content")
                            )
                            if isinstance(text, str) and text.strip():
                                records.append({
                                    "category": str(title),
                                    "text": text.strip(),
                                    "count": item.get("count", 1),
                                    "reference": item.get("reference", ""),
                                })
                    return

                # صيغ أخرى: نص مباشر داخل العنصر
                text = (
                    obj.get("ARABIC_TEXT")
                    or obj.get("arabic_text")
                    or obj.get("text")
                    or obj.get("TEXT")
                    or obj.get("content")
                )

                if isinstance(text, str) and text.strip():
                    records.append({
                        "category": str(title),
                        "text": text.strip(),
                        "count": obj.get("count", obj.get("REPEAT", 1)),
                        "reference": obj.get("REFERENCE", obj.get("reference", "")),
                    })

                # التعامل مع الحقول المتداخلة
                for key, value in obj.items():
                    if key in {
                        "array", "text", "TEXT", "ARABIC_TEXT",
                        "arabic_text", "content", "count", "REPEAT"
                    }:
                        continue
                    if isinstance(value, (dict, list)):
                        walk(value, str(title))

            walk(data)

            # إزالة التكرارات
            unique = []
            seen = set()
            for item in records:
                key = (item["category"], item["text"])
                if key not in seen:
                    seen.add(key)
                    unique.append(item)

            if unique:
                return unique

            errors.append(f"لم يتم التعرف على تنسيق البيانات من: {url}")

        except Exception as exc:
            errors.append(str(exc))

    raise RuntimeError(
        "تعذر تحميل الأذكار. تأكد من اتصال الإنترنت.\n"
        + "\n".join(errors)
    )


# =========================
# حالة التطبيق
# =========================
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "show_adhkar" not in st.session_state:
    st.session_state.show_adhkar = False

# الزر الدائري الثابت
if st.button("📿\nالأذكار", key="adhkar_float"):
    st.session_state.show_adhkar = not st.session_state.show_adhkar
    if st.session_state.show_adhkar:
        st.session_state.page = "الأذكار"
    else:
        st.session_state.page = "الرئيسية"
    st.rerun()

# القائمة الرئيسية
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
# الصفحة الرئيسية
# =========================
if st.session_state.page == "الرئيسية":
    st.markdown("### أهلاً بك في تطبيق القرآن الكريم وحصن المسلم")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📖 القرآن الكريم")
        st.write("اقرأ سور القرآن الكريم واستمع إلى تلاوات القرّاء.")
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

    st.info("يمكنك أيضًا الضغط على الزر الدائري 📿 الموجود أسفل الصفحة لفتح الأذكار.")

# =========================
# صفحة القرآن
# =========================
elif st.session_state.page == "القرآن الكريم":
    st.subheader("📖 القرآن الكريم")

    try:
        surahs = get_surah_list()
    except Exception as exc:
        st.error(f"تعذر تحميل السور: {exc}")
        st.stop()

    surah_names = [
        f'{s["number"]}. {s["name"]}'
        for s in surahs
    ]

    selected_surah_name = st.selectbox(
        "اختر السورة",
        surah_names
    )
    surah_number = surah_names.index(selected_surah_name) + 1

    reciter_name = st.selectbox(
        "اختر القارئ",
        list(RECITERS.keys())
    )
    edition = RECITERS[reciter_name]

    if st.button("تحميل السورة", type="primary", use_container_width=True):
        st.session_state.loaded_surah = surah_number
        st.session_state.loaded_reciter = edition

    if (
        "loaded_surah" in st.session_state
        and st.session_state.loaded_surah == surah_number
        and st.session_state.loaded_reciter == edition
    ):
        try:
            surah = get_surah(surah_number, edition)
            st.markdown(f"### سورة {surah['name']}")

            ayahs = surah.get("ayahs", [])
            if not ayahs:
                st.warning("لم يتم العثور على آيات السورة.")
            else:
                # عرض الآيات
                for ayah in ayahs:
                    text = html.escape(ayah.get("text", ""))
                    st.markdown(
                        f'<div class="ayah">{text}'
                        f'<br><small>﴿ {ayah["numberInSurah"]} ﴾</small></div>',
                        unsafe_allow_html=True
                    )

                # تشغيل الآيات بالتتابع
                audio_urls = [
                    ayah.get("audio")
                    for ayah in ayahs
                    if ayah.get("audio")
                ]

                if audio_urls:
                    urls_json = json.dumps(audio_urls)
                    components.html(
                        f"""
                        <div dir="rtl" style="text-align:center;
                             font-family:sans-serif;padding:10px">
                          <h3>🎧 استمع إلى السورة كاملة</h3>
                          <audio id="quran-player" controls
                                 style="width:100%;max-width:600px"></audio>
                          <p id="quran-status">اضغط تشغيل لبدء التلاوة</p>
                        </div>
                        <script>
                        const urls = {urls_json};
                        const player = document.getElementById('quran-player');
                        const status = document.getElementById('quran-status');
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
            st.error(f"تعذر تحميل السورة أو التلاوة: {exc}")

# =========================
# صفحة الأذكار
# =========================
elif st.session_state.page == "الأذكار":
    st.subheader("📿 حصن المسلم — جميع الأذكار")

    try:
        with st.spinner("جاري تحميل الأذكار..."):
            adhkar = get_adhkar()

        categories = sorted(set(
            item["category"] for item in adhkar
        ))

        selected_category = st.selectbox(
            "اختر قسم الأذكار",
            ["كل الأذكار"] + categories
        )

        search = st.text_input(
            "🔎 ابحث في الأذكار",
            placeholder="مثال: الصباح، المساء، النوم..."
        )

        filtered = adhkar

        if selected_category != "كل الأذكار":
            filtered = [
                item for item in filtered
                if item["category"] == selected_category
            ]

        if search.strip():
            filtered = [
                item for item in filtered
                if search.strip() in item["text"]
                or search.strip() in item["category"]
            ]

        st.caption(f"عدد الأذكار المعروضة: {len(filtered)}")

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
            current_items = filtered[start:start + page_size]

            for index, item in enumerate(current_items, start=start + 1):
                st.markdown(
                    f"#### {index}. {html.escape(item['category'])}"
                )
                st.markdown(
                    f'<div class="dhikr-card">'
                    f'{html.escape(item["text"])}</div>',
                    unsafe_allow_html=True
                )

                count = item.get("count", 1)
                if count and str(count) not in ("1", "None"):
                    st.caption(f"عدد التكرار: {count}")

                if item.get("reference"):
                    st.caption(f"المرجع: {item['reference']}")

                st.divider()

            st.caption(f"صفحة {int(page_num)} من {total_pages}")

    except Exception as exc:
        st.error("لم نتمكن من تحميل الأذكار من المصدر الخارجي.")
        st.write(str(exc))
        st.info(
            "تأكد من اتصال الإنترنت. إذا استمر الخطأ، "
            "فقد يكون تنسيق المصدر قد تغير."
        )

# =========================
# تذييل الصفحة
# =========================
st.markdown(
    """
    <div style="text-align:center; color:#b89430; padding:25px 0;">
        ★ OMAR MELIGY ★
    </div>
    """,
    unsafe_allow_html=True
)
