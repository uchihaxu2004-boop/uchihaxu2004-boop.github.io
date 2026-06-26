import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(page_title="子主題B Delta 模擬", layout="wide")

font_size = 12
plt.rcParams.update({"font.size": font_size})


#%%
def Black_Scholes(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    if option_type == "call":
        option_price = S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
    if option_type == "put":
        option_price = K*np.exp(-r*T)*stats.norm.cdf(-d2)-S0*stats.norm.cdf(-d1)

    return option_price

def Black_Scholes_Delta(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    if option_type == "call":
        Delta = stats.norm.cdf(d1)
    if option_type == "put":
        Delta = -stats.norm.cdf(-d1)

    return Delta

def European_option_simulation(S0, K, r, T, sigma, Z,
                               moment_matching=False,
                               option_type="call"):
    if moment_matching:
        Z = (Z-np.mean(Z, axis=0))/np.std(Z, axis=0)
        # 每個 column 計算平均數和標準差，做 moment matching。

    ST = S0*np.exp((r-0.5*sigma**2)*T+sigma*np.sqrt(T)*Z)

    if option_type == "call":
        payoff = np.maximum(ST-K, 0)
    if option_type == "put":
        payoff = np.maximum(K-ST, 0)

    option_prices = np.exp(-r*T)*np.mean(payoff, axis=0)

    return option_prices


#%%
st.title("子主題 B：European call option Delta 模擬")

st.sidebar.header("參數設定")

S0 = st.sidebar.slider("初始股價 S0（調整 Delta）",
                       min_value=50.0,
                       max_value=150.0,
                       value=100.0,
                       step=1.0)
K = st.sidebar.slider("履約價格 K",
                      min_value=50.0,
                      max_value=150.0,
                      value=100.0,
                      step=1.0)
r = st.sidebar.slider("無風險利率 r",
                      min_value=0.0,
                      max_value=0.2,
                      value=0.02,
                      step=0.01)
T = st.sidebar.selectbox("到期時間 T",
                         options=[0.1, 0.5, 1.0, 2.0, 3.0],
                         index=1)
sigma = st.sidebar.slider("波動率 sigma",
                          min_value=0.01,
                          max_value=1.0,
                          value=0.2,
                          step=0.01)

option_type = "call"
moment_matching = st.sidebar.checkbox("使用 Moment Matching", value=True)

m_paths = st.sidebar.slider("模擬路徑數 m_paths",
                            min_value=100,
                            max_value=10000,
                            value=1000,
                            step=100)
N = 1

fixed_seed = st.sidebar.checkbox("固定亂數種子", value=True)
seed = st.sidebar.number_input("亂數種子 seed",
                               min_value=0,
                               max_value=999999,
                               value=42,
                               step=1)

h_min_power = st.sidebar.slider("h 最小次方",
                                min_value=-16,
                                max_value=-2,
                                value=-16,
                                step=1)
h_max_power = st.sidebar.slider("h 最大次方",
                                min_value=-1,
                                max_value=1,
                                value=1,
                                step=1)
h_points = st.sidebar.slider("h 取點數",
                             min_value=20,
                             max_value=200,
                             value=100,
                             step=10)

random_type = "pseudo"


#%%
delta_true = Black_Scholes_Delta(S0, K, r, T, sigma, option_type=option_type)
hs = np.logspace(h_min_power, h_max_power, h_points)

delta_simulation = np.zeros(len(hs))
error = np.zeros(len(hs))

if fixed_seed:
    np.random.seed(int(seed))
else:
    np.random.seed(None)

for i in range(len(hs)):
    h = hs[i]

    if random_type == "pseudo":
        u = np.random.rand(m_paths, N)
        Z = stats.norm.ppf(u)

    if random_type == "np.random.randn":
        Z = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_price_up = European_option_simulation(S0+h, K, r, T, sigma, Z,
                                                 moment_matching=moment_matching,
                                                 option_type=option_type)

    option_price = European_option_simulation(S0, K, r, T, sigma, Z,
                                              moment_matching=moment_matching,
                                              option_type=option_type)

    delta_simulation[i] = np.mean((option_price_up-option_price)/h)
    error[i] = np.abs((delta_simulation[i]-delta_true)/delta_true)


#%%
col1, col2, col3 = st.columns(3)
col1.metric("True Delta", f"{delta_true:.6f}")
col2.metric("Seed 設定", "固定" if fixed_seed else "不固定")
col3.metric("Moment Matching", "True" if moment_matching else "False")

fig = plt.figure(figsize=(9, 7))

plt.subplot(2, 1, 1)
plt.axhline(y=delta_true,
            color="gray",
            label="True Delta",
            linewidth=2)
plt.plot(hs,
         delta_simulation,
         color="blue",
         linestyle="-",
         label="Simulation Delta",
         linewidth=2)
plt.xlabel("h")
plt.ylabel("Delta")
plt.xscale("log")
plt.legend(loc="upper right", fontsize=8)

plt.subplot(2, 1, 2)
plt.plot(hs,
         error,
         color="blue",
         linestyle="-",
         label="Simulation Delta Error",
         linewidth=2)
plt.axhline(y=0,
            color="gray",
            linewidth=2)
plt.xlabel("h")
plt.ylabel("Absolute Relative Error")
plt.xscale("log")
plt.legend(loc="upper right", fontsize=8)

plt.tight_layout()
st.pyplot(fig)


#%%
# (d) 完整結論：此段只寫在 .py 檔案中，不顯示於 Streamlit 頁面。
report_conclusion = """
完整結論：

本 Streamlit 程式延續子主題 B 的 Delta 模擬分析，目的在於將 European call option 的模擬 Delta
結果以互動方式呈現。使用者可以透過側邊欄調整會影響 Delta 的參數，例如初始股價 S0、履約價格 K、
無風險利率 r、到期時間 T 與波動率 sigma，並觀察 Black-Scholes 理論 Delta 與蒙地卡羅模擬 Delta
之間的差異。

本程式同時提供亂數種子設定與固定/不固定亂數種子的開關。固定亂數種子時，每次執行會產生相同的
亂數序列，因此結果具有可重現性；不固定亂數種子時，每次執行可能產生不同的亂數樣本，因此能呈現
蒙地卡羅模擬受到抽樣誤差影響的特性。

此外，程式也提供 Moment Matching 的 True/False 開關。使用 Moment Matching 時，標準常態亂數會被
校正為平均數接近 0、標準差接近 1，因此能降低部分亂數抽樣誤差，使模擬結果較穩定；不使用
Moment Matching 時，模擬結果會保留原始亂數樣本的抽樣波動。

圖表上半部呈現不同 h 下的 Simulation Delta，並以灰色水平線表示 Black-Scholes 理論 Delta；
圖表下半部則呈現模擬 Delta 相對於理論 Delta 的絕對相對誤差。由此可以觀察到，Delta 估計結果
會受到差分間距 h、亂數種子設定、Moment Matching 與模擬路徑數的影響。

綜合而言，Streamlit 互動頁面可以更直觀地比較不同參數設定下的 Delta 模擬結果，也能幫助理解
蒙地卡羅方法估計希臘值時，亂數抽樣與數值差分設定對結果穩定性的影響。
"""
