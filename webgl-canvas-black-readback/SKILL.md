---
name: webgl-canvas-black-readback
description: Use when a Three.js / WebGL canvas reads back all-black pixels (0,0,0) via drawImage / getImageData / toDataURL / readPixels even though the scene renders correctly (DevTools compositor screenshot shows the frame). drawing buffer cleared after composite; not a render failure.
metadata:
  author: wuji00
---

# WebGL Canvas 回读全黑（伪渲染失败）

## 何时用

Three.js / WebGL 场景渲染正常——DevTools 合成层截图能看到画面，但用下面任一方式回读 canvas 像素得**全黑 (0,0,0,255)**，误判"场景没渲染"：

```js
ctx.drawImage(glCanvas, 0, 0);
ctx.getImageData(w/2, h/2, 1, 1).data;   // → [0,0,0,255]
glCanvas.toDataURL();                      // 偶发空
gl.readPixels(...);                        // 偶发空
```

## 根因

WebGL 默认**性能模式**：每帧合成上屏后 drawing buffer 被**丢弃（clear）**，除非显式保留。规范规定 buffer 内容在合成后仍可读，仅当：

1. 建 context 时传 `preserveDrawingBuffer: true`；**或**
2. 在**同一合成帧内**、浏览器实际合成上屏**之前**回读。

`drawImage(glCanvas)` 走 2D 读取路径，发生在合成**之后** → 读到已清空的 buffer → 全黑。**这是正确浏览器行为，不是 bug，也不是渲染失败。**

## 解决

### 首选：别回读，用合成层截图

调试/验证渲染时，让 DevTools MCP / Playwright / 系统截图抓合成后的页面（走合成器，不经 drawing buffer）：

```
mcp__chrome-devtools__take_screenshot  →  filePath: .../shot.png
```

存盘后用视觉工具分析该 PNG。这才是渲染真实结果。

### 需要程序内读像素时（截图不可用 / 逐像素断言），二选一

```js
// A：建 context 时保留 buffer（有性能/隐私代价，仅调试用）
const renderer = new THREE.WebGLRenderer({ preserveDrawingBuffer: true });
// 之后 toBlob / drawImage / readPixels 都能读

// B：渲染同一帧内立即读（requestAnimationFrame 回调里 render 之后马上读）
renderer.render(scene, camera);
renderer.readRenderTargetPixels(...);   // 或 gl.readPixels
```

生产环境**别开** `preserveDrawingBuffer: true`（拖性能、某些场景有合成瑕疵），只本地调试临时开。

## 预防 / 排查顺序

排查"黑屏"按序确认：① canvas 尺寸/CSS 非零 ② `canvas.getContext('webgl2')` 存在 ③ three 模块加载 ④ **合成层截图有内容**。前三条过了 + 截图有内容 = 渲染正常，回读黑只是 buffer 丢弃。

- **验证渲染是否成功**：永远信合成层截图，别信 `drawImage` 回读。先截图再下结论。
- 写断言像素的测试，用方案 B（同帧 readPixels），别用 2D `drawImage` 桥接。
- Three.js `WebGLRenderer` 默认 `preserveDrawingBuffer:false`；导出图片功能再按需开。

## 触发场景

- Chrome DevTools MCP / Playwright 自动验证 Three.js 渲染产物
- 单测里断言 canvas 中心像素颜色
- 自制"canvas 转 PNG 导出"按钮

关键词：WebGL black, drawImage black, getImageData zeros, readPixels empty, preserveDrawingBuffer, drawing buffer cleared, Three.js 黑屏, canvas 回读全黑。

## 参考

- WebGL spec § Drawing Buffer Lifetime
- Three.js docs：`WebGLRenderer` 构造参数 `preserveDrawingBuffer`
