(() => {
  const sizes = [22, 26, 30];
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch {} };
  let size = Number(read('reading-font-size'));
  if (!sizes.includes(size)) size = 26;
  const button = document.querySelector('[data-font]');
  const status = document.createElement('span');
  status.className = 'font-status'; status.setAttribute('aria-live', 'polite');
  document.body.append(status);
  function apply(announce = false) {
    document.documentElement.style.setProperty('--reading-size', `${size}px`);
    if (button) {
      button.textContent = ['A', 'A+', 'A++'][sizes.indexOf(size)];
      button.title = `字體大小 ${size}px`;
      button.setAttribute('aria-label', `目前字體 ${size}px，點擊切換為 ${sizes[(sizes.indexOf(size) + 1) % sizes.length]}px`);
    }
    if (announce) status.textContent = `字體已調整為 ${size}px`;
  }
  apply();
  button?.addEventListener('click', () => { size = sizes[(sizes.indexOf(size) + 1) % sizes.length]; save('reading-font-size', String(size)); apply(true); });
  const chapter = document.body.dataset.chapter;
  if (chapter) save('last-chapter', chapter);
  const last = read('last-chapter');
  const resume = document.querySelector('#continue');
  const chapterNames = { '1': '一', '2': '二', '3': '三' };
  if (resume && Object.hasOwn(chapterNames, last)) {
    resume.href = `chapter-${last}.html`;
    resume.textContent = `繼續上次篇章：第${chapterNames[last]}篇 →`;
    resume.hidden = false;
  }
  const chapterMenu = document.querySelector('.chapter-menu');
  document.addEventListener('click', event => {
    if (chapterMenu?.open && !chapterMenu.contains(event.target)) chapterMenu.open = false;
  });
  chapterMenu?.addEventListener('click', event => {
    const link = event.target.closest('.section-links a');
    if (!link) return;
    chapterMenu.open = false;
    const heading = document.getElementById(link.hash.slice(1));
    heading?.setAttribute('tabindex', '-1');
    heading?.focus({ preventScroll: true });
  });
  chapterMenu?.addEventListener('keydown', event => {
    if (event.key === 'Escape' && chapterMenu.open) {
      chapterMenu.open = false;
      chapterMenu.querySelector('summary').focus();
    }
  });
})();
