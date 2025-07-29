from functools import partial

import pytest
from rich import print as rprint

from wujing.llm.llm_call import llm_call


@pytest.mark.skip()
def test_llm_call_with_instructor(volces, messages, response_model, context, guided_backend="instructor"):
    resp = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        messages=messages,
        response_model=response_model,
        context=context,
        guided_backend=guided_backend,
        cache_enabled=False,
    )

    rprint(f"{type(resp)=}, {resp=}")


def test_llm_call_with_vllm(vllm, messages, response_model, context, guided_backend="vllm"):
    vllm_call = partial(
        llm_call,
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=messages,
        context=context,
        response_model=response_model,
        guided_backend=guided_backend,
        cache_enabled=False,
    )

    resp = vllm_call()
    rprint(f"{type(resp)=}, {resp=}")

    resp = vllm_call(extra_body={"info": "this is a field of extra_body"})
    rprint(f"{type(resp)=}, {resp=}")

    resp = vllm_call(extra_body={"chat_template_kwargs": {"info": "this is a field of chat_template_kwargs"}})
    rprint(f"{type(resp)=}, {resp=}")


@pytest.mark.skip()
def test_max_tokens(volces, messages):
    resp = llm_call(
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        max_tokens=4096,
        cache_enabled=False,
        messages=messages,
    )

    rprint(f"{type(resp)=}, {resp=}")


@pytest.mark.skip()
def test_max_tokens_with_partial(volces, messages):
    req_with_oai = partial(
        llm_call,
        api_key=volces[1],
        api_base=volces[0],
        model=volces[2],
        max_tokens=4096,
        cache_enabled=False,
    )

    rprint(
        req_with_oai(
            messages=messages,
        )
    )
