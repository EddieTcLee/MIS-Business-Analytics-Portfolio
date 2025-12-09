import streamlit as st
import pandas as pd
import sqlite3
import random
from datetime import datetime, timedelta
import time

# ---------------------------------------------------------
# [安裝與執行教學]
# 1. 確保已安裝套件: pip install streamlit pandas matplotlib
# 2. 在終端機(Terminal)執行: streamlit run ecommerce_price_dashboard.py
# ---------------------------------------------------------

# --- 設定頁面配置 ---
st.set_page_config(page_title="電商競品價格追蹤儀表板", layout="wide")

# --- 資料庫設定 (使用 SQLite 本地資料庫) ---
DB_NAME = "ecommerce_prices.db"

def init_db():
    """初始化資料庫與資料表"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # 建立表格：記錄日期, 平台, 商品名稱, 價格
    c.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            platform TEXT,
            product_name TEXT,
            price INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def generate_mock_data():
    """
    生成過去 30 天的模擬數據 (為了讓圖表一開始就有東西看)
    模擬情境：PChome 和 Momo 兩大平台針對 iPhone 15 和 Dyson 吹風機的價格戰
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 檢查是否已經有資料，若有則不重新生成
    c.execute("SELECT count(*) FROM prices")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    products = ["iPhone 15 128G", "Dyson Supersonic 吹風機", "Sony WH-1000XM5 耳機"]
    platforms = ["PChome 24h", "Momo 購物網"]
    
    # 基準價格
    base_prices = {
        "iPhone 15 128G": 29900,
        "Dyson Supersonic 吹風機": 12900,
        "Sony WH-1000XM5 耳機": 9900
    }

    print("正在生成模擬數據...")
    for day in range(30):
        current_date = (datetime.now() - timedelta(days=30-day)).strftime("%Y-%m-%d")
        
        for p_name in products:
            base = base_prices[p_name]
            for platform in platforms:
                # 模擬價格波動：隨機增減 5%
                fluctuation = random.uniform(0.95, 1.05)
                # 週末可能會特價 (模擬行銷活動)
                if datetime.strptime(current_date, "%Y-%m-%d").weekday() >= 5: 
                    fluctuation -= 0.03 # 週末再降 3%
                
                final_price = int(base * fluctuation)
                # 取整數 (例如 29900 -> 29500) 讓價格看起來更像真的
                final_price = round(final_price / 100) * 100 
                
                c.execute("INSERT INTO prices (date, platform, product_name, price) VALUES (?, ?, ?, ?)",
                          (current_date, platform, p_name, final_price))
    
    conn.commit()
    conn.close()

def fetch_data(product_name):
    """從資料庫讀取特定商品的歷史價格"""
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT date, platform, price FROM prices WHERE product_name = '{product_name}' ORDER BY date"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def run_scraper_simulation():
    """
    模擬爬蟲執行：
    在真實專案中，這裡會使用 requests/BeautifulSoup 或 Selenium 去抓取實際網頁。
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    
    products = ["iPhone 15 128G", "Dyson Supersonic 吹風機", "Sony WH-1000XM5 耳機"]
    platforms = ["PChome 24h", "Momo 購物網"]
    base_prices = {"iPhone 15 128G": 29900, "Dyson Supersonic 吹風機": 12900, "Sony WH-1000XM5 耳機": 9900}
    
    new_data = []
    for p_name in products:
        for platform in platforms:
            # 模擬今日新價格
            price = int(base_prices[p_name] * random.uniform(0.92, 1.02)) # 模擬突然大特價
            price = round(price / 100) * 100
            
            c.execute("INSERT INTO prices (date, platform, product_name, price) VALUES (?, ?, ?, ?)",
                      (today, platform, p_name, price))
            new_data.append(f"抓取成功: {platform} - {p_name} : ${price}")
            
    conn.commit()
    conn.close()
    return new_data

# --- 主程式邏輯 ---

# 1. 初始化
init_db()
generate_mock_data()

# 2. 側邊欄控制項
st.sidebar.title("🔍 競品價格監控系統")
st.sidebar.markdown("模擬電商營運人員的監控視角")

product_list = ["iPhone 15 128G", "Dyson Supersonic 吹風機", "Sony WH-1000XM5 耳機"]
selected_product = st.sidebar.selectbox("請選擇要分析的商品", product_list)

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ 系統操作")
if st.sidebar.button("🚀 執行即時爬蟲 (模擬)"):
    with st.spinner('正在連線至各大電商平台...'):
        time.sleep(1.5) # 假裝在跑
        logs = run_scraper_simulation()
    st.sidebar.success("資料更新完成！")
    for log in logs:
        st.sidebar.text(log)
    st.rerun() # 重新整理頁面以顯示新數據

# 3. 主要內容區
st.title(f"📊 {selected_product} 價格趨勢分析")

# 讀取資料
df = fetch_data(selected_product)

# 計算 KPI
latest_date = df['date'].max()
latest_df = df[df['date'] == latest_date]
lowest_price = latest_df['price'].min()
avg_price = int(latest_df['price'].mean())

col1, col2, col3 = st.columns(3)
col1.metric("今日最低價", f"${lowest_price:,}", delta_color="inverse")
col2.metric("今日市場均價", f"${avg_price:,}")
col3.metric("資料更新日期", latest_date)

# 4. 繪製互動圖表
st.subheader("平台價格走勢比較 (PChome vs Momo)")

# 將資料轉置為適合繪圖的格式 (Pivot)
# Index: Date, Columns: Platform, Values: Price
chart_data = df.pivot(index='date', columns='platform', values='price')

# 使用 Streamlit 內建的折線圖 (基於 Altair/Vega-Lite)
st.line_chart(chart_data)

# 5. 商業洞察分析 (模擬自動產生的報告)
st.subheader("💡 商業洞察報告")
insight_text = ""
p_pchome = latest_df[latest_df['platform'] == 'PChome 24h']['price'].values[0]
p_momo = latest_df[latest_df['platform'] == 'Momo 購物網']['price'].values[0]

if p_pchome < p_momo:
    diff = p_momo - p_pchome
    insight_text += f"⚠️ **警示**：目前 **PChome 24h** 價格比 Momo 便宜 **${diff}**。建議行銷團隊檢查是否需要跟進降價，或強調贈品優勢。"
elif p_momo < p_pchome:
    diff = p_pchome - p_momo
    insight_text += f"⚠️ **警示**：目前 **Momo 購物網** 價格比 PChome 便宜 **${diff}**。請注意競爭對手的促銷活動。"
else:
    insight_text += "✅ 目前兩大平台價格持平，市場行情穩定。"

st.info(insight_text)

# 6. 詳細資料表格
with st.expander("查看原始數據資料表"):
    st.dataframe(df.sort_values(by='date', ascending=False), use_container_width=True)

# 7. 頁尾說明
st.markdown("---")
st.caption("開發者: [EddieTcLee] | 技術棧: Python, Streamlit, SQLite | 用途: 中山大學資管碩專班備審作品集展示")