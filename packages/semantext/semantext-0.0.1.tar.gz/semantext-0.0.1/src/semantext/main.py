import datetime
from typing import Dict, List

# import yaml
from sqlglot import select
from sqlglot.expressions import Column, table_

from semantext.models import (
    FactTable,
    DimTable,
    ChartProperties,
    ChartColumn,
)

from semantext.utils import generate_on_clause, SQLTypes


def generate_sql(
    chart_properties: ChartProperties,
    fact_table: FactTable,
    dims: List[DimTable],
    dialect: str,
):
    fact_cols: Dict[str, SQLTypes] = {
        column.name: column.data_type for column in fact_table.columns
    }
    dim_cols = {
        dim.name: {col.name: col.data_type for col in dim.columns} for dim in dims
    }

    fact_select_cols: List[ChartColumn] = [
        ChartColumn(
            name=metric.column_name,
            table=fact_table.name,
            expression=metric.expression,
            data_type=fact_cols[metric.column_name],
        )
        for metric in chart_properties.metrics
        if metric.table == fact_table.name
    ] + [
        ChartColumn(
            name=dim.column_name,
            table=fact_table.name,
            data_type=fact_cols[dim.column_name],
        )
        for dim in chart_properties.dimensions
        if dim.column_name in fact_cols
    ]
    dims_select_cols: List[ChartColumn] = [
        ChartColumn(
            name=metric.column_name,
            table=metric.table,
            expression=metric.expression,
            data_type=dim_cols[metric.table][metric.column_name],
        )
        for metric in chart_properties.metrics
        if metric.table in dim_cols.keys()
        and metric.column_name in dim_cols[metric.table]
    ] + [
        ChartColumn(
            name=dim.column_name,
            table=dim.table,
            data_type=dim_cols[dim.table][dim.column_name],
        )
        for dim in chart_properties.dimensions
        if dim.table in dim_cols.keys()
    ]
    dims_select_cols = [col for col in dims_select_cols if col not in fact_select_cols]
    final_select = [col.encode_select() for col in fact_select_cols] + [
        col.encode_select() for col in dims_select_cols
    ]
    all_filters = []
    if chart_properties.filters is not None:
        all_filters = [curr_filter for curr_filter in chart_properties.filters]
    all_filters += [
        curr_filter
        for dim in chart_properties.dimensions
        if dim.filters is not None
        for curr_filter in dim.filters
    ]
    fact_where_cols = [
        ChartColumn(
            name=curr_filter.column_name,
            table=fact_table.name,
            operation=curr_filter.operation,
            where_value=curr_filter.value,
            data_type=fact_cols[curr_filter.column_name],
        )
        for curr_filter in all_filters
        if curr_filter.column_name in fact_cols
    ]
    fact_where_cols_names = [curr_filter.name for curr_filter in fact_where_cols]
    dim_where_cols = [
        ChartColumn(
            name=curr_filter.column_name,
            table=curr_filter.table_name,
            operation=curr_filter.operation,
            where_value=curr_filter.value,
            data_type=dim_cols[curr_filter.table_name][curr_filter.column_name],
        )
        for curr_filter in all_filters
        if curr_filter.table_name in dim_cols.keys()
        and curr_filter.column_name not in fact_where_cols_names
    ]

    dim_where_cols = [col for col in dim_where_cols if col not in fact_where_cols]
    query = select(*final_select).from_(table_(fact_table.name))
    if len(dims_select_cols) > 0 or len(dim_where_cols) > 0:
        combined_joined_cols = [col for col in dims_select_cols] + [
            col for col in dim_where_cols
        ]
        for dim_table in {dim.table for dim in combined_joined_cols}:
            dim_in_fact = [
                (
                    dim_fact.join_type,
                    dim_fact.table_name,
                    dim_fact.dim_key,
                    dim_fact.fact_dim_key,
                )
                for dim_fact in fact_table.dimensions
                if dim_fact.name == dim_table
            ][0]
            query = query.join(
                table_(dim_table),
                join_type=dim_in_fact[0],
                on=generate_on_clause(
                    source_table=dim_in_fact[1],
                    source_col=dim_in_fact[2],
                    dest_table=fact_table.name,
                    dest_col=dim_in_fact[3],
                ),
            )
    query = query.group_by(*[col for col in final_select if isinstance(col, Column)])
    combined_where_cols = [
        col.encode_where() for col in fact_where_cols + dim_where_cols
    ]
    if len(combined_where_cols) > 0:
        query = query.where(*combined_where_cols)
    return query.sql(pretty=True, dialect=dialect)


if __name__ == "__main__":
    from pathlib import Path
    import json

    dims = []
    fact = []
    chart_prop = []

    p = Path("./json_examples")
    for curr_file in p.iterdir():
        if "dim" in curr_file.name:
            dims.append(DimTable(**json.loads(curr_file.read_text("utf-8"))))
        elif "fact" in curr_file.name:
            fact.append(FactTable(**json.loads(curr_file.read_text("utf-8"))))
        else:
            chart_prop.append(
                ChartProperties(**json.loads(curr_file.read_text("utf-8")))
            )

    print(
        generate_sql(
            chart_properties=chart_prop[0],
            fact_table=fact[0],
            dims=dims,
            dialect="trino",
        )
    )
