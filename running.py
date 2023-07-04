from gempyp.sdk.Gempytest import gem_pytest
obj=gem_pytest()

obj.filepath='path of testcase file'

if __name__ == "__main__":
    obj.run_tests()
