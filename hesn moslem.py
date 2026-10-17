
import html
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# إعداد التطبيق
# ==========================================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم | OMAR MELIGY",
    page_icon="📖",
    layout="centered",
)

QURAN_API = "https://api.alquran.cloud/v1"
HISN_API = "https://www.hisnmuslim.com/api/ar/"

# ==========================================
# القراء
# ==========================================
RECITERS = {
    "مشاري العفاسي": "ar.alafasy",
    "عبدالرحمن السديس": "ar.abdurrahmaansudais",
    "محمود خليل الحصري": "ar.husary",
    "محمد صديق المنشاوي": "ar.minshawi",
    "عبدالباسط عبدالصمد": "ar.abdulbasitmurattal",
    "أبو بكر الشاطري": "ar.shaatree",
    "ماهر المعيقلي": "ar.mahermuaiqly",
}

# ==========================================
# التصميم والعلامة المائية
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.stApp {
    background-color: var(--background-color);
}

.main-title {
    text-align: center;
    font-size: 32px;
    font-weight: bold;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    opacity: 0.75;
    margin-bottom: 25px;
}

.arabic-quran {
    direction: rtl;
    text-align: justify;
    font-family: 'Amiri', serif;
    font-size: 28px;
    line-height: 2.3;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #b99b4b66;
}

.dhikr {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', serif;
    font-size: 24px;
    line-height: 2.1;
    padding: 18px;
    border: 1px solid #b99b4b66;
    border-radius: 12px;
    margin: 12px 0;
}

/* العلامة المائية الثابتة */
.watermark {
    position: fixed;
    right: 12px;
    bottom: 12px;
    z-index: 999999;
    width: 135px;
    padding: 8px 5px;
    text-align: center;
    pointer-events: none;
    user-select: none;
    opacity: 0.68;
    border: 1px solid #c6a64b66;
    border-radius: 12px;
    background: rgba(30, 30, 30, 0.10);
    backdrop-filter: blur(3px);
}

.watermark-star {
    color: #d4af37;
    font-size: 30px;
    line-height: 1.1;
    text-shadow: 0 0 7px #d4af3755;
}

.watermark-name {
    color: var(--text-color);
    font-family: Arial, sans-serif;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1px;
    white-space: nowrap;
}

@media (max-width: 600px) {
    .arabic-quran {
        font-size: 23px;
    }

    .dhikr {
        font-size: 21px;
    }

    .watermark {
        width: 112px;
        right: 7px;
        bottom: 7px;
    }

    .watermark-name {
        font-size: 11px;
    }
}
</style>

<div class="watermark">
    <div class="watermark-star">★</div>
    <div class="watermark-name">OMAR MELIGY</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# رأس الصفحة
# ==========================================
st.markdown(
    '<div class="main-title">📖 القرآن الكريم وحصن المسلم</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">تلاوة القرآن الكريم والأذكار اليومية</div>',
    unsafe_allow_html=True,
)

# ==========================================
# بيانات القرآن الكريم
# ==========================================
@st.cache_data(ttl=43200)
def get_surahs():
    response = requests.get(
        f"{QURAN_API}/surah",
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("code") != 200:
        raise ValueError("تعذر تحميل قائمة السور")

    return data["data"]


@st.cache_data(ttl=43200)
def get_surah(number, reciter_id):
    response = requests.get(
        f"{QURAN_API}/surah/{number}/{reciter_id}",
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("code") != 200:
        raise ValueError("تعذر تحميل السورة أو القارئ")

    return data["data"]


# ==========================================
# بيانات حصن المسلم
# ==========================================
@st.cache_data(ttl=86400)
def get_hisn():
    response = requests.get(
        HISN_API,
        timeout=25,
    )
    response.raise_for_status()
    return response.json()


# ==========================================
# عرض رسائل الأخطاء
# ==========================================
def show_error(error):
    st.error(f"حدث خطأ أثناء تحميل البيانات: {error}")


# ==========================================
# القائمة الجانبية
# ==========================================
section = st.sidebar.radio(
    "📚 أقسام التطبيق",
    [
        "القرآن الكريم",
        "حصن المسلم",
        "حول التطبيق",
    ],
)

# ==========================================
# قسم القرآن الكريم
# ==========================================
if section == "القرآن الكريم":

    st.header("🕌 القرآن الكريم")

    try:
        surahs = get_surahs()

        surah_options = {
            f'{item["number"]} - {item["name"]}': item["number"]
            for item in surahs
        }

        selected_surah = st.selectbox(
            "📖 اختر السورة",
            list(surah_options.keys()),
        )

        reciter_name = st.selectbox(
            "🎙️ اختر القارئ",
            list(RECITERS.keys()),
        )

        surah_number = surah_options[selected_surah]
        reciter_id = RECITERS[reciter_name]

        with st.spinner("جارٍ تحميل السورة والتلاوة..."):
            surah = get_surah(surah_number, reciter_id)

        st.subheader(surah["name"])
        st.caption(
            f'عدد الآيات: {surah["numberOfAyahs"]} | '
            f'القارئ: {reciter_name}'
        )

        # عرض الآيات
        verses = []

        for ayah in surah["ayahs"]:
            verse_text = html.escape(ayah["text"])
            verse_number = ayah["numberInSurah"]
            verses.append(
                f"{verse_text} ﴿{verse_number}﴾"
            )

        st.markdown(
            '<div class="arabic-quran">'
            + " ۞ ".join(verses)
            + "</div>",
            unsafe_allow_html=True,
        )

        # ======================================
        # مشغل السورة بالتتابع
        # ======================================
        st.divider()
        st.subheader("🎧 استمع إلى السورة")

        audio_ayahs = [
            ayah
            for ayah in surah["ayahs"]
            if ayah.get("audio")
        ]

        if audio_ayahs:
            audio_urls = [
                ayah["audio"]
                for ayah in audio_ayahs
            ]

            playlist_json = json.dumps(audio_urls)

            player_html = """
            <!DOCTYPE html>
            <html lang="ar">
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="
                font-family:sans-serif;
                direction:rtl;
                padding:10px;
            ">

                <div style="
                    text-align:center;
                    margin-bottom:12px;
                    font-weight:bold;
                ">
                    ★ OMAR MELIGY ★
                </div>

                <audio id="player"
                       controls
                       preload="none"
                       style="width:100%">
                </audio>

                <p id="status"
                   style="text-align:center">
                    اضغط تشغيل السورة للبدء
                </p>

                <button id="start"
                    style="
                        display:block;
                        margin:auto;
                        padding:10px 18px;
                        border:0;
                        border-radius:8px;
                        cursor:pointer;
                    ">
                    ▶ تشغيل السورة من البداية
                </button>

                <script>
                    const playlist = PLAYLIST_DATA;
                    const player = document.getElementById("player");
                    const status = document.getElementById("status");
                    const start = document.getElementById("start");

                    let currentIndex = 0;

                    function playVerse(index) {
                        if (index >= playlist.length) {
                            player.pause();
                            status.textContent = "✅ انتهت السورة كاملة";
                            return;
                        }

                        currentIndex = index;
                        player.src = playlist[currentIndex];

                        status.textContent =
                            "الآية " + (currentIndex + 1) +
                            " من " + playlist.length;

                        player.play().catch(function() {
                            status.textContent =
                                "اضغط زر التشغيل لمتابعة التلاوة";
                        });
                    }

                    start.addEventListener("click", function() {
                        playVerse(0);
                    });

                    player.addEventListener("ended", function() {
                        playVerse(currentIndex + 1);
                    });

                    player.addEventListener("error", function() {
                        status.textContent =
                            "تعذر تحميل الصوت. تحقق من اتصال الإنترنت.";
                    });

                    player.addEventListener("play", function() {
                        status.textContent =
                            "جارٍ تشغيل الآية " +
                            (currentIndex + 1) +
                            " من " + playlist.length;
                    });

                    player.src = playlist[0];
                </script>

            </body>
            </html>
            """.replace(
                "PLAYLIST_DATA",
                playlist_json,
            )

            components.html(
                player_html,
                height=200,
                scrolling=False,
            )

            # اختيار آية منفردة
            with st.expander("🔊 تشغيل آية محددة"):
                verse_options = {
                    ayah["numberInSurah"]: ayah["audio"]
                    for ayah in audio_ayahs
                }

                verse_number = st.selectbox(
                    "رقم الآية",
                    list(verse_options.keys()),
                    format_func=lambda n: f"الآية {n}",
                    key="selected_verse",
                )

                st.audio(verse_options[verse_number])

        else:
            st.warning(
                "لا توجد ملفات صوتية متاحة لهذه السورة."
            )

    except Exception as error:
        show_error(error)

# ==========================================
# قسم حصن المسلم
# ==========================================
elif section == "حصن المسلم":

    st.header("🤲 حصن المسلم")

    try:
        hisn_data = get_hisn()

        categories = {
            str(key): value
            for key, value in hisn_data.items()
            if isinstance(value, (dict, list))
        }

        if not categories:
            st.warning("لم يتم العثور على أبواب الأذكار.")

        else:
            category_name = st.selectbox(
                "اختر باب الأذكار",
                list(categories.keys()),
            )

            category = categories[category_name]
            dhikrs = []

            def extract_dhikr(title, item, depth=0):
                if depth > 8:
                    return

                if isinstance(item, str):
                    if item.strip():
                        dhikrs.append((title, item, ""))
                    return

                if isinstance(item, list):
                    for index, child in enumerate(item, 1):
                        extract_dhikr(
                            f"{title} {index}",
                            child,
                            depth + 1,
                        )
                    return

                if not isinstance(item, dict):
                    return

                text_value = (
                    item.get("ARABIC_TEXT")
                    or item.get("arabic_text")
                    or item.get("TEXT")
                    or item.get("text")
                    or item.get("content")
                )

                reference = (
                    item.get("REFERENCE")
                    or item.get("reference")
                    or item.get("source")
                    or ""
                )

                if isinstance(text_value, str) and text_value.strip():
                    title_value = (
                        item.get("TITLE")
                        or item.get("title")
                        or item.get("name")
                        or title
                    )

                    dhikrs.append(
                        (
                            str(title_value),
                            text_value,
                            str(reference),
                        )
                    )
                else:
                    for key, child in item.items():
                        if isinstance(child, (dict, list)):
                            extract_dhikr(
                                str(key),
                                child,
                                depth + 1,
                            )

            if isinstance(category, dict):
                entries = list(category.items())
            else:
                entries = [
                    (str(i + 1), item)
                    for i, item in enumerate(category)
                ]

            for title, item in entries:
                extract_dhikr(str(title), item)

            # إزالة التكرارات
            unique_dhikrs = []
            seen = set()

            for dhikr in dhikrs:
                signature = tuple(dhikr)

                if signature not in seen:
                    seen.add(signature)
                    unique_dhikrs.append(dhikr)

            if unique_dhikrs:
                chosen = st.selectbox(
                    "اختر الذكر",
                    range(len(unique_dhikrs)),
                    format_func=lambda i: unique_dhikrs[i][0],
                )

                title, dhikr_text, reference = unique_dhikrs[chosen]

                st.markdown(
                    '<div class="dhikr">'
                    + html.escape(dhikr_text).replace(
                        "\n", "<br>"
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

                if reference:
                    st.caption(f"المصدر: {reference}")

                st.text_area(
                    "النص للنسخ",
                    value=dhikr_text,
                    height=120,
                )

            else:
                st.warning(
                    "لم يتمكن التطبيق من استخراج الأذكار "
                    "من تنسيق البيانات الحالي."
                )

    except Exception as error:
        show_error(error)

# ==========================================
# حول التطبيق
# ==========================================
else:

    st.header("⭐ حول التطبيق")

    st.markdown("""
    **OMAR MELIGY**

    تطبيق عربي يضم:

    - القرآن الكريم.
    - اختيار القارئ.
    - تشغيل الآيات بالترتيب.
    - الاستماع إلى آية منفردة.
    - أذكار حصن المسلم.

    يحتاج التطبيق إلى اتصال بالإنترنت للحصول على
    نصوص القرآن والتسجيلات الصوتية والأذكار.
    """)

    st.caption("© OMAR MELIGY")
