(() => {
    const PAGES = [
        { t: 'Home',       url: 'index.html',      d: 'Back to the archive entrance', k: 'home index archive entrance start 首頁 回首頁 入口 主頁 開始' },
        { t: 'Log',        url: 'log.html',        d: 'Daily life · photo journal',   k: 'log daily life photo photos journal diary recent lately now today update updates doing 日常 日記 照片 生活 近況 最近 現在 今天 這陣子 動態 在幹嘛 幹嘛 在做什麼 做什麼 在忙 過得如何 大軍在幹嘛 他在幹嘛 你在幹嘛' },
        { t: 'Adventures', url: 'adventures.html', d: 'Travels by country & place',   k: 'adventures adventure travel travels trip trips places place country countries where went visited abroad 旅遊 旅行 旅程 出國 出遊 玩 去哪 去哪玩 去過 國家 地方 地點 景點 哪裡' },
        { t: 'Craft',      url: 'craft.html',      d: 'Projects, reports & work',     k: 'craft projects project work works reports report portfolio making built 作品 報告 專案 作品集 做的東西 做什麼 做什麼報告 做什麼作品 在做什麼 在做什麼專案 成果' },
        { t: 'Reach',      url: 'reach.html',      d: 'Find me across the web',       k: 'reach contact email social links message find connect 聯絡 聯繫 找他 找你 怎麼 怎麼找 怎麼聯絡 信箱 電子郵件 社群 連結 留言 找大軍' },
        { t: 'Join',       url: 'join.html',       d: 'Subscribe to the letter',      k: 'join subscribe newsletter member letter follow sign up 訂閱 加入 會員 電子報 通訊 追蹤 怎麼 怎麼加入 訂閱電子報 成為會員' },
    ];
    // Pre-split each page's keyword bank for intent scoring.
    PAGES.forEach(p => { p.kws = p.k.toLowerCase().split(/\s+/).filter(Boolean); });

    // Score how well a page answers the query. Works for both short typing
    // ("log") and full natural-language sentences ("最近大軍在幹嘛").
    function scorePage(page, q) {
        const hay = (page.t + ' ' + page.k + ' ' + page.d).toLowerCase();
        let score = 0;
        // 1) page keywords that appear inside the query → catches whole sentences
        for (const kw of page.kws) {
            if (kw.length >= 2 && q.includes(kw)) score += kw.length;
        }
        // 2) latin word-tokens from the query found in the page → partial typing
        for (const tok of q.split(/[^a-z0-9]+/).filter(t => t.length >= 2)) {
            if (hay.includes(tok)) score += tok.length;
        }
        // 3) whole query is a substring of the page text → original behaviour
        if (hay.includes(q)) score += q.length;
        return score;
    }

    function rankPages(q) {
        q = q.trim().toLowerCase();
        if (!q) return [];
        return PAGES
            .map(p => ({ page: p, score: scorePage(p, q) }))
            .filter(x => x.score > 0)
            .sort((a, b) => b.score - a.score)
            .map(x => x.page);
    }

    function esc(s) {
        return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    }

    function renderShell(panel) {
        if (panel.querySelector('.site-search-form')) return;
        panel.innerHTML = `
            <form class="site-search-form" role="search">
                <div class="site-search-box">
                    <button type="button" class="site-search-plus" aria-label="Open menu" aria-haspopup="true" aria-expanded="false">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
                    </button>
                    <input type="text" class="site-search-input" autocomplete="off"
                           placeholder="What are you looking for?" aria-label="Search the archive">
                    <button type="submit" class="site-search-submit" aria-label="Go">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>
                    </button>
                </div>
                <ul class="site-search-navmenu" hidden>
                    ${PAGES.map(page => `<li><button type="button" data-q="${esc(page.t)}">${esc(page.t)}</button></li>`).join('')}
                </ul>
                <ul class="site-search-suggest" hidden></ul>
            </form>
        `;
    }

    function initSiteSearch(panel) {
        renderShell(panel);
        const form = panel.querySelector('.site-search-form');
        const input = panel.querySelector('.site-search-input');
        const list = panel.querySelector('.site-search-suggest');
        const plus = panel.querySelector('.site-search-plus');
        const navMenu = panel.querySelector('.site-search-navmenu');
        if (!form || !input || !list) return;

        function render() {
            const items = rankPages(input.value);
            if (!items.length) {
                list.hidden = true;
                list.innerHTML = '';
                return;
            }
            list.innerHTML = items.map((x, i) =>
                `<li><a class="site-search-suggestion${i === 0 ? ' is-top' : ''}" href="${x.url}">` +
                `<span class="site-search-suggestion-title">${esc(x.t)}</span>` +
                `<span class="site-search-suggestion-desc">${esc(x.d)}</span>` +
                `<span class="site-search-suggestion-arrow" aria-hidden="true">&#8599;</span></a></li>`
            ).join('');
            list.hidden = false;
        }

        function bestMatch(q) {
            return rankPages(q)[0] || null;
        }

        function setMenu(open) {
            if (!navMenu || !plus) return;
            navMenu.hidden = !open;
            form.classList.toggle('menu-open', open);
            plus.setAttribute('aria-expanded', String(open));
            if (open) list.hidden = true;
        }

        input.addEventListener('input', () => {
            setMenu(false);
            render();
        });
        input.addEventListener('focus', () => setMenu(false));

        form.addEventListener('submit', e => {
            e.preventDefault();
            const match = bestMatch(input.value);
            if (match) window.location.href = match.url;
        });

        if (plus) {
            plus.addEventListener('click', e => {
                e.stopPropagation();
                setMenu(navMenu.hidden);
            });
        }

        if (navMenu) {
            navMenu.querySelectorAll('button[data-q]').forEach(btn => {
                btn.addEventListener('click', () => {
                    input.value = btn.dataset.q;
                    setMenu(false);
                    list.hidden = true;
                    input.focus();
                });
            });
        }

        document.addEventListener('click', e => {
            if (!panel.contains(e.target)) {
                list.hidden = true;
                setMenu(false);
            }
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                list.hidden = true;
                setMenu(false);
            }
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-site-search]').forEach(initSiteSearch);
    });
})();
