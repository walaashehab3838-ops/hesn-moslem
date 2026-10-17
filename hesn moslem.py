import streamlit as st
import requests
from html import escape

st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="📖",
    layout="centered"
)

st.title("📖 القرآن الكريم وحصن المسلم")

API = "https://api.alquran.cloud/v1"

@st.cache_data
def get_surahs():
    r = requests.get(f"{API}/surah", timeout=20)
    r.raise_for_status()
    return r.json()["data"]

@st.cache_data
def get_quran_surah(number):
    r = requests.get(
        f"{API}/surah/{number}/ar.alafasy",
        timeout=30
    )
    r.raise_for_status()
    return r.json()["data"]

# اختيار القسم
section = st.sidebar.radio(
    "اختار القسم",
    ["القرآن الكريم", "حصن المسلم"]
)

if section == "القرآن الكريم":
    st.header("🕌 القرآن الكريم")

    try:
        surahs = get_surahs()
        names = {
            f'{s["number"]}. {s["name"]}': s["number"]
            for s in surahs
        }

        selected = st.selectbox(
            "اختار السورة",
            list(names.keys())
        )
        number = names[selected]

        surah = get_quran_surah(number)

        st.subheader(surah["name"])
        st.caption(f'عدد الآيات: {surah["numberOfAyahs"]}')

        # عرض جميع الآيات
        verses = " ۞ ".join(
            f'{a["text"]} ﴿{a["numberInSurah"]}﴾'
            for a in surah["ayahs"]
        )

        st.markdown(
            "<div dir='rtl' style='text-align:right;"
            "font-size:25px;line-height:2.2'>"
            + escape(verses) +
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()
        st.subheader("🎧 الاستماع للقرآن")

        audio_urls = [
            a["audio"] for a in surah["ayahs"]
            if a.get("audio")
        ]

        if audio_urls:
            st.write("اختار آية للاستماع إليها:")
            verse_number = st.selectbox(
                "رقم الآية",
                range(1, len(audio_urls) + 1)
            )
            st.audio(audio_urls[verse_number - 1])

            st.caption(
                "لتشغيل السورة كاملة بالترتيب، استخدم "
                "مشغّل السورة الكامل أدناه."
            )

            # مشغل متتابع لجميع الآيات
            playlist_json = __import__("json").dumps(
                audio_urls
            )
            player = """
            <div dir="rtl" style="font-family:sans-serif">
              <p>تشغيل السورة كاملة بالترتيب</p>
              <audio id="quranPlayer" controls
                     style="width:100%"></audio>
              <p id="quranStatus">جاهز للتشغيل</p>
              <script>
                const urls = PLAYLIST;
                const audio = document.getElementById("quranPlayer");
                const status = document.getElementById("quranStatus");
                let index = 0;

                function playVerse(i) {
                  if (i >= urls.length) {
                    status.textContent = "انتهت السورة";
                    return;
                  }
                  index = i;
                  audio.src = urls[index];
                  status.textContent =
                    "الآية " + (index + 1) + " من " + urls.length;
                  audio.play().catch(() => {
                    status.textContent =
                      "اضغط تشغيل لبدء الاستماع";
                  });
                }

                audio.addEventListener("ended", () => {
                  playVerse(index + 1);
                });

                playVerse(0);
              </script>
            </div>
            """.replace("PLAYLIST", playlist_json)

            st.components.v1.html(player, height=130)

    except Exception as e:
        st.error("تعذر تحميل القرآن. تأكد من اتصال الإنترنت.")
        st.caption(st
