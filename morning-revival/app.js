document.addEventListener('DOMContentLoaded', () => {
  // ==========================================================================
  // 1. Font Size Cycling (12pt -> 14pt -> 16pt -> 12pt)
  // ==========================================================================
  const fontSizes = ['12pt', '14pt', '16pt'];
  const fontSizeBtn = document.getElementById('font-size-btn');
  const fontSizeLabel = document.getElementById('font-size-label');

  // Load initial font size from localStorage or default to 14pt
  let currentFontSize = localStorage.getItem('outline_font_size') || '14pt';
  if (!fontSizes.includes(currentFontSize)) {
    currentFontSize = '14pt';
  }

  function applyFontSize(size) {
    fontSizes.forEach(s => document.body.classList.remove(`font-${s}`));
    document.body.classList.add(`font-${size}`);
    if (fontSizeLabel) {
      fontSizeLabel.textContent = size;
    }
    localStorage.setItem('outline_font_size', size);
  }

  // Apply initial font size
  applyFontSize(currentFontSize);

  // Toggle font size on click
  if (fontSizeBtn) {
    fontSizeBtn.addEventListener('click', () => {
      const currentIndex = fontSizes.indexOf(currentFontSize);
      const nextIndex = (currentIndex + 1) % fontSizes.length;
      currentFontSize = fontSizes[nextIndex];
      applyFontSize(currentFontSize);
    });
  }

  // ==========================================================================
  // 2. Theme Toggle (Light / Dark)
  // ==========================================================================
  const themeBtn = document.getElementById('theme-btn');
  const sunIcon = document.getElementById('sun-icon');
  const moonIcon = document.getElementById('moon-icon');

  let currentTheme = localStorage.getItem('outline_theme') || 'light';

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.body.classList.remove('theme-light');
      document.body.classList.add('theme-dark');
      if (sunIcon) sunIcon.classList.add('hidden');
      if (moonIcon) moonIcon.classList.remove('hidden');
    } else {
      document.body.classList.remove('theme-dark');
      document.body.classList.add('theme-light');
      if (sunIcon) sunIcon.classList.remove('hidden');
      if (moonIcon) moonIcon.classList.add('hidden');
    }
    localStorage.setItem('outline_theme', theme);
  }

  // Apply initial theme
  applyTheme(currentTheme);

  // Toggle theme on click
  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      currentTheme = currentTheme === 'light' ? 'dark' : 'light';
      applyTheme(currentTheme);
    });
  }

  // ==========================================================================
  // 3. Mobile TOC Drawer Toggle
  // ==========================================================================
  const mobileTocToggle = document.getElementById('mobile-toc-toggle');
  const tocSidebar = document.getElementById('toc-sidebar');
  const tocOverlay = document.getElementById('toc-overlay');
  const tocCloseBtn = document.getElementById('toc-close-btn');

  function openToc() {
    if (tocSidebar) tocSidebar.classList.add('open');
    if (tocOverlay) tocOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeToc() {
    if (tocSidebar) tocSidebar.classList.remove('open');
    if (tocOverlay) tocOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (mobileTocToggle) mobileTocToggle.addEventListener('click', openToc);
  if (tocCloseBtn) tocCloseBtn.addEventListener('click', closeToc);
  if (tocOverlay) tocOverlay.addEventListener('click', closeToc);

  // Close TOC when clicking a TOC link on mobile
  const tocLinks = document.querySelectorAll('.toc-link');
  tocLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 992) {
        closeToc();
      }
    });
  });

  // ==========================================================================
  // 4. ScrollSpy - Active TOC Link Highlighting
  // ==========================================================================
  const sections = document.querySelectorAll('section[id], div[id^="sec-"]');

  const observerOptions = {
    root: null,
    rootMargin: '-80px 0px -60% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        tocLinks.forEach(link => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach(section => observer.observe(section));
});
