# CFG=1 + 空 prompt 的图像修复机制

## 核心原理

**CFG（Classifier-Free Guidance）= 1 + 空 prompt + low denoise** 是一种"无引导扩散投影"修复策略。

```
不是"根据 prompt 生成细节"
而是"把偏离自然图像分布的像素拉回来"
```

## 机制

### 标准 CFG 模式

扩散模型训练时同时学习条件和无条件分布。推理时通过 CFG 在两者间插值：

```
output = unconditional + CFG × (conditional - unconditional)
```

CFG=7：大幅偏离无条件，严格跟随 prompt
CFG=1：完全不偏离无条件——等价于只走无条件分支

### CFG=1 对修复的意义

多轮编辑后的图像损伤（压缩噪声、VAE 模糊、纹理蜡化）的共同特征：**偏离模型的自然图像训练分布**。

CFG=1 时模型只判断："这个像素是否像训练集中见过的自然图像？不像的地方就修正。"

不引入 prompt 的语义偏差（"它应该是一只猫"），不主动创造新内容。

## 关键参数配合

| 参数 | 值 | 作用 |
|------|-----|------|
| CFG | 1 | 关闭文本引导 |
| prompt | 空 | 不提供语义方向 |
| denoise | 0.25 | 保留 75% 原图，只修正 25% |
| steps | 3 | Turbo 模型足够 |
| checkpoint | z-image-turbo-bf16-aio | 蒸馏加速模型 |

denoise 和 CFG 相互制约：CFG=1 时提高 denoise 不会"修复更多"——只会让模型随机填充，因为没有 prompt 告诉它往哪个方向填。0.25 恰好抹平偏离分布的伪影而不越界。

## 两阶段互补

```
阶段一：RealESRGAN_x4plus (GAN)
  → 4× 放大，注入高频（可能有假纹理、过度锐化）

阶段二：SD Turbo 扩散 (denoise 0.25, CFG 1)
  → 投影回自然流形，抹平 GAN 伪影
```

GAN 提供高频起点，扩散修正分布偏差。单独任一个都不如两者配合。
