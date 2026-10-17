
import html
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# =====================================
# إعدادات التطبيق
# =====================================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="centered",
)

QURAN_API = "https://api.alquran.cloud/v1"
HISN_API = "https://www.hisnmuslim.com/api/ar/"

# =====================================
# تنسيق الواجهة
# =====================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.arabic-quran {
    direction: rtl;
    text-align: justify;
    font-family: 'Amiri', serif;
    font-size: 27px;
    line-height: 2.3;
}

.dhikr {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', serif;
    font-size: 23px;
    line-height: 2.1;
    padding: 18px;
    border: 1px solid #9995;
    border-radius: 12px;
    margin: 12px 0;
}

h1, h2, h3 {
    text-align: center;
}

@media (max-width: 600px) {
    .arabic-quran { font-size: 23px; }
    .dhikr { font-size: 20px; }
}
</style>
""", unsafe_allow_html=True)

st.title("📖 القرآن الكريم وحصن المسلم")
st.caption("اقرأ القرآن الكريم واستمع للتلاوة وتصفح الأذكار")

# =====================================
# تحميل بيانات القرآن
# =====================================
@st.cache_data(ttl=43200)
def get_surahs():
    response = requests.get(
        f"{QURAN_API}/surah",
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["data"]


@st.cache_data(ttl=43200)
def get_surah(number):
    response = requests.get(
        f"{QURAN_API}/surah/{number}/ar.alafasy",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"]


# =====================================
# تحميل بيانات حصن المسلم
# =====================================
@st.cache_data(ttl=86400)
def get_hisn():
    response = requests.get(HISN_API, timeout=25)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("تنسيق بيانات الأذكار غير متوقع")

    return data


# =====================================
# معالجة أخطاء الاتصال
# =====================================
def show_error(error):
    if isinstance(error, requests.exceptions.Timeout):
        st.error("انتهت مهلة الاتصال. حاول مرة أخرى.")
    elif isinstance(error, requests.exceptions.ConnectionError):
        st.error("تعذر الاتصال بالإنترنت.")
    elif isinstance(error, requests.exceptions.HTTPError):
        st.error("الخدمة غير متاحة حاليًا.")
    else:
        st.error("حدث خطأ أثناء تحميل البيانات.")


# =====================================
# القائمة الجانبية
# =====================================
section = st.sidebar.radio(
    "اختر القسم",
    [
        "القرآن الكريم",
        "حصن المسلم",
        "حول التطبيق",
    ],
)

# =====================================
# قسم القرآن الكريم
# =====================================
if section == "القرآن الكريم":

    st.header("🕌 القرآن الكريم")

    try:
        with st.spinner("جارٍ تحميل السور..."):
            surahs = get_surahs()

        surah_options = {
            f'{s["number"]}. {s["name"]}': s["number"]
            for s in surahs
        }

        selected_surah = st.selectbox(
            "اختر السورة",
            list(surah_options.keys()),
        )

        surah_number = surah_options[selected_surah]

        with st.spinner("جارٍ تحميل السورة..."):
            surah = get_surah(surah_number)

        st.subheader(surah["name"])

        st.caption(
            f'عدد الآيات: {surah["numberOfAyahs"]}'
        )

        # عرض جميع الآيات
        verses = []

        for ayah in surah["ayahs"]:
            verse_text = html.escape(ayah["text"])
            verse_number = ayah["numberInSurah"]

            verses.append(
                f"{verse_text} ﴿{verse_number}﴾"
            )

        st.markdown(
            '<div class="arabic-quran" dir="rtl">'
            + " ۞ ".join(verses)
            + "</div>",
            unsafe_allow_html=True,
        )

        # =====================================
        # مشغل السورة كاملة بالتتابع
        # =====================================
        st.divider()
        st.subheader("🎧 استمع إلى السورة كاملة")

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

            playlist_json = json.dumps(
                audio_urls,
                ensure_ascii=True,
            )

            player_html = """
            <!DOCTYPE html>
            <html lang="ar">
            <head>
              <meta charset="UTF-8">
            </head>

            <body style="
                font-family:sans-serif;
                direction:rtl;
                margin:0;
                padding:10px;
            ">

              <h3>مشغل القرآن الكريم</h3>

              <audio
                id="quranPlayer"
                controls
                preload="none"
                style="width:100%">
              </audio>

              <p
                id="quranStatus"
                aria-live="polite">
                اضغط تشغيل لبدء السورة
              </p>

              <button
                id="startButton"
                style="
                  padding:10px 18px;
                  border:0;
                  border-radius:8px;
                  cursor:pointer;
                ">
                ▶ تشغيل السورة من البداية
              </button>

              <script>
                const urls = PLAYLIST_DATA;

                const audio =
                    document.getElementById("quranPlayer");

                const status =
                    document.getElementById("quranStatus");

                const startButton =
                    document.getElementById("startButton");

                let index = 0;

                function loadVerse(i, autoplay) {
                    if (i >= urls.length) {
                        audio.pause();
                        status.textContent =
                            "✅ انتهت السورة كاملة";
                        return;
                    }

                    index = i;
                    audio.src = urls[index];

                    status.textContent =
                        "الآية " + (index + 1) +
                        " من " + urls.length;

                    if (autoplay) {
                        audio.play().catch(() => {
                            status.textContent =
                                "اضغط تشغيل لمتابعة التلاوة";
                        });
                    }
                }

                startButton.addEventListener(
                    "click",
                    function() {
                        loadVerse(0, true);
                    }
                );

                audio.addEventListener(
                    "ended",
                    function() {
                        loadVerse(index + 1, true);
                    }
                );

                audio.addEventListener(
                    "error",
                    function() {
                        status.textContent =
                            "تعذر تحميل الصوت. تحقق من الإنترنت.";
                    }
                );

                audio.addEventListener(
                    "play",
                    function() {
                        status.textContent =
                            "جارٍ تشغيل الآية " + (index + 1) +
                            " من " + urls.length;
                    }
                );

                loadVerse(0, false);
              </script>

            </body>
            </html>
            """.replace(
                "PLAYLIST_DATA",
                playlist_json,
            )

            components.html(
                player_html,
                height=190,
                scrolling=False,
            )

            st.caption(
                "ينتقل المشغل تلقائيًا إلى الآية التالية "
                "حتى نهاية السورة، إذا توفرت ملفات الصوت."
            )

            # تشغيل آية منفردة عند الحاجة
            with st.expander("الاستماع إلى آية محددة"):
                audio_map = {
                    ayah["numberInSurah"]: ayah["audio"]
                    for ayah in audio_ayahs
                }

                selected_verse = st.selectbox(
                    "رقم الآية",
                    list(audio_map.keys()),
                    format_func=lambda n: f"الآية {n}",
                    key="single_verse",
                )

                st.audio(audio_map[selected_verse])

        else:
            st.warning(
                "لا تتوفر ملفات صوتية لهذه السورة حاليًا."
            )

    except Exception as error:
        show_error(error)

        if st.button("إعادة المحاولة"):
            st.cache_data.clear()
            st.rerun()


# =====================================
# قسم حصن المسلم
# =====================================
elif section == "حصن المسلم":

    st.header("🤲 حصن المسلم")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            data = get_hisn()

        categories = {
            str(name): value
            for name, value in data.items()
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

            if isinstance(category, dict):
                entries = list(category.items())
            else:
                entries = [
                    (str(i + 1), item)
                    for i, item in enumerate(category)
                ]

            dhikrs = []

            def extract_dhikr(title, item, depth=0):
                # حماية من التداخل غير المتوقع
                if depth > 8:
                    return

                if isinstance(item, str):
                    if item.strip():
                        dhikrs.append((title, item, ""))
                    return

                if isinstance(item, list):
                    for i, child in enumerate(item, 1):
                        extract_dhikr(
                            f"{title} {i}",
                            child,
                            depth + 1,
                        )
                    return

                if not isinstance(item, dict):
                    return

                text = (
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

                if isinstance(text, str) and text.strip():
                    display_title = (
                        item.get("TITLE")
                        or item.get("title")
                        or item.get("name")
                        or title
                    )

                    dhikrs.append(
                        (
                            str(display_title),
                            text,
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

            for title, item in entries:
                extract_dhikr(str(title), item)

            # إزالة التكرارات
            unique_dhikrs = []
            seen = set()

            for item in dhikrs:
                signature = tuple(item)

                if signature not in seen:
                    seen.add(signature)
                    unique_dhikrs.append(item)

            if unique_dhikrs:
                selected_index = st.selectbox(
                    "اختر الذكر",
                    range(len(unique_dhikrs)),
                    format_func=lambda i: (
                        unique_dhikrs[i][0]
                    ),
                )

                title, text, reference = (
                    unique_dhikrs[selected_index]
                )

                st.markdown(
                    '<div class="dhikr" dir="rtl">'
                    + html.escape(text).replace(
                        "\n", "<br>"
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

                if reference:
                    st.caption(f"المصدر: {reference}")

                st.text_area(
                    "نص الذكر للنسخ",
                    value=text,
                    height=120,
                )

            else:
                st.warning(
                    "تم الاتصال بمصدر الأذكار، لكن تعذر "
                    "استخراج النصوص. قد يكون تنسيق البيانات "
                    "الخارجية قد تغير."
                )

    except Exception as error:
        show_error(error)

        st.info(
            "يعتمد هذا القسم على خدمة خارجية. "
            "قد تكون الخدمة غير متاحة أو تغير تنسيق بياناتها."
        )

        if st.button("إعادة تحميل الأذكار"):
            get_hisn.clear()
            st.rerun()


# =====================================
# حول التطبيق
# =====================================
else:

    st.header("ℹ️ حول التطبيق")

    st.markdown("""
    ### مميزات التطبيق

    - عرض سور القرآن الكريم وآياتها.
    - الاستماع إلى آية محددة.
    - تشغيل السورة بالترتيب حتى نهايتها.
    - تصفح أبواب الأذكار في حصن المسلم.
    - واجهة عربية متوافقة مع أحجام الشاشات المختلفة.

    ### ملاحظات

    - يحتاج التطبيق إلى اتصال بالإنترنت.
    - يعتمد الصوت على خدمة خارجية.
    - قد تتوقف الخدمة أو تتغير روابط الصوت.
    - إذا تعذر تحميل إحدى الآيات، فقد يتوقف التسلسل عندها.
    """)

    st.caption("تم تطوير التطبيق باستخدام Python وStreamlit.")
