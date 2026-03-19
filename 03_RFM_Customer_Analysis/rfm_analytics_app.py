import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import platform
import os

# ---------------------------------------------------------
# [安裝與執行教學]
# 1. 安裝套件: pip install streamlit pandas matplotlib seaborn
# 2. 執行程式: streamlit run rfm_analytics_app.py
# python -m streamlit run rfm_analytics_app.py
# ---------------------------------------------------------

# --- 1. 系統配置與字體設定 (解決中文亂碼問題) ---
st.set_page_config(page_title="RFM 顧客價值分析系統", layout="wide")

def get_chinese_font():
    """偵測系統中的計算中文字體路徑"""
    system = platform.system()
    if system == "Windows":
        font_path = "C:/Windows/Fonts/msjh.ttc" # 微軟正黑體
        if os.path.exists(font_path): return font_path
        return "C:/Windows/Fonts/simhei.ttf"
    elif system == "Darwin": # Mac
        return "/System/Library/Fonts/PingFang.ttc"
    return None

CHINESE_FONT_PATH = get_chinese_font()
if CHINESE_FONT_PATH and os.path.exists(CHINESE_FONT_PATH):
    from matplotlib.font_manager import FontProperties
    font_prop = FontProperties(fname=CHINESE_FONT_PATH)
    plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
    plt.rcParams['axes.unicode_minus'] = False
    sns.set(font=font_prop.get_name())

# --- 2. 模擬交易資料生成 (Mock Data) ---
@st.cache_data
def generate_transaction_data(n_rows=1000):
    """生成模擬的電商訂單資料 (Transaction Data)"""
    np.random.seed(42)
    
    # 模擬 200 位客戶
    customer_ids = [f'C{str(i).zfill(3)}' for i in range(1, 201)]
    
    data = []
    # 設定起始日期 (一年前)
    start_date = datetime.date.today() - datetime.timedelta(days=365)
    
    for _ in range(n_rows):
        cust_id = np.random.choice(customer_ids)
        
        # 模擬日期：越接近現在的日期，交易機率越高 (模擬業務成長)
        days_offset = np.random.randint(0, 365)
        date = start_date + datetime.timedelta(days=days_offset)
        
        # 模擬金額：大部分消費落在 500-3000，少數大額
        amount = int(np.random.gamma(shape=2, scale=1000)) + 100
        
        data.append([cust_id, date, amount])
        
    df = pd.DataFrame(data, columns=['CustomerID', 'OrderDate', 'Amount'])
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    return df

# --- 3. RFM 計算核心邏輯 ---
def calculate_rfm(df):
    """
    計算 Recency, Frequency, Monetary 並進行評分
    """
    # 設定基準日 (Snapshot Date)：通常是資料中最後一天交易日的隔天
    snapshot_date = df['OrderDate'].max() + datetime.timedelta(days=1)
    
    # Group By CustomerID 進行聚合運算
    rfm = df.groupby('CustomerID').agg({
        'OrderDate': lambda x: (snapshot_date - x.max()).days, # Recency: 距今幾天
        'CustomerID': 'count',                                 # Frequency: 購買次數
        'Amount': 'sum'                                        # Monetary: 總消費金額
    })
    
    # 重新命名欄位
    rfm.rename(columns={
        'OrderDate': 'Recency',
        'CustomerID': 'Frequency',
        'Amount': 'Monetary'
    }, inplace=True)
    
    # --- RFM 打分機制 (1-5分，5分最好) ---
    # 使用 pd.qcut 將資料分為 5 等份 (Quintiles)
    
    # Recency: 越小越好 (分數越高) -> 標籤 [5, 4, 3, 2, 1]
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: 越大越好 (分數越高) -> 標籤 [1, 2, 3, 4, 5]
    # 注意：如果數據重複值太多 (例如很多人只買1次)，qcut 會報錯，改用 rank method
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    # Monetary: 越大越好 -> 標籤 [1, 2, 3, 4, 5]
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    # 將 category 轉為 int 以便計算
    rfm['R_Score'] = rfm['R_Score'].astype(int)
    rfm['F_Score'] = rfm['F_Score'].astype(int)
    rfm['M_Score'] = rfm['M_Score'].astype(int)
    
    # 計算 RFM 總分 (簡單加總或加權)
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    # --- 客戶分群規則 (Segmentation) ---
    def segment_customer(row):
        # 這裡使用常見的簡化規則，可根據商業邏輯調整
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        
        if r >= 4 and f >= 4 and m >= 4:
            return "🏆 VIP客戶"
        elif r >= 3 and f >= 3 and m >= 3:
            return "💎 忠誠客戶"
        elif r >= 4 and f == 1:
            return "🌱 新進潛力客戶"
        elif r <= 2 and f >= 4:
            return "⚠️ 流失預警客戶" #(曾經買很多，但很久沒來了)
        elif r <= 2 and f <= 2:
            return "💤 沉睡/流失客戶"
        else:
            return "🙂 一般挽留客戶"
            
    rfm['Customer_Segment'] = rfm.apply(segment_customer, axis=1)
    
    return rfm

# --- 4. Streamlit UI ---

st.sidebar.title("🔍 RFM 分析控制台")
st.sidebar.info("模擬資料：200位客戶，1000筆訂單")
if st.sidebar.button("🔄 重新生成模擬數據"):
    st.cache_data.clear()
    st.rerun()

st.title("📊 電商會員價值分析模型 (RFM Model)")
st.markdown("透過 **Recency (最近購買日)**、**Frequency (頻率)**、**Monetary (金額)** 三大指標，將客戶精準分群。")

# 1. 載入與處理資料
df_orders = generate_transaction_data()
rfm_df = calculate_rfm(df_orders)

# 2. 關鍵指標 (KPI)
col1, col2, col3, col4 = st.columns(4)
col1.metric("總營收 (Total Revenue)", f"${rfm_df['Monetary'].sum():,.0f}")
col2.metric("平均客單價 (AOV)", f"${df_orders['Amount'].mean():,.0f}")
col3.metric("活躍會員數", f"{len(rfm_df)}")
col4.metric("VIP 客戶佔比", f"{(len(rfm_df[rfm_df['Customer_Segment'].str.contains('VIP')]) / len(rfm_df) * 100):.1f}%")

st.divider()

# 3. 視覺化分析
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("👥 客戶分群分佈 (Segmentation)")
    
    # 畫圓餅圖或長條圖
    segment_counts = rfm_df['Customer_Segment'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=segment_counts.values, y=segment_counts.index, palette="viridis", ax=ax)
    ax.set_xlabel("客戶數")
    st.pyplot(fig)

with col_chart2:
    st.subheader("💰 價值分佈矩陣 (R vs F)")
    st.markdown("觀察重點：右上角為高價值群，右下角為需挽留群")
    
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    # 繪製散佈圖：X軸為 Recency (天數), Y軸為 Frequency (次數)
    # 用 Monetary 大小決定點的大小
    sns.scatterplot(
        data=rfm_df, 
        x='Recency', 
        y='Frequency', 
        hue='Customer_Segment', 
        size='Monetary',
        sizes=(20, 200),
        alpha=0.7,
        palette="deep",
        ax=ax2
    )
    # 畫一條虛線做區隔
    ax2.axvline(x=rfm_df['Recency'].mean(), color='gray', linestyle='--')
    ax2.axhline(y=rfm_df['Frequency'].mean(), color='gray', linestyle='--')
    ax2.set_xlabel("距今未消費天數 (Recency)")
    ax2.set_ylabel("消費頻率 (Frequency)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    st.pyplot(fig2)

# 4. 行銷策略建議 (Actionable Insights)
st.subheader("💡 智慧行銷策略建議")

selected_segment = st.selectbox("請選擇要分析的客群：", rfm_df['Customer_Segment'].unique())
target_data = rfm_df[rfm_df['Customer_Segment'] == selected_segment]

st.write(f"目前選定客群：**{selected_segment}** (共 {len(target_data)} 人)")

strategy_text = ""
if "VIP" in selected_segment:
    strategy_text = "🎯 **策略：尊榮禮遇與推薦計畫**\n\n這群人是營收主力。不要過度打擾，但要提供專屬感。\n* 邀請加入私密社團或新品搶先購。\n* 設計 M GM (Member Get Member) 推薦獎勵。"
elif "忠誠" in selected_segment:
    strategy_text = "🎯 **策略：提升客單價 (Upsell)**\n\n他們買得很頻繁。試著推薦高單價商品或組合包。\n* 滿額贈禮活動。\n* 訂閱制服務推廣。"
elif "流失預警" in selected_segment:
    strategy_text = "🎯 **策略：主動喚回 (Reactivation)**\n\n曾經是大戶，但最近不來了。必須立刻行動！\n* 發送「好久不見」專屬 8 折券。\n* 詢問滿意度調查，找出不再購買的原因。"
elif "新進" in selected_segment:
    strategy_text = "🎯 **策略：培養習慣**\n\n剛來不久。目標是讓他們產生第二次購買。\n* 提供「下單回購禮」。\n* 新手教學內容行銷。"
else:
    strategy_text = "🎯 **策略：自動化促銷**\n\n對於沉睡或一般客戶，使用低成本的 Email/Line 自動推播即可，不需投入過多人工資源。"

st.info(strategy_text)

# 5. 資料檢視
with st.expander("查看詳細客戶名單"):
    st.dataframe(rfm_df.sort_values(by='RFM_Score', ascending=False), use_container_width=True)

st.caption("開發者: [EddieTcLee] | 技術棧: Python, Pandas, RFM Analysis, Streamlit")