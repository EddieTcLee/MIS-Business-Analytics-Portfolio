import streamlit as st
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from snownlp import SnowNLP
import random
import os
import platform

# ---------------------------------------------------------
# [安裝與執行教學]
# 1. 安裝套件: pip install streamlit pandas matplotlib jieba wordcloud snownlp
# 2. 執行程式: python -m streamlit run sentiment_analysis_dashboard.py
# ---------------------------------------------------------

# --- 1. 系統配置與字體設定 (解決中文亂碼問題) ---
st.set_page_config(page_title="社群輿情與情感分析系統", layout="wide")

def get_chinese_font():
    """優先使用專案目錄下的字體檔 (解決 Streamlit 雲端亂碼問題)"""
    # 這是你剛剛上傳到 GitHub 的字體檔名
    font_path = "NotoSansTC-Regular.ttf" 
    
    # 檢查檔案是否存在
    if os.path.exists(font_path):
        return font_path
    else:
        st.error(f"⚠️ 找不到字體檔案：{font_path}。請確認字體檔是否已成功推送到 GitHub 且檔名正確！")
        return None

CHINESE_FONT_PATH = get_chinese_font()

# 設定 Matplotlib 字體以顯示中文
if CHINESE_FONT_PATH and os.path.exists(CHINESE_FONT_PATH):
    from matplotlib.font_manager import FontProperties
    font_prop = FontProperties(fname=CHINESE_FONT_PATH)
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    plt.rcParams['axes.unicode_minus'] = False
else:
    st.warning("⚠️ 未偵測到中文字體，圖表中的中文可能會顯示為方框。")

# --- 2. 模擬資料生成 (Mock Data) ---
def load_mock_data():
    """生成模擬的餐廳 Google Maps 評論數據"""
    reviews = [
        # 正面評論
        "這家餐廳的牛排真的太好吃了，鮮嫩多汁！", "服務生態度非常親切，環境也很乾淨。",
        "CP值很高，下次一定會再來。", "甜點是亮點，雖然主餐稍微普通，但整體體驗很好。",
        "出餐速度快，很適合上班族中午來吃。", "隱藏版菜單真的令人驚艷！",
        "雖然價格稍貴，但食材真的很新鮮，物超所值。", "家庭聚餐的好地方，有提供兒童座椅。",
        
        # 中性/普通評論
        "味道還可以，但是排隊排太久了。", "中規中矩，沒有特別驚艷的地方。",
        "價格偏高，但份量有點少。", "裝潢很漂亮，適合拍照，但食物普通。",
        "停車不太方便，建議騎車來。", 
        
        # 負面評論
        "服務態度很差，服務生愛理不理的。", "湯送上來是冷的，跟店家反應也沒有處理。",
        "衛生環境堪憂，桌子黏黏的。", "完全不推，這個價位可以吃到更好的。",
        "牛排煎得太老了，跟石頭一樣硬。", "預約了還要等30分鐘，動線規劃很亂。",
        "這是我吃過最糟糕的義大利麵，太鹹了。", "結帳時多算了錢，要注意看帳單。"
    ]
    
    # 隨機生成 50 筆數據
    data = []
    platforms = ["Google Maps", "Facebook", "Dcard"]
    for i in range(50):
        review = random.choice(reviews)
        platform_name = random.choice(platforms)
        # 簡單模擬：如果評論包含負面關鍵字，分數給低一點
        if any(w in review for w in ["差", "冷", "硬", "亂", "糟糕", "不推"]):
            rating = random.randint(1, 2)
        elif any(w in review for w in ["普通", "还可以", "久"]):
            rating = random.randint(3, 3)
        else:
            rating = random.randint(4, 5)
            
        data.append({
            "id": i + 1,
            "platform": platform_name,
            "text": review,
            "user_rating": rating
        })
    
    return pd.DataFrame(data)

# --- 3. 核心分析功能 ---

def analyze_sentiment(df):
    """使用 SnowNLP 進行情感分析"""
    # SnowNLP 的 sentiments 屬性會回傳 0~1 的數值，越接近 1 代表越正面
    df['sentiment_score'] = df['text'].apply(lambda x: SnowNLP(x).sentiments)
    
    # 定義情感標籤
    def get_label(score):
        if score > 0.6: return "正面 (Positive)"
        elif score < 0.4: return "負面 (Negative)"
        else: return "中性 (Neutral)"
        
    df['sentiment_label'] = df['sentiment_score'].apply(get_label)
    return df

def generate_wordcloud(text_list):
    """生成文字雲"""
    # 1. 結巴斷詞
    text = " ".join(text_list)
    # 載入繁體結巴模式 (可選)
    # jieba.set_dictionary('dict.txt.big') 
    
    words = jieba.cut(text)
    
    # 2. 去除停用詞 (Stopwords)
    stopwords = set(["的", "了", "是", "也", "都", "就", "但", "很", "在", "有", "我", "去", "吃", "這", "那"])
    filtered_words = [w for w in words if w not in stopwords and len(w) > 1] # 過濾單字
    
    final_text = " ".join(filtered_words)
    
    # 3. 繪製文字雲
    wc = WordCloud(
        font_path=CHINESE_FONT_PATH, # 重要：必須指定中文字體
        background_color="white",
        width=800,
        height=400,
        max_words=100
    ).generate(final_text)
    
    return wc, filtered_words

# --- 4. Streamlit UI 介面 ---

# 側邊欄
st.sidebar.title("📊 輿情分析控制台")
data_source = st.sidebar.radio("選擇資料來源", ["載入範例資料 (餐廳評論)", "上傳 CSV 檔案 (進階功能)"])

if data_source == "載入範例資料 (餐廳評論)":
    raw_df = load_mock_data()
    st.sidebar.success("✅ 範例資料已載入")
else:
    uploaded_file = st.sidebar.file_uploader("上傳您的評論 CSV (需包含 'text' 欄位)", type="csv")
    if uploaded_file:
        raw_df = pd.read_csv(uploaded_file)
        if 'text' not in raw_df.columns:
            st.error("CSV 檔案必須包含 'text' 欄位")
            st.stop()
    else:
        st.info("請上傳檔案或切換至範例資料")
        st.stop()

# 主畫面
st.title("🗣️ 產品/服務 輿情情感分析儀表板")
st.markdown("透過 **NLP 自然語言處理** 技術，自動分析消費者評論，提煉商業洞察。")

# 進行分析
with st.spinner('正在進行情感運算與斷詞分析...'):
    df = analyze_sentiment(raw_df)
    
# 1. 數據概覽
col1, col2, col3 = st.columns(3)
avg_score = df['sentiment_score'].mean()
positive_ratio = (df['sentiment_label'] == '正面 (Positive)').mean() * 100
col1.metric("平均情感分數 (0-1)", f"{avg_score:.2f}")
col2.metric("正面評論佔比", f"{positive_ratio:.1f}%")
col3.metric("總評論數", f"{len(df)} 則")

# 2. 情感分佈圖 (Pie Chart)
st.subheader("1. 情感傾向分佈")
col_chart, col_table = st.columns([1, 1])

with col_chart:
    sentiment_counts = df['sentiment_label'].value_counts()
    fig1, ax1 = plt.subplots()
    ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', 
            colors=['#66b3ff', '#ff9999', '#99ff99'], startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # 如果沒有中文字體，使用備用顯示方式
    if not CHINESE_FONT_PATH:
        st.pyplot(fig1)
        st.caption("若圖表文字顯示方框，請檢查系統是否安裝微軟正黑體")
    else:
        st.pyplot(fig1)

with col_table:
    st.dataframe(df[['text', 'sentiment_label', 'sentiment_score']].head(10), height=300)

# 3. 文字雲分析
st.subheader("2. 關鍵字文字雲 (Word Cloud)")
st.markdown("分析消費者最常提到的關鍵詞：")

# 分別產生 正面 vs 負面 文字雲
sentiment_filter = st.radio("選擇要分析的評論類型：", ["全部", "正面 (Positive)", "負面 (Negative)"], horizontal=True)

if sentiment_filter == "全部":
    target_text = df['text'].tolist()
elif sentiment_filter == "正面 (Positive)":
    target_text = df[df['sentiment_label'] == "正面 (Positive)"]['text'].tolist()
else:
    target_text = df[df['sentiment_label'] == "負面 (Negative)"]['text'].tolist()

if target_text:
    wc_img, keywords = generate_wordcloud(target_text)
    
    # 顯示文字雲圖片
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2.imshow(wc_img, interpolation='bilinear')
    ax2.axis("off")
    st.pyplot(fig2)
    
    # 顯示高頻詞統計
    st.write("🔥 **高頻關鍵詞 Top 10：**")
    from collections import Counter
    word_counts = Counter(keywords).most_common(10)
    st.bar_chart(pd.DataFrame(word_counts, columns=["關鍵字", "次數"]).set_index("關鍵字").T)
else:
    st.warning("沒有符合條件的評論資料。")

# 4. 商業洞察建議 (模擬生成)
st.subheader("💡 商業洞察與建議")
insight = ""
if avg_score < 0.4:
    insight = "⚠️ **警示：** 整體情感偏向負面。消費者主要抱怨集中在「服務態度」與「等待時間」。建議立即檢討外場人員培訓與訂位流程。"
elif avg_score > 0.7:
    insight = "✅ **優良：** 客戶滿意度高。關鍵字顯示「好吃的牛排」與「CP值」是主要優勢，建議在行銷素材中加強這些賣點。"
else:
    insight = "ℹ️ **觀察：** 評價呈現兩極化或持平。部分產品受到好評，但服務流程可能有改善空間。需進一步分析負評細節。"

st.info(insight)

# 頁尾
st.markdown("---")
st.caption("開發者: [EddieTcLee] | 技術棧: Python, Jieba (NLP), SnowNLP, Streamlit")