import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import streamlit as st


st.set_page_config(page_title="子主題C Barrier option 模擬", layout="wide")

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


def GBM_simulation_paths(S0, r, T, sigma, Z, moment_matching=False):
    if moment_matching:
        Z = (Z-np.mean(Z, axis=0))/np.std(Z, axis=0)
        # 每個 column 計算平均數和標準差，做 moment matching。

    NumPaths, n = Z.shape
    dt = T/n
    mu = r-sigma**2/2
    R = mu*dt+sigma*np.sqrt(dt)*Z

    S = S0*np.ones((NumPaths, n+1))
    for j in range(n):
        S[:, j+1] = S[:, j]*np.exp(R[:, j])

    return S


def make_standard_normal(m_paths, n, random_type="pseudo"):
    if random_type == "pseudo":
        u = np.random.rand(m_paths, n)
        Z = stats.norm.ppf(u)

    if random_type == "np.random.randn":
        Z = np.random.randn(m_paths, n)

    if random_type == "np.random.normal":
        Z = np.random.normal(loc=0.0, scale=1.0, size=(m_paths, n))

    return Z


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


def barrier_option_simulation(S0, K, B, r, T, sigma, Z,
                              moment_matching=False,
                              barrier_type="down-and-out"):
    S = GBM_simulation_paths(S0, r, T, sigma, Z,
                             moment_matching=moment_matching)
    vanilla_price, down_and_out_price, down_and_in_price = \
        barrier_prices_from_paths(S, K, B, r, T)

    if barrier_type == "down-and-out":
        option_price = down_and_out_price
    if barrier_type == "down-and-in":
        option_price = down_and_in_price
    if barrier_type == "vanilla":
        option_price = vanilla_price

    return option_price


def barrier_delta_simulation(S0, K, B, r, T, sigma, Z, h,
                             moment_matching=False,
                             barrier_type="down-and-out"):
    option_price_up = barrier_option_simulation(S0+h, K, B, r, T, sigma, Z,
                                                moment_matching=moment_matching,
                                                barrier_type=barrier_type)
    option_price = barrier_option_simulation(S0, K, B, r, T, sigma, Z,
                                             moment_matching=moment_matching,
                                             barrier_type=barrier_type)

    Delta = (option_price_up-option_price)/h

    return Delta


def compute_price_curves(S0, K, r, T, sigma, B_levels,
                         m_paths, n, seed_value,
                         moment_matching=True,
                         resample_each_barrier=False,
                         random_type="pseudo"):
    prices_vanilla = np.zeros(len(B_levels))
    prices_DO = np.zeros(len(B_levels))
    prices_DI = np.zeros(len(B_levels))

    np.random.seed(seed_value)

    if not resample_each_barrier:
        Z = make_standard_normal(m_paths, n, random_type)
        S = GBM_simulation_paths(S0, r, T, sigma, Z,
                                 moment_matching=moment_matching)

        for i in range(len(B_levels)):
            B = B_levels[i]
            prices_vanilla[i], prices_DO[i], prices_DI[i] = \
                barrier_prices_from_paths(S, K, B, r, T)

    if resample_each_barrier:
        for i in range(len(B_levels)):
            B = B_levels[i]
            Z = make_standard_normal(m_paths, n, random_type)
            S = GBM_simulation_paths(S0, r, T, sigma, Z,
                                     moment_matching=moment_matching)
            prices_vanilla[i], prices_DO[i], prices_DI[i] = \
                barrier_prices_from_paths(S, K, B, r, T)

    return prices_vanilla, prices_DO, prices_DI


def benchmark_barrier_delta(S0, K, B, r, T, sigma, h, n,
                            reference_paths, seed,
                            moment_matching=True,
                            barrier_type="down-and-out",
                            random_type="pseudo"):
    np.random.seed(seed)
    Z_reference = make_standard_normal(reference_paths, n, random_type)
    Delta = barrier_delta_simulation(S0, K, B, r, T, sigma, Z_reference, h,
                                     moment_matching=moment_matching,
                                     barrier_type=barrier_type)

    return Delta


#%%
st.title("子主題 C：Barrier European call option 模擬")

if "unfixed_seed_value_c" not in st.session_state:
    st.session_state.unfixed_seed_value_c = np.random.randint(1, 2**31-1)

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
sigma = st.sidebar.slider("波動率 sigma",
                          min_value=0.01,
                          max_value=1.0,
                          value=0.2,
                          step=0.01)

max_barrier = max(11.0, min(99.0, S0-1.0))
default_B_min = min(60.0, max_barrier-1.0)
default_B_max = max(default_B_min+1.0, min(99.0, max_barrier))

B_min = st.sidebar.slider("barrier level 起點",
                          min_value=10.0,
                          max_value=max_barrier-1.0,
                          value=default_B_min,
                          step=1.0)
B_max = st.sidebar.slider("barrier level 終點",
                          min_value=B_min+1.0,
                          max_value=max_barrier,
                          value=max(B_min+1.0, default_B_max),
                          step=1.0)
B_points = st.sidebar.slider("barrier level 取點數",
                             min_value=10,
                             max_value=80,
                             value=40,
                             step=5)
B_selected = st.sidebar.slider("Delta 使用的 barrier B",
                               min_value=B_min,
                               max_value=B_max,
                               value=min(max(90.0, B_min), B_max),
                               step=1.0)

moment_matching = st.sidebar.checkbox("使用 Moment Matching", value=True)
m_paths = st.sidebar.slider("模擬路徑數 m_paths",
                            min_value=100,
                            max_value=10000,
                            value=1000,
                            step=100)
fixed_seed = st.sidebar.checkbox("固定亂數種子", value=True)
seed = st.sidebar.number_input("亂數種子 seed",
                               min_value=0,
                               max_value=999999,
                               value=42,
                               step=1)
if st.sidebar.button("重新產生不固定 seed"):
    st.session_state.unfixed_seed_value_c = np.random.randint(1, 2**31-1)

st.sidebar.subheader("Delta 差分設定")
delta_barrier_type = st.sidebar.selectbox("Delta barrier type",
                                          options=["down-and-out", "down-and-in"],
                                          index=0)
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


#%%
option_type = "call"
random_type = "pseudo"

time_intervals_year = 252
dt = 1/time_intervals_year
n = int(T/dt)

B_levels = np.linspace(B_min, B_max, B_points)
effective_seed = int(seed) if fixed_seed else int(st.session_state.unfixed_seed_value_c)
unfixed_seed = int(st.session_state.unfixed_seed_value_c)

vanilla_call_BS = Black_Scholes(S0, K, r, T, sigma,
                                option_type=option_type)
vanilla_delta_BS = Black_Scholes_Delta(S0, K, r, T, sigma,
                                       option_type=option_type)

prices_vanilla_same, prices_DO_same, prices_DI_same = \
    compute_price_curves(S0, K, r, T, sigma, B_levels,
                         int(m_paths), n, effective_seed,
                         moment_matching=moment_matching,
                         resample_each_barrier=False,
                         random_type=random_type)

prices_vanilla_for_loop, prices_DO_for_loop, prices_DI_for_loop = \
    compute_price_curves(S0, K, r, T, sigma, B_levels,
                         int(m_paths), n, effective_seed,
                         moment_matching=moment_matching,
                         resample_each_barrier=True,
                         random_type=random_type)

prices_vanilla_fixed, prices_DO_fixed, prices_DI_fixed = \
    compute_price_curves(S0, K, r, T, sigma, B_levels,
                         int(m_paths), n, int(seed),
                         moment_matching=moment_matching,
                         resample_each_barrier=True,
                         random_type=random_type)

prices_vanilla_unfixed, prices_DO_unfixed, prices_DI_unfixed = \
    compute_price_curves(S0, K, r, T, sigma, B_levels,
                         int(m_paths), n, unfixed_seed,
                         moment_matching=moment_matching,
                         resample_each_barrier=True,
                         random_type=random_type)


#%%
hs = np.logspace(h_min_power, h_max_power, h_points)
delta_same_Z = np.zeros(len(hs))
delta_for_loop = np.zeros(len(hs))
error_same_Z = np.zeros(len(hs))
error_for_loop = np.zeros(len(hs))

reference_paths = min(max(int(m_paths)*3, 3000), 12000)
h_reference = 1e-2
delta_benchmark = benchmark_barrier_delta(S0, K, B_selected, r, T, sigma,
                                          h_reference, n,
                                          reference_paths,
                                          int(seed)+100,
                                          moment_matching=moment_matching,
                                          barrier_type=delta_barrier_type,
                                          random_type=random_type)
denominator = max(abs(delta_benchmark), 1e-12)

np.random.seed(effective_seed)
Z_same = make_standard_normal(int(m_paths), n, random_type)

for i in range(len(hs)):
    h = hs[i]
    delta_same_Z[i] = barrier_delta_simulation(S0, K, B_selected, r, T, sigma,
                                               Z_same, h,
                                               moment_matching=moment_matching,
                                               barrier_type=delta_barrier_type)
    error_same_Z[i] = np.abs((delta_same_Z[i]-delta_benchmark)/denominator)

np.random.seed(effective_seed)

for i in range(len(hs)):
    h = hs[i]
    Z_for_loop = make_standard_normal(int(m_paths), n, random_type)
    delta_for_loop[i] = barrier_delta_simulation(S0, K, B_selected, r, T, sigma,
                                                 Z_for_loop, h,
                                                 moment_matching=moment_matching,
                                                 barrier_type=delta_barrier_type)
    error_for_loop[i] = np.abs((delta_for_loop[i]-delta_benchmark)/denominator)


#%%
col1, col2, col3, col4 = st.columns(4)
col1.metric("Seed 設定", "固定" if fixed_seed else "不固定")
col2.metric("Moment Matching", "True" if moment_matching else "False")
col3.metric("Vanilla call BS price", f"{vanilla_call_BS:.6f}")
col4.metric("Vanilla Delta BS", f"{vanilla_delta_BS:.6f}")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Delta barrier B", f"{B_selected:.2f}")
col6.metric("Benchmark Barrier Delta", f"{delta_benchmark:.6f}")
col7.metric("本次有效 seed", f"{effective_seed}")
col8.metric("不固定 seed", f"{unfixed_seed}")

tab1, tab2, tab3, tab4 = st.tabs([
    "C 價格與 barrier level",
    "C-(a) 固定與不固定 seed",
    "C-(b) Delta 與 h",
    "數值結果"
])
with tab1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(B_levels,
             prices_DO_same,
             color="blue",
             linestyle="--",
             linewidth=2,
             label="down-and-out call, same paths")
    ax1.plot(B_levels,
             prices_DO_for_loop,
             color="blue",
             linestyle="-",
             linewidth=2,
             label="down-and-out call, paths in for loop")
    ax1.plot(B_levels,
             prices_DI_same,
             color="red",
             linestyle="--",
             linewidth=2,
             label="down-and-in call, same paths")
    ax1.plot(B_levels,
             prices_DI_for_loop,
             color="red",
             linestyle="-",
             linewidth=2,
             label="down-and-in call, paths in for loop")
    ax1.axhline(y=vanilla_call_BS,
                color="gray",
                linestyle=":",
                linewidth=2,
                label="European call price (Black-Scholes)")
    ax1.set_xlabel("barrier level")
    ax1.set_ylabel("option price")
    ax1.set_title("Barrier European call option simulation price and barrier level")
    ax1.legend(fontsize=8)
    ax1.grid(alpha=0.3)
    fig1.tight_layout()
    st.pyplot(fig1)


with tab2:
    fig2 = plt.figure(figsize=(10, 8))

    plt.subplot(2, 1, 1)
    plt.axhline(y=vanilla_call_BS,
                color="gray",
                linestyle=":",
                linewidth=2,
                label="European call price (Black-Scholes)")
    plt.plot(B_levels,
             prices_DO_fixed,
             color="blue",
             linewidth=2,
             label="down-and-out, fixed seed")
    plt.plot(B_levels,
             prices_DO_unfixed,
             color="red",
             linewidth=2,
             label="down-and-out, unfixed seed")
    plt.xlabel("barrier level")
    plt.ylabel("option price")
    plt.title("Down-and-out call price: fixed seed and unfixed seed")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.axhline(y=vanilla_call_BS,
                color="gray",
                linestyle=":",
                linewidth=2,
                label="European call price (Black-Scholes)")
    plt.plot(B_levels,
             prices_DI_fixed,
             color="green",
             linewidth=2,
             label="down-and-in, fixed seed")
    plt.plot(B_levels,
             prices_DI_unfixed,
             color="gold",
             linewidth=2,
             label="down-and-in, unfixed seed")
    plt.xlabel("barrier level")
    plt.ylabel("option price")
    plt.title("Down-and-in call price: fixed seed and unfixed seed")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig2)


with tab3:
    fig3 = plt.figure(figsize=(9, 7))

    plt.subplot(2, 1, 1)
    plt.axhline(y=delta_benchmark,
                color="gray",
                label="Benchmark Barrier Delta",
                linewidth=2)
    plt.plot(hs,
             delta_same_Z,
             color="blue",
             linestyle="--",
             label="Simulation Delta (same Z)",
             linewidth=2)
    plt.plot(hs,
             delta_for_loop,
             color="blue",
             linestyle="-",
             label="Simulation Delta (Z in for loop)",
             linewidth=2)
    plt.xlabel("h")
    plt.ylabel("Delta")
    plt.xscale("log")
    plt.legend(loc="upper right", fontsize=8)

    plt.subplot(2, 1, 2)
    plt.plot(hs,
             error_same_Z,
             color="blue",
             linestyle="--",
             label="Error (same Z)",
             linewidth=2)
    plt.plot(hs,
             error_for_loop,
             color="blue",
             linestyle="-",
             label="Error (Z in for loop)",
             linewidth=2)
    plt.axhline(y=0,
                color="gray",
                linewidth=2)
    plt.xlabel("h")
    plt.ylabel("Absolute Relative Error")
    plt.xscale("log")
    plt.legend(loc="upper right", fontsize=8)

    plt.tight_layout()
    st.pyplot(fig3)


with tab4:
    selected_index = np.argmin(np.abs(B_levels-B_selected))
    st.write("代表性 barrier level 數值")
    st.dataframe({
        "barrier level": B_levels,
        "DO same paths": prices_DO_same,
        "DI same paths": prices_DI_same,
        "DO fixed seed": prices_DO_fixed,
        "DO unfixed seed": prices_DO_unfixed,
        "DI fixed seed": prices_DI_fixed,
        "DI unfixed seed": prices_DI_unfixed,
    })

    st.write("目前選取的 barrier B")
    st.write({
        "B": float(B_levels[selected_index]),
        "Down-and-out price": float(prices_DO_same[selected_index]),
        "Down-and-in price": float(prices_DI_same[selected_index]),
        "DO + DI": float(prices_DO_same[selected_index]+prices_DI_same[selected_index]),
        "Vanilla call BS price": float(vanilla_call_BS),
        "Benchmark Barrier Delta": float(delta_benchmark),
    })


#%%
"""
結論：

本 Streamlit 程式依照子主題 C 的題目設計，將 Barrier European call option 的
價格與 Delta 分成三個部分呈現。第一個分頁探討 barrier level 對 down-and-out
call 與 down-and-in call 價格的影響，並比較所有 barrier 共用同一批路徑與每個
barrier 重新抽樣的差異。第二個分頁比較固定亂數種子與不固定亂數種子下，不同
barrier level 的評價結果。第三個分頁則依照子主題 B 的 Delta 討論方式，使用
forward difference 觀察 Barrier Delta 在不同 h 下的模擬結果與誤差。

Barrier option 是 path-dependent payoff，因此價格不只取決於到期股價 ST，也取決於
整段期間股價是否曾經碰到 barrier。當 barrier level 越接近初始股價時，down-and-out
call 越容易失效，價格會下降；down-and-in call 越容易生效，價格會上升。固定 seed
或共用同一批亂數可以讓曲線較平滑，較容易觀察 barrier level 本身的影響；不固定 seed
或每個 barrier 重新抽樣則會呈現蒙地卡羅抽樣誤差造成的自然波動。

在 Delta 部分，因為障礙選擇權沒有像 vanilla European call 那樣簡單的解析 Delta，
所以程式用較多參考路徑建立 Benchmark Barrier Delta，再用不同 h 的 forward difference
進行比較。當 h 過小時容易受到浮點數與抽樣誤差影響；當 h 過大時又不再能代表局部敏感度。
因此，Barrier Delta 的估計需要搭配適當 h、固定 seed、common random numbers 與
moment matching，才能得到較穩定且可解釋的結果。
"""
