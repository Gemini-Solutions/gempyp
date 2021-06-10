def test(a, b):
   """
   Concatenates two strings
   Parameters:
   -----------
   a: Any string object
   b: Any string object
   Returns:
   String object
   Examples:
   ---------
   >>> test('Hello','World')
   'Hello World'
   """
   return a+' '+b


def test():
   print("hello1")

def test2():
   print("hello3")
   return "hello3"

def parse_argument():
    pass

class Pygem():
     def __init__(self):
         #read the conf here
         #create suite level result dictionary here
         #create test level result dictionary here
         pass

     def execute():
         #create a pool of process here
         # create testcase object depending upon type of testcase and call the function run using that object
         
         #update the result for each test case
         #identifying independent task and tasks which have dependency here, create task roster here for executor to run
         pass


if __name__ == "__main__":
    obj = Pygem()
    obj.execute()
