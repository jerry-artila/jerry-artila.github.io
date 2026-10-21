// PSRP 字體切換與個別項目引經展開/收合控制
(function() {
  const FONT_LEVELS = ['md', 'lg', 'xl']; // 中、大、特大
  const FONT_LABELS = {
    'md': '字體: 中',
    'lg': '字體: 大',
    'xl': '字體: 特'
  };

  function init() {
    // 1. 初始化字體大小
    const savedFont = localStorage.getItem('psrp_font_size') || 'md';
    applyFont(savedFont);

    // 2. 頂部字體切換按鈕事件
    const fontBtn = document.getElementById('btn-font-toggle');
    if (fontBtn) {
      fontBtn.addEventListener('click', toggleFontSize);
    }

    // 3. 綱目項目後方的個別引經按鈕事件
    document.querySelectorAll('.scripture-toggle-btn').forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.stopPropagation();
        const contentBox = this.closest('.item-content');
        if (!contentBox) return;
        const scripturesList = contentBox.querySelector('.scriptures');
        if (!scripturesList) return;

        const isCurrentlyExpanded = scripturesList.classList.contains('expanded');
        if (isCurrentlyExpanded) {
          scripturesList.classList.remove('expanded');
          this.classList.remove('expanded');
          this.setAttribute('aria-expanded', 'false');
          this.innerHTML = '經文 ▾';
        } else {
          scripturesList.classList.add('expanded');
          this.classList.add('expanded');
          this.setAttribute('aria-expanded', 'true');
          this.innerHTML = '經文 ▴';
        }
      });
    });
  }

  function applyFont(level) {
    const body = document.body;
    body.classList.remove('font-lg', 'font-xl');
    if (level === 'lg') {
      body.classList.add('font-lg');
    } else if (level === 'xl') {
      body.classList.add('font-xl');
    }
    localStorage.setItem('psrp_font_size', level);

    const fontBtn = document.getElementById('btn-font-toggle');
    if (fontBtn) {
      fontBtn.textContent = FONT_LABELS[level] || '字體: 中';
    }
  }

  function toggleFontSize() {
    const current = localStorage.getItem('psrp_font_size') || 'md';
    const nextIdx = (FONT_LEVELS.indexOf(current) + 1) % FONT_LEVELS.length;
    const nextLevel = FONT_LEVELS[nextIdx];
    applyFont(nextLevel);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();