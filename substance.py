import urllib.request, json
import pubchempy as pcp
from bs4 import BeautifulSoup
import pre_processing
import logging


def get_cid_of(potential_substance):
    if potential_substance:
        try:
            data = pcp.get_compounds(potential_substance, 'name')
        except:
            logging.error("Error while searching for CID on PubChem.")
            return None

        if data:
            data = data[0]
            return data.cid
        else:
            logging.warning("No CID from PubChem found.")
            return None
    else:
        logging.error("No CID from PubChem found.")
        return None


def request_substance_json(substance_cid):
    url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/" + substance_cid + "/JSON/"
    try:
        with urllib.request.urlopen(url, timeout=20) as url:
            data = json.loads(url.read())
    except ValueError:
        logging.error('Value error while loading substance json data!')
        return None
    except urllib.error.URLError as err:
        logging.error(err)
        return None

    return data


def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


def get_hazardous_attribute_of(substance_cid):
    substance_data = request_substance_json(substance_cid)

    if not substance_data:
        logging.error('No substance data available!')
        return []

    hazardous_attributes = []
    section = substance_data['Record']['Section']
    for toc_heading in section:
        if toc_heading['TOCHeading'] == 'Safety and Hazards':
            node = toc_heading['Section']
            try:
                node_list = node[0]['Section'][0]['Information'][0]['Value']['StringWithMarkup'][0]
                for nd in node_list['Markup']:
                    if not has_numbers(nd['Extra']):
                        hazardous_attributes.append(nd['Extra'])
            except:
                logging.warning('Hazardous attributes not found')
                return []

    return hazardous_attributes


def get_name_from_cas(cas):
    url = "https://chem.nlm.nih.gov/chemidplus/number/" + cas
    try:
        with urllib.request.urlopen(url, timeout=20) as url:
            data = url.read()
            soup = BeautifulSoup(data)
            element = soup.find_all("div", class_="lc2-left")[0].text.strip()
            name = str(element.split("RN")[0])
            name = name.split('[', 1)[0].split(None, 1)[1].lower().replace(" ", "_").rstrip('_')
            #name2 = name.split(None, 1)[1].lower()
            #name2 = name2.split(None, 1)[1].lower()
            #name2 = name.replace(" ", "_").rstrip('_')
            proc_name = pre_processing.snake2camel(name)
            return proc_name

    except urllib.error.URLError as err:
        logging.error(err)
        return None
