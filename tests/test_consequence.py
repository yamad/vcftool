import json

from vcftool.vcfparse import most_serious_consequence


def test_basic():
    consequences = {
        "missense_variant": {},
        "downstream_gene_variant": {},
        "stop_lost": {},
    }
    assert most_serious_consequence(consequences) == "stop_lost"


def test_single_entry():
    consequences = {"missense_variant": {}}
    assert most_serious_consequence(consequences) == "missense_variant"


def test_empty():
    consequences = {}
    assert most_serious_consequence(consequences, "MISSING") == "MISSING"


def test_null_api():
    api_response = '{ "consequence": null }'
    json_res = json.loads(api_response)
    assert most_serious_consequence(json_res["consequence"], "MISSING") == "MISSING"
