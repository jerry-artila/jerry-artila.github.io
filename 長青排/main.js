// Tailwind CSS 字體大小類別陣列（從小到大）
const fontSizeClasses = [
  'text-xs',      // 12px
  'text-sm',      // 14px
  'text-base',    // 16px
  'text-lg',      // 18px
  'text-xl',      // 20px
  'text-2xl',     // 24px
  'text-3xl',     // 30px
  'text-4xl',     // 36px (預設)
  'text-5xl',     // 48px
  'text-6xl',     // 60px
  'text-7xl',     // 72px
  'text-8xl',     // 96px
  'text-9xl'      // 128px
];

// 當前字體大小索引（預設為 text-4xl，索引為 7）
let currentFontSizeIndex = 7;

// 獲取主要內容元素
const mainElement = document.getElementById('main');

// 獲取按鈕元素
const increaseButton = document.querySelector('button:first-of-type');
const decreaseButton = document.querySelector('button:last-of-type');

// 更新字體大小的函數
function updateFontSize() {
  // 移除所有字體大小類別
  fontSizeClasses.forEach(className => {
    mainElement.classList.remove(className);
  });
  
  // 添加當前選中的字體大小類別
  mainElement.classList.add(fontSizeClasses[currentFontSizeIndex]);
}

// 增加字體大小
increaseButton.addEventListener('click', () => {
  if (currentFontSizeIndex < fontSizeClasses.length - 1) {
    currentFontSizeIndex++;
    updateFontSize();
  }
});

// 減少字體大小
decreaseButton.addEventListener('click', () => {
  if (currentFontSizeIndex > 0) {
    currentFontSizeIndex--;
    updateFontSize();
  }
});
