from typing import Any
import dsp
import itertools


class LlamaAdapter:
    def __call__(self, parts: dict):
        instructions, guidelines, rdemos, ademos, query, long_query = parts["instructions"], parts["guidelines"], parts["rdemos"], parts["ademos"], parts["query"], parts["long_query"]
        rdemos = "\n\n".join(rdemos)
        if len(rdemos) >= 1 and len(ademos) == 0 and not long_query:
            # rdemos_and_query = "\n\n".join([rdemos, query])
            parts = [
                "[INST] <<SYS>>\n"+instructions,
                guidelines+"\n<</SYS>>",
                rdemos+"[/INST]\n"+query
            ]
        elif len(rdemos) == 0:
            parts = [
                "[INST] <<SYS>>\n"+instructions,
                guidelines+"\n<</SYS>>",
                *ademos,
                "[/INST]\n"+query,
            ]
        else:
            parts = [
                "[INST] <<SYS>>\n"+instructions,
                rdemos,
                guidelines+"\n<</SYS>>",
                *ademos,
                "[/INST]\n"+query,
            ]

        prompt = "\n\n---\n\n".join([p.strip() for p in parts if p])
        prompt = prompt.strip()
        return prompt
    
    
    

class DavinciAdapter:
    def __call__(self, parts: dict):
        instructions, guidelines, rdemos, ademos, query, long_query = parts["instructions"], parts["guidelines"], parts["rdemos"], parts["ademos"], parts["query"], parts["long_query"]
        rdemos = "\n\n".join(rdemos)
        if len(rdemos) >= 1 and len(ademos) == 0 and not long_query:
            rdemos_and_query = "\n\n".join([rdemos, query])
            parts = [
                instructions,
                guidelines,
                rdemos_and_query,
            ]
        elif len(rdemos) == 0:
            parts = [
                instructions,
                guidelines,
                *ademos,
                query,
            ]
        else:
            parts = [
                instructions,
                rdemos,
                guidelines,
                *ademos,
                query,
            ]

        prompt = "\n\n---\n\n".join([p.strip() for p in parts if p])
        prompt = prompt.strip()
        return prompt
    

class TurboAdapter:
    """
        OpenAI Turbo Docs. See https://platform.openai.com/docs/guides/chat/introduction
    """

    def __init__(self, system_turn=False, multi_turn=False, strict_turn=False):
        self.system_turn = system_turn
        self.multi_turn = multi_turn
        self.strict_turn = strict_turn

    # def __call__(self, parts: list, include_rdemos: bool, include_ademos: bool, include_ademos: bool, include_context: bool):
    def __call__(self, parts: dict):
        prompt = {}
        prompt["model"] = dsp.settings.lm.kwargs["model"]
        
        instructions, guidelines, rdemos, ademos, query, long_query = parts["instructions"].strip(), parts["guidelines"].strip(), parts["rdemos"], parts["ademos"], parts["query"].strip(), parts["long_query"]       
        rdemos = "\n\n".join(rdemos).strip()
        rdemos_and_query = "\n\n".join([rdemos, query]).strip()
        messages = []
        
        if len(rdemos) >= 1 and len(ademos) == 0 and not long_query:
            if self.system_turn and self.multi_turn:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": guidelines},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": rdemos},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": query},
                ]
                messages = [m for m in messages if m]

            elif self.system_turn and not self.multi_turn:
                rdemos_and_query = "\n\n".join([rdemos, query])
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [guidelines, rdemos_and_query] if p])},
                ]
                
            elif not self.system_turn and self.multi_turn:
                messages = [
                    {"role": "user", "content": instructions},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": guidelines},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": rdemos},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": query},
                ]
                messages = [m for m in messages if m]

            elif not self.system_turn and not self.multi_turn:
                rdemos_and_query = "\n\n".join([rdemos, query])
                messages = [
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [instructions, guidelines, rdemos_and_query] if p])},
                ]

        elif len(rdemos) == 0:
            if self.system_turn and self.multi_turn:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": guidelines},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                ]
                for ademo in ademos:
                    messages.append({"role": "user", "content": ademo})
                    messages.append({"role": "assistant", "content": "Got it."} if self.strict_turn else {}),
                messages.append({"role": "user", "content": query})
                messages = [m for m in messages if m]

            elif self.system_turn and not self.multi_turn:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [guidelines, *ademos, query] if p]) },
                ]

            elif not self.system_turn and self.multi_turn:
                messages = [
                    {"role": "user", "content": instructions},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": guidelines},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                ]
                for ademo in ademos:
                    messages.append({"role": "user", "content": ademo})
                    messages.append({"role": "assistant", "content": "Got it."} if self.strict_turn else {})
                messages.append({"role": "user", "content": query})
                messages = [m for m in messages if m]

            elif not self.system_turn and not self.multi_turn:
                messages = [
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [instructions, guidelines, *ademos, query] if p])},
                ]
            
        else:
            if self.system_turn and self.multi_turn:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": rdemos},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                ]
                messages.append({"role": "user", "content": guidelines})
                messages.append({"role": "assistant", "content": "Got it."} if self.strict_turn else {})
                
                for ademo in ademos:
                    messages.append({"role": "user", "content": ademo})
                    messages.append({"role": "assistant", "content": "Got it."} if self.strict_turn else {})
                messages.append({"role": "user", "content": query})
                messages = [m for m in messages if m]

            elif self.system_turn and not self.multi_turn:
                messages = [
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [rdemos, guidelines, *ademos, query] if p]) },
                ]

            elif not self.system_turn and self.multi_turn:
                messages = [
                    {"role": "user", "content": instructions},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": rdemos},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                    {"role": "user", "content": guidelines},
                    {"role": "assistant", "content": "Got it."} if self.strict_turn else {},
                ]
                for ademo in ademos:
                    messages.append({"role": "user", "content": ademo})
                    messages.append({"role": "assistant", "content": "Got it."} if self.strict_turn else {})
                messages.append({"role": "user", "content": query})
                messages = [m for m in messages if m]

            elif not self.system_turn and not self.multi_turn:
                messages = [
                    {"role": "user", "content": "\n\n---\n\n".join([p.strip() for p in [instructions, rdemos, guidelines, *ademos, query] if p])},
                ]

        prompt["messages"] = messages
        return prompt
    

