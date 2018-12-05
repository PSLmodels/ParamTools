import json

from marshmallow.validate import OneOf

class OneOfFromFile(OneOf):

    def __init__(self, choicefilepath, labels=None, error=None):
        with open(choicefilepath, 'r') as f:
            data = json.loads(f.read())
        super().__init__(data["choices"], labels=labels, error=None)