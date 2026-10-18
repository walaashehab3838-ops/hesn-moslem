
import html
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="wide",
)

API = "https://api.alquran.cloud/v1"

RECITERS = {
    "مشاري العفاسي": "Alafasy_128kbps",
    "عبدالرحمن السديس": "Abdurrahmaan_As-Sudais_192kbps",
    "محمود خليل الحصري": "Husary_128kbps",
    "محمد صديق المنشاوي": "Minshawy_Murattal_128kbps",
    "عبدالباسط عبدالصمد": "Abdul_Basit_Murattal_192kbps",
    "أبو بكر الشاطري": "Abu_Bakr_Ash-Shaatree_128kbps",
    "ماهر المعيقلي": "MaherAlMuaiqly128kbps",
}

SURAHS = [
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


# --------------------------------------------------
# التصميم والألوان
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Amiri:wght@400;700&display=swap');

    .stApp {
        background: linear-gradient(145deg, #063d2c, #0d6041, #063526);
    }

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
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
        padding: 25px 12px;
        margin-bottom: 22px;
        border: 1px solid #c5a34a;
        border-radius: 20px;
        background: rgba(3, 45, 31, 0.85);
        color: #fff8df;
    }

    .hero h1 {
        color: #f2d780;
        font-family: 'Amiri', serif;
    }

    .section-title {
        color: #f2d780;
        font-family: 'Amiri', serif;
        text-align: center;
        font-size: 28px;
        margin: 20px 0;
    }

    .reciter-card, .zikr-card {
        background: rgba(3, 43, 30, 0.85);
        border: 1px solid #c5a34a;
        border-radius: 16px;
        padding: 18px 14px;
        margin: 12px 0;
        text-align: center;
        color: #fff8df;
    }

    .reciter-name {
        font-family: 'Amiri', serif;
        font-size: 23px;
        font-weight: bold;
        color: #f2d780;
    }

    .ayah-card {
        direction: rtl;
        text-align: center;
        background: rgba(3, 43, 30, 0.85);
        border: 1px solid #c5a34a;
        border-radius: 16px;
        padding: 20px 14px;
        margin: 12px 0;
        color: #fff8df;
        font-family: 'Amiri', serif;
        font-size: 25px;
        line-height: 2.1;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .ayah-number {
        display: inline-block;
        color: #f2d780;
        font-size: 18px;
        white-space: nowrap;
        padding: 0 5px;
    }

    .zikr-card {
        direction: rtl;
        font-family: 'Amiri', serif;
        font-size: 22px;
        line-height: 2;
    }

    div[data-testid="stButton"] {
        width: 100%;
    }

    div[data-testid="stButton"] > button {
        display: block !important;
        width: 100% !important;
        min-height: 50px !important;
        height: auto !important;
        padding: 10px 14px !important;
        margin: 5px 0 !important;
        box-sizing: border-box !important;
        background: #f0d77f !important;
        border: 2px solid #c5a34a !important;
        border-radius: 12px !important;
        color: #102f23 !important;
        -webkit-text-fill-color: #102f23 !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        line-height: 1.5 !important;
        text-align: center !important;
        white-space: normal !important;
        overflow: visible !important;
        box-shadow: none !important;
    }

    div[data-testid="stButton"] > button p {
        color: #102f23 !important;
        -webkit-text-fill-color: #102f23 !important;
        font-family: 'Cairo', sans-serif !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        line-height: 1.5 !important;
        text-align: center !important;
        white-space: normal !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #fff0ad !important;
        border-color: #f2d780 !important;
    }

    .footer {
        text-align: center;
        color: #f2d780;
        border-top: 1px solid #c5a34a;
        margin-top: 35px;
        padding: 22px 8px;
    }

    @media (max-width: 600px) {
        .ayah-card {
            font-size: 22px;
            padding: 16px 10px;
        }

        .section-title {
            font-size: 24px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# تحميل القرآن الكريم
# --------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def load_surah(number):
    response = requests.get(
        f"{API}/surah/{number}",
        timeout=25,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("code") != 200:
        raise ValueError("لم ينجح تحميل السورة.")

    data = payload.get("data", {})
    ayahs = data.get("ayahs", [])

    if not ayahs:
        raise ValueError("لم يتم العثور على آيات.")

    return [
        {
            "text": item.get("text", ""),
            "number": item.get("numberInSurah", index + 1),
        }
        for index, item in enumerate(ayahs)
        if item.get("text")
    ]


def build_audio_urls(surah_number, reciter, count):
    folder = RECITERS[reciter]

    return [
        (
            f"https://everyayah.com/data/{folder}/"
            f"{surah_number:03d}{ayah_number:03d}.mp3"
        )
        for ayah_number in range(1, count + 1)
    ]


# --------------------------------------------------
# حالة التطبيق
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "reciter" not in st.session_state:
    st.session_state.reciter = "مشاري العفاسي"

if "surah" not in st.session_state:
    st.session_state.surah = 1


# --------------------------------------------------
# القائمة الجانبية
# --------------------------------------------------

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
    st.markdown("### 🎙️ القارئ المفضل")

    reciter_names = list(RECITERS.keys())

    selected_sidebar_reciter = st.selectbox(
        "اختر القارئ",
        reciter_names,
        index=reciter_names.index(st.session_state.reciter),
        key="sidebar_reciter",
    )

    st.session_state.reciter = selected_sidebar_reciter

    if st.button("▶️ استماع إلى القرآن", key="sidebar_listen"):
        st.session_state.page = "القرآن الكريم"
        st.session_state.surah = 1
        st.rerun()


# --------------------------------------------------
# رأس الصفحة
# --------------------------------------------------

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


# --------------------------------------------------
# الصفحة الرئيسية
# --------------------------------------------------

if st.session_state.page == "الرئيسية":
    st.markdown(
        "<div class='section-title'>🎙️ القراء</div>",
        unsafe_allow_html=True,
    )

    reciter_names = list(RECITERS.keys())

    for start in range(0, len(reciter_names), 2):
        columns = st.columns(2)

        for offset, column in enumerate(columns):
            index = start + offset

            if index >= len(reciter_names):
                continue

            reciter_name = reciter_names[index]

            with column:
                st.markdown(
                    f"""
                    <div class="reciter-card">
                        <div class="reciter-name">
                            🎧 {html.escape(reciter_name)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if st.button(
                    "📖 قراءة القرآن",
                    key=f"read_{index}",
                    use_container_width=True,
                ):
                    st.session_state.reciter = reciter_name
                    st.session_state.page = "القرآن الكريم"
                    st.session_state.surah = 1
                    st.rerun()

                if st.button(
                    "▶️ استماع",
                    key=f"listen_{index}",
                    use_container_width=True,
                ):
                    st.session_state.reciter = reciter_name
                    st.session_state.page = "القرآن الكريم"
                    st.session_state.surah = 1
                    st.rerun()

    left, right = st.columns(2)

    with left:
        st.markdown(
            """
            <div class="zikr-card">
                📖<br><b>القرآن الكريم</b><br>
                قراءة الآيات والاستماع للتلاوات
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("افتح القرآن الكريم", key="home_quran"):
            st.session_state.page = "القرآن الكريم"
            st.rerun()

    with right:
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


# --------------------------------------------------
# صفحة القرآن الكريم
# --------------------------------------------------

elif st.session_state.page == "القرآن الكريم":
    st.markdown(
        "<div class='section-title'>📖 القرآن الكريم</div>",
        unsafe_allow_html=True,
    )

    surah_labels = [
        f"{number} - سورة {name}"
        for number, name in enumerate(SURAHS, start=1)
    ]

    selected_label = st.selectbox(
        "اختر السورة",
        surah_labels,
        index=max(0, min(st.session_state.surah - 1, 113)),
        key="surah_choice",
    )

    surah_number = surah_labels.index(selected_label) + 1
    st.session_state.surah = surah_number

    reciter_names = list(RECITERS.keys())

    selected_reciter = st.selectbox(
        "اختر القارئ",
        reciter_names,
        index=reciter_names.index(st.session_state.reciter),
        key="quran_reciter",
    )

    st.session_state.reciter = selected_reciter

    st.markdown(
        f"<div class='section-title'>سورة {SURAHS[surah_number - 1]}</div>",
        unsafe_allow_html=True,
    )

    if st.button("🔄 إعادة تحميل الآيات", key="reload_surah"):
        load_surah.clear()
        st.rerun()

    try:
        with st.spinner("جارٍ تحميل الآيات..."):
            ayahs = load_surah(surah_number)

        st.success("تم تحميل نص السورة.")

        urls = build_audio_urls(
            surah_number,
            selected_reciter,
            len(ayahs),
        )

        safe_urls = json.dumps(urls, ensure_ascii=True)
        safe_surah_name = html.escape(SURAHS[surah_number - 1])

        components.html(
            f"""
            <div dir="rtl" style="
                background:#073b2a;
                border:1px solid #c5a34a;
                border-radius:16px;
                padding:16px;
                color:#fff8df;
                text-align:center;
                font-family:Arial,sans-serif;
            ">
                <h3 style="color:#f2d780;">
                    ▶️ استماع إلى سورة {safe_surah_name}
                </h3>

                <audio
                    id="quran-player"
                    controls
                    preload="metadata"
                    style="display:block;width:100%;min-height:45px;"
                ></audio>

                <p
                    id="quran-status"
                    style="color:#f2d780;"
                >
                    اضغط تشغيل لبدء التلاوة
                </p>

                <div style="display:flex;gap:10px;">
                    <button
                        id="prev-ayah"
                        type="button"
                        style="
                            flex:1;min-height:48px;padding:10px;
                            border:0;border-radius:10px;
                            background:#f0d77f;color:#102f23;
                            font-size:16px;font-weight:bold;cursor:pointer;
                        "
                    >الآية السابقة</button>

                    <button
                        id="next-ayah"
                        type="button"
                        style="
                            flex:1;min-height:48px;padding:10px;
                            border:0;border-radius:10px;
                            background:#f0d77f;color:#102f23;
                            font-size:16px;font-weight:bold;cursor:pointer;
                        "
                    >الآية التالية</button>
                </div>
            </div>

            <script>
                const audioUrls = {safe_urls};
                const player = document.getElementById("quran-player");
                const status = document.getElementById("quran-status");
                let currentAyah = 0;

                function loadAyah(index, playNow) {{
                    currentAyah = Math.max(
                        0,
                        Math.min(index, audioUrls.length - 1)
                    );

                    player.src = audioUrls[currentAyah];
                    status.textContent =
                        "الآية " + (currentAyah + 1) +
                        " من " + audioUrls.length;

                    if (playNow) {{
                        player.play().catch(() => {{
                            status.textContent =
                                "اضغط زر التشغيل لبدء التلاوة";
                        }});
                    }}
                }}

                player.addEventListener("ended", () => {{
                    if (currentAyah < audioUrls.length - 1) {{
                        loadAyah(currentAyah + 1, true);
                    }} else {{
                        status.textContent = "انتهت تلاوة السورة";
                    }}
                }});

                player.addEventListener("error", () => {{
                    status.textContent =
                        "تعذّر تحميل الصوت. جرّب قارئًا آخر.";
                }});

                document.getElementById("prev-ayah").onclick = () => {{
                    loadAyah(currentAyah - 1, true);
                }};

                document.getElementById("next-ayah").onclick = () => {{
                    loadAyah(currentAyah + 1, true);
                }};

                loadAyah(0, false);
            </script>
            """,
            height=235,
            scrolling=False,
        )

        st.markdown("---")

        st.markdown(
            "<div class='section-title'>آيات السورة</div>",
            unsafe_allow_html=True,
        )

        if surah_number not in (1, 9):
            st.markdown(
                """
                <div class="ayah-card">
                    بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ
                </div>
                """,
                unsafe_allow_html=True,
            )

        # عرض نص الآية ورقمها داخل المربع نفسه
        for ayah in ayahs:
            ayah_text = html.escape(ayah["text"])
            ayah_number = ayah["number"]

            st.markdown(
                f"""
                <div class="ayah-card">
                    {ayah_text}
                    <span class="ayah-number">
                        ﴿ {ayah_number} ﴾
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    except Exception as error:
        st.error(
            "تعذّر تحميل السورة. تأكد من اتصال الإنترنت وحاول مرة أخرى."
        )

        with st.expander("تفاصيل الخطأ"):
            st.code(str(error))

        if st.button("إعادة المحاولة", key="retry_surah"):
            load_surah.clear()
            st.rerun()


# --------------------------------------------------
# صفحة الأذكار
# --------------------------------------------------

elif st.session_state.page == "الأذكار":
    st.markdown(
        "<div class='section-title'>🤲 حصن المسلم</div>",
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
        key="azkar_category",
    )

    shown_count = 0

    for index, zikr in enumerate(AZKAR):
        if (
            category != "جميع الأذكار"
            and zikr["category"] != category
        ):
            continue

        shown_count += 1

        st.markdown(
            f"""
            <div class="zikr-card">
                <div style="color:#f2d780;font-weight:bold;">
                    {html.escape(zikr["title"])}
                </div>

                <div>{html.escape(zikr["text"])}</div>

                <div style="font-size:16px;color:#f2d780;">
                    التكرار: {html.escape(zikr["count"])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if shown_count == 0:
        st.info("لا توجد أذكار في هذا القسم حاليًا.")


# --------------------------------------------------
# تذييل الموقع
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        <div style="font-size:18px;font-weight:bold;">
            ☪ القرآن الكريم وحصن المسلم ☪
        </div>
        <div style="margin-top:8px;">
            تقبّل الله منا ومنكم صالح الأعمال
        </div>
        <div style="margin-top:12px;font-size:14px;">
            OMAR MELIGY
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
