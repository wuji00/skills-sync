/* 全站导航 · 单文件注入（模板：改下面 SITE_NAME / LINKS / THEME_KEY 即可）
 * 用法：任意页面 <script src="/nav.js" defer></script>
 * 行为：固定顶栏；移动端下滑隐藏、上滑显示；当前页高亮；
 *       深色模式切换（各页面 :root[data-theme="dark"] 共用同一套存储键）。
 */
(function () {
  // ==== 配置区：按你的站点改这三行 ====
  var SITE_NAME = '你的名字';
  var LINKS = [
    { href: '/work/', label: '作品' },
    { href: '/about/', label: '关于' },
  ];
  var THEME_KEY = 'my-site-theme';
  // ==== 配置区结束 ====
  var themable = true;

  /* ---------- 样式 ---------- */
  var css = [
    '.sk-nav{position:fixed;top:0;left:0;right:0;z-index:9990;height:64px;display:flex;align-items:center;justify-content:space-between;gap:16px;padding:0 max(22px, calc((100vw - 760px)/2));',
    'background:rgba(250,251,252,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);',
    'font-family:"Inter",ui-sans-serif,-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;',
    'transform:translateY(0);transition:transform .28s ease,background-color .18s ease;}',
    '[data-theme="dark"] .sk-nav{background:rgba(0,0,0,.78);}',
    '.sk-nav a{text-decoration:none;}',
    '.sk-brand{display:flex;align-items:baseline;gap:10px;color:inherit;min-width:0;}',
    '.sk-brand b{font-size:15.5px;font-weight:700;color:var(--text,#0c0d10);white-space:nowrap;}',
    '.sk-brand span{font-size:12px;color:var(--light,#8a8b90);white-space:nowrap;}',
    '.sk-links{display:flex;align-items:center;gap:2px;overflow-x:auto;scrollbar-width:none;-ms-overflow-style:none;}',
    '.sk-links::-webkit-scrollbar{display:none;}',
    '.sk-links a{padding:8px 12px;border-radius:8px;font-size:14px;color:var(--muted,#5e5f66);white-space:nowrap;}',
    '.sk-links a:hover{color:var(--text,#0c0d10);background:var(--fill,rgba(12,13,16,.04));}',
    '.sk-links a.on{color:var(--text,#0c0d10);font-weight:700;}',
    '.sk-theme{flex:none;width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;margin-left:6px;',
    'border:none;border-radius:50%;background:transparent;color:var(--muted,#5e5f66);cursor:pointer;padding:0;}',
    '.sk-theme svg{width:16px;height:16px;display:block;}',
    '.sk-theme:hover{background:var(--fill,rgba(12,13,16,.04));color:var(--text,#0c0d10);}',
    '.sk-nav--hidden{transform:translateY(-100%);}',
    'body{padding-top:64px !important;}',
    '@media (max-width:640px){.sk-brand span{display:none;}.sk-links a{padding:8px 9px;font-size:13.5px;}.sk-nav{padding:0 14px;}}',
  ].join('');
  var styleEl = document.createElement('style');
  styleEl.textContent = css;
  document.head.appendChild(styleEl);

  /* ---------- DOM ---------- */
  var nav = document.createElement('header');
  nav.className = 'sk-nav';
  var path = location.pathname;
  var linksHtml = LINKS.map(function (l) {
    var on = path.indexOf(l.href) === 0 ? ' class="on"' : '';
    return '<a href="' + l.href + '"' + on + '>' + l.label + '</a>';
  }).join('');
  nav.innerHTML =
    '<a class="sk-brand" href="/"><b>' + SITE_NAME + '</b></a>' +
    '<div class="sk-links">' + linksHtml +
    (themable ? '<button class="sk-theme" type="button" aria-label="切换深色模式">深色</button>' : '') +
    '</div>';
  document.body.prepend(nav);

  /* ---------- 主题（仅 site.css 页面） ---------- */
  if (themable) {
    var root = document.documentElement;
    var btn = nav.querySelector('.sk-theme');
    var saved = localStorage.getItem(THEME_KEY);
    var prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
    var ICON_SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
    var ICON_MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
    function resolve() { return saved || (prefersDark.matches ? 'dark' : 'light'); }
    function apply(t) {
      root.dataset.theme = t;
      btn.innerHTML = t === 'dark' ? ICON_SUN : ICON_MOON; // 深色下显示太阳（点击回浅色），反之月亮
      btn.setAttribute('aria-label', t === 'dark' ? '切换到浅色模式' : '切换到深色模式');
      btn.setAttribute('aria-pressed', String(t === 'dark'));
    }
    apply(resolve());
    btn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      saved = next;
      localStorage.setItem(THEME_KEY, next);
      apply(next);
    });
    prefersDark.addEventListener('change', function () {
      if (!localStorage.getItem(THEME_KEY)) apply(resolve());
    });
  }

  /* ---------- 滚动隐藏/显示（所有尺寸）：下滑隐藏，上滑显示 ---------- */
  var lastY = window.scrollY;
  window.addEventListener('scroll', function () {
    var y = window.scrollY;
    if (y < 16 || y < lastY - 2) nav.classList.remove('sk-nav--hidden');      // 上滑或接近顶部 → 显示
    else if (y > lastY + 4 && y > 56) nav.classList.add('sk-nav--hidden');    // 下滑 → 隐藏
    lastY = y;
  }, { passive: true });
})();
