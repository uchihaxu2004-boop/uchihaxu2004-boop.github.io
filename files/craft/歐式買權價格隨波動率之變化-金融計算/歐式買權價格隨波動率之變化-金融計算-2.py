import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

font_size = 14
plt.rcParams.update({"font.size": font_size})

plt.close("all")


#%%
def Black_Scholes(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    if option_type == "call":
        option_price = S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
    if option_type == "put":
        option_price = K*np.exp(-r*T)*stats.norm.cdf(-d2)-S0*stats.norm.cdf(-d1)

    return option_price

def European_option_simulation(S0, K, r, T, sigma, Z, moment_matching=False, option_type="call"):
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
# 參數設定
S0 = 100.0
K = 100.0
r = 0.02
T = 0.5

option_type = "call"
moment_matching = True

m_paths = 1000
N = 1

random_type = "pseudo"


#%%
# 探討不同波動率 sigma 對 European call option 模擬價格的影響
sigmas = np.linspace(0.1, 0.6, 26)

option_prices_seed_for_loop_mean = np.zeros(len(sigmas))
option_prices_no_seed_for_loop_mean = np.zeros(len(sigmas))


#%%
# 固定亂數種子，並在 for 迴圈中每一個 sigma 重新產生亂數
seed = 42
np.random.seed(seed)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_seed_for_loop = np.random.rand(m_paths, N)
        Z_seed_for_loop = stats.norm.ppf(u_seed_for_loop)

    if random_type == "np.random.randn":
        Z_seed_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_seed_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_seed_for_loop = European_option_simulation(S0, K, r, T, sigma, Z_seed_for_loop,
                                                             moment_matching=moment_matching,
                                                             option_type=option_type)

    option_prices_seed_for_loop_mean[i] = np.mean(option_prices_seed_for_loop)


#%%
# 不固定亂數種子，並在 for 迴圈中每一個 sigma 重新產生亂數
np.random.seed(None)

for i in range(len(sigmas)):
    sigma = sigmas[i]

    if random_type == "pseudo":
        u_no_seed_for_loop = np.random.rand(m_paths, N)
        Z_no_seed_for_loop = stats.norm.ppf(u_no_seed_for_loop)

    if random_type == "np.random.randn":
        Z_no_seed_for_loop = np.random.randn(m_paths, N)

    if random_type == "np.random.normal":
        Z_no_seed_for_loop = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, N))

    option_prices_no_seed_for_loop = European_option_simulation(S0, K, r, T, sigma, Z_no_seed_for_loop,
                                                                moment_matching=moment_matching,
                                                                option_type=option_type)

    option_prices_no_seed_for_loop_mean[i] = np.mean(option_prices_no_seed_for_loop)


#%%
# 圖：比較固定與不固定亂數種子下，European call option 模擬價格與 sigma 之關係
plt.figure(figsize=(10, 6))

plt.plot(sigmas,
         option_prices_seed_for_loop_mean,
         color="blue",
         linewidth=2,
         linestyle="-",
         label="fixed seed = 42")

plt.plot(sigmas,
         option_prices_no_seed_for_loop_mean,
         color="red",
         linewidth=2,
         linestyle="-",
         label="unfixed seed")

plt.xlabel(r"$\sigma$")
plt.ylabel("European call option price")
plt.title("European call option simulation price: fixed seed and unfixed seed")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


#%%
"""
結論：

本程式延續子主題 A 的設定，目的在於比較不同波動率 sigma 下，亂數種子固定與不固定時，
European call option 蒙地卡羅模擬價格的差異。其他參數皆保持不變，包括 S0 = 100、K = 100、
r = 0.02、T = 0.5、m_paths = 1000、N = 1，以及 moment_matching = True。

固定亂數種子 seed = 42 的好處，是每次執行程式時都會產生相同的亂數序列，因此模擬結果具有
可重現性，方便檢查程式與比較不同參數下的結果。不固定亂數種子時，程式每次執行都可能產生
不同的亂數樣本。本題在每一個 sigma 下都重新抽一批亂數，因此曲線會比較容易出現抽樣波動，
反映蒙地卡羅模擬本身受到亂數抽樣影響的特性。

由圖表可以觀察到，不論亂數種子是否固定，European call option 的模擬價格都會隨著 sigma 增加
而上升。這表示前一題得到的主要結論並不是只由特定 seed 造成，而是與買權本身的性質有關。
當波動率提高時，到期股價的分散程度增加，股價大幅上漲的可能性提高，因此買權價格也會上升。

兩條線之間若出現些微差距，主要原因是固定 seed 與不固定 seed 所使用的亂數樣本不同。
由於本題 m_paths = 1000 且 N = 1，模擬樣本數有限，因此不同亂數樣本會造成模擬價格的輕微變動。
不過在使用 moment matching 後，亂數樣本會被校正成平均數接近 0、標準差接近 1，
因此兩條曲線的整體趨勢仍然相近。

綜合而言，本次比較顯示固定 seed 可以提升模擬結果的可重現性，而不固定 seed 則可以呈現蒙地卡羅
模擬在不同亂數樣本下的自然變動。雖然兩者的數值可能略有不同，但圖表共同支持同一個結論：
在其他條件固定下，European call option 的模擬價格會隨波動率 sigma 上升而增加。
"""
