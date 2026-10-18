import html
import requests
import streamlit as st
import streamlit.components.v1 as components

# القرآن الكريم وحصن المسلم — OMAR MELIGY
st.set_page_config(
    page_title="القرآن الكريم وحصن المسلم",
    page_icon="☪️",
    layout="wide",
)

API_BASE = "https://api.alquran.cloud/v1"

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
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل",
    "الإسراء", "الكهف", "مريم", "طه", "الأنبياء", "الحج",
    "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل",
    "القصص", "العنكبوت", "الروم", "لقمان", "السجدة",
    "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص",
    "الزمر", "غافر", "فصلت", "الشورى", "الزخرف",
    "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح",
    "الحجرات", "ق", "الذاريات", "الطور", "النجم", "القمر",
    "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر",
    "الممتحنة", "الصف", "الجمعة", "المنافقون", "التغابن",
    "الطلاق", "التحريم", "الملك", "القلم", "الحاقة",
    "المعارج", "نوح", "الجن", "المزمل", "المدثر",
    "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات",
    "عبس", "التكوير", "الانفطار", "المطففين", "الانشقاق",
    "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر",
    "البلد", "الشمس", "الليل", "الضحى", "الشرح", "التين",
    "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل",
    "قريش", "الماعون", "الكوثر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس",
]

AZKAR = [
    (
        "أذكار الصباح والمساء",
        [
            (
                "أصبحنا وأصبح الملك لله، والحمد لله، لا إله إلا الله "
                "وحده لا شريك له، له الملك وله الحمد وهو على كل شيء قدير. "
                "رب أسألك خير ما في هذا اليوم وخير ما بعده، وأعوذ بك من "
                "شر ما في هذا اليوم وشر ما بعده.",
                1,
            ),
            (
                "اللهم بك أصبحنا وبك أمسينا وبك نحيا وبك نموت وإليك النشور.",
                1,
            ),
            (
                "رضيت بالله ربًا، وبالإسلام دينًا، وبمحمد ﷺ نبيًا.",
                3,
            ),
            ("سبحان الله وبحمده.", 100),
            ("أستغفر الله وأتوب إليه.", 100),
        ],
    ),
    (
        "أذكار بعد الصلاة",
        [
            ("أستغفر الله.", 3),
            (
                "اللهم أنت السلام ومنك السلام، تباركت يا ذا الجلال والإكرام.",
                1,
            ),
            ("سبحان الله.", 33),
            ("الحمد لله.", 33),
            ("الله أكبر.", 34),
        ],
    ),
    (
        "أذكار النوم",
        [
            ("باسمك اللهم أموت وأحيا.", 1),
            ("اللهم قني عذابك يوم تبعث عبادك.", 3),
            ("سبحان الله.", 33),
            ("الحمد لله.", 33),
            ("الله أكبر.", 34),
        ],
    ),
    (
        "أذكار الاستيقاظ",
        [
            (
                "الحمد لله الذي أحيانا بعدما أماتنا وإليه النشور.",
                1,
            ),
            (
                "لا إله إلا الله وحده لا شريك له، له الملك وله الحمد "
                "وهو على كل شيء قدير، سبحان الله، والحمد لله، ولا إله "
                "إلا الله، والله أكبر، ولا حول ولا قوة إلا بالله.",
                1,
            ),
        ],
    ),
]

# -------------------- التصميم --------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background: linear-gradient(
            180deg,
            #f7fbf5 0%,
            #eef5e9 100%
        );
    }

    .block-container {
        max-width: 1150px;
        padding-top: 1.4rem;
    }

    .hero {
        background: linear-gradient(135deg, #0b5137, #16734c);
        color: #fff;
        border: 1px solid #c5a34a;
        border-radius: 22px;
        padding: 28px 20px;
        text-align: center;
        box-shadow: 0 8px 25px #164b2a18;
    }

    .hero h1 {
        color: #f5d779;
        font-family: 'Amiri', serif;
        font-size: 2.5rem;
        margin: 0 0 8px;
    }

    .hero p {
        margin: 0;
        font-size: 1rem;
    }

    .section-title {
        color: #14583b;
        font-family: 'Amiri', serif;
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
        margin: 10px 0 18px;
    }

    .ayah-card {
        background: #fffef8;
        border: 1px solid #e4d7a7;
        border-right: 5px solid #c8a548;
        border-radius: 13px;
        padding: 16px 18px;
        margin: 10px 0;
        color: #173c2b;
        text-align: justify;
        line-height: 2.2;
        font-family: 'Amiri', serif;
        font-size: 1.55rem;
        direction: rtl;
    }

    .ayah-number {
        color: #9a7620;
        white-space: nowrap;
        font-size: 1.1rem;
        margin-right: 8px;
    }

    .zikr-card {
        background: #fffef8;
        border: 1px solid #e4d7a7;
        border-radius: 15px;
        padding: 18px;
        margin: 10px 0;
        color: #173c2b;
        line-height: 2;
        font-size: 1.15rem;
    }

    .footer {
        text-align: center;
        color: #e8d17a;
        background: #104b35;
        border-radius: 16px;
        padding: 22px 12px;
        margin-top: 30px;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #c8a548;
        font-weight: 700;
    }

    [data-testid="stSidebar"] {
        background: #e8f1e5;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- تحميل السور --------------------

@st.cache_data(ttl=3600, show_spinner=False)
def load_surah(number: int):
    response = requests.get(
        f"{API_BASE}/surah/{number}",
        timeout=20,
    )
    response.raise_for_status()

    payload = response.json()

    if payload.get("code") != 200:
        raise ValueError(
            "تعذر تحميل السورة من مصدر القرآن الكريم."
        )

    return payload["data"]


# -------------------- رابط الصوت --------------------

def audio_url(
    surah_number: int,
    ayah_number_in_surah: int,
    reciter_key: str,
) -> str:
    return (
        f"https://everyayah.com/data/{reciter_key}/"
        f"{surah_number:03d}{ayah_number_in_surah:03d}.mp3"
    )


# -------------------- التذييل --------------------

def show_footer():
    st.markdown(
        """
        <div class="footer" dir="rtl">
            <div style="font-size:20px;font-weight:bold;">
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


# -------------------- القائمة الجانبية --------------------

st.sidebar.markdown("## ☪ القرآن الكريم")

page = st.sidebar.radio(
    "انتقل إلى",
    ["الرئيسية", "القرآن الكريم", "حصن المسلم"],
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "نسأل الله أن يجعل القرآن ربيع قلوبنا"
)


# -------------------- واجهة التطبيق --------------------

st.markdown(
    """
    <div class="hero" dir="rtl">
        <h1>☪ القرآن الكريم وحصن المسلم ☪</h1>
        <p>
            كتاب الله الكريم وأذكار المسلم اليومية في مكان واحد
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# الصفحة الرئيسية
# =====================================================

if page == "الرئيسية":

    st.markdown(
        '<div class="section-title">'
        'أهلًا بك في رحاب القرآن الكريم'
        '</div>',
