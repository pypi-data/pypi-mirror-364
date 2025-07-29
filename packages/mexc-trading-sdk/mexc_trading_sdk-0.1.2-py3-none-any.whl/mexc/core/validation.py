from typing_extensions import TypeVar

T = TypeVar('T')

def lazy_validator(Type: type[T]):
  from functools import cache
  @cache
  def adapter():
    from pydantic import TypeAdapter
    return TypeAdapter(Type) # type: ignore
  
  def validate(data: str) -> T:
    return adapter().validate_json(data)

  return validate

DEFAULT_VALIDATE = True
# import importlib.util
# if importlib.util.find_spec('pydantic') is not None:
#   DEFAULT_VALIDATE = True
# else:
#   DEFAULT_VALIDATE = False
