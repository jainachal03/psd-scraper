import copy
import json
import requests
from urllib.parse import urljoin as join, quote
from bs4 import BeautifulSoup
from utils import cfg, parse_resp


BASE_URL = "http://psd.bits-pilani.ac.in"
STUDENT_URL = join(BASE_URL, "Student/")
PB_URL = join(STUDENT_URL, "ViewActiveStationProblemBankData.aspx/")
STATION_PB_DETAILS_URL = join(STUDENT_URL, "StationproblemBankDetails.aspx/")
STATION_PREF_URL = join(STUDENT_URL, "StudentStationPreference.aspx/")
sess = requests.Session()


def login():
    if "ASP.NET_SessionId" in sess.cookies:
        return True
    LOGIN_URL = join(BASE_URL, "Login.aspx")
    resp = sess.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    form = soup.find("form", id="Form2")
    payload = {}
    for inp in form.find_all("input"):
        try:
            payload[inp["id"]] = inp["value"]
        except KeyError:
            pass
    payload["TxtEmail"] = cfg["creds"]["email"]
    payload["txtPass"] = cfg["creds"]["password"]
    pr = requests.Request("POST", LOGIN_URL, data=payload).prepare()
    sess.send(pr)
    return "ASP.NET_SessionId" in sess.cookies


def get_pb_detail():
    try:
        with open("pb.json") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    PB_DETAIL_URL = join(PB_URL, "getPBdetail")
    r = sess.post(
        PB_DETAIL_URL,
        data='{batchid: "undefined"}',
        headers={"Content-Type": "application/json"},
    )
    pb = json.loads(r.text[6:-2].replace('\\"', '"'))
    with open("pb.json", "w") as f:
        json.dump(pb, f, indent=4)
    return pb


def get_pb_popup(station_id):
    PB_POPUP_URL = join(PB_URL, "getPBPOPUP")
    r = sess.post(
        PB_POPUP_URL,
        data=json.dumps({"StationId": str(station_id)}),
        headers={"Content-Type": "application/json"},
    )
    return parse_resp(r)


def get_proj_details(company_id, station_id, batch_id, ps_type):
    PROJ_URL = join(STATION_PB_DETAILS_URL, "ViewPB")
    query = {
        "CompanyId": company_id,
        "StationId": station_id,
        "BatchIdFor": batch_id,
        "PSTypeFor": ps_type,
    }
    sess.get(STATION_PB_DETAILS_URL, params=query)
    r = sess.post(
        PROJ_URL,
        data='{batchid: "undefined" }',
        headers={"Content-Type": "application/json"},
    )
    return parse_resp(r)


def fetch_full_details():
    pb = get_pb_detail()
    for station in pb:
        station["projs"] = get_pb_popup(station["StationId"])
        for proj in station["projs"]:
            proj["details"] = get_proj_details(
                proj["CompanyId"],
                proj["StationId"],
                proj["BatchIdFor"],
                proj["PSTypeFor"],
            )
    return pb


def extract_relevant(full):
    relevant = copy.deepcopy(full)
    n1 = ["StationId", "Tags", "CompanyId", "City", "CompanyName", "projs"]
    n2 = ["ProjectId", "ProjectTitle", "PBDescription", "TotalReqdStudents"]
    for s in relevant:
        a = s.copy()
        for key in a:
            if key not in n1:
                del s[key]
        projs = []
        for proj in s["projs"]:
            for p in proj["details"]:
                b = p.copy()
                for k, v in b.items():
                    if k not in n2:
                        del p[k]
                    elif isinstance(v, str):
                        v = v.replace("\\n", "\n")
                        p[k] = v.encode().decode("unicode-escape")
                p["batch"] = proj["BatchName"]
            projs.append(p.copy())
        s["projs"] = projs
    return relevant


def get_stations_info():
    INFO_URL = join(STATION_PREF_URL, "getinfoStation")
    r = sess.post(
        INFO_URL, data='{CompanyId: "0"}', headers={"Content-Type": "application/json"}
    )
    return parse_resp(r)


def fetch_prefs():
    PREF_URL = join(STATION_PREF_URL, "chkStationpref")
    print(PREF_URL)
    r = sess.post(
        PREF_URL, data='{contactid: "0"}', headers={"Content-Type": "application/json"}
    )
    # print(r)
    return parse_resp(r)


def post_prefs(prefs):
    """Doesn't work"""
    SAVE_PREF_URL = join(STATION_PREF_URL, "saveStudentStationPref")
    a = json.dumps(prefs, separators=(",", ":")).replace('"', "'")
    d = quote(a).replace("%27", "'").replace("false'", "false'%2C")
    b = f'{{ jsondata: "{d}", jsonvalue: "", contistation: "0"}}'
    print(b)
    sess.post(SAVE_PREF_URL, headers={"Content-Type": "application/json"}, data=a)
    # print(SAVE_PREF_URL, r.url, r.request.headers, r)


def update_prefs():
    """Doesn't work"""
    with open("shortlisted.json") as f:
        shortlist = json.load(f)
    shortlist_stations = [stat["StationId"] for stat in shortlist]
    old_prefs = fetch_prefs()
    print(old_prefs)
    top = list(
        filter(lambda station: station["StationId"] in shortlist_stations, old_prefs)
    )
    # bottom = [stat for stat in old_prefs if stat not in top]
    # comb = top + bottom
    post_data = []
    for ind, s in enumerate(old_prefs, 1):
        post_data.append(
            {
                "isActive": "1",
                "PreferenceNo": str(ind),
                "StationId": str(s["StationId"]),
                "Accommodation": "false",
            }
        )
    post_prefs(post_data)


def main():
    if not login():
        return
    full = fetch_full_details()
    with open("full.json", "w") as f:
        json.dump(full, f, indent=4)
    print(fetch_prefs())


if __name__ == "__main__":
    main()
