要使用 Vite 安裝 Vue 2 的開發環境，你可以按照以下步驟進行操作：

### 1. 創建一個新的 Vite 項目
首先，使用 Vite 創建一個新的項目。你可以使用以下命令：

```bash
npm create vite@latest my-vue2-app
```

這將提示你選擇一個框架。由於 Vite 默認支持 Vue 3，你需要選擇 `vanilla`（純 JavaScript）模板，然後手動配置 Vue 2。

### 2. 進入項目目錄
創建項目後，進入項目目錄：

```bash
cd my-vue2-app
```

### 3. 安裝 Vue 2 和相關依賴
接下來，安裝 Vue 2 和 Vite 的 Vue 2 插件：

```bash
npm install vue@2
npm install vite-plugin-vue2 --save-dev
```

### 4. 配置 `vite.config.js`
在項目根目錄下創建或修改 `vite.config.js` 文件，配置 Vite 以支持 Vue 2：

```javascript
import { defineConfig } from 'vite';
import { createVuePlugin } from 'vite-plugin-vue2';

export default defineConfig({
  plugins: [createVuePlugin()],
});
```

### 5. 修改 `main.js`
在 `src` 目錄下創建或修改 `main.js` 文件，初始化 Vue 2 應用：

```javascript
import Vue from 'vue';
import App from './App.vue';

new Vue({
  render: h => h(App),
}).$mount('#app');
```

### 6. 創建 `App.vue`
在 `src` 目錄下創建 `App.vue` 文件，這是你的根組件：

```vue
<template>
  <div id="app">
    <h1>Hello Vue 2 with Vite!</h1>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
```

### 7. 修改 `index.html`
確保 `index.html` 文件中有一個 `div` 元素，用於掛載 Vue 應用：

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vue 2 with Vite</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

### 8. 運行開發服務器
最後，運行開發服務器：

```bash
npm run dev
```

現在，你應該可以在瀏覽器中看到一個簡單的 Vue 2 應用運行在 Vite 開發環境中。

### 9. 構建生產版本
當你準備好構建生產版本時，可以運行：

```bash
npm run build
```

這將生成一個優化的生產版本，存放在 `dist` 目錄中。

### 總結
通過以上步驟，你已經成功使用 Vite 配置了一個 Vue 2 的開發環境。Vite 提供了快速的開發體驗，並且通過 `vite-plugin-vue2` 插件，你可以繼續使用 Vue 2 進行開發。