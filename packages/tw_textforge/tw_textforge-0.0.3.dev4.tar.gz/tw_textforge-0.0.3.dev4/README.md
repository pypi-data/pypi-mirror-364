![logo](https://raw.githubusercontent.com/TsukiSama9292/TW-TextForge/refs/heads/main/assets/TW-TextForge_Preview.png)

[![GitHub last commit](https://img.shields.io/github/last-commit/TsukiSama9292/TW-TextForge)](https://github.com/TsukiSama9292/TW-TextForge/commits/main)
[![GitHub workflow](https://github.com/TsukiSama9292/TW-TextForge/actions/workflows/tests.yml/badge.svg)](https://github.com/TsukiSama9292/TW-TextForge/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/tw_textforge)](https://pypi.org/project/tw_textforge/)

## 使用須知

1. 考試試題之使用符合著作權法

    根據中華民國政府的[著作權法](https://law.moj.gov.tw/LawClass/LawAll.aspx?PCode=J0070017) - 第9條 

    > 1. 下列各款不得為著作權之標的︰  
    一、憲法、法律、命令或公文。  
    二、中央或地方機關就前款著作作成之翻譯物或編輯物。  
    三、標語及通用之符號、名詞、公式、數表、表格、簿冊或時曆。  
    四、單純為傳達事實之新聞報導所作成之語文著作。  
    **五、依法令舉行之各類考試試題及其備用試題。**

    依法舉辦的考試試題是不具備著作權的  
    適用該條款的考試，包含：學測、會考、學校段考試題，但是不包含補習班、出版商自製的試題  
    複雜情況：若學校段考考題使用了出版商的題目，那該題目仍然受到著作權的保護，為了規避法律風險，最佳實踐方案是只收集大考考試試題  
    該專案有調整題目敘述，**即重製題目**，讓資料更適合 NLP  
    請務必根據 **Apache 2.0許可證** 使用專案程式碼  
    也請務必遵守資料集的 **指定許可證**
    
    衍生參考資料: [考試題目也有著作權嗎？－林正椈律師](https://www.glorylaw.com.tw/knowledge-detail/1429/)
    

2. 基於語言模型的合成資料集 - 上下游關係

    上游：正在使用該工具的你/妳，身為API呼叫者  
    下游：使用合成資料集的他/她，你/妳不是下游  

    常見模型提供商的使用條款: OpenAI, Google  
    - 皆禁止以輸出訓練競爭模型  
    - 使用者皆擁有輸出。OpenAI: 可自由分發; Google: 需遵守法律，未限制分發  
    - 截止 2025/07/20 使用條款無直接追溯力，下游使用者可根據資料集的協議使用資料集  
    
    上游透過本工具，呼叫 Gemini API 產生合成資料集，並且上游釋出該資料集為 MIT 協議，下游使用者即可自由使用該資料集


## 支援情況

### 作業系統

| 作業系統 | 支援 | 備註 | 開發者情況 |
|--------|------|-----|----------|
| Linux | ✅ | 測試時，使用 Github Action ubuntu-latest | 日常使用 Ubuntu |
| Windows | ✅ | 測試時，使用 Github Action windows-latest | 偶爾使用 |
| MacOS | ✅ | 測試時，使用 Github Action macos-13| 沒有 Mac 裝置 |

### Python 版本

這跟專案依賴套件有關  
推薦: 3.10 ~ 3.12  
目前較推薦: 3.11  

## 快速安裝 - [uv 套件管理工具](https://docs.astral.sh/uv/getting-started/installation/)

### 生產階段(本套件可能不太適合鎖死版本)
[Pypi 套件庫](https://pypi.org/project/tw_textforge/)

```bash
pip install tw_textforge
```

### 開發階段(給有興趣的人自行衍生開發)

```bash
uv venv
uv pip install -e .[dev]
```

## 公開資料
[學測考試試題整理](https://docs.google.com/spreadsheets/d/e/2PACX-1vRtnMPEutqfeoQS2BNu2MGvSfM-ti-dNJTIDkd3BxMyAh7E0w-bbIShMgafX805UHSyyexNs_LxU0So/pubhtml)

## [範本](https://github.com/TsukiSama9292/TW-TextForge/tree/main/examples)

### [1. 載入 CSV 檔並且上傳到 Huggice Face Hub](https://github.com/TsukiSama9292/TW-TextForge/blob/main/examples/Dataset_Load_And_Upload.ipynb)

載入 CSV 靜態資料檔案並且上傳到 Huggice Face  
後續可利用 Datasets 的流式讀取(streaming) 載入資料集，降低模型訓練硬體需求  
算是 Datasets 的 "Hello World!"

### [2. LangGraph 單 Agent 範本](https://github.com/TsukiSama9292/TW-TextForge/blob/main/examples/GSATChineseGraph_QuestionAnalysis.ipynb)

生成題目解析作為訓練資料之一，讓 NLP 相關訓練效果更好

### [3. 修改系統路徑導入模組，適合修改內部程式碼](https://github.com/TsukiSama9292/TW-TextForge/blob/main/examples/Modules_Hot_Update.ipynb)

該方法在安裝過專案包的 Docker Image 也適用，可讓開發更容易

### [4. 擷取學測試題的題目和選項、答案，自動複製到剪貼簿(若支援)](https://github.com/TsukiSama9292/TW-TextForge/blob/main/examples/Modules_Hot_Update.ipynb)