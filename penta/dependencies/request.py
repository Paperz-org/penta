

from typing import Annotated

from penta.request import Request
from fast_depends import Depends
from penta import context



RequestDependency = Annotated[Request, Depends(context.get_request)]
