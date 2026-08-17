# 达芬奇脚本 API 连接：Python 3.12 加载 fusionscript.dll 正解（2026-08-17 实测）

## 症状

Python 3.12 下 `import DaVinciResolveScript` 报：

```
File "C:\Users\HMSJ\scripts_dvr\DaVinciResolveScript.py", line 19, in <module>
    import fusionscript as script_module
ModuleNotFoundError: No module named 'fusionscript'
...
File "C:\Users\HMSJ\scripts_dvr\DaVinciResolveScript.py", line 48, in <module>
    script_module = importlib.util.module_from_spec(spec)
AttributeError: 'NoneType' object has no attribute 'loader'
```

## 根因

桥文件 `DaVinciResolveScript.py` 内部回退路径用
`importlib.util.spec_from_file_location("fusionscript", path + "fusionscript" + ext)`，
其中 `ext = ".dll"`（Windows）。**Python 3.12 的 `spec_from_file_location` 不识别 `.dll` 扩展
（只认 `.pyd`），返回 None** → `module_from_spec(None)` 抛 AttributeError。
（Python 3.12 已移除 `imp` 模块，`HAVE_IMP` 分支永远不触发。）

## 正解：显式 ExtensionFileLoader

```python
import sys
sys.path.insert(0, 'C:/Users/HMSJ/scripts_dvr')          # 桥文件目录

import importlib.util, importlib.machinery
dll = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
loader = importlib.machinery.ExtensionFileLoader('fusionscript', dll)
spec = importlib.util.spec_from_loader('fusionscript', loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
sys.modules['fusionscript'] = mod                        # 必须先注册，桥文件顶层 import fusionscript 才找得到

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp('Resolve')
```

- dll 实际位置：`C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll`
  （在 Resolve 根目录，**不在** `Fusion/` 子目录）
- 顺序铁律：`sys.modules['fusionscript'] = mod` 必须在 `import DaVinciResolveScript` **之前**
- 桥文件里还 import 了其它 fusions*.dll（fusionsystem/fusioncontrols 等），ExtensionFileLoader
  加载的 fusionscript 模块会自行带出，实测无需手动加载其余的

## scriptapp 返回 None 的排查（连接失败三层）

1. Resolve 没在运行——先启动 Resolve.exe
2. Preferences → General → External Scripting 未设 *Local*（Preference 里 Save/Load 交互式脚本，
   Local/Remote 网络脚本模式）——免费版无此选项也无脚本 API
3. 桥/dll 路径错

## 验证技巧

- `resolve = dvr.scriptapp('Resolve')` 成功返回对象即链路通；`pm.GetProjectManager()` 再
  `pm.GetCurrentProject().GetName()` 确认当前项目
- `pm.GetProjectList()` 在无项目时返回 None 是**正常**现象，不要当失败
- 用 `.GetName()` 判连接成功，别用 `GetProjectList()`（空库时 None）

## 与 SKILL.md 的关系

SKILL.md「验证方式」节的达芬奇自动化条目原写法「importlib 替代已废弃的 imp」不准确——
本机 Python 3.12 实测默认桥文件加载路径必失败，按本文配方显式加载才通。