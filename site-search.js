(() => {
    const PAGES = [
        { t: 'Home',       url: 'index.html',      d: 'Back to the archive entrance', k: 'home index archive 首頁' },
        { t: 'Log',        url: 'log.html',        d: 'Daily life · photo journal',   k: 'log daily life photo photos journal diary 日常 日記 照片 生活' },
        { t: 'Adventures', url: 'adventures.html', d: 'Travels by country & place',   k: 'adventures travel trips places country countries 旅遊 旅行 國家 地方' },
        { t: 'Craft',      url: 'craft.html',      d: 'Projects, reports & work',     k: 'craft projects project work reports portfolio 作品 報告 專案' },
        { t: 'Reach',      url: 'reach.html',      d: 'Find me across the web',       k: 'reach contact email social links 聯絡 社群' },
        { t: 'Join',       url: 'join.html',       d: 'Subscribe to the letter',      k: 'join subscribe newsletter member letter 訂閱 會員' },
    ];

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
            const q = input.value.trim().toLowerCase();
            const items = q === '' ? [] : PAGES.filter(x => (x.t + ' ' + x.k + ' ' + x.d).toLowerCase().includes(q));
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
            q = q.trim().toLowerCase();
            if (!q) return null;
            return PAGES.find(x => (x.t + ' ' + x.k + ' ' + x.d).toLowerCase().includes(q)) || null;
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
