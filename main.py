import requests
from bs4 import BeautifulSoup
import re
import json
import os

websiteURL = "https://www.mohfw.gov.in/"

content = {"timestamp": '',
           "totalPassengersScreened": 0,
           "totalConfirmedCases": 0,
           "totalConfirmedIndianNationals": 0,
           "totalConfirmedForeignNationals": 0,
           "totalCuredOrDischarded": 0,
           "totalDeaths": 0,
           "result": {}
           }

item = {"state": '',
        "stateTotalConfirmedIndianNationals": 0,
        "stateTotalConfirmedForeignNationals": 0,
        "curedOrDischarged": 0,
        "deaths": 0,
        "stateTotalCases": 0
        }

itemList = ["index", "state", "stateTotalConfirmedIndianNationals",
            "stateTotalConfirmedForeignNationals",
            "curedOrDischarged", "deaths", "stateTotalCases"]

def getLastUpdatedTimeStamp(soup):
    res = ""
    element = soup.body.findAll(text=re.compile('including foreign nationals, as on'))
    parsed_string = element[0].split("on")[-1]
    for i in range(len(parsed_string) + 1):
        if (not parsed_string[i].isdigit()):
            i += 1
            continue
        if (parsed_string[i].isdigit()):
            while (parsed_string[i] != 'M' and i < len(parsed_string)):
                res += parsed_string[i]
                i += 1
            res += 'M'
            return res
    return res

def getTotalPassengersScreened(soup):
    res = ""
    element = soup.body.findAll(text=re.compile('Total number of passengers'))
    parsed_string = element[0]
    for i in range(len(parsed_string) + 1):
        if (not parsed_string[i].isdigit()):
            i += 1
            continue
        if (parsed_string[i].isdigit()):
            while (parsed_string[i].isdigit() or parsed_string[i] == ','):
                if (parsed_string[i] != ','):
                    res += parsed_string[i]
                i += 1
            return int(res)
    return int(res)


def getTotalConfirmedCases(soup):
    res = ""
    element = soup.body.findAll(text=re.compile('Total number of confirmed'))
    parsed_string = element[0].split(":")[1]
    for i in range(len(parsed_string)):
        if (not parsed_string[i].isdigit()):
            i += 1
            continue
        if (parsed_string[i].isdigit()):
            while (parsed_string[i].isdigit() or parsed_string[i] == ','):
                if (parsed_string[i] != ','):
                    res += parsed_string[i]
                i += 1
            return int(res)
    return res

def parseTableData(soup, data):
    table = soup.find('table')
    table_rows = table.find_all('tr')

    header = table_rows[0].find_all('td')

    index = 1
    data['result'] = {}

    for tr in table_rows[1:-1]:
        td = tr.find_all('td')
        i = 1
        data['result'][index] = item
        for i in range(len(td)):
            if(td[i].text.isdigit()):
                data['result'][index][itemList[i]] = int(td[i].text)
            else:
                data['result'][index][itemList[i]] = td[i].text
        data['result'][index]['stateTotalCases'] = data['result'][index]['stateTotalConfirmedIndianNationals'] + data['result'][index]['stateTotalConfirmedForeignNationals']
        data['totalConfirmedIndianNationals'] += data['result'][index]['stateTotalConfirmedIndianNationals']
        data['totalConfirmedForeignNationals'] += data['result'][index]['stateTotalConfirmedForeignNationals']
        data['totalCuredOrDischarded'] += data['result'][index]['curedOrDischarged']
        data['totalDeaths'] += data['result'][index]['deaths']
        index +=1

def generateOutputFile(soup, data):
    filename = "covid_"
    extension = ".json"

    output_file = filename + getLastUpdatedTimeStamp(soup) + extension

    with open(output_file, 'w') as outfile:
        json.dump(data, outfile)

    write_json(data, output_file)

def getResponseData():
    response = requests.get(websiteURL)
    response_text = response.text
    return response_text

def jsonBuilder():
    soup = BeautifulSoup(getResponseData(), 'lxml')
    data = content
    data['timestamp'] = getLastUpdatedTimeStamp(soup)
    data['totalPassengersScreened'] = getTotalPassengersScreened(soup)
    data['totalConfirmedCases'] = getTotalConfirmedCases(soup)
    parseTableData(soup, data)
    print(data)
    generateOutputFile(soup, data)
    return json.dump(data)


def write_json(data, filename):
    DATAFOLDER = os.path.join(os.curdir, "data")
    try:
        if not os.path.isdir(DATAFOLDER):
            os.mkdir(DATAFOLDER)

        if not os.path.isfile(DATAFOLDER):
            open(os.path.join(DATAFOLDER, filename), "w").close()

        with open(os.path.join(DATAFOLDER, filename), "w") as f:
            json.dump(data, f)
        return True
    except Exception as e:
        print(e)
        return False

def main():
    jsonBuilder()

if __name__ == '__main__':
    main()
