
from sqlalchemy.ext.declarative import DeclarativeMeta
from dataclasses import dataclass, asdict
from sqlalchemy import inspect
import decimal
from datetime import date, datetime, time, timedelta
from collections.abc import Iterable
from sqlalchemy.orm.collections import InstrumentedList
from uuid import UUID
from enum import Enum

def json_serial(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    elif isinstance(obj, timedelta):
        return str(obj)
    elif isinstance(type(obj), DeclarativeMeta):  # Handle all SQLAlchemy objects
        return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    elif isinstance(obj, UUID):  # Handle UUID objects.
        return str(obj)
    elif isinstance(obj, decimal.Decimal):  # Handle Decimal objects.
        return float(obj)
    elif isinstance(obj, Enum):  # Handle Enum objects.
        return obj.name
    elif isinstance(obj, InstrumentedList):  # Handle SQLAlchemy relationship objects.
        return [serialize(elem) for elem in obj]
    elif isinstance(obj, Iterable):
        return [serialize(item) for item in obj]
    raise TypeError("Type %s not serializable" % type(obj)) 

def serialize(obj):
    if type(obj) is list:
        return [serialize(i) for i in obj]
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    elif isinstance(obj, dict):
        obj = obj.copy()
        for key in obj:
            obj[key] = serialize(obj[key])
        return obj
    else:
        return json_serial(obj)