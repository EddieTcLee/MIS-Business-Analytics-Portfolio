# 資訊管理與商業分析作品集 (Business Analytics Portfolio)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-blue)

歡迎來到我的 repo！本作品集展示了我如何運用 **Python 全端技術** 與 **資料科學方法**，解決實際的商業問題。
作為一名具備 **C#/.NET** 與 **Python** 能力的軟體工程師，我致力於連結「系統開發」與「數據決策」之間的橋樑。

## 📂 專案導覽 (Project Showcase)

本倉庫包含三個針對不同商業場景的實作專案，皆採用 Streamlit 建構互動式儀表板，模擬真實的決策輔助系統。

| 序號 | 專案名稱 | 核心議題 | 技術關鍵字 | 程式碼路徑 |
| :---: | :--- | :--- | :--- | :--- |
| 01 | **電商競品價格追蹤儀表板** | 市場競爭策略 | `Web Crawler`, `SQLite`, `Automation` | [🚀 線上試玩](https://eddie-price-tracker.streamlit.app/) \| [📂 查看程式碼](./01_Price_Tracker) |
| 02 | **社群輿情與情感分析系統** | 顧客之聲 (VOC) | `NLP (SnowNLP)`, `Jieba`, `WordCloud` | [🚀 線上試玩](https://eddie-sentiment-analysis.streamlit.app/) \| [📂 查看程式碼](./02_Sentiment_Analysis) |
| 03 | **RFM 顧客價值分群模型** | 精準行銷 | `RFM Model`, `Data Mining`, `Marketing Strategy` | [🚀 線上試玩](https://eddie-rfm-analysis.streamlit.app/) \| [📂 查看程式碼](./03_RFM_Customer_Analysis) |

## 🌳 專案結構 (Project Structure)

```text
Business-Analytics-Portfolio/
├── README.md                   # 專案說明文件
├── requirements.txt            # Python 相依套件列表
├── 01_Price_Tracker/           # [專案 1] 價格追蹤
│   ├── app.py                  # Streamlit 主程式
│   ├── database.db             # SQLite 資料庫 (模擬)
│   └── scraper.py              # 爬蟲邏輯模組
├── 02_Sentiment_Analysis/      # [專案 2] 輿情分析
│   ├── app.py                  # Streamlit 主程式
│   ├── visualizer.py           # 文字雲與圖表繪製
│   └── data/                   # 測試用評論資料
└── 03_RFM_Customer_Analysis/   # [專案 3] RFM 模型
    ├── app.py                  # Streamlit 主程式
    ├── rfm_model.py            # RFM 計算邏輯核心
    └── utils.py                # 資料清洗工具
```

## 🚀 技術棧 (Tech Stack)

* **語言 (Languages):** Python 3.11, SQL
* **資料處理 (Data Engineering):** Pandas, NumPy, SQLite
* **自然語言處理 (NLP):** Jieba (斷詞), SnowNLP (情感運算)
* **視覺化與前端 (Visualization & UI):** Streamlit, Matplotlib, Seaborn, WordCloud
* **版本控制 (Version Control):** Git, GitHub

## 📝 專案詳細介紹

### 1. 📈 電商競品價格追蹤儀表板
> **競爭對手降價了嗎？我們該跟進嗎？**

* **對應課程：** 電子商務、管理資訊系統
* **功能亮點：**
    * 模擬爬蟲資料流與資料庫 (SQLite) 寫入機制。
    * 自動計算價差並發出商業警示 (Alert System)。
    * 展現全端工程師對於 Data Pipeline 與自動化的掌握度。

### 2. 🗣️ 社群輿情與情感分析系統
> **消費者在網路上怎麼討論我們的產品？**

* **對應課程：** 社群媒體分析、服務品質管理
* **功能亮點：**
    * 整合 **Jieba** 中文斷詞與 **SnowNLP** 情感分析模型。
    * 視覺化「文字雲」快速識別產品痛點（例如：服務態度、出餐速度）。
    * 提供量化的情感分數指標 (Sentiment Score KPI)，輔助客觀決策。

### 3. 🏆 RFM 顧客價值分群模型
> **誰是我們的高價值客戶？誰即將流失？**

* **對應課程：** 商業分析實務、資料庫系統
* **功能亮點：**
    * 自動生成模擬交易數據，並清洗轉換為 R (最近消費日)、F (頻率)、M (金額) 指標。
    * 透過 **五分位數法 (Quintile)** 進行科學化評分分群。
    * 針對「VIP」、「瞌睡客戶」自動生成差異化行銷策略建議。

---

## 📬 聯絡資訊

如果您對我的作品有興趣，歡迎透過以下方式聯繫：

* **Email:** [eddie.tc.lee@gmail.com](mailto:eddie.tc.lee@gmail.com)
* **GitHub:** [https://github.com/EddieTcLee](https://github.com/EddieTcLee)

    
