from gempyp.sdk.Gempytest import gem_pytest
from testFunction import TestFunction
import os

def test_string_assertion():
    obj=gem_pytest()
    obj.reporter.addRow("Details for assertion expression","Expression is \"loud noises\".upper() == \"LOUD NOISES\"",obj.status.INFO)
    obj.assert_("loud noises".upper() == "LOUD NOISES")

def test_list_assertion():
    obj=gem_pytest()
    obj.reporter.addRow("Details for assertion expression","Expression is list(reversed([1, 2, 3, 4])) == [4, 3, 2, 1]",obj.status.INFO)
    obj.assert_(list(reversed([1, 2, 3, 4])) == [4, 3, 2, 1])


def test_loop_assertion():
    obj=gem_pytest()
    obj.reporter.addRow("Details for assertion expression","Expression is 37 in {num for num in range(2, 50) if not any(num '%' div == 0 for div in range(2, num))}",obj.status.INFO)
    obj.assert_(37 in {
        num
        for num in range(2, 50)
        if not any(num % div == 0 for div in range(2, num))
    })

@gem_pytest.gpytest.fixture
def setup_data():
    data = [1, 2, 3, 4, 5]
    return data

def test_fixture_marker(setup_data):
    obj=gem_pytest()
    obj.reporter.addRow("Details for the testcase","In this testcase fixture marker of pytest is used. Fixtures are used to feed some data to the tests such as database connections, URLs to test and some sort of input data",obj.status.INFO)
    obj.reporter.addRow("Details for the assertion expression","Expression is sum(setup_data) > 15 where setup_data function is called with the help of fixture marker",obj.status.INFO)
    obj.assert_(sum(setup_data) > 15)

@gem_pytest.gpytest.mark.parametrize("num1, num2, expected_sum", [(2, 3, 5)])
def test_integer_parametrize_marker(num1, num2, expected_sum):
    obj=gem_pytest()
    obj.reporter.addRow("Details for the testcase","In this testcase parametrize marker with numbers is used. It checks that a certain input leads to an expected output and it can contain multiple set of values as well",obj.status.INFO)
    obj.reporter.addRow("Details for the assertion expression","Expression is num1 + num2 != expected_sum",obj.status.INFO)
    obj.assert_(num1 + num2 != expected_sum)

@gem_pytest.gpytest.mark.parametrize("string, expected_length", [("Hello", 5)])
def test_string_parametrize_marker(string, expected_length):
    obj=gem_pytest()
    obj.reporter.addRow("Details for the testcase","In this testcase parametrize marker with string is used. It checks that a certain input leads to an expected output and it can contain multiple set of values as well.",obj.status.INFO)
    obj.reporter.addRow("Details for the assertion expression","Expression is len(string) == expected_length",obj.status.INFO)
    obj.assert_(len(string) == expected_length)

def test_ternary_operator_assertion():
    obj=gem_pytest()
    obj.reporter.addRow("Details of assertion","Used ternary operator for assertion.",obj.status.INFO)
    obj.assert_(True if 8+1==9 else False)

def test_function_testcase():
    obj=gem_pytest()
    obj.reporter.addRow("Details of testcase","In this testcase value for assertion is used from the method of another class.",obj.status.INFO)
    obj.assert_(TestFunction.balance==101)

@gem_pytest.gpytest.mark.webtest
def test_custom_Marker():
    obj=gem_pytest()
    obj.reporter.addRow("Details of the testcase","Custom marker is used in this testcase. Custom marker is build in pytest.ini file and we can execute the particular marker as well using pytest -m marker command.",obj.status.PASS)

def test_set_runtype_runmode():
    obj=gem_pytest()
    # os.environ["JEWEL"]="JEWEL_RUN_TYPE"
    # os.environ["JEWEL_JOB"]="JEWEL_RUN_MODE"
    obj.reporter.addRow("Details of the testcase","Run type and run mode is set manually in this testcase",obj.status.PASS)