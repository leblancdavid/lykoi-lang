"""Second additive attempt; first source/freeze/evidence remain unchanged."""
import sys
import traceback
import successor2
import preflight75 as preflight
import context75 as x

if __name__ == '__main__':
    stage = sys.argv[1]
    try:
        {'prepare':preflight.prepare,'qualify':preflight.qualify,'finish':preflight.finish}[stage]()
    except BaseException as exc:
        if x.OUT.exists():
            x.write('HALT-'+stage+'.json',dict(error=str(exc),traceback=traceback.format_exc(),automatic_retry=False))
        raise
