
import streamlit as st
import requests
import json
import html
import streamlit.components.v1 as components

# =========================
# إعدادات التطبيق
# =========================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

QURAN_API = "https://api.alquran.cloud/v1"

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
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at top, #176b48 0%, transparent 65%),
            linear-gradient(145deg, #063d2c, #0b5139 55%, #063526);
        color: #fffdf2;
    }

    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
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
        padding: 30px 12px;
        border: 1px solid #c7a84b;
        border-radius: 22px;
        background: linear-gradient(135deg, #0b5038, #063323);
        box-shadow: 0 8px 30px rgba(0,0,0,.2);
        margin-bottom: 22px;
    }

    .hero h1 {
        font-family: 'Amiri', serif;
        color: #f2d780;
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        margin: 0;
    }

    .section-title {
        color: #f2d780;
        font-family: 'Amiri', serif;
        text-align: center;
        font-size: 30px;
        margin: 20px 0;
    }

    .reciter-card {
        border: 1px solid #c5a34a;
        border-radius: 16px;
        padding: 20px 12px;
        text-align: center;
        background: rgba(4, 43, 30, .8);
        margin-bottom: 10px;
        min-height: 85px;
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
        background: rgba(4, 44, 31, .84);
        border: 1px solid #bda04a;
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        color: #fff8df;
        font-family: 'Amiri', serif;
        font-size: 25px;
        line-height: 2.1;
    }

    .ayah-number {
        color: #e8c65f;
        font-size: 16px;
        margin-right: 8px;
        white-space: nowrap;
    }

    .zikr-card {
        direction: rtl;
        text-align: center;
        background: rgba(4, 44, 31, .84);
        border: 1px solid #bda04a;
        border-radius: 16px;
        padding: 22px;
        margin: 14px 0;
        color: #fff8df;
        font-family: 'Amiri', serif;
        font-size: 24px;
        line-height: 2;
    }

    div.stButton > button {
        width: 100%;
        border: 1px solid #e0c260;
        border-radius: 12px;
        background: #c8a74d;
        color: #103d2b;
        font-weight: 800;
        min-height: 44px;
        transition: .2s;
    }

    div.stButton > button:hover {
        background: #f0d77f;
        color: #063d2c;
        border-color: #f0d77f;
    }

    div[data-baseweb="select"] > div {
        background-color: #f8f2df;
        color: #153c2c;
        border-radius: 10px;
    }

    .footer {
        text-align: center;
        padding: 22px 8px;
        margin-top: 36px;
        color: #f0d77f;
        border-top: 1px solid #bda04a;
        font-size: 14px;
    }

    audio {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# جلب البيانات من API
# =========================
def api_get(path):
    """طلب البيانات مع مهلة اتصال ورسالة خطأ مفهومة."""
    url = f"{QURAN_API}/{path}"

    try:
        response = requests.get(url, timeout=25)
        response.raise_for_status()
        result = response.json()

        if result.get("code") != 200:
            raise ValueError(result.get("status", "تعذّر جلب البيانات"))

        return result.get("data")

    except requests.RequestException as exc:
        st.error(
            "تعذّر الاتصال بمصدر القرآن الكريم. "
            "تحقق من اتصال الإنترنت وحاول مرة أخرى."
        )
        st.caption(f"تفاصيل الاتصال: {exc}")
        return None

    except (ValueError, json.JSONDecodeError) as exc:
        st.error("وصل رد غير متوقع من مصدر البيانات.")
        st.caption(str(exc))
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def get_surahs():
    data = api_get("surah")
    return data if isinstance(data, list) else []


@st.cache_data(ttl=3600, show_spinner=False)
def get_surah_text(surah_number):
    """النص القرآني مستقل عن إصدار الصوت."""
    data = api_get(f"surah/{surah_number}")
    return data if isinstance(data, dict) else None


@st.cache_data(ttl=1800, show_spinner=False)
def get_surah_audio(surah_number, edition):
    """جلب روابط التلاوة حسب القارئ المختار."""
    data = api_get(f"surah/{surah_number}/{edition}")
    return data if isinstance(data, dict) else None


# =========================
# الأذكار
# =========================
AZKAR = [
    {
        "title": "أذكار الصباح",
        "text": "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
        "count": "مرة واحدة",
    },
    {
        "title": "ذكر",
        "text": "سبحان الله وبحمده.",
        "count": "مائة مرة",
    },
    {
        "title": "ذكر",
        "text": "أستغفر الله وأتوب إليه.",
        "count": "يُكثر منه",
    },
    {
        "title": "سيد الاستغفار",
        "text": "اللهم أنت ربي لا إله إلا أنت، خلقتني وأنا عبدك، وأنا على عهدك ووعدك ما استطعت، أعوذ بك من شر ما صنعت، أبوء لك بنعمتك عليّ، وأبوء بذنبي، فاغفر لي فإنه لا يغفر الذنوب إلا أنت.",
        "count": "مرة صباحًا أو مساءً",
    },
    {
        "title": "ذكر",
        "text": "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
        "count": "عشر مرات أو أكثر",
    },
    {
        "title": "الصلاة على النبي ﷺ",
        "text": "اللهم صل وسلم على نبينا محمد.",
        "count": "يُكثر منها",
    },
    {
        "title": "أذكار المساء",
        "text": "أمسينا وأمسى الملك لله، والحمد لله، لا إله إلا الله وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير.",
        "count": "مرة واحدة",
    },
]

# =========================
# حالة التنقل
# =========================
if "page" not in st.session_state:
    st.session_state.page = "الرئيسية"

if "selected_reciter" not in st.session_state:
    st.session_state.selected_reciter = "مشاري العفاسي"

if "selected_surah" not in st.session_state:
    st.session_state.selected_surah = 1


def go_to_quran(reciter=None):
    if reciter in RECITERS:
        st.session_state.selected_reciter = reciter

    st.session_state.page = "القرآن الكريم"


# =========================
# الشريط الجانبي
# =========================
with st.sidebar:
    st.markdown(
        "<div class='section-title'>☪ حصن المسلم</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

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

    sidebar_reciter = st.selectbox(
        "القارئ",
        list(RECITERS.keys()),
        index=list(RECITERS.keys()).index(
            st.session_state.selected_reciter
        ),
        key="sidebar_reciter",
    )

    st.session_state.selected_reciter = sidebar_reciter

    if st.button("استماع للقرآن", key="sidebar_listen"):
        st.session_state.selected_surah = 1
        st.session_state.page = "القرآن الكريم"
        st.rerun()

# =========================
# رأس الصفحة
# =========================
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

# =========================
# الصفحة الرئيسية
# =========================
if st.session_state.page == "الرئيسية":

    st.markdown(
        "<div class='section-title'>🎙️ اختر قارئك المفضل</div>",
        unsafe_allow_html=True,
    )

    reciter_names = list(RECITERS.keys())

    for start in range(0, len(reciter_names), 2):
        cols = st.columns(2)

        for offset, col in enumerate(cols):
            index = start + offset

            if index >= len(reciter_names):
                continue

            name = reciter_names[index]

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

                if st.button(
                    "📖 قراءة القرآن",
                    key=f"read_{index}",
                ):
                    go_to_quran(name)
                    st.rerun()

                if st.button(
                    "▶️ استماع",
                    key=f"listen_{index}",
                ):
                    go_to_quran(name)
                    st.rerun()

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="zikr-card">
                📖<br>
                <b>القرآن الكريم</b><br>
                اقرأ الآيات واستمع إلى التلاوات
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
                🤲<br>
                <b>حصن المسلم</b><br>
                أذكار الصباح والمساء وأذكار متنوعة
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("افتح الأذكار", key="home_azkar"):
            st.session_state.page = "الأذكار"
            st.rerun()

# =========================
# صفحة القرآن الكريم
# =========================
elif st.session_state.page == "القرآن الكريم":

    st.markdown(
        "<div class='section-title'>📖 القرآن الكريم</div>",
        unsafe_allow_html=True,
    )

    surahs = get_surahs()

    if not surahs:
        st.warning(
            "لم نتمكن من تحميل قائمة السور. "
            "حاول تحديث الصفحة بعد قليل."
        )
    else:
        surah_names = [
            f"{s['number']}. {s['name']} — {s['englishName']}"
            for s in surahs
        ]

        default_index = max(
            0,
            min(
                int(st.session_state.selected_surah) - 1,
                len(surahs) - 1,
            ),
        )

        col1, col2 = st.columns(2)

        with col1:
            chosen_surah_label = st.selectbox(
                "اختر السورة",
                surah_names,
                index=default_index,
                key="surah_select",
            )

        with col2:
            reciter_name = st.selectbox(
                "اختر القارئ",
                list(RECITERS.keys()),
                index=list(RECITERS.keys()).index(
                    st.session_state.selected_reciter
                ),
                key="quran_reciter",
            )
            st.session_state.selected_reciter = reciter_name

        surah_number = surah_names.index(chosen_surah_label) + 1
        st.session_state.selected_surah = surah_number

        surah_info = surahs[surah_number - 1]

        st.markdown(
            f"<div class='section-title'>{html.escape(surah_info['name'])}</div>",
            unsafe_allow_html=True,
        )

        # جلب النص والصوت بشكل منفصل
        with st.spinner("جارٍ تحميل آيات السورة..."):
            text_data = get_surah_text(surah_number)

        with st.spinner("جارٍ تجهيز التلاوة..."):
            audio_data = get_surah_audio(
                surah_number,
                RECITERS[reciter_name],
            )

        # عرض الصوت إن كان متاحًا
        audio_urls = []

        if audio_data and isinstance(audio_data.get("ayahs"), list):
            for ayah in audio_data["ayahs"]:
                url = ayah.get("audio")
                audio_urls.append(url if isinstance(url, str) else "")

        if audio_urls and any(audio_urls):
            valid_urls = [u for u in audio_urls if u]

            escaped_urls = json.dumps(
                valid_urls,
                ensure_ascii=False,
            ).replace("</", "<\\/")

            components.html(
                f"""
                <div dir="rtl" style="
                    background:#073b2a;
                    border:1px solid #c5a34a;
                    border-radius:16px;
                    padding:18px;
                    color:#fff8df;
                    font-family:Arial,sans-serif;
                    text-align:center;
                ">
                    <div style="
                        font-size:20px;
                        font-weight:bold;
                        color:#f2d780;
                        margin-bottom:12px;
                    ">
                        ▶️ استماع إلى سورة {html.escape(surah_info['name'])}
                    </div>

                    <audio id="quranAudio"
                           controls
                           preload="metadata"
                           style="width:100%;">
                    </audio>

                    <div id="audioStatus" style="
                        margin-top:10px;
                        font-size:14px;
                        color:#f2d780;
                    ">
                        اضغط تشغيل لبدء التلاوة
                    </div>

                    <div style="
                        display:flex;
                        gap:10px;
                        margin-top:14px;
                    ">
                        <button id="previousAyah" style="
                            flex:1;
                            padding:10px;
                            border:0;
                            border-radius:8px;
                            background:#c8a74d;
                            color:#103d2b;
                            font-weight:bold;
                            cursor:pointer;
                        ">الآية السابقة</button>

                        <button id="nextAyah" style="
                            flex:1;
                            padding:10px;
                            border:0;
                            border-radius:8px;
                            background:#c8a74d;
                            color:#103d2b;
                            font-weight:bold;
                            cursor:pointer;
                        ">الآية التالية</button>
                    </div>
                </div>

                <script>
                    const audioUrls = {escaped_urls};
                    const player = document.getElementById("quranAudio");
                    const status = document.getElementById("audioStatus");
                    let currentAyah = 0;

                    function loadAyah(index, autoplay) {{
                        if (!audioUrls.length) return;

                        currentAyah = Math.max(
                            0,
                            Math.min(index, audioUrls.length - 1)
                        );

                        player.src = audioUrls[currentAyah];
                        status.textContent =
                            "الآية " + (currentAyah + 1) +
                            " من " + audioUrls.length;

                        if (autoplay) {{
                            player.play().catch(() => {{
                                status.textContent =
                                    "اضغط تشغيل لبدء الاستماع";
                            }});
                        }}
                    }}

                    player.addEventListener("ended", function() {{
                        if (currentAyah < audioUrls.length - 1) {{
                            loadAyah(currentAyah + 1, true);
                        }} else {{
                            status.textContent = "انتهت تلاوة السورة";
                        }}
                    }});

                    player.addEventListener("error", function() {{
                        status.textContent =
                            "تعذر تشغيل هذا المقطع. جرّب تحديث الصفحة أو اختيار قارئ آخر.";
                    }});

                    document.getElementById("previousAyah")
                        .addEventListener("click", function() {{
                            loadAyah(currentAyah - 1, true);
                        }});

                    document.getElementById("nextAyah")
                        .addEventListener("click", function() {{
                            loadAyah(currentAyah + 1, true);
                        }});

                    loadAyah(0, false);
                </script>
                """,
                height=230,
                scrolling=False,
            )
        else:
            st.warning(
                "تعذّر تحميل التلاوة لهذا القارئ حاليًا. "
                "يمكنك تجربة قارئ آخر أو المحاولة لاحقًا."
            )

        st.markdown("---")
        st.markdown(
            "<div class='section-title'>آيات السورة</div>",
            unsafe_allow_html=True,
        )

        if text_data and isinstance(text_data.get("ayahs"), list):
            ayahs = text_data["ayahs"]

            if surah_number != 1 and surah_number != 9:
                st.markdown(
                    "<div class='ayah-card'>"
                    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"
                    "</div>",
                    unsafe_allow_html=True,
                )

            for ayah in ayahs:
                ayah_text = html.escape(ayah.get("text", ""))
                ayah_number = ayah.get("numberInSurah", "")

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

        else:
            st.error(
                "لم نتمكن من تحميل نص الآيات. "
                "تحقق من اتصال الإنترنت ثم حاول مرة أخرى."
            )

# =========================
# صفحة الأذكار
# =========================
elif st.session_state.page == "الأذكار":

    st.markdown(
        "<div class='section-title'>🤲 حصن المسلم — الأذكار</div>",
        unsafe_allow_html=True,
    )

    zikr_filter = st.selectbox(
        "اختر قسم الأذكار",
        [
            "جميع الأذكار",
            "أذكار الصباح",
            "أذكار المساء",
            "أذكار متنوعة",
        ],
    )

    for index, zikr in enumerate(AZKAR):
        title = zikr["title"]

        if zikr_filter == "أذكار الصباح" and title != "أذكار الصباح":
            continue

        if zikr_filter == "أذكار المساء" and title != "أذكار المساء":
            continue

        if zikr_filter == "أذكار متنوعة" and title in [
            "أذكار الصباح",
            "أذكار المساء",
        ]:
            continue

        st.markdown(
            f"""
            <div class="zikr-card">
                <div style="color:#f2d780;font-weight:bold;">
                    {html.escape(title)}
                </div>
                <div>{html.escape(zikr['text'])}</div>
                <div style="font-size:16px;color:#e5cb76;">
                    التكرار: {html.escape(zikr['count'])}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("📋 نسخ الذكر", key=f"copy_zikr_{index}"):
            st.code(zikr["text"], language=None)
            st.info(
                "يمكنك تحديد النص ونسخه من المربع أعلاه."
            )

# =========================
# التذييل
# =========================
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
