import re
import unicodedata
from bs4 import BeautifulSoup


def populate_inner_dict_spec(inner_dictionary, div):
    result_list = []
    label = div.find('div', {'class': 'text-grey'}).text
    value = div.find('div', {'class': 'text-bold'}).text
    column_dict = {}
    text_value = re.sub(' +', ' ', str.strip(label).replace('\n', ' '))
    column_dict["text"] = unicodedata.normalize("NFKD", text_value)
    column_dict["is_th"] = True
    result_list.append(column_dict)
    column_dict = {}
    text_value = re.sub(' +', ' ', str.strip(value).replace('\n', ' '))
    text_value = unicodedata.normalize("NFKD", text_value)
    if len(text_value) == 0:
        text_value = div.find('div', {'class': 'text-bold'}).img['alt']
    if text_value == 'X' or text_value == 'No':
        text_value = '[icon-no]'
    if text_value == 'Y' or text_value == 'Yes':
        text_value = '[icon-yes]'
    if text_value == '':
        text_value = '[icon-yes]'
    column_dict["text"] = str(text_value)
    column_dict["is_th"] = False
    result_list.append(column_dict)
    inner_dictionary["table"].append(result_list)
    return inner_dictionary


def get_extra_spec(soup, heading_id, table_id):
    inner_dictionary = {}
    inner_dictionary["content"] = None
    spec_content = soup.find('div', {'id': table_id})
    if spec_content is None:
        return None
    inner_dictionary["heading"] = str.strip(soup.find('h2', {'id': heading_id}).text)
    th = spec_content.find_all('td', {'class': 'tdright-extras'})
    td = spec_content.find_all('td', {'class': 'tdleft-extras'})
    if len(th) == len(td):
        inner_dictionary["table"] = []
        for i in range(0, len(th)):
            label = th[i].text
            result_list = []
            column_dict = {}
            column_dict["text"] = re.sub(' +', ' ', str.strip(label).replace('\n', ' '))
            column_dict["is_th"] = True
            result_list.append(column_dict)
            column_dict = {}
            text_value = td[i].img['alt']
            if text_value == 'X' or text_value == 'No':
                text_value = '[icon-no]'
            if text_value == 'Y' or text_value == 'Yes':
                text_value = '[icon-yes]'
            if text_value == '':
                text_value = '[icon-yes]'
            column_dict["text"] = text_value
            column_dict["is_th"] = False
            result_list.append(column_dict)
            inner_dictionary["table"].append(result_list)
    return inner_dictionary


def get_section_data_spec(mob_soup, heading_value, id_=None):
    inner_dictionary = {}
    if heading_value == 'Undercarriage':
        inner_dictionary["type"] = "undercarriageAccordion"
    tech_specs = mob_soup.find('div', {'id': id_})

    if tech_specs is None:
        return None

    head_tag = 'h4'
    if heading_value == 'Axles and tyres' or heading_value == 'Axles and tyres of trailer':
        head_tag = 'h3'
    all_h4s = tech_specs.find_all(head_tag)
    sub_headings = []
    for sub_ in all_h4s:
        sub_headings.append(re.sub(' +', ' ', str.strip(sub_.text)).replace('\n', ''))
    indices = [0]
    for it in re.finditer('<' + head_tag, str(tech_specs)):
        start_ind = it.span()[0]
        indices.append(start_ind)
    indices.append(len(str(tech_specs)))
    inner_dictionary["content"] = None
    inner_dictionary["heading"] = heading_value
    inner_dictionary["table"] = []
    if len(indices) > 2:
        inner_dictionary["section"] = []
    h_counter = 0
    sub_columns = []
    for i in range(1, len(indices)):
        inner_soup = BeautifulSoup(str(tech_specs)[indices[i - 1]: indices[i]], 'lxml')
        spec_divs = inner_soup.find_all('div', {'class': 'overflow-hidden row mx-0 px-0'})
        if i == 1:
            for div in spec_divs:
                inner_dictionary = populate_inner_dict_spec(inner_dictionary, div)
        else:
            if sub_headings[h_counter] == 'Spare tyre':
                continue
            inner_section = {}
            inner_section["content"] = None
            inner_section["heading"] = sub_headings[h_counter]
            inner_section["table"] = []
            if len(spec_divs) == 0 and (
                    heading_value == 'Axles and tyres' or heading_value == 'Axles and tyres of trailer'):
                spec_divs = inner_soup.find_all('div', {'class': 'overflow-hidden'})
                axle_test = inner_soup.find('table', {'class': 'axleTyreStructure'})
                sub_columns.append(axle_test)
            for div in spec_divs:
                inner_section = populate_inner_dict_spec(inner_section, div)

            inner_dictionary["section"].append(inner_section)
            h_counter += 1

    if len(sub_columns) > 0:
        inner_dictionary = populate_axle_dims_spec(inner_dictionary, sub_columns)
    return inner_dictionary


def populate_axle_dims_spec(inner_dictionary, sub_columns):
    dict_keys = ["left_first", "left", "mid", "right_first", "right"]
    for i in range(0, len(inner_dictionary['section'])):
        data = str(sub_columns[i])
        mid_index = data.find('<td class="axlePart">')
        left_data = data[:mid_index]
        right_data = data[mid_index:]

        mid_div = sub_columns[i].find('div', {'class': 'axle-info'})
        mid_value = str(re.sub(' +', ' ', str.strip(mid_div.text)))

        left_values, right_values = [], []
        left_soup = BeautifulSoup(left_data, 'lxml')
        right_soup = BeautifulSoup(right_data, 'lxml')
        col_dict = {}
        left_tds = left_soup.find_all('td', {'class': 'tyreLeft'})
        keys = ['left_first', "left"]
        if len(left_tds) == 1:
            keys = ["left"]
        for k in range(0, len(left_tds)):
            value = re.sub(' +', ' ', str.strip(left_tds[k].find('div').text))
            left_values.append(value)
            col_dict[keys[k]] = value

        col_dict['mid'] = mid_value

        right_tds = right_soup.find_all('td', {'class': 'tyreLeft'})
        keys = ['right_first', "right"]
        if len(right_tds) == 1:
            keys = ["right"]
        for k in range(0, len(right_tds)):
            value = re.sub(' +', ' ', str.strip(right_tds[k].find('div').text))
            right_values.append(value)
            col_dict[keys[k]] = value

        col_dict["type"] = "axle"
        inner_dictionary["section"][i]["table"].append([col_dict])
    return inner_dictionary


def get_about_section_spec(soup, class_name, heading_value):
    inner_dictionary = {}
    tech_specs = soup.find('div', {'class': class_name})
    if tech_specs is None:
        return None
    paragraph = tech_specs.text
    if paragraph:
        inner_dictionary['content'] = str.strip(paragraph)
    inner_dictionary['table'] = None
    inner_dictionary['heading'] = heading_value
    return inner_dictionary
