import json

with open("config.json") as f:
    cfg = json.load(f)



def clean(d):
    if isinstance(d, list):
        for a in d:
            clean(a)
    elif isinstance(d, dict):
        for k, v in d.copy().items():
            if not v or v == " - " or v == "-":
                del d[k]
    return d


def parse_resp(resp):
    return clean(
        json.loads(
            resp.text[6:-2]
            .replace('\\"', '"')
            .replace("\\n", "\n")
            .encode()
            .decode("unicode-escape")
        )
    )
