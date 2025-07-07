from typing import Annotated

from penta.dependencies.depends import Depends

from penta import context
from penta.request import Request

RequestDependency = Annotated[Request, Depends(context.get_request)]
