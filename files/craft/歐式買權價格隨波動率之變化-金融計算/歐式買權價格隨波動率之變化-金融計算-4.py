import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(page_title="子主題A-(c)選擇權價格模擬", layout="wide")

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
st.title("子主題A-(c)：European call option 模擬價格與波動率")

st.sidebar.header("參數設定")

S0 = st.sidebar.slider("初始股價 S0",
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

sigma_range = st.sidebar.slider("sigma 範圍",
                                min_value=0.01,
                                max_value=1.0,
                                value=(0.1, 0.6),
                                step=0.01)
sigma_points = st.sidebar.slider("sigma 取點數",
                                 min_value=10,
                                 max_value=100,
                                 value=26,
                                 step=1)

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

random_type = "pseudo"


#%%
sigmas = np.linspace(sigma_range[0], sigma_range[1], sigma_points)

option_prices_same_Z_mean = np.zeros(len(sigmas))
option_prices_for_loop_mean = np.zeros(len(sigmas))

if fixed_seed:
    np.random.seed(int(seed))
else:
    np.random.seed(None)

if random_type == "pseudo":
    u = np.random.rand(m_paths, N)
    Z = stats.norm.ppf(u)

if random_type == "np.random.randn":
    Z = np.random.randn(m_paths, N)

if random_type == "np.random.normal":
    Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

for i in range(len(sigmas)):
    sigma = sigmas[i]

    option_prices_same_Z = European_option_simulation(S0, K, r, T, sigma, Z,
                                                      moment_matching=moment_matching,
                                                      option_type=option_type)

    option_prices_same_Z_mean[i] = np.mean(option_prices_same_Z)


if fixed_seed:
    np.random.seed(int(seed))
else:
    np.random.seed(None)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_for_loop = np.random.rand(m_paths, N)
        Z_for_loop = stats.norm.ppf(u_for_loop)

    if random_type == "np.random.randn":
        Z_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_for_loop = European_option_simulation(S0, K, r, T, sigma, Z_for_loop,
                                                        moment_matching=moment_matching,
                                                        option_type=option_type)

    option_prices_for_loop_mean[i] = np.mean(option_prices_for_loop)


#%%
col1, col2, col3 = st.columns(3)
col1.metric("Seed 設定", "固定" if fixed_seed else "不固定")
col2.metric("Moment Matching", "True" if moment_matching else "False")
col3.metric("sigma 範圍", f"{sigma_range[0]:.2f} - {sigma_range[1]:.2f}")

fig = plt.figure(figsize=(10, 6))

plt.plot(sigmas,
         option_prices_same_Z_mean,
         color="blue",
         linewidth=2,
         linestyle="--",
         label="same Z")

plt.plot(sigmas,
         option_prices_for_loop_mean,
         color="blue",
         linewidth=2,
         linestyle="-",
         label="Z in for loop")

plt.xlabel(r"$\sigma$")
plt.ylabel("European call option price")
plt.title("European call option simulation price and volatility")
plt.legend(loc="upper left", fontsize=8)
plt.grid(alpha=0.3)
plt.tight_layout()
st.pyplot(fig)


#%%
# (d) 完整結論：此段只寫在 .py 檔案中，不顯示於 Streamlit 頁面。
report_conclusion = """
完整結論：

本 Streamlit 程式延續子主題 A 的 European call option 蒙地卡羅模擬設定，
目的在於用互動方式觀察波動率 sigma 對買權價格的影響。頁面保留
S0 = 100、K = 100、r = 0.02、T = 0.5、m_paths = 1000、N = 1 等基礎設定，
並讓使用者透過側邊欄調整 sigma 範圍、模擬路徑數、亂數種子是否固定、
亂數種子數值，以及是否使用 Moment Matching。

固定亂數種子時，程式每次執行會產生相同的亂數序列，因此結果具有可重現性；
不固定亂數種子時，程式每次執行都可能重新抽到不同樣本，因此可以觀察蒙地卡羅
模擬受到亂數抽樣影響而產生的自然波動。Moment Matching 的設定則用來控制是否
將標準常態亂數重新標準化，使樣本平均數接近 0、標準差接近 1，以降低抽樣誤差。

圖表中藍色虛線為所有 sigma 共用同一批亂數 Z 所得到的模擬價格，
藍色實線則是在 for 迴圈中每一個 sigma 重新抽取亂數的模擬價格。
共用同一批 Z 時，曲線通常較平滑，因為不同 sigma 之間的亂數來源一致；每個 sigma
重新抽亂數時，曲線較容易呈現抖動，這反映的是蒙地卡羅模擬的抽樣誤差，而不是
選擇權定價理論本身改變。

由互動圖表可以觀察到，在其他參數固定時，European call option 的價格會隨著
sigma 增加而上升。原因是買權的 payoff 最低為 0，但當股價大幅上漲時，payoff
會隨著 ST-K 增加；因此較高的波動率會增加到期股價大幅上漲的可能性，進而提高
買權的期望 payoff 與折現後價格。

綜合而言，Streamlit 互動頁面能更直觀呈現波動率、亂數種子與 Moment Matching
對蒙地卡羅模擬結果的影響。固定 seed 主要提供可重現性，不固定 seed 則顯示抽樣
不確定性；Moment Matching 有助於降低亂數樣本偏差。不論使用哪一種設定，整體結果
皆支持子主題 A 的主要結論：在 GBM 假設下，European call option 價格與波動率
sigma 呈現正向關係。
"""
