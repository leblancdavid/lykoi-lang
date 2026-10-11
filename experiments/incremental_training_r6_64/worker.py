"""Reuse the exact cache-release training mechanics; B-only data and scorer."""
import os
import sys
import threading
import time
import run


def effective_source():
    source=(run.ROOT/'benchmark/results/phase6/r6_59/EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    old="'round': 'R6.59', 'run_number'"
    assert source.count(old)==1
    source=source.replace(old,"'round': 'R6.64', 'run_number'")
    # Diagnostic worker is independently frozen below; training/reload remain inherited.
    return source[:source.index('def diagnostic(track, index):')]


def diagnostics(track):
    import torch
    from transformers import AutoTokenizer, GenerationConfig
    frozen_check()
    q52.seed()
    torch.cuda.reset_peak_memory_stats()
    model, quant=load_trained() if track=='adapter' else prepare_base()
    model.eval()
    tokenizer=AutoTokenizer.from_pretrained(STORE/'checkpoint',local_files_only=True,trust_remote_code=False)
    generation=GenerationConfig.from_dict(read(OUT/'DIAGNOSTIC-PROTOCOL.json')['resolved_generation_configuration'])
    started=time.perf_counter()
    stop=threading.Event()
    current_started=[None]
    minimum_free=[memory()['device_free_bytes']]
    def monitor():
        while not stop.wait(0.1):
            try:
                values=memory()
                minimum_free[0]=min(minimum_free[0],values['device_free_bytes'])
                assert current_started[0] is None or time.perf_counter()-current_started[0]<=120, 'DIAGNOSTIC_TIMEOUT'
            except BaseException as exc:
                write(f'DIAGNOSTIC-{track.upper()}-ABORT.json',dict(error=str(exc),memory=read(OUT/'MEMORY-LATEST.json')))
                os._exit(71)
    thread=threading.Thread(target=monitor,daemon=True)
    thread.start()
    entries=[]
    try:
        for row in read(OUT/'DIAGNOSTICS.json')['records']:
            ids,labels,measure=q52.encoded(row,tokenizer)
            # Paired teacher-forced loss uses eval mode and the exact frozen mask.
            with torch.inference_mode():
                x=torch.tensor([ids],device='cuda')
                y=torch.tensor([labels],device='cuda')
                output=model(input_ids=x,attention_mask=torch.ones_like(x),labels=y,use_cache=False)
                loss=output.loss.item()
                assert __import__('math').isfinite(loss)
                del output,x,y
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            memory()
            prompt=tokenizer.apply_chat_template(row['prompt'],tokenize=False,add_generation_prompt=True)
            x=tokenizer(prompt,add_special_tokens=False,return_tensors='pt').to('cuda')
            assert x.input_ids.shape[1]+128<=2048
            torch.cuda.synchronize()
            inference_start=time.perf_counter()
            current_started[0]=inference_start
            with torch.inference_mode():
                generated=model.generate(**x,generation_config=generation,use_cache=False)
            torch.cuda.synchronize()
            seconds=time.perf_counter()-inference_start
            current_started[0]=None
            output_ids=generated[0,x.input_ids.shape[1]:].cpu().tolist()
            content_ids=output_ids[:-1] if output_ids and output_ids[-1] in generation.eos_token_id else output_ids
            text=tokenizer.decode(content_ids,skip_special_tokens=False)
            result=dict(episode_id=row['episode_id'],group=row['group'],output=text,output_token_ids=output_ids,
                        output_tokens=len(output_ids),input_tokens=x.input_ids.shape[1],inference_seconds=seconds,
                        teacher_forced_loss=loss,eos_terminated=bool(output_ids and output_ids[-1] in generation.eos_token_id),
                        scores=score(text,row),prompt_identity=identity(row['prompt']))
            entries.append(result)
            write(f'DIAGNOSTIC-{track.upper()}-{row["episode_id"].split("/")[-1]}.json',result)
            del generated,x
            torch.cuda.empty_cache()
            memory()
            print(row['episode_id'],result['scores']['schema_valid'],result['scores']['behavioral_acceptance'],flush=True)
        write(f'DIAGNOSTIC-{track.upper()}.json',dict(status='PASS',track=track,records=entries,
              seconds=time.perf_counter()-started,minimum_sampled_device_free_bytes=minimum_free[0],quantization=quant,**memory()))
    finally:
        stop.set()
        thread.join(timeout=2)


if __name__=='__main__':
    exec(compile(effective_source(),'R6.64-effective-worker','exec'),globals())
    mode=sys.argv[1]
    if mode=='train': train()
    elif mode=='reload': reload()
    elif mode in ('base','adapter'): diagnostics(mode)
    else: raise ValueError(mode)
