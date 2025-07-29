import uuid

import pyarrow as pa
import pyarrow.compute as pc

table = pa.Table.from_arrays(
    [
        [uuid.uuid4().bytes, uuid.uuid4().bytes],
    ],
    schema=pa.schema(
        [
            pa.field("id", pa.uuid()),
        ],
    ),
)

unique = pc.count_distinct(table["id"])
