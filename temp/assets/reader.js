/* ============================================================
   樂齡英文精讀館 — Shared Interactive Reader Script
   ============================================================ */

(function () {
  "use strict";

  const FONT_SIZES = ["sm", "md", "lg", "xl"];
  const FONT_LABELS = {
    sm: "標準",
    md: "大字",
    lg: "特大",
    xl: "超大",
  };

  const THEMES = ["warm", "dark", "contrast"];
  const THEME_LABELS = {
    warm: "護眼",
    dark: "夜間",
    contrast: "白底",
  };

  const STORAGE_FONT_KEY = "senior_reader_font_size";
  const STORAGE_THEME_KEY = "senior_reader_theme";

  function safeGetStorage(key, fallback) {
    try {
      return window.localStorage.getItem(key) || fallback;
    } catch (_) {
      return fallback;
    }
  }

  function safeSetStorage(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_) {
      // Ignore storage errors in private mode / restricted file:// contexts
    }
  }

  /* ----------------------------------------------------------
     1. Font Size Controls
     ---------------------------------------------------------- */
  function applyFontSize(size) {
    const validSize = FONT_SIZES.includes(size) ? size : "md";
    document.documentElement.setAttribute("data-font-size", validSize);
    safeSetStorage(STORAGE_FONT_KEY, validSize);

    const badge = document.getElementById("font-size-badge");
    if (badge) {
      badge.textContent = FONT_LABELS[validSize];
    }

    const decBtn = document.getElementById("btn-font-dec");
    const incBtn = document.getElementById("btn-font-inc");
    if (decBtn) decBtn.disabled = validSize === FONT_SIZES[0];
    if (incBtn) incBtn.disabled = validSize === FONT_SIZES[FONT_SIZES.length - 1];
  }

  function initFontControls() {
    const saved = safeGetStorage(STORAGE_FONT_KEY, "md");
    applyFontSize(saved);

    const decBtn = document.getElementById("btn-font-dec");
    const incBtn = document.getElementById("btn-font-inc");

    if (decBtn) {
      decBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-font-size") || "md";
        const idx = FONT_SIZES.indexOf(current);
        if (idx > 0) applyFontSize(FONT_SIZES[idx - 1]);
      });
    }

    if (incBtn) {
      incBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-font-size") || "md";
        const idx = FONT_SIZES.indexOf(current);
        if (idx < FONT_SIZES.length - 1) applyFontSize(FONT_SIZES[idx + 1]);
      });
    }
  }

  /* ----------------------------------------------------------
     2. Theme Controls (Warm Paper -> Dark -> High Contrast)
     ---------------------------------------------------------- */
  function applyTheme(theme) {
    const validTheme = THEMES.includes(theme) ? theme : "warm";
    document.documentElement.setAttribute("data-theme", validTheme);
    safeSetStorage(STORAGE_THEME_KEY, validTheme);

    const themeBtn = document.getElementById("btn-theme");
    if (themeBtn) {
      const icon = validTheme === "dark" ? "🌙" : validTheme === "contrast" ? "☀️" : "📖";
      themeBtn.textContent = `${icon} ${THEME_LABELS[validTheme]}`;
      themeBtn.setAttribute("aria-label", `切換閱讀配色，目前為${THEME_LABELS[validTheme]}模式`);
    }
  }

  function initThemeControls() {
    const saved = safeGetStorage(STORAGE_THEME_KEY, "warm");
    applyTheme(saved);

    const themeBtn = document.getElementById("btn-theme");
    if (themeBtn) {
      themeBtn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "warm";
        const next = THEMES[(THEMES.indexOf(current) + 1) % THEMES.length];
        applyTheme(next);
      });
    }
  }

  /* ----------------------------------------------------------
     3. Speech Pronunciation (Web Speech API)
     ---------------------------------------------------------- */
  function speakWord(text, buttonEl) {
    if (!("speechSynthesis" in window)) return;

    window.speechSynthesis.cancel();

    document.querySelectorAll(".speak-btn.is-speaking").forEach((btn) => {
      btn.classList.remove("is-speaking");
      btn.textContent = "🔊 發音";
    });

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 0.85; // Slightly slower & clearer for senior learners

    // Prefer an American English voice if available
    const voices = window.speechSynthesis.getVoices();
    const enUS =
      voices.find((v) => v.lang === "en-US" && /Samantha|Alex|Google US English|Natural/i.test(v.name)) ||
      voices.find((v) => v.lang === "en-US") ||
      voices.find((v) => v.lang && v.lang.startsWith("en"));
    if (enUS) utterance.voice = enUS;

    if (buttonEl) {
      buttonEl.classList.add("is-speaking");
      buttonEl.textContent = "🔊 唸讀中";
    }

    const resetBtn = () => {
      if (buttonEl) {
        buttonEl.classList.remove("is-speaking");
        buttonEl.textContent = "🔊 發音";
      }
    };

    utterance.onend = resetBtn;
    utterance.onerror = resetBtn;
    window.speechSynthesis.speak(utterance);
  }

  function initSpeechButtons(root) {
    const scope = root || document;
    const supported = "speechSynthesis" in window;
    scope.querySelectorAll(".speak-btn").forEach((btn) => {
      if (!supported) {
        btn.style.display = "none";
        return;
      }
      if (btn.dataset.bound === "true") return;
      btn.dataset.bound = "true";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const word = btn.getAttribute("data-speak");
        if (word) speakWord(word, btn);
      });
    });
  }

  /* ----------------------------------------------------------
     4. Vocabulary Highlight Click -> Open Drawer & Focus Card
     ---------------------------------------------------------- */
  function initInlineVocabLinks() {
    document.querySelectorAll(".vocab-inline[data-vocab-id]").forEach((mark) => {
      mark.addEventListener("click", () => {
        const targetId = mark.getAttribute("data-vocab-id");
        const vocabCard = document.getElementById(targetId);
        if (!vocabCard) return;

        const drawer = vocabCard.closest("details.vocab-drawer");
        if (drawer && !drawer.open) {
          drawer.open = true;
        }

        // Remove previous highlights
        document.querySelectorAll(".vocab-item.is-highlighted").forEach((el) => {
          el.classList.remove("is-highlighted");
        });

        vocabCard.classList.add("is-highlighted");
        vocabCard.scrollIntoView({ behavior: "smooth", block: "center" });

        window.setTimeout(() => {
          vocabCard.classList.remove("is-highlighted");
        }, 2600);
      });
    });
  }

  /* ----------------------------------------------------------
     5. Expand / Collapse All Vocabulary Drawers
     ---------------------------------------------------------- */
  function initToggleAllVocab() {
    const toggleBtn = document.getElementById("btn-toggle-vocab");
    if (!toggleBtn) return;

    const drawers = Array.from(document.querySelectorAll("details.vocab-drawer"));
    if (drawers.length === 0) {
      toggleBtn.style.display = "none";
      return;
    }

    function syncLabel() {
      const allOpen = drawers.every((d) => d.open);
      toggleBtn.textContent = allOpen ? "收合註解" : "展開註解";
      toggleBtn.classList.toggle("is-active", allOpen);
    }

    toggleBtn.addEventListener("click", () => {
      const allOpen = drawers.every((d) => d.open);
      drawers.forEach((d) => {
        d.open = !allOpen;
      });
      syncLabel();
    });

    drawers.forEach((d) => {
      d.addEventListener("toggle", syncLabel);
    });

    syncLabel();
  }

  /* ----------------------------------------------------------
     6. Auto-Generate Full Article Vocabulary Review
     ---------------------------------------------------------- */
  function initFullGlossary() {
    const container = document.getElementById("glossary-list");
    const countEl = document.getElementById("glossary-count");
    if (!container) return;

    const items = document.querySelectorAll(".vocab-drawer .vocab-item");
    if (countEl) {
      countEl.textContent = String(items.length);
    }

    items.forEach((item) => {
      const clone = item.cloneNode(true);
      clone.removeAttribute("id");
      clone.classList.remove("is-highlighted");
      // Reset bound attribute so speech buttons inside glossary bind cleanly
      clone.querySelectorAll(".speak-btn").forEach((btn) => {
        delete btn.dataset.bound;
      });
      container.appendChild(clone);
    });

    initSpeechButtons(container);
  }

  /* ----------------------------------------------------------
     7. Reading Progress Bar & Back-to-Top Button
     ---------------------------------------------------------- */
  function initScrollHelpers() {
    const progressFill = document.getElementById("progress-fill");
    const backToTop = document.getElementById("back-to-top");

    function onScroll() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight =
        document.documentElement.scrollHeight - document.documentElement.clientHeight;

      if (progressFill && docHeight > 0) {
        const pct = Math.min(100, Math.max(0, (scrollTop / docHeight) * 100));
        progressFill.style.width = `${pct}%`;
      }

      if (backToTop) {
        backToTop.classList.toggle("is-visible", scrollTop > 380);
      }
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (backToTop) {
      backToTop.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  }

  /* ----------------------------------------------------------
     8. Index Page Search & Category Filter
     ---------------------------------------------------------- */
  function initIndexFilters() {
    const searchInput = document.getElementById("article-search");
    const pillBtns = Array.from(document.querySelectorAll(".pill-btn[data-category]"));
    const cards = Array.from(document.querySelectorAll(".article-card[data-category]"));
    const countEl = document.getElementById("article-count");
    const emptyState = document.getElementById("empty-state");

    if (cards.length === 0) return;

    let activeCategory = "all";

    function filterCards() {
      const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
      let visibleCount = 0;

      cards.forEach((card) => {
        const cat = card.getAttribute("data-category") || "";
        const text = card.textContent.toLowerCase();
        const matchCat = activeCategory === "all" || cat.split(",").includes(activeCategory);
        const matchQuery = !query || text.includes(query);

        const show = matchCat && matchQuery;
        card.style.display = show ? "" : "none";
        if (show) visibleCount += 1;
      });

      if (countEl) {
        countEl.textContent = `共 ${visibleCount} 篇文章`;
      }
      if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? "block" : "none";
      }
    }

    if (searchInput) {
      searchInput.addEventListener("input", filterCards);
    }

    pillBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        activeCategory = btn.getAttribute("data-category") || "all";
        pillBtns.forEach((b) => b.classList.toggle("is-active", b === btn));
        filterCards();
      });
    });

    filterCards();
  }

  /* ----------------------------------------------------------
     Init Everything on DOM Ready
     ---------------------------------------------------------- */
  document.addEventListener("DOMContentLoaded", () => {
    initFontControls();
    initThemeControls();
    initSpeechButtons(document);
    initInlineVocabLinks();
    initToggleAllVocab();
    initFullGlossary();
    initScrollHelpers();
    initIndexFilters();
  });
})();
