"""Prepare explicit acceptance observations before any scored author dispatch."""
import itertools
from evidence import HERE, ROOT, load, save, sha, now


class Reject(Exception):
    def __init__(self, code, offset):
        self.code, self.offset = code, offset


def oracle(task, data, modified=False):
    def fail(code, at):
        raise Reject(code, at)
    def read(i):
        if i >= len(data):
            fail('TRUNCATED', len(data))
        return data[i]
    try:
        if len(data) > 64:
            fail('INPUT_LIMIT', 64)
        if task == 'T1':
            mode = read(0)
            if mode not in ((0,1,2) if modified else (0,1)):
                fail('MODE',0)
            x, y = read(1), read(2)
            if len(data)>3:
                fail('TRAILING',3)
            raw = x+y+10*mode
            value = dict(amount=min(raw,200), clipped=raw>200)
            output = bytes([value['amount'], int(value['clipped'])])
        elif task == 'T2':
            version = read(0)
            if version not in ((1,2) if modified else (1,)):
                fail('VERSION',0)
            value = []
            i = 1
            records = 0
            while i<len(data):
                if records == 8:
                    fail('OCCURRENCE_LIMIT',i)
                n = read(i)
                if n>4:
                    fail('RUN',i)
                v = read(i+1)
                value += [v]*n
                if modified and version==2 and n:
                    value.append(255)
                i += 2
                records += 1
            output = bytes(value)
        elif task == 'T3':
            value=[]
            for i in range(0,len(data),2):
                if len(value)==8:
                    fail('OCCURRENCE_LIMIT',i)
                start=read(i)
                if start>15:
                    fail('RANGE',i)
                end=read(i+1)
                if end>15:
                    fail('RANGE',i+1)
                if start>end:
                    fail('ORDER',i)
                if any(v['end']>start for v in value):
                    fail('OVERLAP',i)
                value.append(dict(start=start,end=end))
            output=bytes([len(value)])+data
        else:
            depth=pairs=0
            for i,v in enumerate(data):
                if i==8:
                    fail('OCCURRENCE_LIMIT',i)
                if v not in (40,41):
                    fail('SYNTAX',i)
                if v==40:
                    depth+=1
                    if depth>2:
                        fail('DEPTH',i)
                else:
                    if not depth:
                        fail('UNDERFLOW',i)
                    depth-=1
                    pairs+=1
            if depth:
                fail('UNCLOSED',len(data))
            value=dict(pairs=pairs)
            output=bytes([pairs])
        return dict(status='success',value=value,output=output.hex())
    except Reject as e:
        return dict(status='reject',code=e.code,offset=e.offset)


def rows(task, inputs, modified=False):
    unique=list(dict.fromkeys(bytes(x) for x in inputs))
    return [dict(id=f'{task}-{i:04d}',hex=x.hex(),expected=oracle(task,x,modified))
            for i,x in enumerate(unique)]


def main():
    inputs={}
    inputs['T1']=[bytes([m,x,y]) for m in (0,1) for x,y in itertools.product(
        (0,1,9,10,99,100,189,190,199,200,201,254,255),repeat=2)]
    inputs['T1'] += [b'',b'\0',b'\0\1',b'\1',b'\1\xff',b'\0\0\0\0',
        b'\3',b'\xff',b'\3\0\0\0',b'\0'*65]
    inputs['T2']=[b'\1',b'',b'\0',b'\3',b'\xff',b'\1\0',b'\1\4',b'\1\5',
        b'\1\5\0',b'\1\0\xff\3\4\1\0',b'\1'+b'\4\xff'*8,
        b'\1'+b'\0\0'*8+b'\xff',b'\1'+b'\1\0'*8+b'\0\0',b'\1'*65]
    inputs['T2'] += [bytes([1,n,v]) for n in range(5) for v in (0,1,127,255)]
    inputs['T2'] += [bytes([1,a,7,b,9]) for a,b in itertools.product(range(5),repeat=2)]
    inputs['T3']=[bytes([a,b]) for a,b in itertools.product((0,1,7,14,15,16,255),repeat=2)]
    inputs['T3'] += [b'',b'\0',b'\xff',b'\0\1\1\2',b'\0\1\0\2',
        b'\2\2\2\2',b'\2\3\1\1',b'\0\1\0',b'\0\1\0\2\xff',
        b'\0\0'*8,b'\0\0'*8+b'\xff',b'\0'*65]
    inputs['T3'] += [bytes([a,b,c,d]) for a,b,c,d in itertools.product((0,1,2),repeat=4)]
    inputs['T4']=[bytes(x) for n in range(9) for x in itertools.product((40,41),repeat=n)]
    inputs['T4'] += [b'X',b'()X',b'(((X',b'()()()()X',b'()()()()(',
        b'\xff',b'(\xff',b'('*65]
    for t,x in inputs.items():
        save(HERE/'acceptance'/f'{t}.json',rows(t,x))
    m1=[bytes([2,x,y]) for x,y in itertools.product((0,1,179,180,199,200,255),repeat=2)]
    m1 += [b'\2',b'\2\0',b'\2\0\0\0',b'\2'*65]
    m2=[bytes([2,n,v]) for n in range(5) for v in (0,1,255)]
    m2 += [b'\2',b'\2\0',b'\2\5',b'\2\0\7\2\xff\1\0',
        b'\2'+b'\4\xff'*8,b'\2'+b'\0\0'*8+b'\xff',b'\2'*65]
    save(HERE/'sealed'/'M1.json',rows('T1',m1,True))
    save(HERE/'sealed'/'M2.json',rows('T2',m2,True))
    names=['PROTOCOL.md','BASELINE.json','evidence.py','prepare.py']
    names += [p.relative_to(HERE).as_posix() for folder in ('tasks','acceptance')
              for p in sorted((HERE/folder).rglob('*')) if p.is_file()]
    save(HERE/'TASK-FREEZE.json',dict(utc=now(),files={n:sha(HERE/n) for n in names},
        counts={t:len(load(HERE/'acceptance'/f'{t}.json')) for t in inputs}))
    save(HERE/'MODIFICATION-SEAL.json',dict(utc=now(),files={p.relative_to(HERE).as_posix():sha(p)
        for p in sorted((HERE/'sealed').glob('*')) if p.is_file()},
        access='withheld by cooperative instructions; no hard filesystem denial'))
    print('Task and modification expectations frozen before author dispatch')


if __name__=='__main__':
    main()
