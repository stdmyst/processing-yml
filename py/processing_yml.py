from bs4 import (ProcessingInstruction, Doctype, NavigableString,
                 BeautifulSoup as Soup)
from sys import stdin

import requests
import lxml
import json


def pars_yml(tree):
    cache = {}
    result = {}
    
    for sub_tree in tree.contents:
        if isinstance(sub_tree, bs4.element.ProcessingInstruction):
            result["ProcessingInstruction"] = str(sub_tree)
        elif isinstance(sub_tree, bs4.element.Doctype):
            result["Doctype"] = str(sub_tree)
        else:
           if str(sub_tree) != "\n":
               if isinstance(sub_tree, bs4.element.NavigableString):
                   return str(sub_tree)
               if sub_tree.attrs != {}:
                   if sub_tree.name not in result:
                       result[sub_tree.name] = {}
                       cache[sub_tree.name] = 0
                   result[sub_tree.name][cache[sub_tree.name]] = pars_yml(sub_tree)
                   try:
                       result[sub_tree.name][cache[sub_tree.name]]["attrs"] = sub_tree.attrs
                   except TypeError:
                       p = result[sub_tree.name][cache[sub_tree.name]]
                       result[sub_tree.name][cache[sub_tree.name]] = {"attrs": sub_tree.attrs, f"{sub_tree.name}": p}
                   finally:
                       cache[sub_tree.name] += 1
               else:
                   result[sub_tree.name] = pars_yml(sub_tree)
    return result

  
def process_yml(url, count, write_to_json=False):
    if "http" in url:
        try:
            req = requests.get(url)
            req.raise_for_status()
            print(req)
            req.encoding = "UTF-8"
            soup = Soup(req.text, "xml")
        except requests.HTTPError as e:
            print(f'{count}. {e} -> Сannot be processed: "{url}"')
            return
        except Exception as e:
            print(f'{count}. {e} -> Сannot be processed: "{url}"')
            return
    else:
        try:
            with open(url, encoding="UTF-8") as f:
                soup = Soup(f, "xml")
        except OSError as e:
            print(f'{count}. {e} -> Сannot be processed: "{url}"')
            return        
    result = pars_yml(soup)
    
    if write_to_json:
        with open(f"{count}.json", "w", encoding="UTF-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result  
                    

def main():
    print("Enter urls here separated by 'Enter'. Use 'CTRL + Z' at the end:\n")
    urls = stdin.readlines()
    result = {}
    count = 0
    for url in urls:
        if url == "":
            continue
        
        result[count] = process_yml(url.rstrip("\n"), count, write_to_json=True)
        count += 1


if __name__ == "__main__":
    main()
