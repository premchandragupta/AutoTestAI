
import os, json, asyncio, hashlib
import aioredis
from typing import List, Dict
from langchain import LLMChain, PromptTemplate
from langchain.llms import OpenAI as LcOpenAI

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
AI_CACHE_TTL = int(os.getenv("AI_CACHE_TTL", "3600"))

PROMPT_TEMPLATE = """You are an expert QA engineer. Given the following requirement text, generate a list of concise test cases.
For each test case provide: title, type (positive/negative/boundary), steps, expected_result, and a one-line description.
Return output in JSON array format like:
[{"title":"...", "type":"positive", "steps":"1. ...", "expected_result":"...", "description":"..."}, ...]

Requirement text:
"""{requirement}"""
"""

_redis = None

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

def _make_chain():
    model_name = os.getenv("LC_MODEL", "gpt-4o-mini")
    temperature = float(os.getenv("LC_TEMPERATURE", "0.0"))
    if not OPENAI_KEY:
        return None
    llm = LcOpenAI(openai_api_key=OPENAI_KEY, model_name=model_name, temperature=temperature)
    prompt = PromptTemplate(input_variables=["requirement"], template=PROMPT_TEMPLATE)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain

async def _call_chain(requirement_text: str) -> List[Dict]:
    chain = _make_chain()
    if not chain:
        return [{
            "title": "Mock: Valid login",
            "type": "positive",
            "steps": "1. Go to login. 2. Enter valid email/password. 3. Submit.",
            "expected_result": "User is logged in and redirected to dashboard.",
            "description": "Basic positive test for login."
        }]
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, chain.run, requirement_text)
    text = resp.strip()
    try:
        data = json.loads(text)
        return data
    except Exception:
        import re
        m = re.search(r"(\[.*\])", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                pass
    return [{
        "title": "Fallback: Generated Test Case",
        "type": "positive",
        "steps": "1. Review requirement. 2. Execute steps manually.",
        "expected_result": "Expected behavior observed.",
        "description": "Fallback test case."
    }]

async def generate_test_cases(requirement_text: str, max_cases: int = 12) -> List[Dict]:
    redis = await _get_redis()
    key = "ai_cache:" + hashlib.sha256(requirement_text.encode("utf-8")).hexdigest()
    cached = await redis.get(key)
    if cached:
        try:
            data = json.loads(cached)
            return data[:max_cases]
        except Exception:
            pass
    result = await _call_chain(requirement_text)
    try:
        await redis.set(key, json.dumps(result), ex=AI_CACHE_TTL)
    except Exception:
        pass
    return result[:max_cases]
