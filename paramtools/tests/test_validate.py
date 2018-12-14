import json
import os

import pytest

from paramtools.validate import OneOfFromFile


@pytest.fixture
def choicefile(tmpdir):
    choicedict = {"choices": ["hey", "there"]}
    p = tmpdir.join("test.json")
    p.write(json.dumps(choicedict))
    return os.path.join(p.dirname, "test.json")


def test_oneoffromfile(choicefile):
    r = OneOfFromFile(choicefile)
    assert r.choices == ["hey", "there"]
