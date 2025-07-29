import pyarrow as pa
import pyarrow.compute as pc

table = pa.Table.from_arrays(
    [
        ["{}", "[1,2,3]"],
    ],
    schema=pa.schema(
        [
            pa.field("json_data", pa.json_(pa.string())),
        ],
    ),
)

bounds = pc.min_max(table["json_data"])
