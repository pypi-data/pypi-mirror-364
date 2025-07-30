import teradataml as tdml

def randn(num_rows=1000, num_cols=10, colnames=None, row_id=False):
    """
    Generate a Teradata DataFrame with random standard (Mean=0, VAR=SD=1) normally distributed columns.

    Parameters
    ----------
    num_rows : int, optional, default = 100
        Number of rows to generate.

    num_cols : int, optional, default = 1
        Number of random normal columns (ignored if `colnames` is provided).

    colnames : list of str, optional
        Custom column names. If given, overrides `num_cols`.

    row_id : bool, optional, default = False
        Whether to include a unique row ID ("row_id" )column using TD_FillRowID.

    Returns
    -------
    teradataml DataFrame
        A DataFrame with normally distributed random columns (and optional row ID).
    """
    if colnames:
        cols = colnames
    else:
        cols = [f"x_{i}" for i in range(num_cols)]

    gen_exprs = []
    for col in cols:
        expr = (
            "SQRT(-2.0 * LN(CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295))"
            "* COS(2.0 * 3.14159265358979323846 * CAST((RANDOM(-2147483648, 2147483647)+2147483648) AS FLOAT)/4294967295)"
        )
        gen_exprs.append(f"{expr} AS {col}")

    gen_exprs = '\n, '.join(gen_exprs)
    inner_query = f"SELECT myone FROM (SELECT 1 as myone) t SAMPLE WITH REPLACEMENT {num_rows}"
    main_query = f"SELECT \n{gen_exprs} \nFROM ({inner_query}) t"

    if row_id:
        final_query = f'''
        WITH random_data AS (
            {main_query}
        )
        SELECT row_id, {", ".join(cols)}  FROM TD_FillRowID (
            ON random_data AS InputTable
            USING RowIDColumnName ('row_id')
        ) AS dt
        '''
    else:
        final_query = main_query

    return tdml.DataFrame.from_query(final_query)
