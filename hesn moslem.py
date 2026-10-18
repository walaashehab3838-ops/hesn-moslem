
import streamlit as st
import requests
import html
import json
import streamlit.components.v1 as components

# ==================================================
# إعدادات التطبيق
# ==================================================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="wide",
)

QURAN_CLOUD = "https://api.alquran.cloud/v1"
QURAN_COM = "https://api.quran.com/api/v4"

RECITERS = {
    "مشاري العفاسي": "Alafasy_128kbps",
    "عبدالرحمن السديس": "Abdurrahmaan_As-Sudais_192kbps",
    "محمود خليل الحصري": "Husary_128kbps",
    "محمد صديق المنشاوي": "Minshawy_Murattal_128kbps",
    "عبدالباسط عبدالصمد": "Abdul_Basit_Murattal_192kbps",
    "أبو بكر الشاطري": "Abu_Bakr_Ash-Shaatree_128kbps",
    "ماهر المعيقلي": "MaherAlMuaiqly128kbps",
}

SURAH_NAMES = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة",
    "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر",
    "النحل", "الإسراء", "الكهف", "مريم", "طه",
    "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان",
    "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر",
    "يس", "الصافات", "ص", "الزمر", "غافر",
    "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية",
    "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
    "الذاريات", "الطور", "النجم", "القمر", "الرحمن",
    "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجمعة", "المنافقون", "التغابن", "الطلاق",
    "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة",
    "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
    "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج",
    "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين",
    "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
    "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس",
]

# ==================================================
# التصميم
# ==================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background: linear-gradient(145deg, #063d2c, #0d6041, #063526);
        color: #fff8df;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #052f23;
        border-left: 1px solid #c5a34a;
    }

    h1, h2, h3, p, label {
        color: #fff8df;
    }

    .hero {
        text-align: center;
        padding: 28px 12px;
        border: 1px solid #c7a84b;
        border-radius: 22px;
        background: linear-gradient(135deg, #0b5038, #063323);
        margin-bottom: 22px;
    }

    .hero h1 {
        color: #f2d780;
        font-family: 'Amiri', serif;
        font-size: 38px;
    }

    .section-title {
        color: #f2d780;
        font-family: 'Amiri', serif;
        text-align: center;
        font-size: 29px;
        margin: 20px 0;
    }

    .reciter-card {
        border: 1px solid #c5a34a;
        border-radius: 16px;
        padding: 18px 10px;
        text-align: center;
        background: rgba(4,43,30,.8);
        margin-bottom: 10px;
    }

    .reciter-name {
        color: #f5d979;
        font-family: 'Amiri', serif;
        font-size: 22px;
        font-weight: bold;
    }

    .ayah-card {
        direction: rtl;
        text-align: center;
        background: rgba(4,44,31,.84);
        border: 1px solid #bda04a;
        border-radius: 16px;
        padding: 20px 14px;
        margin: 12px 0;
        color: #fff8df;
        font-family: 'Amiri', serif;
        font-size: 25px;
        line-height: 2.1;
        overflow-wrap: anywhere;
    }

    .zikr-card {
        direction: rtl;
        text-align: center;
        background: rgba(4,44,31,.84);
        border: 1px solid #bda04a;
        border-radius: 16px;
        padding: 22px 14px;
        margin: 14px 0;
        color: #fff8df;
        font-family: 'Amiri', serif;
        font-size: 23px;
        line-height: 2;
    }

    div.stButton > button {
        width: 100%;
        border: 1px solid #e0c260;
        border-radius: 12px;
        background: #c8a74d;
        color: #103d2b;
        font-weight: 800;
        min-height: 43px;
    }

    div.stButton > button:hover {
        background: #f0d77f;
        color: #063d2c;
        border-color: #f0d77f;
    }

    .footer {
        text-align: center;
        padding: 22px 8px;
        margin-top: 36px;
        color: #f0d77f;
        border-top: 1px solid #bda04a;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# أدوات الاتصال
# ==================================================
def fetch_json(url):
    response = requests.get(
        url,
        timeout=25,
        headers={"User-Agent": "HesnMoslemStreamlit/1.0"},
    )
    response.raise_for_status()
    return response.json()


# ==================================================
# تحميل نص القرآن
# ==================================================
def load_text_from_quran_com(surah_number):
    all_ayahs = []

    for page in range(1, 10):
        url = (
            f"{QURAN_COM}/verses/by_chapter/{surah_number}"
            f"?language=ar&words=false&per_page=50"
            f"&page={page}&fields=text_uthmani"
        )

        result = fetch_json(url)
        verses = result.get("verses", [])

        if not verses:
            break

        for verse in verses:
            verse_key = verse.get("verse_key", "")
            text = verse.get("text_uthmani", "")

            if not text or ":" not in verse_key:
                continue

            try:
                number = int(verse_key.split(":")[-1])
            except ValueError:
                continue

            all_ayahs.append({
                "text": text,
                "numberInSurah": number,
            })

        if len(verses) < 50:
            break

    if not all_ayahs:
        raise ValueError("لم يرجع مصدر Quran.com أي آيات.")

    return {
        "name": SURAH_NAMES[surah_number - 1],
        "ayahs": all_ayahs,
    }


def load_text_from_cloud(surah_number):
    result = fetch_json(
        f"{QURAN_CLOUD}/surah/{surah_number}"
    )

    if result.get("code") != 200:
        raise ValueError("مصدر القرآن الأساسي لم يُرجع استجابة ناجحة.")

    data = result.get("data", {})
    raw_ayahs = data.get("ayahs", [])

    if not raw_ayahs:
        raise ValueError("لم يتم العثور على آيات.")

    return {
        "name": data.get("name", SURAH_NAMES[surah_number - 1]),
        "ayahs": [
            {
                "text": ayah.get("text", ""),
                "numberInSurah": ayah.get("numberInSurah", i + 1),
            }
            for i, ayah in enumerate(raw_ayahs)
            if ayah.get("text")
        ],
    }


@st.cache_data(ttl=3600, show_spinner=False)
def get_surah_text(surah_number):
    errors = []

    try:
        return load_text_from_quran_com(surah_number)
    except Exception as exc:
        errors.append(f"Quran.com: {exc}")

    try:
        return load_text_from_cloud(surah_number)
    except Exception as exc:
        errors.append(f"AlQuran Cloud: {exc}")

    return {
        "error": "\n".join(errors),
        "ayahs": [],
    }


# ==================================================
# روابط الصوت المباشرة
# ==================================================
def get_surah_audio(surah_number, reciter_name, ayah_count):
    folder = RECITERS.get(reciter_name)

    if not folder:
        return []

    # اسم الملف: رقم السورة 3 أرقام + رقم الآية 3 أرقام
    return [
        (
            f"https://everyayah.com/data/{folder}/"
            f"{surah_number:03d}{ayah_number:03d}.mp3"
        )
        for ayah_number in range(1, ayah_count + 1)
    ]


# ==================================================
# الأذكار
# ==================================================
AZKAR = [
    {
        "category": "أذكار الصباح",
        "title": "ذكر الصباح",
        "text": "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
        "count": "مرة واحدة",
    },
    {
        "category": "أذكار المساء",
        "title": "ذكر المساء",
        "text": "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
        "count": "مرة واحدة",
    },
    {
        "category": "أذكار متنوعة",
        "title": "التسبيح",
        "text": "سبحان الله وبحمده.",
        "count": "مائة مرة",
    },
    {
        "category": "أذكار متنوعة",
        "title": "الاستغفار",
        "text": "أستغفر الله وأتوب إليه.",
        "count": "يُكثر منه",
    },
    {
        "category": "أذكار متنوعة",
        "title": "سيد الاستغفار",
        "text": "اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي، فاغفر لي فإنه لا يغفر الذنوب إلا أنت.",
        "count": "مرة صباحًا أو مساءً",
    },
    {
        "category": "أذكار متنوعة",
        "title": "الصلاة على النبي ﷺ",
        "text": "اللهم صل وسلم على نبينا محمد.",
        "count": "يُكثر منها",
    },
]

# ==================================================
# حالة الصفحات
# ==================================================
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "selected_reciter" not in st.session_state:
    st.session_state.selected_reciter = "مشاري العفاسي"

if "selected_surah" not in st.session_state:
    st.session_state.selected_surah = 1


def open_quran(reciter=None):
    if reciter in RECITERS:
        st.session_state.selected_reciter = reciter

    st.session_state.page = "القرآن الكريم"


# ==================================================
# الشريط الجانبي
# ==================================================
with st.sidebar:
    st.markdown(
        "<div class='section-title'>☪ حصن المسلم</div>",
        unsafe_allow_html=True,
    )

    if st.button("🏠 الرئيسية", key="nav_home"):
        st.session_state.page = "الرئيسية"
        st.rerun()

    if st.button("📖 القرآن الكريم", key="nav_quran"):
        st.session_state.page = "القرآن الكريم"
        st.rerun()

    if st.button("🤲 الأذكار", key="nav_azkar"):
        st.session_state.page = "الأذكار"
        st.rerun()

    st.markdown("---")
    st.markdown("### 🎙️ اختر القارئ")

    reciter_names = list(RECITERS.keys())

    sidebar_reciter = st.selectbox(
        "القارئ",
        reciter_names,
        index=reciter_names.index(st.session_state.selected_reciter),
        key="sidebar_reciter",
    )

    st.session_state.selected_reciter = sidebar_reciter

    if st.button("▶️ استماع للقرآن", key="sidebar_listen"):
        st.session_state.selected_surah = 1
        st.session_state.page = "القرآن الكريم"
        st.rerun()


# ==================================================
# رأس الصفحة
# ==================================================
st.markdown(
    """
    <div class="hero">
        <h1>☪ القرآن الكريم وحصن المسلم ☪</h1>
        <p>﴿ وَاذْكُرُوا اللَّهَ كَثِيرًا لَعَلَّكُمْ تُفْلِحُونَ ﴾</p>
        <p>القرآن الكريم والتلاوات والأذكار اليومية</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# الصفحة الرئيسية
# ==================================================
if st.session_state.page == "الرئيسية":
    st.markdown(
        "<div class='section-title'>🎙️ اختر قارئك المفضل</div>",
        unsafe_allow_html=True,
    )

    names = list(RECITERS.keys())

    for start in range(0, len(names), 2):
        columns = st.columns(2)

        for offset, col in enumerate(columns):
            index = start + offset

            if index >= len(names):
                continue

            name = names[index]

            with col:
                st.markdown(
                    f"""
                    <div class="reciter-card">
                        <div class="reciter-name">
                            🎧 {html.escape(name)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button("📖 قراءة القرآن", key=f"read_{index}"):
                    open_quran(name)
                    st.rerun()

                if st.button("▶️ استماع", key=f"listen_{index}"):
                    open_quran(name)
                    st.session_state.selected_surah = 1
                    st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="zikr-card">
                📖<br><b>القرآن الكريم</b><br>
                قراءة الآيات والاستماع إلى التلاوات
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("افتح القرآن الكريم", key="home_quran"):
            st.session_state.page = "القرآن الكريم"
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="zikr-card">
                🤲<br><b>حصن المسلم</b><br>
                أذكار الصباح والمساء والأذكار المتنوعة
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("افتح الأذكار", key="home_azkar"):
            st.session_state.page = "الأذكار"
            st.rerun()


# ==================================================
# صفحة القرآن الكريم
# ==================================================
elif st.session_state.page == "القرآن الكريم":
    st.markdown(
        "<div class='section-title'>📖 القرآن الكريم</div>",
        unsafe_allow_html=True,
    )

    surah_labels = [
        f"{i}. سورة {name}"
        for i, name in enumerate(SURAH_NAMES, start=1)
    ]

    default_index = max(
        0,
        min(st.session_state.selected_surah - 1, 113),
    )

    col1, col2 = st.columns(2)

    with col1:
        selected_label = st.selectbox(
            "اختر السورة",
            surah_labels,
            index=default_index,
            key="surah_select",
        )

    with col2:
        selected_reciter = st.selectbox(
            "اختر القارئ",
            list(RECITERS.keys()),
            index=list(RECITERS.keys()).index(
                st.session_state.selected_reciter
            ),
            key="quran_reciter",
        )
        st.session_state.selected_reciter = selected_reciter

    surah_number = surah_labels.index(selected_label) + 1
    st.session_state.selected_surah = surah_number

    st.markdown(
        f"<div class='section-title'>سورة {SURAH_NAMES[surah_number - 1]}</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 إعادة تحميل الآيات", key="reload_text"):
        get_surah_text.clear()
        st.rerun()

    with st.spinner("جارٍ تحميل نص القرآن الكريم..."):
        surah_data = get_surah_text(surah_number)

    if surah_data and surah_data.get("ayahs"):
        st.success("تم تحميل نص السورة.")

        # مشغل الصوت المباشر
        audio_urls = get_surah_audio(
            surah_number,
            selected_reciter,
            len(surah_data["ayahs"]),
        )

        if audio_urls:
            safe_urls = json.dumps(
                audio_urls,
                ensure_ascii=False,
            ).replace("</", "<\\/")

            components.html(
                f"""
                <div dir="rtl" style="
                    background:#073b2a;
                    border:1px solid #c5a34a;
                    border-radius:16px;
                    padding:16px;
                    text-align:center;
                    color:#fff8df;
                    font-family:Arial,sans-serif;
                ">
                    <h3 style="color:#f2d780;">
                        ▶️ استماع إلى سورة {html.escape(SURAH_NAMES[surah_number - 1])}
                    </h3>

                    <audio id="quranPlayer"
                           controls
                           preload="metadata"
                           style="width:100%;">
                    </audio>

                    <p id="audioStatus" style="color:#f2d780;">
                        اضغط تشغيل لبدء التلاوة
                    </p>

                    <div style="display:flex;gap:8px;">
                        <button id="previousAyah" style="
                            flex:1;padding:10px;border:0;border-radius:8px;
                            background:#c8a74d;color:#103d2b;font-weight:bold;
                        ">الآية السابقة</button>

                        <button id="nextAyah" style="
                            flex:1;padding:10px;border:0;border-radius:8px;
                            background:#c8a74d;color:#103d2b;font-weight:bold;
                        ">الآية التالية</button>
                    </div>
                </div>

                <script>
                const audioUrls = {safe_urls};
                const player = document.getElementById("quranPlayer");
                const status = document.getElementById("audioStatus");
                let current = 0;

                function loadAyah(index, shouldPlay) {{
                    current = Math.max(0, Math.min(index, audioUrls.length - 1));
                    player.src = audioUrls[current];
                    status.textContent =
                        "الآية " + (current + 1) + " من " + audioUrls.length;

                    if (shouldPlay) {{
                        player.play().catch(() => {{
                            status.textContent =
                                "تعذّر بدء التشغيل تلقائيًا؛ اضغط تشغيل.";
                        }});
                    }}
                }}

                player.addEventListener("ended", () => {{
                    if (current < audioUrls.length - 1) {{
                        loadAyah(current + 1, true);
                    }} else {{
                        status.textContent = "انتهت تلاوة السورة.";
                    }}
                }});

                player.addEventListener("error", () => {{
                    status.textContent =
                        "تعذّر تحميل ملف الصوت. جرّب قارئًا آخر.";
                }});

                document.getElementById("previousAyah").onclick =
                    () => loadAyah(current - 1, true);

                document.getElementById("nextAyah").onclick =
                    () => loadAyah(current + 1, true);

                loadAyah(0, false);
                </script>
                """,
                height=230,
                scrolling=False,
            )

        st.markdown("---")
        st.markdown(
            "<div class='section-title'>آيات السورة</div>",
            unsafe_allow_html=True,
        )

        if surah_number not in (1, 9):
            st.markdown(
                "<div class='ayah-card'>"
                "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
                "</div>",
                unsafe_allow_html=True,
            )

        for ayah in surah_data["ayahs"]:
            ayah_text = html.escape(ayah.get("text", ""))
            ayah_number = ayah.get("numberInSurah", "")

            st.markdown(
                f"""
                <div class="ayah-card">
                    {ayah_text}
                    <span style="color:#e8c65f;font-size:16px;">
                        ﴿ {ayah_number} ﴾
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.error("تعذّر تحميل نص الآيات من المصدرين.")

        error_detail = (
            surah_data.get("error", "")
            if isinstance(surah_data, dict)
            else ""
        )

        if error_detail:
            with st.expander("عرض تفاصيل الخطأ"):
                st.code(error_detail)

        st.info(
            "جرّب إعادة التحميل بعد قليل، أو افتح تفاصيل الخطأ "
            "إذا استمرت المشكلة."
        )


# ==================================================
# صفحة الأذكار
# ==================================================
elif st.session_state.page == "الأذكار":
    st.markdown(
        "<div class='section-title'>🤲 حصن المسلم — الأذكار</div>",
        unsafe_allow_html=True,
    )

    category = st.selectbox(
        "اختر قسم الأذكار",
        [
            "جميع الأذكار",
            "أذكار الصباح",
            "أذكار المساء",
            "أذكار متنوعة",
        ],
    )

    for index, zikr in enumerate(AZKAR):
        if (
            category != "جميع الأذكار"
            and zikr["category"] != category
        ):
            continue

        st.markdown(
            f"""
            <div class="zikr-card">
                <div style="color:#f2d780;font-weight:bold;">
                    {html.escape(zikr['title'])}
                </div>
                <div>{html.escape(zikr['text'])}</div>
                <div style="font-size:16px;color:#e5cb76;">
                    التكرار: {html.escape(zikr['count'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📋 عرض النص للنسخ", key=f"copy_{index}"):
            st.code(zikr["text"], language=None)


# ==================================================
# التذييل
# ==================================================
st.markdown(
    """
    <div class="footer">
        🌿 اللهم اجعل القرآن الكريم ربيع قلوبنا ونور صدورنا 🌿
        <br><br>
        OMAR MELIGY
    </div>
    """,
    unsafe_allow_html=True,
)
