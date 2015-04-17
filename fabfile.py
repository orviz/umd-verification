
from fabric.state import output

from umd.products.argus import *
from umd.products.creamce import *
from umd.products.storm import *


#print output
output.status = False
output.stdout = False
output.warnings = False
output.running = False
output.user = False
output.stderr = False
output.aborts = False
output.debug = False
