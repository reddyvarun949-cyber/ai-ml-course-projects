# Working with Tables in pandas

Topic: Python & Data

## What a DataFrame is
pandas is the standard Python library for tabular data. A DataFrame is a table with named columns and an index for the
rows, much like a spreadsheet you control with code. Each column is a Series, and every value in a column usually has
the same type. You will use pandas to load, inspect, clean and summarise almost every dataset in this course.

## Loading and inspecting data
Read a CSV file with `df = pd.read_csv("file.csv")`. Then look before you analyse: `df.head()` shows the first rows,
`df.shape` gives the number of rows and columns, `df.info()` lists the column types and how many values are present,
and `df.describe()` summarises the numeric columns with count, mean, standard deviation, minimum and maximum.

## Selecting and filtering
Pick one column with `df["price"]` and several with `df[["price", "city"]]`. Filter rows with a condition:
`df[df["price"] > 100]`. Combine conditions with `&` (and) and `|` (or), putting each condition in brackets. Use
`df.loc[rows, columns]` to select by labels and `df.iloc[rows, columns]` to select by position.

## Missing values and duplicates
Real data has gaps. `df.isna().sum()` counts the missing values in each column. You can drop rows with `dropna`, or
fill gaps with `fillna`, for example with the median. Duplicate rows are found with `df.duplicated()` and removed with
`drop_duplicates`. Always write down how many rows you removed and why, so others can check your work.

## Grouping and aggregating
`groupby` splits the table into groups, applies a calculation to each group and combines the results. For example,
`df.groupby("city")["price"].mean()` gives the average price per city. You can ask for several statistics at once with
`agg`, such as count, mean and maximum. This split-apply-combine pattern answers most "per category" questions.

## Combining tables
`pd.merge(orders, customers, on="customer_id")` joins two tables on a shared key column, like a SQL join. Choose
`how="left"` to keep every row from the first table even when there is no match. `pd.concat` stacks tables on top of
each other when they have the same columns.

## Creating new columns
New columns are often calculated from existing ones: `df["price_per_sqft"] = df["price"] / df["area"]`. Vectorised
operations like this work on the whole column at once and are much faster than looping over rows.
