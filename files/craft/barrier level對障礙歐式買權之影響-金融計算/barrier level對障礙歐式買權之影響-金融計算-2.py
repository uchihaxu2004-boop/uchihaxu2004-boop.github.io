import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

plt.close("all")

font_size = 14
plt.rcParams.update({"font.size": font_size})

def Black_Scholes(S0, K, r, T, sigma, option_type="call"):
    d1 = (np.log(S0/K)+(r+sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1-sigma*np.sqrt(T)
    if option_type == "call":
        option_price = S0*stats.norm.cdf(d1)-K*np.exp(-r*T)*stats.norm.cdf(d2)
    if option_type == "put":
        option_price = K*np.exp(-r*T)*stats.norm.cdf(-d2)-S0*stats.norm.cdf(-d1)

    return option_price

def GBM_simulation_paths(S0, r, T, sigma, Z):
    NumPaths, n = Z.shape
    dt = T/n
    mu = r-sigma**2/2
    R = mu*dt+sigma*np.sqrt(dt)*Z

    S = S0*np.ones((NumPaths, n+1))
    for j in range(n):
        S[:, j+1] = S[:, j]*np.exp(R[:, j])

    return S


def barrier_prices_from_paths(S, K, B, r, T):
    ST = S[:, -1]
    min_S = np.min(S, axis=1)
    vanilla_payoff = np.maximum(ST-K, 0)

    down_and_out_payoff = vanilla_payoff*(min_S > B)
    down_and_in_payoff = vanilla_payoff*(min_S <= B)

    vanilla_price = np.exp(-r*T)*np.mean(vanilla_payoff)
    down_and_out_price = np.exp(-r*T)*np.mean(down_and_out_payoff)
    down_and_in_price = np.exp(-r*T)*np.mean(down_and_in_payoff)

    return vanilla_price, down_and_out_price, down_and_in_price



S0 = 100.0    
K = 100.0    
r = 0.02      
T = 0.5       
sigma = 0.2  
option_type = "call"

time_intervals_year = 252
dt = 1/time_intervals_year
n = int(T/dt)

m_paths = 1000    
seed = 42

B_levels = np.arange(50, 100, 2)
vanilla_call_BS = Black_Scholes(S0, K, r, T, sigma,
                                option_type=option_type)

print("Vanilla European call option price (Black-Scholes) =",
      vanilla_call_BS)


#%%
# 情況 1：固定 random seed。
# 固定 seed 的重點是：所有 barrier level 都使用同一批 GBM paths。
# 因此不同 B 的價格差異主要來自 barrier level 本身，
# 不會混入每個 B 重新抽不同亂數造成的抽樣誤差。
np.random.seed(seed)

u_fixed = np.random.rand(m_paths, n)
Z_fixed = stats.norm.ppf(u_fixed)
S_fixed = GBM_simulation_paths(S0, r, T, sigma, Z_fixed)

prices_DO_fixed = np.zeros(len(B_levels))
prices_DI_fixed = np.zeros(len(B_levels))
prices_vanilla_fixed = np.zeros(len(B_levels))

for i in range(len(B_levels)):
    B = B_levels[i]
    prices_vanilla_fixed[i], prices_DO_fixed[i], prices_DI_fixed[i] = \
        barrier_prices_from_paths(S_fixed, K, B, r, T)


#%%
# 情況 2：不固定 random seed。
# 不固定 seed 的比較目標是：每個 barrier level 都重新抽一批不同亂數。
# 因此這裡先用 np.random.seed(None)，再把「產生亂數」放在 B 迴圈內。
# 如此一來，每一個 B 的價格估計都來自不同 GBM paths。
np.random.seed(None)

prices_DO_unfixed = np.zeros(len(B_levels))
prices_DI_unfixed = np.zeros(len(B_levels))
prices_vanilla_unfixed = np.zeros(len(B_levels))

for i in range(len(B_levels)):
    B = B_levels[i]

    u_unfixed = np.random.rand(m_paths, n)
    Z_unfixed = stats.norm.ppf(u_unfixed)
    S_unfixed = GBM_simulation_paths(S0, r, T, sigma, Z_unfixed)

    prices_vanilla_unfixed[i], prices_DO_unfixed[i], prices_DI_unfixed[i] = \
        barrier_prices_from_paths(S_unfixed, K, B, r, T)


#%%
# 圖：不同 barrier level 下，fixed seed 與 unfixed seed 的價格比較。
# 依題目重點，只畫價格曲線，不畫直方圖。
plt.figure(figsize=(10, 8))

plt.subplot(2, 1, 1)
plt.axhline(y=vanilla_call_BS,
            color="red",
            linewidth=2,
            label="Vanilla call (Black-Scholes)")
plt.plot(B_levels,
         prices_DO_fixed,
         color="blue",
         marker="o",
         linewidth=2,
         label="Down-and-out (fixed seed)")
plt.plot(B_levels,
         prices_DO_unfixed,
         color="purple",
         marker="x",
         linestyle="--",
         linewidth=2,
         label="Down-and-out (unfixed seed)")
plt.xlabel("barrier level B")
plt.ylabel("option price")
plt.title("Down-and-out call price vs barrier level")
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(2, 1, 2)
plt.axhline(y=vanilla_call_BS,
            color="red",
            linewidth=2,
            label="Vanilla call (Black-Scholes)")
plt.plot(B_levels,
         prices_DI_fixed,
         color="green",
         marker="s",
         linewidth=2,
         label="Down-and-in (fixed seed)")
plt.plot(B_levels,
         prices_DI_unfixed,
         color="orange",
         marker="x",
         linestyle="--",
         linewidth=2,
         label="Down-and-in (unfixed seed)")
plt.xlabel("barrier level B")
plt.ylabel("option price")
plt.title("Down-and-in call price vs barrier level")
plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()


#%%
# 輸出代表性數值，方便報告引用。
print("\n子主題 C-(a)")
print("B, DO fixed, DO unfixed, DI fixed, DI unfixed")

B_examples = [50, 70, 80, 90, 98]
for B in B_examples:
    index = np.argmin(np.abs(B_levels-B))
    print(f"{B_levels[index]:.0f}, "
          f"{prices_DO_fixed[index]:.6f}, "
          f"{prices_DO_unfixed[index]:.6f}, "
          f"{prices_DI_fixed[index]:.6f}, "
          f"{prices_DI_unfixed[index]:.6f}")


#%%
# In-out parity 檢查。
# fixed seed 下，每個 B 都用同一批路徑，所以 DO + DI 會等於同批路徑下的 vanilla MC。
# unfixed seed 下，每個 B 各自抽樣，因此每個 B 的 DO+DI 也等於該 B 那批路徑的 vanilla MC，
# 但跨 B 比較時曲線可能較不平滑。
parity_error_fixed = prices_DO_fixed+prices_DI_fixed-prices_vanilla_fixed
parity_error_unfixed = prices_DO_unfixed+prices_DI_unfixed-prices_vanilla_unfixed

print("\nIn-out parity error")
print("fixed seed max abs error =",
      f"{np.max(np.abs(parity_error_fixed)):.6e}")
print("unfixed seed max abs error =",
      f"{np.max(np.abs(parity_error_unfixed)):.6e}")


#%%
# 結論：
conclusion = """
子主題 C-(a) 結論：
1. 本題比較在評價 Barrier European call option 時，
   不同 barrier level 是否使用同一批亂數，對模擬價格曲線的影響。
   固定 seed 的情況下，所有 barrier level 共用同一批 GBM paths；
   不固定 seed 的情況下，每一個 barrier level 都重新抽一批不同 paths。

2. 從 down-and-out call 的圖可以看出，
   barrier level B 越接近 S0=100，選擇權越容易被觸發失效，
   因此 down-and-out call 價格會下降。
   固定 seed 曲線通常較平滑，因為不同 B 的價格差異主要來自 barrier 本身；
   不固定 seed 曲線可能略有抖動，因為每個 B 的價格估計還混入不同亂數抽樣誤差。

3. 從 down-and-in call 的圖可以看出，
   barrier level B 越接近 S0=100，越容易觸發生效，
   因此 down-and-in call 價格會上升。
   這和 down-and-out call 形成互補關係。

4. 固定 seed 的好處是可重現性與比較乾淨。
   因為所有 B 共用同一批路徑，所以圖形變化主要反映 barrier level 對價格的影響。
   這和前面子主題使用 common random numbers 的想法一致，
   可以降低參數比較時的亂數雜訊。

5. 不固定 seed 比較接近每個 barrier level 各自重新做一次 Monte Carlo 實驗。
   它可以反映重新抽樣時可能產生的隨機變化，
   但在比較不同 B 的價格曲線時，會讓曲線較容易出現抽樣造成的小幅波動。

6. In-out parity 檢查顯示，對同一批路徑而言：
        Down-and-out call + Down-and-in call = Vanilla call
   因為每條路徑不是沒有碰到 barrier，就是有碰到 barrier。
   程式輸出的 parity error 非常接近 0，表示 payoff 分解正確。

7. 綜合而言，若目標是清楚比較 barrier level 對價格的影響，
   建議使用固定 seed，讓不同 B 使用同一批亂數。
   若目標是觀察每次重新模擬可能造成的估計差異，
   則可以使用不固定 seed。
   但不論 seed 是否固定，主要結論相同：
   B 越接近 S0，down-and-out call 價格越低，down-and-in call 價格越高。
"""

print(conclusion)
