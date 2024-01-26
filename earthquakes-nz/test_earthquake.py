from earthquake import main


def test_earthquake():
    naive, rf = main()
    assert rf["te_sc"] < naive["te_sc"]
