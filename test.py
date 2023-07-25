from testFunction import TestFunction
import pytest

def test_string_assertion():
    assert ("loud noises".upper() == "LOUD NOISES")

def test_list_assertion():
    assert (list(reversed([1, 2, 3, 4])) == [4, 3, 2, 1])


def test_loop_assertion():
    assert (37 in {
        num
        for num in range(2, 50)
        if not any(num % div == 0 for div in range(2, num))
    })

@pytest.fixture
def setup_data():
    data = [1, 2, 3, 4, 5]
    return data

def test_fixture_marker(setup_data):
    assert (sum(setup_data) > 15)

@pytest.mark.parametrize("num1, num2, expected_sum", [(2, 3, 5), (1,1,2), (2,0,0)])
def test_integer_parametrize_marker(num1, num2, expected_sum):
    assert (num1 + num2 != expected_sum)

@pytest.mark.parametrize("string, expected_length", [("Hello", 5),("World",9),("Too",3)])
def test_string_parametrize_marker(string, expected_length):
    assert (len(string) == expected_length)

def test_ternary_operator_assertion():
    assert (True if 8+1==9 else False)

def test_function_testcase():
    assert (TestFunction.balance==101)

@pytest.mark.webtest
def test_custom_Marker():
    assert 9+1==8
