from typing import Dict, List


def xmlToDict(root) -> Dict:
    Result = {}
    for element in root:
        # if element has children
        if len(element) != 0:
            # check if the element childern are list or dict

            # if element has only 1 children
            # or if first 2 elements are not same we treat them as dict
            if len(element) == 1 or element[0].tag.upper() != element[1].tag.upper():
                Result[element.tag.upper()] = xmlToDict(element)

            # we treat them as list
            else:
                Result[element.tag.upper()] = xmlToList(element)

        # if the element doesnot have any children
        else:
            Result[element.tag.upper()] = element.text
    return Result


def xmlToList(root) -> List:
    Result = []

    for element in root:
        # if element has children
        # same logic as xmlToDict
        if len(element) != 0:
            if len(element) == 1 or element[0].tag != element[1].tag:
                Result.append(xmlToDict(element))

            # we treat them as list
            else:
                Result.append(xmlToList(element))

        else:
            Result.append(element.text)

    return Result
