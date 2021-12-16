from typing import Dict, List


def xmlToDict(root) -> Dict:
    Result = {}
    for element in root:
        # if element has children
        if element:
            # check if the element childern are list or dict

            # if element has only 1 children
            # or if first 2 elements are not same we treat them as dict
            if (len(element) == 1 or element[0].tag != element[1].tag):
                Result[element.tag] = xmlToDict(element)
            
            # we treat them as list
            else: 
                Result[element.tag] = xmlToList(element)

        # if the element doesnot have any children
        if not element:
            Result[element.tag] = element.text
    return Result





def xmlToList(root) -> List:
    Result = []

    for element in root:
        # if element has children
        # same logic as xmlToDict
        if element:
            if (len(element) == 1 or element[0].tag != element[1].tag):
                Result.append(xmlToDict(element))
            
            # we treat them as list
            else: 
                Result.append(xmlToList(element))

        
        if not element:
            Result.append(element.text)
        
    return Result