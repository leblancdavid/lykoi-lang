"""Task-blind ASCII JSON grammar mask using already-installed regex/Transformers."""
import time
import regex
import torch
from transformers import LogitsProcessor

STRING = r'"(?:[^"\\\x00-\x1f\x7f-\uffff]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"'
INTEGER = r'-?(?:0|[1-9][0-9]{0,18})'
OPERAND = r'\{(?:"ref":' + STRING + r'|"const":(?:' + INTEGER + r'|true|false|null))\}'
PATTERN = (r'\{"id":"selected","type":"(?:Int64|Bool)","deps":\[(?:' + STRING +
           r'(?:,' + STRING + r')?)?\],"node":\{"op":"value","expr":\{"(?:add|le|eq)":\[' +
           OPERAND + ',' + OPERAND + r'\]\}\}\}')


class StructuralMask(LogitsProcessor):
    def __init__(self, tokenizer, prompt_length, validate):
        started = time.perf_counter()
        self.tokenizer, self.prompt_length, self.validate = tokenizer, prompt_length, validate
        self.grammar = regex.compile(PATTERN)
        self.pieces = []
        for token_id in range(len(tokenizer)):
            if token_id in tokenizer.all_special_ids:
                continue
            text = tokenizer.decode([token_id], skip_special_tokens=False)
            if text and text.isascii():
                self.pieces.append((token_id, text))
        self.eos = tokenizer.eos_token_id
        self.setup_seconds = time.perf_counter() - started
        self.calls = 0
        self.seconds = 0.0
        self.allowed_counts = []

    def accepts(self, text):
        match = self.grammar.fullmatch(text, partial=True)
        if match is None:
            return False, False
        if match.partial:
            return True, False
        try:
            self.validate(text)
        except Exception:
            return False, False
        return True, True

    def __call__(self, input_ids, scores):
        started = time.perf_counter()
        prefix = self.tokenizer.decode(input_ids[0, self.prompt_length:].tolist(), skip_special_tokens=False)
        viable, complete = self.accepts(prefix)
        assert viable, 'GRAMMAR_PREFIX_REJECTED'
        allowed = [self.eos] if complete else [i for i, text in self.pieces if self.accepts(prefix + text)[0]]
        assert allowed, 'GRAMMAR_DEAD_END'
        masked = torch.full_like(scores, -float('inf'))
        masked[:, allowed] = scores[:, allowed]
        # This sync makes mask timing include transfer/enforcement, separate from forward timing.
        torch.cuda.synchronize()
        self.seconds += time.perf_counter() - started
        self.calls += 1
        self.allowed_counts.append(len(allowed))
        return masked
