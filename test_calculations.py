from calculations import percentage, classes_can_bunk, classes_to_recover, predict

def test_recovery_example():
    assert classes_to_recover(68, 100, 75) == 28

def test_percentage():
    assert percentage(68, 100) == 68.0

def test_bunk():
    assert classes_can_bunk(80, 100, 75) == 6

def test_prediction():
    assert round(predict(68, 100, 10, 5)["percentage"], 2) == 67.83
