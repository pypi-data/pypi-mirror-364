from inspect import _empty
from json.decoder import JSONDecodeError

import orjson
from pydantic import BaseModel, RootModel


def _json_arbitrary_serializer(obj):
    if type(obj).__str__ is not object.__str__:
        # We need only the custom __str__ method,
        # to not accidentally serialize objects that are not meant to be serialized.
        return str(obj)

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


ORJSON_DEFAULT_OPTIONS = orjson.OPT_SERIALIZE_UUID | orjson.OPT_OMIT_MICROSECONDS


def json_dumps(data, indent=False) -> str:
    if not indent:
        return orjson.dumps(
            data, option=ORJSON_DEFAULT_OPTIONS, default=_json_arbitrary_serializer
        ).decode()

    return orjson.dumps(
        data,
        option=ORJSON_DEFAULT_OPTIONS | orjson.OPT_INDENT_2,
        default=_json_arbitrary_serializer,
    ).decode()


def json_loads(data: str):
    return orjson.loads(data)


def json_decode_error_fragment(e: JSONDecodeError) -> str:
    start = max(0, e.pos - 20)
    end = min(len(e.doc), e.pos + 20)
    msg = e.msg[:-2] if e.msg.endswith(" at") else e.msg

    prev_newline = e.doc.rfind("\n", start, e.pos)
    if prev_newline != -1:
        hint_pointer = "^".rjust(e.colno)
    else:
        hint_pointer = "^".rjust(e.colno - start)

    next_newline = e.doc.find("\n", e.pos, end)
    if next_newline != -1:
        fragment = [
            e.doc[start:next_newline],
            "\n",
            hint_pointer,
            msg,
            e.doc[next_newline:end],
        ]
    else:
        fragment = [
            e.doc[start:end],
            "\n",
            hint_pointer,
            msg,
        ]

    return "".join(fragment)


def arbitrary_type_to_pydantic(type_):
    """
    Convert an arbitrary type to a Pydantic model type.
    Args:
        type_: The type to convert, can be a Pydantic model class or a type hint.
    Returns:
        tuple[type, bool]: The converted type and a boolean indicating if the type is a RootModel.
    """
    is_root = False

    if type_ is not _empty and type_ is not None:
        if not isinstance(type_, type) or not issubclass(type_, BaseModel):
            type_ = RootModel[type_]
            is_root = True
    else:
        type_ = None

    return type_, is_root
