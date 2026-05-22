# 📊 全球市場 & 台股電子盤 戰情看板

一頁式 Streamlit 看板，自動抓取 yfinance 即時數據。

## 涵蓋數據

| 區塊 | 內容 |
|------|------|
| 焦點原物料 | 黃金、白銀、銅、布倫特原油、WTI、天然氣、鈀、鉑 |
| 全球指數 | 道瓊、S&P500、那斯達克、費城半導體 + 走勢圖 |
| 美股科技 Top7 | NVDA、AMD、INTC、MU、TSLA、TSM、AAPL |
| 台股 | 加權指數、台積電 + 雙線走勢圖 |
| 匯率 | 美元/台幣（升貶值標示）、美元指數 DXY |
| 美國公債 | 3M、5Y、10Y、30Y 殖利率 + 趨勢 |

## 部署到 Streamlit Cloud（免費）

1. Fork 或 push 此 repo 到你的 GitHub
2. 到 [share.streamlit.io](https://share.streamlit.io)
3. New app → 選此 repo → Main file: `app.py`
4. Deploy

約 2 分鐘部署完成，拿到公開 URL。

## 本機開發

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 搭配 n8n 自動截圖

部署後拿到 URL（例如 `https://your-app.streamlit.app`），
可以用 n8n 的 HTTP Request 節點搭配截圖 API 產生圖片發送到 Telegram。
