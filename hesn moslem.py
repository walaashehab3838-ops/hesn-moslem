
import html
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="centered",
)

QURAN_API = "https://api.alquran.cloud/v1"
HISN_API = "https://www.hisnmuslim.com/api/ar/"

# =========================
# تصميم الواجهة
# =========================
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
st.caption("تلاوة القرآن الكريم والأذكار اليومية")

# =========================
# جلب بيانات القرآن
# =========================
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


# =========================
# جلب بيانات حصن المسلم
# =========================
@st.cache_data(ttl=86400)
def get_hisn():
    response = requests.get(HISN_API, timeout=25)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("تنسيق بيانات الأذكار غير متوقع")

    return data


# =========================
# رسائل الأخطاء
# =========================
def show_error(error):
    if isinstance(error, requests.exceptions.Timeout):
        st.error("انتهت مهلة الاتصال. حاول مرة أخرى.")
    elif isinstance(error, requests.exceptions.ConnectionError):
        st.error("تعذر الاتصال بالإنترنت.")
    elif isinstance(error, requests.exceptions.HTTPError):
        st.error("خدمة البيانات غير متاحة حاليًا.")
    else:
        st.error("حدث خطأ أثناء تحميل البيانات.")


# =========================
# القائمة الرئيسية
# =========================
section = st.sidebar.radio(
    "اختر القسم",
    [
        "القرآن الكريم",
        "حصن المسلم",
        "حول التطبيق",
    ],
)

# =========================
# قسم القرآن الكريم
# =========================
if section == "القرآن الكريم":
    st.header("🕌 القرآن الكريم")

    try:
        with st.spinner("جارٍ تحميل السور..."):
            surahs = get_surahs()

        labels = {
            f'{s["number"]}. {s["name"]}': s["number"]
            for s in surahs
        }

        selected = st.selectbox(
            "اختر السورة",
            list(labels.keys()),
        )

        number = labels[selected]

        with st.spinner("جارٍ تحميل الآيات..."):
            surah = get_surah(number)

        st.subheader(surah["name"])
        st.caption(
            f'عدد الآيات: {surah["numberOfAyahs"]}'
        )

        # عرض آيات السورة
        verses = []

        for ayah in surah["ayahs"]:
            text = html.escape(ayah["text"])
            verse_number = ayah["numberInSurah"]

            verses.append(
                f'{text} ﴿{verse_number}﴾'
            )

        st.markdown(
            '<div class="arabic-quran" dir="rtl">'
            + " ۞ ".join(verses)
            + "</div>",
            unsafe_allow_html=True,
        )

        # =========================
        # مشغل الصوت
        # =========================
        st.divider()
        st.subheader("🎧 الاستماع إلى القرآن")

        audio_ayahs = [
            ayah for ayah in surah["ayahs"]
            if ayah.get("audio")
        ]

        if audio_ayahs:
            audio_map = {
                ayah["numberInSurah"]: ayah["audio"]
                for ayah in audio_ayahs
            }

            selected_verse = st.selectbox(
                "اختر رقم الآية",
                list(audio_map.keys()),
                format_func=lambda n: f"الآية {n}",
                key="single_verse",
            )

            st.audio(audio_map[selected_verse])

            st.markdown("**تشغيل آيات السورة بالتتابع**")
            st.caption(
                "اضغط زر التشغيل لبدء التلاوة. "
                "سيحاول المشغّل الانتقال إلى الآية التالية تلقائيًا."
            )

            playlist = json.dumps(
                [a["audio"] for a in audio_ayahs],
                ensure_ascii=True,
            )

            player_html = """
            <div dir="rtl"
                 style="font-family:sans-serif;padding:8px">
              <audio id="player" controls
                     preload="none"
                     style="width:100%"></audio>
              <p id="status">جاهز للتشغيل</p>

              <script>
                const urls = PLAYLIST_DATA;
                const player = document.getElementById("player");
                const status = document.getElementById("status");
                let index = 0;

                function loadVerse(i, autoplay) {
                  if (i >= urls.length) {
                    status.textContent = "انتهت السورة.";
                    player.pause();
                    return;
                  }

                  index = i;
                  player.src = urls[index];
                  status.textContent =
                    "الآية " + (index + 1) +
                    " من " + urls.length;

                  if (autoplay) {
                    player.play().catch(() => {
                      status.textContent =
                        "اضغط تشغيل لمتابعة التلاوة.";
                    });
                  }
                }

                player.addEventListener("ended", function() {
                  loadVerse(index + 1, true);
                });

                player.addEventListener("error", function() {
                  status.textContent =
                    "تعذر تحميل الصوت. تحقق من الإنترنت.";
                });

                loadVerse(0, false);
              </script>
            </div>
            """.replace("PLAYLIST_DATA", playlist)

            components.html(
                player_html,
                height=115,
                scrolling=False,
            )
        else:
            st.warning("لا تتوفر روابط صوتية لهذه السورة.")

    except Exception as error:
        show_error(error)

        if st.button("إعادة المحاولة"):
            st.cache_data.clear()
            st.rerun()


# =========================
# قسم حصن المسلم
# =========================
elif section == "حصن المسلم":
    st.header("🤲 حصن المسلم")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            hisn_data = get_hisn()

        categories = {
            str(name): value
            for name, value in hisn_data.items()
            if isinstance(value, (list, dict))
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
                items = list(category.items())
            else:
                items = [
                    (str(i + 1), item)
                    for i, item in enumerate(category)
                ]

            # استخراج النصوص من تنسيقات JSON الشائعة
            dhikrs = []

            def extract_dhikr(title, item):
                if isinstance(item, str):
                    dhikrs.append((title, item, ""))
                    return

                if isinstance(item, list):
                    for i, child in enumerate(item, 1):
                        extract_dhikr(f"{title} {i}", child)
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
                    title = (
                        item.get("TITLE")
                        or item.get("title")
                        or item.get("name")
                        or title
                    )
                    dhikrs.append(
                        (str(title), text, str(reference))
                    )
                else:
                    for key, child in item.items():
                        if isinstance(child, (dict, list, str)):
                            extract_dhikr(str(key), child)

            for title, item in items:
                extract_dhikr(str(title), item)

            # إزالة التكرارات الناتجة عن اختلاف شكل البيانات
            unique_dhikrs = []
            seen = set()

            for item in dhikrs:
                signature = (item[0], item[1], item[2])
                if signature not in seen:
                    seen.add(signature)
                    unique_dhikrs.append(item)

            if unique_dhikrs:
                choice = st.selectbox(
                    "اختر الذكر",
                    range(len(unique_dhikrs)),
                    format_func=lambda i: unique_dhikrs[i][0],
                )

                title, dhikr_text, reference = unique_dhikrs[choice]

                st.markdown(
                    '<div class="dhikr" dir="rtl">'
                    + html.escape(dhikr_text).replace(
                        "\n", "<br>"
                    )
                    + "</div>",
                    unsafe_allow_html=True,
                )

                if reference:
                    st.caption(f"المصدر: {reference}")

                st.text_area(
                    "نص الذكر للنسخ",
                    value=dhikr_text,
                    height=120,
                )
            else:
                st.warning(
                    "وصلت البيانات، لكن تعذر استخراج نصوص الأذكار. "
                    "قد يكون تنسيق الخدمة قد تغير."
                )

    except Exception as error:
        show_error(error)
        st.info(
            "يعتمد قسم حصن المسلم على خدمة خارجية. "
            "إذا استمر الخطأ، فقد تكون الخدمة غير متاحة "
            "أو تغير عنوانها أو تنسيق بياناتها."
        )

        if st.button("إعادة تحميل الأذكار"):
            get_hisn.clear()
            st.rerun()


# =========================
# حول التطبيق
# =========================
else:
    st.header("ℹ️ حول التطبيق")

    st.markdown("""
    يوفر التطبيق:

    - قراءة سور القرآن الكريم وآياتها.
    - الاستماع إلى آية محددة.
    - تشغيل آيات السورة بالتتابع.
    - تصفح أبواب الأذكار في حصن المسلم.

    **ملاحظات:**

    - يحتاج التطبيق إلى الإنترنت لتحميل المحتوى.
    - قد تتغير خدمات البيانات الخارجية أو تتوقف.
    - قد يمنع المتصفح تشغيل الصوت تلقائيًا.
    - يُستحسن مراجعة مصادر الأذكار عند الحاجة إلى التحقق.
    """)

    st.caption("بُني باستخدام Python وStreamlit.")
