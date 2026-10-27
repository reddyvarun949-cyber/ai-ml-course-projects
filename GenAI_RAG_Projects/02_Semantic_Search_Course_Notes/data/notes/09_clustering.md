# Clustering

Topic: Machine Learning

## Unsupervised learning
In clustering there is no target column. The algorithm groups rows that are similar to each other, and people then
study the groups and give them meaning. Typical uses are customer segmentation, grouping similar documents and finding
unusual records that do not fit any group.

## k-means
k-means needs the number of clusters, k, in advance. It places k centre points, assigns every row to its nearest centre,
moves each centre to the average of its rows, and repeats until the assignments stop changing. Because it uses
distances, features must be scaled first, otherwise the column with the largest numbers dominates. k-means works best
when the groups are roughly round and of similar size.

## Choosing the number of clusters
The **elbow method** plots the within-cluster sum of squares (inertia) for several values of k and looks for the point
where adding clusters stops helping much. The **silhouette score**, from -1 to 1, measures how much closer each point is
to its own cluster than to the next one; higher is better. In business problems, the final choice also depends on how
many groups people can actually act on.

## Other clustering methods
- **Hierarchical (agglomerative) clustering** merges the closest groups step by step and can be drawn as a tree called
  a dendrogram.
- **DBSCAN** finds dense regions of points, does not need k, and labels isolated points as noise. It handles odd
  shapes but is sensitive to its distance setting.

## Interpreting clusters
After clustering, profile each group: compute the average of every feature per cluster and compare it with the overall
average. Give each cluster a short descriptive name only if the profile supports it. Check stability by re-running
with different random seeds; groups that change every run should not drive business decisions.

## Visualising clusters
With many features, reduce them to two dimensions with PCA and colour each point by its cluster. Overlap in the 2D
picture does not always mean overlap in the full space, because the projection loses information.

   

