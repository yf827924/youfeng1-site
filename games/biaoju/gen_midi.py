#!/usr/bin/env python3
# 生成真实中国民乐 MIDI + 游戏用音符 JSON（纯标准库，无需第三方依赖）
# 改进：旋律带强弱对比 + 附点/切分节奏型 + 连音(legato)标记；低音改为有律动的分解节奏。
import json, struct, os

OUT = os.path.dirname(os.path.abspath(__file__))
TPQ = 480  # ticks per quarter

NOTE_IDX = {'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def note_to_midi(name):
    m = name[0]; acc = name[1] if name[1] in '#' else ''; oct = int(name[2 if acc else 1])
    semi = NOTE_IDX[m] + (1 if acc=='#' else 0)
    return (oct+1)*12 + semi

def vlq(n):
    out = [n & 0x7f]; n >>= 7
    while n: out.insert(0, (n & 0x7f) | 0x80); n >>= 7
    return bytes(out)

def write_midi(path, tempo, channels):
    spq = 60000000 // tempo
    events = []
    for ch, notes in channels.items():
        for (n, s, d, v) in notes:
            events.append((s, True, ch, n, v))
            events.append((s+d, False, ch, n, 0))
    events.sort(key=lambda e: (e[0], 0 if e[1] else 1))
    track = b''; last = 0
    track += vlq(0) + b'\xff\x51\x03' + struct.pack('>I', spq)[1:]
    for (tick, isOn, ch, note, vel) in events:
        delta = tick - last; last = tick; track += vlq(delta)
        if isOn: track += bytes([0x90 | ch, note, vel])
        else: track += bytes([0x80 | ch, note, 0])
    track += vlq(0) + b'\xff\x2f\x00'
    data = b'MThd' + struct.pack('>IHHH', 6, 0, 1, TPQ)
    data += b'MTrk' + struct.pack('>I', len(track)) + track
    with open(path, 'wb') as f: f.write(data)

# ---------- 旋律定义（拍为单位，四分音符=1拍）----------
# 字段: (音名, 起始拍, 时值拍, 力度0-127, 是否连音到下一音)
# 力度梯度: 句头/重音强(92-98) 正常(82-88) 经过音弱(68-74) 长音尾渐弱
# 低音只用采样集内音名(C/A/F#/D# 各八度)，音高最准、无需变调

# 茉莉花（C 大调五声，tempo 90）—— 带附点与切分，更歌唱
JASMINE_TEMPO = 90
jasmine_rh = [
 ('E4',0,1.0,96,True),('E4',1,1.0,86,True),('G4',2,1.0,90,True),('A4',3,1.0,92,True),
 ('C5',4,1.5,95,True),('C5',5.5,0.5,76,True),('A4',6,1.0,88,True),('G4',7,1.0,90,True),
 ('G4',8,0.75,84,True),('A4',8.75,0.25,70,True),('G4',9,1.0,88,True),('E4',10,1.0,90,True),
 ('G4',11,1.0,86,True),('E4',12,1.0,84,True),('D4',13,2.0,92,False),
 ('E4',15,1.0,84,True),('D4',16,1.0,80,True),('E4',17,1.0,86,True),
 ('C4',18,1.5,90,True),('D4',19.5,0.5,74,True),('C4',20,2.0,94,False),
 ('A4',22,1.0,86,True),('C4',23,3.0,98,False),
]
# 低音: 每拍"根-五/三"八分律动 (采样集内音名: C2/A2/F#2/D#2)
jasmine_bass = [
 ('C2',0,0.5,74,True),('G2not',0.5,0.5,60,True),   # G2 不在采样集, 用 C2 替代八度跳动
 ('C2',1,0.5,74,True),('A2',1.5,0.5,62,True),
 ('C2',2,0.5,74,True),('G2not',2.5,0.5,60,True),
 ('C2',3,0.5,74,True),('A2',3.5,0.5,62,True),
 ('C2',4,0.5,76,True),('G2not',4.5,0.5,60,True),
 ('C2',5,0.5,76,True),('A2',5.5,0.5,62,True),
 ('C2',6,0.5,74,True),('G2not',6.5,0.5,60,True),
 ('C2',7,0.5,74,True),('A2',7.5,0.5,62,True),
 ('C2',8,0.5,74,True),('G2not',8.5,0.5,60,True),
 ('C2',9,0.5,74,True),('A2',9.5,0.5,62,True),
 ('C2',10,0.5,74,True),('G2not',10.5,0.5,60,True),
 ('C2',11,0.5,74,True),('A2',11.5,0.5,62,True),
 ('C2',12,0.5,74,True),('G2not',12.5,0.5,60,True),
 ('C2',13,0.5,74,True),('A2',13.5,0.5,62,True),
 ('C2',14,0.5,74,True),('G2not',14.5,0.5,60,True),
 ('C2',15,0.5,74,True),('A2',15.5,0.5,62,True),
 ('C2',16,0.5,74,True),('G2not',16.5,0.5,60,True),
 ('C2',17,0.5,74,True),('A2',17.5,0.5,62,True),
 ('C2',18,0.5,76,True),('G2not',18.5,0.5,60,True),
 ('C2',19,0.5,76,True),('A2',19.5,0.5,62,True),
 ('C2',20,0.5,76,True),('G2not',20.5,0.5,60,True),
 ('C2',21,0.5,76,True),('A2',21.5,0.5,62,True),
 ('C2',22,0.5,74,True),('G2not',22.5,0.5,60,True),
 ('C2',23,2.0,80,False),
]
# 修正低音: 把占位 G2not 替换为采样集内 F#2 (IV级, 半音误差内)
for i,(n,s,d,v,l) in enumerate(jasmine_bass):
    if n=='G2not': jasmine_bass[i]=('F#2',s,d,v,l)

# 彩云追月（tempo 72，悠扬）—— 附点拖腔 + 切分，月色感
MOON_TEMPO = 72
moon_rh = [
 ('E4',0,1.0,90,True),('G4',1,1.0,86,True),('A4',2,1.0,88,True),('C5',3,1.5,94,True),
 ('A4',4.5,0.5,80,True),('G4',5,1.0,86,True),('E4',6,1.0,84,True),('G4',7,1.0,86,True),
 ('D4',8,1.0,82,True),('E4',9,1.0,86,True),('G4',10,1.0,88,True),('E4',11,1.0,84,True),
 ('D4',12,1.0,82,True),('C4',13,1.0,84,True),('D4',14,2.0,92,False),
 ('A4',16,1.0,88,True),('C5',17,1.0,90,True),('D5',18,1.0,92,True),('E5',19,1.5,96,True),
 ('D5',20.5,0.5,80,True),('C5',21,1.0,88,True),('A4',22,1.0,86,True),('C5',23,1.0,88,True),
 ('G4',24,1.0,84,True),('A4',25,1.0,86,True),('C5',26,1.0,88,True),('A4',27,1.0,86,True),
 ('G4',28,1.0,84,True),('E4',29,1.0,82,True),('G4',30,2.0,94,False),
]
moon_bass = [
 ('C2',0,1.0,70,True),('A2',1,1.0,58,True),('C2',2,1.0,70,True),('A2',3,1.0,58,True),
 ('C2',4,1.0,72,True),('A2',5,1.0,58,True),('C2',6,1.0,70,True),('A2',7,1.0,58,True),
 ('C2',8,1.0,70,True),('A2',9,1.0,58,True),('C2',10,1.0,70,True),('A2',11,1.0,58,True),
 ('C2',12,1.0,70,True),('A2',13,1.0,58,True),
 ('C2',14,2.0,78,False),
 ('A2',16,1.0,68,True),('F#2',17,1.0,58,True),('A2',18,1.0,68,True),('F#2',19,1.0,58,True),
 ('A2',20,1.0,68,True),('F#2',21,1.0,58,True),('A2',22,1.0,68,True),('F#2',23,1.0,58,True),
 ('C2',24,1.0,70,True),('A2',25,1.0,58,True),('C2',26,1.0,70,True),('A2',27,1.0,58,True),
 ('C2',28,1.0,70,True),('A2',29,1.0,58,True),
 ('C2',30,2.0,78,False),
]

def build(tempo, rh, bass):
    spb = 60.0 / tempo
    ch0=[]; ch1=[]; json_notes=[]; end=0
    for (n,s,d,v,leg) in rh:
        m=note_to_midi(n); st=int(round(s*TPQ)); du=int(round(d*TPQ))
        ch0.append((m,st,du,max(40,min(127,v))))
        json_notes.append({'t':round(s*spb,3),'d':round(d*spb,3),'n':n,'v':v/127.0,'voice':0,'leg':leg})
        end=max(end,s+d)
    for (n,s,d,v,leg) in bass:
        m=note_to_midi(n); st=int(round(s*TPQ)); du=int(round(d*TPQ))
        ch1.append((m,st,du,max(40,min(127,v))))
        json_notes.append({'t':round(s*spb,3),'d':round(d*spb,3),'n':n,'v':v/127.0,'voice':1,'leg':leg})
        end=max(end,s+d)
    ch0.sort(key=lambda x:x[1]); ch1.sort(key=lambda x:x[1])
    return {'tempo':tempo,'channels':{0:ch0,1:ch1},'json':json_notes,'dur':round(end*spb,3)}

def main():
    songs = {
        'jasmine': build(JASMINE_TEMPO, jasmine_rh, jasmine_bass),
        'caiyun':  build(MOON_TEMPO, moon_rh, moon_bass),
    }
    for name, s in songs.items():
        write_midi(os.path.join(OUT,'midi',name+'.mid'), s['tempo'], s['channels'])
        with open(os.path.join(OUT,'midi',name+'.json'),'w',encoding='utf-8') as f:
            json.dump({'tempo':s['tempo'],'dur':s['dur'],'notes':s['json']}, f, ensure_ascii=False)
        lh=sum(1 for x in s['json'] if x['voice']==1)
        print(f"{name}: notes={len(s['json'])} (melody={len(s['json'])-lh}, bass={lh}) dur={s['dur']}s midi={os.path.getsize(os.path.join(OUT,'midi',name+'.mid'))}B json={os.path.getsize(os.path.join(OUT,'midi',name+'.json'))}B")

if __name__ == '__main__':
    main()
