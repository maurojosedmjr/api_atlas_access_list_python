import os
import requests
from requests.auth import HTTPDigestAuth
import json

PUBLIC_KEY = os.getenv("PUBLIC_KEY_ATLAS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY_ATLAS")
PROJECT_ID_ATLAS = os.getenv("PROJECT_ID_ATLAS")


def get_access_lists(puclic_key: str, private_key: str, project_id: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    url = f"""https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/accessList?pretty=true"""

    result = requests.get(
        url,
        headers=headers,
        auth=HTTPDigestAuth(puclic_key, private_key)
    )

    result_dict = {}

    if result.status_code == 200:
        for r in result.json()["results"]:
            if r["cidrBlock"] not in result_dict.keys():
                result_dict.update(
                    {
                        r["ipAddress"]: {
                            "ip": r["cidrBlock"],
                            "comment": r["comment"],
                            "links": r["links"],
                        }
                    }
                )

    if result_dict.keys():
        return {"Success": result_dict}
    else:
        return {"Error": "Ocorreu algum erro recuperando a lista de endereços!"}


def post_new_ip_to_access_list(
    ip: str,
    comment: str,
    puclic_key: str,
    private_key: str,
    project_id: str
) -> str:
    url = f"""https://cloud.mongodb.com/api/atlas/v1.0/groups/{project_id}/accessList?pretty=true"""

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    body = [{"cidrBlock": f"""{ip}/32""", "comment": comment}]

    result = requests.post(
        url,
        headers=headers,
        auth=HTTPDigestAuth(puclic_key, private_key),
        data=json.dumps(body),
    )

    if result.status_code == 200:
        return {"Success": f"""O ip {ip} foi adicionado com sucesso junto do comentario {comment}"""}
    else:
        return {"Error": result.text}


def check_current_public_ip() -> str:
    data = str(requests.get('http://checkip.dyndns.com/').text)
    return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)


whitelist = get_access_lists(PUBLIC_KEY, PRIVATE_KEY, PROJECT_ID_ATLAS)

current_ip = check_current_public_ip()

if "Success" in whitelist:
    same_ip = True if current_ip in whitelist["Success"] else False

if not same_ip:
    result = post_new_ip_to_access_list(
        ip=current_ip,
        comment="Mauro",
        puclic_key=PUBLIC_KEY,
        private_key=PRIVATE_KEY,
        project_id=PROJECT_ID_ATLAS
    )
