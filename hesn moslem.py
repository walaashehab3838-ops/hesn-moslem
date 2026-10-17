
import html
import json
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم | OMAR MELIGY",
    page_icon="📖",
    layout="centered",
)

QURAN_API = "https://api.alquran.cloud/v1"
HISN_API = "https://www.hisnmuslim.com/api/ar/"

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
# التصميم والعلامة المائية في منتصف الشاشة
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.watermark {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    z-index: 0;
    pointer-events: none;
    user-select: none;
    text-align: center;
    opacity: 0.12;
    width: 90vw;
    max-width: 650px;
}

.watermark-star {
    color: #c9a227;
    font-size: clamp(65px, 12vw, 120px);
    line-height: 1.1;
    text-shadow: 0 0 12px #c9a22744;
}

.watermark-name {
    color: var(--text-color);
    font-family: Arial, sans-serif;
    font-weight: 900;
    font-size: clamp(27px, 6vw, 58px);
    letter-spacing: 3px;
    white-space: nowrap;
}

.stMainBlockContainer {
    position: relative;
    z-index: 1;
    background: transparent;
}

.arabic-quran {
    direction: rtl;
    text-align: justify;
    font-family: 'Amiri', serif;
    font-size: 27px;
    line-height: 2.3;
    padding: 18px;
    border: 1px solid #b99b4b55;
    border-radius: 14px;
    background: transparent;
}

.dhikr {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', serif;
    font-size: 23px;
    line-height: 2.1;
    padding: 16px;
    border: 1px solid #b99b4b55;
    border-radius: 12px;
    margin: 10px 0;
    background: transparent;
}

.app-heading {
    text-align: center;
    font-weight: bold;
}

@media (max-width: 600px) {
    .arabic-quran { font-size: 22px; }
    .dhikr { font-size: 20px; }
    .watermark-name { letter-spacing: 1px; }
}
</style>

<div class="watermark" aria-hidden="true">
    <div class="watermark-star">★</div>
    <div class="watermark-name">OMAR MELIGY</div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    '<h1 class="app-heading">📖 القرآن الكريم وحصن المسلم</h1>',
    unsafe_allow_html=True,
)
st.caption("تلاوة القرآن الكريم والأذكار اليومية")

# ==========================================
# جلب بيانات القرآن
# ==========================================
@st.cache_data(ttl=43200)
def get_surahs():
    r = requests.get(f"{QURAN_API}/surah", timeout=25)
    r.raise_for_status()
    data = r.json()

    if data.get("code") != 200:
        raise ValueError("تعذر تحميل قائمة السور")

    return data["data"]


@st.cache_data(ttl=43200)
def get_surah(number, reciter_id):
    r = requests.get(
        f"{QURAN_API}/surah/{number}/{reciter_id}",
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    if data.get("code") != 200:
        raise ValueError("تعذر تحميل السورة بهذا القارئ")

    return data["data"]


# ==========================================
# جلب جميع بيانات حصن المسلم
# ==========================================
@st.cache_data(ttl=86400)
def get_hisn():
    r = requests.get(HISN_API, timeout=30)
    r.raise_for_status()
    data = r.json()

    if not isinstance(data, dict):
        raise ValueError("تنسيق بيانات الأذكار غير متوقع")

    return data


# ==========================================
# استخراج الأذكار من مختلف أشكال البيانات
# ==========================================
TEXT_KEYS = (
    "ARABIC_TEXT",
    "arabic_text",
    "TEXT",
    "text",
    "content",
    "dhikr",
)

TITLE_KEYS = (
    "TITLE",
    "title",
    "name",
    "NAME",
)

REFERENCE_KEYS = (
    "REFERENCE",
    "reference",
    "source",
    "SOURCE",
)

def first_value(item, keys):
    for key in keys:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_dhikr_records(data):
    records = []
    seen = set()

    def walk(node, path="", depth=0):
        if depth > 15:
            return

        if isinstance(node, list):
            for index, child in enumerate(node, start=1):
                walk(child, f"{path} - {index}".strip(" -"), depth + 1)
            return

        if not isinstance(node, dict):
            return

        text_value = first_value(node, TEXT_KEYS)

        if text_value:
            title = first_value(node, TITLE_KEYS) or path or "ذكر"
            reference = first_value(node, REFERENCE_KEYS)

            # منع تكرار الذكر نفسه
            signature = (title, text_value, reference)

            if signature not in seen:
                seen.add(signature)
                records.append({
                    "category": path or "أذكار متنوعة",
                    "title": title,
                    "text": text_value,
                    "reference": reference,
                })

            # لا نكرر البحث داخل النص الذي تم استخراجه
            for key, child in node.items():
                if key not in TEXT_KEYS and isinstance(child, (dict, list)):
                    walk(child, str(key), depth + 1)
            return

        for key, child in node.items():
            if isinstance(child, (dict, list)):
                next_path = f"{path} / {key}".strip(" /")
                walk(child, next_path, depth + 1)

    walk(data)
    return records


# ==========================================
# قائمة الأقسام
# ==========================================
section = st.sidebar.radio(
    "اختر القسم",
    ["القرآن الكريم", "حصن المسلم", "حول التطبيق"],
)

# ==========================================
# القرآن الكريم
# ==========================================
if section == "القرآن الكريم":
    st.header("🕌 القرآن الكريم")

    try:
        surahs = get_surahs()

        surah_options = {
            f'{s["number"]} - {s["name"]}': s["number"]
            for s in surahs
        }

        selected_surah = st.selectbox(
            "اختر السورة",
            list(surah_options.keys()),
        )

        reciter_name = st.selectbox(
            "🎙️ اختر القارئ",
            list(RECITERS.keys()),
        )

        with st.spinner("جارٍ تحميل السورة..."):
            surah = get_surah(
                surah_options[selected_surah],
                RECITERS[reciter_name],
            )

        st.subheader(surah["name"])
        st.caption(
            f'عدد الآيات: {surah["numberOfAyahs"]} | القارئ: {reciter_name}'
        )

        verses = [
            f'{html.escape(a["text"])} ﴿{a["numberInSurah"]}﴾'
            for a in surah["ayahs"]
        ]

        st.markdown(
            '<div class="arabic-quran">'
            + " ۞ ".join(verses)
            + "</div>",
            unsafe_allow_html=True,
        )

        st.divider()
        st.subheader("🎧 استمع إلى السورة")

        audio_ayahs = [
            a for a in surah["ayahs"] if a.get("audio")
        ]

        if audio_ayahs:
            playlist_json = json.dumps(
                [a["audio"] for a in audio_ayahs]
            )

            player_html = """
            <html lang="ar">
            <body style="font-family:sans-serif;direction:rtl;padding:8px">
                <audio id="player" controls
                       preload="none" style="width:100%"></audio>
                <p id="status">اضغط تشغيل السورة للبدء</p>
                <button id="start">▶ تشغيل السورة من البداية</button>
                <script>
                    const urls = PLAYLIST_DATA;
                    const player = document.getElementById("player");
                    const status = document.getElementById("status");
                    let index = 0;

                    function playAt(i) {
                        if (i >= urls.length) {
                            player.pause();
                            status.textContent = "✅ انتهت السورة كاملة";
                            return;
                        }

                        index = i;
                        player.src = urls[index];
                        status.textContent =
                            "الآية " + (index + 1) + " من " + urls.length;

                        player.play().catch(() => {
                            status.textContent =
                                "اضغط تشغيل لمتابعة التلاوة";
                        });
                    }

                    document.getElementById("start").onclick = () => playAt(0);
                    player.addEventListener("ended", () => playAt(index + 1));
                    player.addEventListener("error", () => {
                        status.textContent = "تعذر تحميل ملف الصوت";
                    });

                    player.src = urls[0];
                </script>
            </body>
            </html>
            """.replace("PLAYLIST_DATA", playlist_json)

            components.html(player_html, height=150)

            with st.expander("🔊 تشغيل آية محددة"):
                audio_map = {
                    a["numberInSurah"]: a["audio"]
                    for a in audio_ayahs
                }

                verse_num = st.selectbox(
                    "رقم الآية",
                    list(audio_map.keys()),
                    format_func=lambda n: f"الآية {n}",
                )
                st.audio(audio_map[verse_num])

        else:
            st.warning("لا توجد تسجيلات صوتية متاحة حاليًا.")

    except Exception as e:
        st.error(f"تعذر تحميل القرآن: {e}")


# ==========================================
# حصن المسلم - جميع الأذكار المتاحة
# ==========================================
elif section == "حصن المسلم":
    st.header("🤲 حصن المسلم")
    st.write("ابحث في الأذكار واختر الباب أو الذكر الذي تريد قراءته.")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            hisn_data = get_hisn()

        records = extract_dhikr_records(hisn_data)

        if not records:
            st.warning(
                "لم نتمكن من استخراج الأذكار من الخدمة الحالية. "
                "قد يكون تنسيق بيانات المصدر قد تغير."
            )
        else:
            st.success(f"تم استخراج {len(records)} ذكرًا من المصدر.")

            search = st.text_input(
                "🔎 ابحث في الأذكار",
                placeholder="مثال: الصباح، المساء، النوم...",
            ).strip()

            # تحديد الأبواب المتاحة بحسب بيانات المصدر
            categories = sorted({
                record["category"] for record in records
            })

            selected_category = st.selectbox(
                "📚 اختر باب الأذكار",
                ["جميع الأبواب"] + categories,
            )

            filtered = records

            if selected_category != "جميع الأبواب":
                filtered = [
                    r for r in filtered
                    if r["category"] == selected_category
                ]

            if search:
                filtered = [
                    r for r in filtered
                    if search in r["title"]
                    or search in r["text"]
                    or search in r["category"]
                ]

            st.caption(f"عدد النتائج: {len(filtered)}")

            if not filtered:
                st.info("لا توجد نتائج مطابقة لبحثك.")
            else:
                # عرض كل الأذكار المطابقة على صفحات
                page_size = 20
                total_pages = max(
                    1,
                    (len(filtered) + page_size - 1) // page_size,
                )

                page = st.number_input(
                    "صفحة الأذكار",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    step=1,
                )

                start = (int(page) - 1) * page_size
                end = start + page_size

                for number, record in enumerate(
                    filtered[start:end],
                    start=start + 1,
                ):
                    with st.container():
                        st.markdown(
                            f"**{number}. {html.escape(record['title'])}**"
                        )

                        st.markdown(
                            '<div class="dhikr">'
                            + html.escape(record["text"]).replace(
                                "\n", "<br>"
                            )
                            + "</div>",
                            unsafe_allow_html=True,
                        )

                        if record["reference"]:
                            st.caption(
                                "المصدر: " + record["reference"]
                            )

                        with st.expander("نسخ أو عرض نص الذكر"):
                            st.text_area(
                                "النص",
                                value=record["text"],
                                height=100,
                                key=f"dhikr_text_{number}",
                            )

                        st.divider()

                if total_pages > 1:
                    st.caption(
                        f"صفحة {int(page)} من {total_pages}. "
                        "غيّر رقم الصفحة لعرض بقية الأذكار."
                    )

    except Exception as e:
        st.error(f"تعذر تحميل الأذكار: {e}")
        st.info(
            "تحقق من اتصال الإنترنت، فقد تكون خدمة الأذكار "
            "غير متاحة مؤقتًا."
        )

# ==========================================
# حول التطبيق
# ==========================================
else:
    st.header("⭐ OMAR MELIGY")
    st.markdown("""
    تطبيق القرآن الكريم وحصن المسلم، ويحتوي على:

    - اختيار السورة والقارئ.
    - قراءة آيات القرآن الكريم.
    - تشغيل التلاوة بالتتابع.
    - تصفح الأذكار والبحث فيها.
    - علامة مائية باسم OMAR MELIGY في منتصف الشاشة.
    """)

    st.caption("© OMAR MELIGY")
