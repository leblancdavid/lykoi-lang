"""Second-version launcher, changing only the explicit worker entry-point path."""
import successor2
import context75 as x

source = (x.HERE/'dispatch75.py').read_text(encoding='utf-8')
assert "x.HERE/'worker75.py'" in source
source = source.replace("x.HERE/'worker75.py'", "x.HERE/'worker_v2.py'")
exec(compile(source,'r675-successor-launcher','exec'))
