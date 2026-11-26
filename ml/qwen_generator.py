"""Адаптер загруженной Qwen для пайплайна Lab 5."""

import time

import torch

from ml.prompts.lab5 import summarize_prompt


class QwenSummaryGenerator:
    """Генератор описаний с параметрами эксперимента Lab 5."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()

    def __call__(self, game_id, store_description):
        prompt = summarize_prompt(
            game_id,
            store_description,
            variant="final",
        )

        text = self.tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )

        device = next(self.model.parameters()).device
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        ).to(device)

        if device.type == "cuda":
            torch.cuda.synchronize(device)

        started = time.perf_counter()

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        if device.type == "cuda":
            torch.cuda.synchronize(device)

        elapsed = time.perf_counter() - started
        input_length = inputs["input_ids"].shape[1]
        generated = outputs[0, input_length:]

        eos_ids = self.model.generation_config.eos_token_id
        if eos_ids is None:
            eos_ids = self.tokenizer.eos_token_id

        if isinstance(eos_ids, int):
            eos_ids = [eos_ids]
        elif eos_ids is None:
            eos_ids = []

        stopped = (
            len(generated) > 0
            and generated[-1].item() in eos_ids
        )

        return {
            "response": self.tokenizer.decode(
                generated,
                skip_special_tokens=True,
            ),
            "finish_reason": "stop" if stopped else "length",
            "latency_s": round(elapsed, 4),
            "prompt_tokens": int(input_length),
            "completion_tokens": int(len(generated)),
            "model": self.model.config.name_or_path,
        }
