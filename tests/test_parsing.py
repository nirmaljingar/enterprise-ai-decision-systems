from eads.decision.parsing import parse_action


def test_parses_order_quantity_and_region():
    action = parse_action("order_quantity=250 region=eu")
    assert action.type == "order"
    assert action.quantity == 250
    assert action.region == "EU"
    assert action.parsed


def test_region_default_applies_when_absent():
    action = parse_action("order_quantity=10", region_default="US")
    assert action.region == "US"


def test_parses_route_and_mitigation():
    assert parse_action("route=B").type == "route"
    assert parse_action("route=B").label == "B"
    assert parse_action("mitigation=hold_order").type == "mitigation"


def test_unknown_output_is_not_parsed():
    action = parse_action("ship 999999 units to RU")
    assert action.type == "unknown"
    assert not action.parsed
    assert action.quantity is None
