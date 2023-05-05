__version__ = "0.1.1"
# Define the project package
class gempyp:
    pass

# Import the mark module from the mark.py file
from .Annotations import skip
# Make mark module accessible as an attribute of the project package
gempyp.Annotations = skip

