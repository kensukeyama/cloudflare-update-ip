import requests
import json

IPFIY_URL = "https://api.ipify.org"
CLOUDFLARE_URL = "https://api.cloudflare.com/client/v4/"
CLOUDFLARE_BEARER_AUTH = "xxxxxxxxxxxxxxxxxxxxx"
SERVER_NAME = "hogehoge.com"


def getClientIpAddress():
    try:
        response = requests.get(IPFIY_URL)
        response.raise_for_status()
        return response.text

    except requests.exceptions.RequestException as e:
        print("Error : ",e)
        exit(1)

def getZoneIdentifier():
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(CLOUDFLARE_BEARER_AUTH)}

    try: 
        response = requests.get(CLOUDFLARE_URL + "zones", headers=headers)
        response.raise_for_status()
        json_object = response.json()

        for site in json_object["result"]:
            if (site["name"] == SERVER_NAME):
                return site["id"]

        print("Not found your server ({}) on Cloudflare.".format(SERVER_NAME))
        exit(1)

    except requests.exceptions.RequestException as e:
        print("Error : ",e)
        exit(1)

    except TypeError as e:
        print("Error: Not found any servers on Cloudflare.")
        exit(1)
        
def getDnsRecordIdList(zone_id):
    dns_id_list = []
    url = CLOUDFLARE_URL + "zones/{}/dns_records".format(zone_id)
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(CLOUDFLARE_BEARER_AUTH)}
    try: 
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        json_object = response.json()

        for site in json_object["result"]:
            site_dict = {}
            if (site["type"] == "A"):
                site_dict["name"] = site["name"]
                site_dict["id"] = site["id"]
                dns_id_list.append(site_dict.copy())

        if dns_id_list:
            return dns_id_list
        else:
            print("Error: No items for updating IP address.")
            exit(1)

    except requests.exceptions.RequestException as e:
        print("Error : ",e)
        exit(1)

def updateDnsRecord(client_ip, zone_id, dns_id_list):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer {}'.format(CLOUDFLARE_BEARER_AUTH)}
    data = {'content' : client_ip}
    status_list = []
    for address in dns_id_list:
        url = CLOUDFLARE_URL + "zones/{}/dns_records/{}".format(zone_id, address["id"])
        response = requests.patch(url, json = data, headers=headers)
        json_object = response.json()
        status_list.append(json_object)

    return status_list

def showStatus(status, dns_id_list):
    print("== Result ==")
    for site_num in range(len(status)):
        site = status[site_num]
        if (site["result"]): 
            print("Name: " + site["result"]["name"])
            print("Success: {}".format("Success" if site["success"] else "Fail"))
            print("ID: " + site["result"]["id"])
            print("IP: " + site["result"]["content"])
            if (site["errors"]):
                print(len(site["errors"]))
            if (site["messages"]):
                print(site["messages"])
        else:
            print("Name: {}".format(dns_id_list[site_num]["name"]))
            print("Success: {}".format("Success" if site["success"] else "Fail"))
            print("code: {}".format(site["errors"][0]["code"]))
            print("Message: " + site["errors"][0]["message"])
        print()

if __name__ == "__main__":
    client_ip = getClientIpAddress()
    zone_id = getZoneIdentifier()
    dns_id_list = getDnsRecordIdList(zone_id)
    status = updateDnsRecord(client_ip, zone_id, dns_id_list)
    showStatus(status, dns_id_list)

    
