"""生成扒谱工具分级测试音频（合成 ground truth）。

用法: python make_test_audio.py [输出目录]
默认输出目录: C:/Users/<user>/AppData/Local/Temp/paipu_test

三级难度:
- scale_pure.wav     纯正弦 C 大调音阶 C4..C5（理想场景，测音高识别上限）
- scale_harmonic.wav 带 2/3 次泛音的同音阶（模拟真实乐器，测去谐波能力）
- chords.wav         三和弦进行 C-G-Am-F（多声部，测复调识别）

验证方法: 工具识别结果 → MIDI note → 音名 names[midi%12]+(midi//12-1)，与真实值对比。
真实音阶: C4(60) D4(62) E4(64) F4(65) G4(67) A4(69) B4(71) C5(72)
真实和弦: C=(60,64,67) G=(55,59,62) Am=(57,60,64) F=(53,57,60)

注: Windows 原生 Python 不认 MSYS /tmp 路径，输出目录用 Windows 盘符路径（C:/...）。
"""
import wave, struct, math, os, sys

sr = 44100
OUT = r'C:/Users/HMSJ/AppData/Local/Temp/paipu_test'
if len(sys.argv) > 1:
    OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def note(freq, dur, amp=0.5, harmonics=1):
    n = int(sr * dur)
    out = []
    for i in range(n):
        t = i / sr
        v = 0.0
        for h in range(1, harmonics + 1):
            v += math.sin(2 * math.pi * freq * h * t) * (amp / h)
        out.append(v)
    return out


def write_wav(path, samples):
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b''.join(
            struct.pack('<h', max(-32767, min(32767, int(s * 32767))))
            for s in samples))


C4, D4, E4, F4, G4, A4, B4, C5 = 261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25
G3, A3, B3, F3 = 196.00, 220.00, 246.94, 174.61

# 测试1：纯正弦 C 大调音阶
s1 = []
for f in [C4, D4, E4, F4, G4, A4, B4, C5]:
    s1 += note(f, 0.5)
write_wav(OUT + '/scale_pure.wav', s1)

# 测试2：带泛音音阶（模拟真实乐器）
s2 = []
for f in [C4, D4, E4, F4, G4, A4, B4, C5]:
    s2 += note(f, 0.5, harmonics=3)
write_wav(OUT + '/scale_harmonic.wav', s2)

# 测试3：三和弦进行 C-G-Am-F（多声部）
s3 = []
chords = [(C4, E4, G4), (G3, B3, D4), (A3, C4, E4), (F3, A3, C4)]
for ch in chords:
    for f in ch:
        for i, v in enumerate(note(f, 1.2, amp=0.3)):
            if i < len(s3):
                s3[i] += v
            else:
                s3.append(v)
write_wav(OUT + '/chords.wav', s3)

for fn in sorted(os.listdir(OUT)):
    print(fn, os.path.getsize(OUT + '/' + fn))
print('DONE:', OUT)
