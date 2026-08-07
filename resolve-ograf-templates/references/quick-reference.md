# OGraf 速查卡

## 最少可工作的 manifest

```json
{
  "$schema": "https://ograf.ebu.io/v1/specification/json-schemas/graphics/schema.json",
  "id": "com.example.foo", "version": "1.0.0", "name": "Foo",
  "main": "foo.js",
  "supportsRealTime": false, "supportsNonRealTime": true,
  "stepCount": 1,
  "schema": {
    "type": "object", "additionalProperties": false,
    "properties": {
      "headline": {"type":"string","title":"标题","default":"Hello"}
    },
    "required": ["headline"]
  },
  "v_bmd": {"duration": 5}
}
```

## 参数类型→Fusion 控件

| 类型 | JSON Schema | 附加字段 | Fusion 控件 |
|------|------------|---------|------------|
| 文本 | `"type":"string"` | — | 文本输入框 |
| 颜色 | `"type":"string"` | `"gddType":"color-rrggbb"`, `"pattern":"^#[0-9a-f]{6}$"` | **原生拾色器** |
| 颜色+透明 | `"type":"string"` | `"gddType":"color-rrggbbaa"`, `"pattern":"^#[0-9a-f]{8}$"` | 拾色器+Alpha |
| 整数 | `"type":"integer"` | `"minimum":0, "maximum":100` | 整数滑块 |
| 浮点 | `"type":"number"` | `"minimum":0, "maximum":1` | 浮点滑块 |
| 布尔 | `"type":"boolean"` | — | 复选框 |
| 下拉选择 | `"type":"string"` | `"t":"select"` + `"opts":{"val1":"标签1",...}` | 下拉框（需特殊渲染） |

**`select` 类型在 studio 中的渲染**：`rProps()` 中 `v.t==='font'||v.t==='select'` 分支，font 用 FONTS 数组，select 用 `Object.entries(v.opts)` 生成 option。漏掉这个分支时下拉会渲染为普通文本框。

**上限 20 个参数**（每个颜色算 1 个）。颜色在 JS 中用 CSS 自定义属性接收：
```javascript
this.style.setProperty("--c1", this._state.primaryColor);
```

## 确定性渲染 `_setFrame` 样板

```javascript
function C(v,l,h){return Math.max(l,Math.min(v,h))}  // clamp
function E(t){return 1-Math.pow(1-t,3)}               // easeOutCubic

_setFrame(sec){
  if(this._step===0||sec<0||sec>5){scene.style.opacity="0";return}
  scene.style.opacity="1";
  // 阶段1：装饰元素动画 (0 - 0.7s)
  const t1=E(C(sec/0.7,0,1));
  line.style.transform=`scaleY(${t1.toFixed(3)})`;
  // 阶段2：文字延迟淡入 (0.3 - 0.8s)  
  name.style.opacity=C((sec-0.3)/0.5,0,1).toFixed(2);
  sub.style.opacity=C((sec-0.5)/0.5,0,1).toFixed(2);
}
```

**禁止项**：`Math.random()`、`setTimeout`/`setInterval`、CSS `animation`/`transition`、任何异步操作。

**动画参数在设计阶段应可调**：总时长、各阶段延迟和持续时间作为 template props 暴露——studio.html 的「动画」分组即为这个目的。

## 确定性粒子引擎

粒子必须从设计元素锚点发出，有明确源头——不是满屏随机装饰，要"有迹可循，为画面服务"。

```javascript
function seedRand(s){let h=0;for(let i=0;i<s.length;i++){h=((h<<5)-h)+s.charCodeAt(i);h|=0}return function(){h=(h*1103515245+12345)&0x7fffffff;return h/0x7fffffff}}

// 锚点式粒子预设
const PRESETS={
  brushDrip:{  // 墨滴——从墨线位置渗出
    anchor:[8,60],spread:[4,8],count:8,
    size:[2,5],life:[1.5,3],fall:[3,8],drift:[-2,2],
    color:'rgba(205,184,150,0.25)'
  },
  silkDust:{   // 纸尘——从横批扬起
    anchor:[50,72],spread:[35,6],count:20,
    size:[0.5,2],life:[3,6],fall:[-1,2],drift:[-6,6],
    color:'rgba(196,168,124,0.2)'
  },
};

function renderParticles(canvas,preset,timestamp,w,h){
  const ctx=canvas.getContext('2d');ctx.clearRect(0,0,w,h);
  const c=PRESETS[preset];if(!c)return;
  const rng=seedRand(preset+'|'+Math.floor(timestamp*12));
  const ox=w*c.anchor[0]/100, oy=h*c.anchor[1]/100;  // 锚点
  for(let i=0;i<c.count;i++){
    const seed=rng();
    const life=c.life[0]+(c.life[1]-c.life[0])*seed;
    const age=((timestamp*1000)%(life*1000))/1000/life;
    const x=ox+(rng()-0.5)*c.spread[0]*w/100+age*c.drift[1]*rng();
    const y=oy+(rng()-0.5)*c.spread[1]*h/100+age*60*c.fall[1]*(1-age*0.7);
    const s=c.size[0]+(c.size[1]-c.size[0])*rng();
    const alpha=(1-age)*(1-age);
    ctx.fillStyle=c.color.replace(/[\d.]+\)$/,m=>parseFloat(m)*alpha+')');
    ctx.beginPath();ctx.arc(x,y,s,0,Math.PI*2);ctx.fill();
  }
}
```

**Canvas 必须在 `innerHTML` 之后创建**，否则被清空：
```javascript
el.innerHTML = h;         // 先设 HTML
el.appendChild(canvas);   // 后加 Canvas
```

## 安装路径

```
# 用户级（开发推荐）
%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Templates\Edit\Titles\OGraf\

# .drfx 打包（分发）
zip 内结构: Edit/Titles/OGraf/foo.ograf.json + foo.js
```

## 官方文档位置

```
C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\OGraf HTML Templates\Documentation\
```

**重点文件**：`02-Resolve-Integration.md`（确定性渲染）、`05-Properties-and-Controls.md`（参数映射）、`03-Web-Component-API.md`（8 个方法签名）。
