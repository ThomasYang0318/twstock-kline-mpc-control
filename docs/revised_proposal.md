# 基於 K 線市場狀態辨識與 Model Predictive Control 之台股個股部位調整系統

資工三 楊啓宏 411285003  
資工三 崔燕宗 411285037

## 摘要

股票市場具有高度動態與不確定性，單純預測股價漲跌並不足以形成穩定且可執行的交易策略。實際交易中，投資人除了需要判斷市場方向，也必須決定持股比例、控制換手率、處理交易成本，並降低最大回撤風險。因此，本研究提出一套結合 K 線市場狀態辨識與 Model Predictive Control, MPC 的台股個股部位調整系統。本系統以台股歷史 OHLCV 資料建立趨勢、動能與波動度特徵，將其轉換為預期報酬與風險訊號，再由 MPC 控制器在報酬、風險與交易成本之間進行最佳化，動態決定下一期目標持股比例。為避免資料洩漏，本研究採用時間序列非重疊切分，使用前段歷史資料進行控制器參數校準，並保留最後 3 至 5 年作為最終 holdout 回測期間。以 2330.TW 之 2010 至 2025 年資料進行初步實驗，在 2010-01-04 至 2021-12-29 訓練期選取 MPC 參數，並於 2021-12-30 至 2025-12-30 holdout 期間回測，初始資金 100 萬元成長至約 502 萬元，最大回撤為 -8.02%，Sharpe Ratio 為 2.7831。初步結果顯示，將 K 線狀態訊號與 MPC 部位控制結合，可作為台股個股交易策略研究的可行架構。

## 1. Introduction

股票市場是一個高度動態且不確定的系統，價格變動受到公司基本面、產業趨勢、總體經濟、資金流向與投資人情緒等多種因素影響。因此，如何從歷史交易資料中擷取有效訊號，並將其轉換為實際可執行的交易決策，是金融科技與智慧型控制應用中的重要研究議題。

在傳統技術分析中，K 線圖是投資人常用的市場判斷工具。K 線圖同時呈現開盤價、最高價、最低價與收盤價，因此可反映短期市場多空力量的變化。過去已有研究針對台灣股票市場檢驗 K 線圖的預測能力，例如 Lu 使用台灣股票日資料研究 K 線圖在台股市場中的獲利能力，顯示 K 線型態具有作為台股技術分析研究基礎的可行性 [1]。近年來，機器學習與深度學習方法也開始將 K 線資料轉換為影像或序列特徵，並利用 CNN、LSTM 或 Transformer 等模型進行價格方向預測與型態辨識 [2], [3]。

然而，預測股價方向並不等於能形成穩定交易策略。實際交易中，若直接將預測結果轉換為買賣訊號，可能造成過度交易、交易成本侵蝕報酬，或因未考慮波動風險而導致回測結果過度樂觀。換言之，市場狀態辨識模型回答的是「市場可能往哪裡走」，但交易系統還需要回答「應該持有多少部位」。因此，本研究將 K 線訊號視為市場狀態輸入，並導入 Model Predictive Control 作為智慧型控制器，將預測訊號轉換為連續的持股比例決策。

本研究目前已完成一套 Python 實作原型，包含資料抓取、技術特徵建構、MPC 控制器、歷史回測、跨股票比較、資料來源紀錄、近即時報價抓取，以及非重疊 train/holdout 實驗流程。相較於僅在單一期間回測，本研究進一步將調參資料與最終回測資料切開，保留最後數年作為 out-of-sample holdout，以降低資料洩漏與過度擬合風險。

## 2. Motivation

本研究動機來自於現有 K 線研究與股票預測方法在實際交易應用上的限制。雖然已有研究證明 K 線可用於台股市場分析 [1]，也有研究將 K 線轉換為影像並透過深度學習模型進行型態辨識與價格方向預測 [2], [3]，但多數方法仍主要停留在「預測漲跌」層次，尚未完整處理部位控制、交易成本與風險管理問題。

在實際交易中，預測上漲不代表應該滿倉買進，預測下跌也不代表必須立即全部賣出。若交易系統忽略目前持股比例、波動度、換手成本與最大回撤風險，可能在盤整市場中頻繁進出，導致扣除成本後績效下降。Cagliero et al. 指出，機器學習交易系統可能產生過多錯誤訊號，因此需要額外機制篩選或控制交易建議 [4]。

因此，本研究希望解決的核心問題是：如何將 K 線市場狀態訊號轉換為可執行且具有風險控制能力的持股比例決策。為此，本研究採用 MPC 作為控制架構。MPC 可在多期規劃視窗內同時考慮預期報酬、風險懲罰與交易成本，並輸出下一期目標持股比例。此架構使交易決策不再是二元買賣訊號，而是介於 0% 至 100% 之間的連續部位控制問題。

## 3. Method

本研究方法分為資料蒐集、特徵建構、市場狀態訊號、MPC 控制器、非重疊訓練與回測五個部分。

### 3.1 資料蒐集與資料來源驗證

本研究使用台股個股歷史 OHLCV 資料，包含開盤價、最高價、最低價、收盤價與成交量。目前系統以 Yahoo Finance 作為程式化資料來源，透過 `yfinance` 抓取台股資料。例如台積電 2330 會轉換為 Yahoo Finance ticker `2330.TW`。本研究同時記錄資料抓取指令、資料區間、列數與 SHA256 雜湊值，並建議以臺灣證交所個股日成交資訊作為官方交叉驗證來源。

目前 2330.TW 長期資料範圍為 2010-01-04 至 2025-12-30，共 3912 筆日 K 資料。該資料用於非重疊 train/holdout 實驗，其 SHA256 為：

```text
ce5a8c4eae99c32894b4d52090abca2c3cf9bd36ab6483d859971f48f96ea886
```

### 3.2 K 線特徵與市場狀態訊號

在目前原型中，本研究先以可解釋的技術特徵作為市場狀態訊號，包括日報酬率、快速移動平均、慢速移動平均、趨勢強度、短期動能與滾動波動度。系統以趨勢與動能組合形成 `signal`，並以滾動標準差估計風險。此設計可作為後續 CNN、LSTM 或 Transformer 市場狀態辨識模型的 baseline。

目前訊號定義如下：

```text
signal = 0.65 * trend + 0.35 * momentum
```

其中 `trend` 由快速均線與慢速均線比例計算，`momentum` 由短期價格變化率計算，`volatility` 則由歷史報酬率滾動標準差估計。為避免極端訊號導致控制器過度反應，系統將訊號限制在合理區間。

### 3.3 MPC 智慧型控制器

MPC 控制器的目標是根據市場狀態訊號、波動度與目前持股比例，決定未來規劃視窗中的目標持股比例。本研究目前採用單一股票、長倉-only 的設定，持股比例限制為 0% 至 100%，不允許放空。

控制器在每一交易日解下列概念性最佳化問題：

```text
minimize  - expected_return * weight
          + risk_aversion * volatility^2 * weight^2
          + turnover_penalty * (weight_t - weight_{t-1})^2
          + transaction_cost * |weight_t - weight_{t-1}|
```

其中第一項鼓勵系統在預期報酬較高時增加持股，第二項懲罰高波動風險，第三項降低頻繁換手，第四項近似交易成本。MPC 每次會計算一段 horizon 的持股計畫，但實際只執行第一期控制量，下一交易日再根據新資料重新最佳化。

### 3.4 非重疊訓練與 Holdout 回測

為避免訓練與回測資料重疊，本研究加入 chronological split。系統先使用較早期間的資料校準 MPC 超參數，例如 horizon、risk aversion 與 turnover penalty，再將最後 3 至 5 年保留為 holdout 期間，只用於最終回測。

以 2330.TW 長期資料為例，本研究採用以下切分：

| Period | Start | End | Rows | Purpose |
| --- | --- | --- | ---: | --- |
| Train | 2010-01-04 | 2021-12-29 | 2943 | MPC 參數選擇 |
| Holdout | 2021-12-30 | 2025-12-30 | 969 | 最終 out-of-sample 回測 |

此流程確保 holdout 結果不會參與參數選擇，降低 overfitting 與資料洩漏風險。

### 3.5 評估指標

本研究使用下列指標評估策略：

- 累積報酬率
- 年化報酬率
- 年化波動率
- Sharpe Ratio
- 最大回撤
- 最終資產
- 持股比例變化與換手成本

後續研究可進一步加入買進持有、均線策略、單純 K 線分類策略作為 baseline，並比較是否能降低最大回撤與過度交易。

## 4. Preliminary Results

### 4.1 單一期間初步回測

在較早的初步回測中，本研究使用 2022-01-03 至 2025-12-30 的 2330.TW 日 K 資料進行測試。初始資金為 100 萬元，策略最終資產約為 353.5 萬元，總報酬率為 253.55%，最大回撤為 -12.15%，Sharpe Ratio 為 1.9721。此結果顯示 MPC 控制器可根據趨勢訊號動態調整部位，但由於該實驗未完整切分訓練與測試資料，因此僅能作為初步 baseline。

### 4.2 非重疊 Train/Holdout 結果

為提高實驗可信度，本研究進一步使用 2010-01-04 至 2025-12-30 的長期資料。系統在 2010-01-04 至 2021-12-29 的訓練期中搜尋 MPC 超參數，最佳參數如下：

| Parameter | Value |
| --- | ---: |
| Horizon | 10 |
| Risk aversion | 20.0 |
| Turnover penalty | 0.5 |
| Transaction cost | 0.001 |

接著，系統將該組參數固定，於 2021-12-30 至 2025-12-30 的 holdout 期間進行最終回測：

| Metric | Train | Holdout |
| --- | ---: | ---: |
| Total return | 2430.67% | 402.46% |
| Annualized return | 31.89% | 52.24% |
| Annualized volatility | 14.53% | 18.77% |
| Sharpe Ratio | 2.1951 | 2.7831 |
| Max drawdown | -11.81% | -8.02% |
| Final equity | 25,306,686.11 | 5,024,644.52 |

此結果比單一期間回測更具參考價值，因為最終 holdout 期間沒有參與參數選擇。雖然結果顯示策略在 2330.TW 上具有良好績效，但仍需透過更多股票、不同 holdout 年數與 walk-forward validation 進一步確認穩健性。

### 4.3 跨股票比較

本研究亦使用同一套策略對多檔台股進行初步比較，包括 2330、2317、2454、2603、2882、2303 與 2412。以 2022-01-03 至 2025-12-30 單一期間結果觀察，2330、2317 與 2454 的報酬表現較佳，其中 2317 在報酬與最大回撤之間呈現較佳平衡；2603 雖有較高報酬，但最大回撤較大，顯示策略對不同產業與波動特性的股票仍需進行穩健性分析。

## 5. Expected Contributions

本研究預期貢獻如下：

1. 提出一套將 K 線市場狀態訊號轉換為連續持股比例的智慧型控制架構。
2. 使用 MPC 同時考慮預期報酬、風險與交易成本，降低單純買賣訊號造成的過度交易問題。
3. 建立可重現的台股 OHLCV 資料流程，包含資料來源、SHA256 驗證與官方來源交叉驗證建議。
4. 導入非重疊 train/holdout 實驗設計，避免使用同一段期間同時調參與回測。
5. 提供 Python CLI 工具，支援資料抓取、回測、參數校準、近即時報價與論文風格圖表產生。

## 6. Limitations and Future Work

目前系統仍有以下限制。第一，現階段市場狀態訊號主要由移動平均、動能與波動度等技術特徵組成，尚未完整導入 CNN、LSTM 或 Transformer 模型。第二，目前回測主要為單一股票 long-only 部位控制，尚未處理多股票投資組合配置、資金分配與相關性風險。第三，Yahoo Finance 資料應視為可程式化取得的歷史與近即時資料來源，不應直接宣稱為交易所等級即時 tick 資料。第四，雖然目前加入 holdout 切分，但仍需要 walk-forward validation 與更多股票樣本以評估策略穩健性。

後續研究將朝三個方向擴充。首先，加入更完整的 K 線型態辨識模型，將過去 N 日 K 線序列輸入 LSTM、Transformer 或圖像模型，以產生更細緻的市場狀態機率。其次，加入交易稅、手續費、滑價與單日最大部位調整限制，使模擬更接近實際台股交易環境。最後，將目前單一股票控制器擴充為多資產 MPC，進一步處理投資組合權重、產業分散與風險平價限制。

## References

以下參考文獻沿用原 proposal 版本；正式提交前仍建議逐筆以 DOI、出版社頁面或 Google Scholar 再次確認格式與書目資訊。

[1] T.-H. Lu, “The profitability of candlestick charting in the Taiwan stock market,” *Pacific-Basin Finance Journal*, vol. 26, pp. 65–78, 2014.

[2] J.-H. Chen and Y.-C. Tsai, “Encoding candlesticks as images for pattern classification using convolutional neural networks,” *Financial Innovation*, vol. 6, Article 26, 2020.

[3] C.-C. Hung and Y.-J. Chen, “DPP: Deep predictor for price movement from candlestick charts,” *PLOS ONE*, vol. 16, no. 6, e0252404, 2021.

[4] L. Cagliero, J. Fior, and P. Garza, “Shortlisting machine learning-based stock trading recommendations using candlestick pattern recognition,” *Expert Systems with Applications*, Article 119493, 2023.

[5] X. Li, A. S. Uysal, and J. M. Mulvey, “Multi-period portfolio optimization using model predictive control with mean-variance and risk parity frameworks,” *European Journal of Operational Research*, vol. 299, no. 3, pp. 1158–1176, 2022.

[6] F. Abbracciavento, F. Tappi, and S. Formentin, “Model predictive control for multi-period portfolio optimization: A trading-oriented learning approach,” *International Journal of Control*, vol. 98, no. 4, pp. 754–764, 2025.

