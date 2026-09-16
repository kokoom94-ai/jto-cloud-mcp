"""Input contract and deterministic budget calculations; no network or AI calls."""
from datetime import date
import re

SECTIONS = {
    "background": "추진배경 및 목적",
    "direction": "추진방향",
    "previous_results": "전년도 주요성과",
    "analysis": "현황분석 및 문제점",
    "implementation": "세부 추진계획(안)",
    "schedule": "추진일정(안)",
}
MAX_MONEY = 999_999_999_999


def string(maximum=240, minimum=1):
    return {"type": "string", "minLength": minimum, "maxLength": maximum}


def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}


def array(items, maximum=20):
    return {"type": "array", "items": items, "minItems": 1, "maxItems": maximum}


BLOCK = obj({"text": string(), "details": array(string(), 10), "subdetails": array(string(), 10), "note": string()}, ["text"])
TABLE_SECTIONS = ("previous_results", "analysis", "implementation", "schedule")
TABLE_ROW = {"type": "array", "items": string(100, 0), "minItems": 5, "maxItems": 5}
SECTION_TABLE = obj({"headers": {**TABLE_ROW, "items": string(30)}, "rows": array(TABLE_ROW, 30)})
MONEY = {"type": "integer", "minimum": 0, "maximum": MAX_MONEY}
PLAN_SCHEMA = obj({
    "project_name": string(32),
    "plan_title": string(42),
    "document_date": {**string(10, 10), "format": "date", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
    "department": string(30), "author": string(20), "position": string(20),
    "sections": obj({k: array(BLOCK) for k in SECTIONS}),
    "budget": obj({
        "account": string(100), "payment_method": string(100),
        "items": array(obj({"category": string(16), "description": string(200),
                            "amount": MONEY, "note": string(40, 0)},
                           ["category", "description", "amount"]), 40),
        "declared_total": MONEY,
    }, ["account", "payment_method", "items"]),
    "expected_effects": array(string()),
    "is_example": {"type": "boolean"},
    "section_tables": obj({key: SECTION_TABLE for key in TABLE_SECTIONS}, []),
}, ["project_name", "plan_title", "document_date", "department", "author", "position",
    "sections", "budget", "expected_effects"])
PLAN_SCHEMA["$schema"] = "https://json-schema.org/draft/2020-12/schema"
PLAN_SCHEMA["title"] = "JTO 사업계획 입력 v1.0"
PLAN_SCHEMA['properties']['research'] = obj({
    'as_of': {'type':'string','format':'date','minLength':10,'maxLength':10},
    'status': string(40),
    'sources': {'type':'array','minItems':0,'maxItems':30,'items':obj({
        'id':string(20),'title':string(200),'country':string(60),'url':string(2048),
        'published':string(60),'checked_on':{'type':'string','format':'date','minLength':10,'maxLength':10},
        'insight':string(500)})}
})
PLAN_SCHEMA['properties']['missing_inputs'] = {'type':'array','items':string(240),'minItems':0,'maxItems':30}


class ValidationError(ValueError):
    pass


def validate_schema(value, schema, path="$", errors=None):
    """Validate the bounded JSON Schema subset used by this server."""
    errors = [] if errors is None else errors
    kind = schema.get("type")
    valid = {"object": lambda: isinstance(value, dict),
             "array": lambda: isinstance(value, list),
             "string": lambda: isinstance(value, str),
             "integer": lambda: type(value) is int,
             "boolean": lambda: type(value) is bool}[kind]()
    if not valid:
        errors.append(f"{path}: {kind} 형식이어야 합니다.")
        return errors
    if kind == "object":
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: 필수 항목입니다.")
        props = schema.get("properties", {})
        for key, item in value.items():
            if key not in props:
                if schema.get("additionalProperties") is False:
                    errors.append(f"{path}.{key}: 정의되지 않은 항목입니다.")
            else:
                validate_schema(item, props[key], f"{path}.{key}", errors)
    elif kind == "array":
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 10**9):
            errors.append(f"{path}: 항목 수 범위를 벗어났습니다.")
        for i, item in enumerate(value):
            validate_schema(item, schema["items"], f"{path}[{i}]", errors)
    elif kind == "string":
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 10**9):
            errors.append(f"{path}: 문자열 길이 범위를 벗어났습니다.")
        if schema.get("minLength", 0) and not value.strip():
            errors.append(f"{path}: 공백만 입력할 수 없습니다.")
        if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in value):
            errors.append(f"{path}: 줄바꿈·제어문자·유효하지 않은 XML 문자를 사용할 수 없습니다.")
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            errors.append(f"{path}: 형식이 올바르지 않습니다.")
        if schema.get("format") == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                errors.append(f"{path}: 유효한 YYYY-MM-DD 날짜가 필요합니다.")
    elif kind == "integer":
        if not schema.get("minimum", -10**20) <= value <= schema.get("maximum", 10**20):
            errors.append(f"{path}: 허용 범위를 벗어났습니다.")
    return errors


def validate_plan(plan):
    errors = validate_schema(plan, PLAN_SCHEMA)
    warnings = []
    total = None
    if not errors:
        total = sum(row["amount"] for row in plan["budget"]["items"])
        if total > MAX_MONEY:
            errors.append("$.budget.items: 예산 합계가 999,999,999,999원을 초과합니다.")
        declared = plan["budget"].get("declared_total")
        if declared is not None and total != declared:
            errors.append(f"$.budget.declared_total: 입력 합계 {declared:,}원과 항목 합계 {total:,}원이 다릅니다.")
        if not total:
            warnings.append("예산이 0원입니다. 무예산 사업인지 확인하십시오.")
        if plan.get("is_example"):
            warnings.append("예제 자료입니다. 실제 사업·예산·승인 자료가 아닙니다.")
        if any(len(s) > 100 for s in walk_strings(plan)):
            warnings.append("긴 문장이 포함되어 있습니다. 한글에서 줄바꿈·표 넘침을 확인하십시오.")
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "budget_total": total, "facts_verified": False,
            "notice": "형식·합계 검사이며 사실관계, 예산 적정성 또는 결재 승인을 의미하지 않습니다."}


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def korean_money(number):
    if type(number) is not int or not 0 <= number <= MAX_MONEY:
        raise ValueError("금액 범위 오류")
    if number == 0:
        return "영원"
    digits = "일이삼사오육칠팔구"
    result = []
    for group, unit in ((number // 100_000_000, "억"),
                        (number // 10_000 % 10_000, "만"), (number % 10_000, "")):
        if not group:
            continue
        part = ""
        for power, small_unit in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
            digit = group // power % 10
            if digit:
                part += ("" if digit == 1 and power > 1 else digits[digit - 1]) + small_unit
        result.append(part + unit)
    return "".join(result) + "원"
