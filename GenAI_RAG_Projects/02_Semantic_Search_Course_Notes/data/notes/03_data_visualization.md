# Data Visualization

Topic: Python & Data

## Why plot your data
A chart can show in seconds what a table of numbers hides: a skewed distribution, an outlier, a trend over time or
two groups that behave differently. Plotting is part of exploratory data analysis (EDA), the step where you get to
know the data before building any model.

## Choosing the right chart
- **Histogram:** the distribution of one numeric column. Shows skew, gaps and unusual values.
- **Box plot:** compares a numeric column across categories and marks outliers as dots beyond the whiskers.
- **Scatter plot:** the relationship between two numeric columns, for example area and price.
- **Line chart:** how a value changes over time.
- **Bar chart:** counts or averages per category.
- **Heatmap:** a grid of colours, often used to show the correlation between every pair of numeric columns.

## Matplotlib and seaborn
Matplotlib is the base plotting library in Python. You create a figure, draw on its axes and add a title and axis
labels. Seaborn is built on Matplotlib and makes statistical charts with one line, for example
`sns.histplot(df["price"])` or `sns.boxplot(data=df, x="city", y="price")`. Seaborn also adds colour by category with
the `hue` argument.

## Making charts readable
Every chart needs a clear title, labelled axes with units, and a sensible scale. Avoid 3D effects and too many colours.
If labels overlap, rotate them or make the figure wider. Sort bars by value so the reader can compare them quickly.
Use colour to highlight one important group rather than to decorate.

## Reading a chart honestly
Check the axis range before drawing conclusions: a bar chart whose y-axis does not start at zero can make a small
difference look huge. Remember that a pattern in a scatter plot shows correlation, not cause. With very many points,
use transparency (`alpha`) so dense areas are visible.

## Quick tip
Call `plt.tight_layout()` before showing a figure so titles and labels do not overlap.
