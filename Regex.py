# contains all pre compiled regex that may be needed, is NOT included in BASE

import re

is_link = re.compile(r"^(https?://)?\S+\.\S+(\/?\.?(\S+)?)*$")
contains_link = re.compile(r"(https?://)?\S+\.\S+(\/?\.?(\S+)?)*")


