# 原创合成演示音频

每段10秒，48kHz/16bit/双声道，同相信号。音频由build/audio.py生成，无外部音乐版权素材。不是鸿蒙实机录音或性能测试。

- P01可选播放01_scene_mix.wav，听音乐持续、游戏和提醒加入。
- P04可选对照02_continuous.wav与03_simulated_dropout.wav。后者在3.4秒和6.2秒人为加入90/140毫秒静音，边缘4毫秒渐变；只辅助感知人为欠载，不能证明PA与HPAE差异。
- 01_scene_mix.wav与02_continuous.wav是同一内容的两个兼容别名，SHA256相同，并非两份独立声音或旧新引擎录音。
- 各段全程RMS约-24dBFS，RMS匹配不等于严格感知响度匹配。实际数据见measurements.json。
- 打开交付目录的index.html手动播放，音频未嵌入PPTX。移动时保持资源目录结构。现场请先以低音量试听，工具没有完成扬声器声压和主观听感验收。
- 重新生成时默认保护已存在文件。用python build/audio.py --output 临时输出目录验证复现；确认替换时才使用--overwrite。
