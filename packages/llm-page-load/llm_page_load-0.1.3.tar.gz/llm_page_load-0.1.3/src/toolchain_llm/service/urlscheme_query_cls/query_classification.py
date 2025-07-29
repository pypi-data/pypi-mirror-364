import json
from llmcore_sdk.models import Friday

query_classification_model = Friday(
    model="gpt-4o-2024-05-13",
    max_tokens=2048,
    temperature=0.1,
    direction="scheme_query_classification",
)

def query_cls(query_labeled: dict, query_need_infer: dict) -> dict:
    if query_labeled and query_need_infer:
        prompt_content = f"""
Please help me categorize the provided key:value pairs and return a JSON object where the key is the name of the query key and the value is the category type. The categorization rules are as follows:
---

Enum Type: "enum" 
**
The parameter has a limited and fixed number of values.
Typically used to represent a certain state, type, or category.
These values are usually defined as enumerations in code to facilitate management and usage.
Some common keys: {query_labeled.get('enum', [])} 
**

Boolean Type: "boolean" 
**
The parameter is a boolean type, which means it is either true or false. It is usually used to represent whether a certain feature or option is enabled or whether a certain state is true. Some parameters with values 0 or 1 could also be boolean type.
Some common keys: {query_labeled.get('boolean', [])} 
**

DateTime Type: "time" 
**
The parameter represents a date or time. It is used to represent a specific point in time or a time period. Examples are: ["2024-07-18", "2024-07-19T15:30:00Z", "1626252859291" (timestamp)] etc.
Some common keys: {query_labeled.get('time', [])} 
**

JSON Type: "json" 
**
The parameter is a JSON object type. It is used to represent complex data structures and can contain multiple key-value pairs.
Some common keys: {query_labeled.get('json', [])} 
**

Location Type: "location" 
**
The parameter is a latitude and longitude value or city ID, usually representing geographic location information.
Some common keys: {query_labeled.get('location', [])} 
**

Other Type: "other" 
**
Other types, such as string or numeric types.
Some common keys: {query_labeled.get('other', [])} 
**

The key:value pairs that need to be categorized are: {query_need_infer}

Please note the following:

Strictly refer to the common keys. If a common key matches a certain category, it should be classified into that category.
Pay special attention to the classification of "enum" and "other" categories, and classify them rigorously according to the rules.
Please return your classification results in JSON format.
    """
        ans = query_classification_model.complex_chat(
            messages=[{"role": "user", "content": prompt_content}],
            response_format={"type": "json_object"},
        )
        return json.loads(ans)
    else:
        return {}
    


if __name__ == "__main__":
    query_need_infer = {"mrn_version": "1", "mrn_biz": "food", "source": "merchantdz"}
    result = query_cls(
        {
            "enum": ["source", "mrn_source"],
            "boolean": ["auto_test_tag", "isPhoenixHomepage"],
            "time": ["trialStartDate", "metrics_start_time"],
            "json": ["baseParams"],
            "other": ["mrn_biz", "mrn_version"],
        },
        query_need_infer,
    )
