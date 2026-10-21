from pathlib import Path
import numpy as np
import wave,json,hashlib,argparse
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Generate original synthetic teaching WAVs; not device recordings.')
parser.add_argument('--output',type=Path,default=R/'assets/audio')
parser.add_argument('--overwrite',action='store_true')
args=parser.parse_args();O=args.output.resolve();O.mkdir(parents=True,exist_ok=True)
if not args.overwrite and any((O/n).exists() for n in ['01_scene_mix.wav','02_continuous.wav','03_simulated_dropout.wav','measurements.json','README.md']):
 raise SystemExit('Existing demo assets preserved. Use --output NEW_DIRECTORY to verify reproducibility or --overwrite to replace.')
SR=48000;t=np.arange(SR*10)/SR
def fade(x):
 x=x.copy();n=960;x[:n]*=np.linspace(0,1,n);x[-n:]*=np.linspace(1,0,n);return x
def tone(start,dur,f,amp=.16):
 x=np.zeros_like(t);a=int(start*SR);n=int(dur*SR);u=np.arange(n)/SR
 env=np.minimum(u/.015,1)*np.exp(-u*3/max(dur,.1))*np.minimum((dur-u)/.04,1)
 x[a:a+n]=amp*env*(np.sin(2*np.pi*f*u)+.22*np.sin(2*np.pi*f*2*u));return x
music=np.zeros_like(t)
for j,f in enumerate([261.63,329.63,392,523.25,440,392,329.63,293.66,261.63,329.63,392,493.88,440,392,293.66,329.63]):music+=tone(j*.6,.6,f,.115)
music=fade(music+.035*np.sin(2*np.pi*130.815*t)*(.6+.4*np.sin(2*np.pi*.2*t)))
mix=music+tone(2.6,.35,659,.12)+tone(2.95,.35,880,.1)+tone(5.7,.55,392,.16)+tone(7.1,.22,784,.11)+tone(7.34,.45,1046.5,.1)
drop=mix.copy()
for st,dur in [(3.4,.09),(6.2,.14)]:
 a=int(st*SR);b=int((st+dur)*SR);n=192;drop[a-n:a]*=np.linspace(1,0,n);drop[a:b]=0;drop[b:b+n]*=np.linspace(0,1,n)
report=[]
for name,x in {'01_scene_mix':mix,'02_continuous':mix,'03_simulated_dropout':drop}.items():
 x=x*(10**(-24/20))/np.sqrt(np.mean(x*x));pcm=np.round(np.column_stack((x,x))*32767).astype('<i2')
 assert np.max(np.abs(pcm.astype(float)))/32768<.501
 p=O/(name+'.wav')
 with wave.open(str(p),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
 report.append({'file':p.name,'seconds':10,'sample_rate':SR,'channels':2,'bits':16,'peak_dBFS':float(20*np.log10(np.max(np.abs(pcm.astype(float)))/32768)),'rms_dBFS':float(20*np.log10(np.sqrt(np.mean((pcm.astype(float)/32768)**2)))),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'measurements.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(O/'README.md').write_text('''# 原创合成演示音频

每段10秒，48kHz/16bit/双声道，同相信号。音频由build/audio.py生成，无外部音乐版权素材。不是鸿蒙实机录音或性能测试。

- P01可选播放01_scene_mix.wav，听音乐持续、游戏和提醒加入。
- P04可选对照02_continuous.wav与03_simulated_dropout.wav。后者在3.4秒和6.2秒人为加入90/140毫秒静音，边缘4毫秒渐变；只辅助感知人为欠载，不能证明PA与HPAE差异。
- 01_scene_mix.wav与02_continuous.wav是同一内容的两个兼容别名，SHA256相同，并非两份独立声音或旧新引擎录音。
- 各段全程RMS约-24dBFS，RMS匹配不等于严格感知响度匹配。实际数据见measurements.json。
- 打开交付目录的index.html手动播放，音频未嵌入PPTX。移动时保持资源目录结构。现场请先以低音量试听，工具没有完成扬声器声压和主观听感验收。
- 重新生成时默认保护已存在文件。用python build/audio.py --output 临时输出目录验证复现；确认替换时才使用--overwrite。
''',encoding='utf-8')
print('Generated 3 original WAV demos')
