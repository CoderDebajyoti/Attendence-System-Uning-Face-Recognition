# Recognition Matching

This document details the similarity scoring and matching operations.

## Predictions
When a face grayscale crop is preprocessed, it is passed to the LBPH model predict function:
```python
label_id, distance = self.recognizer.predict(gray_face)
```
- **`label_id`**: The database ID (`student.id`) of the closest matching student.
- **`distance`**: The Chi-Square distance between the preprocessed face's LBP histogram and the trained student's LBP histograms.

## Normalizing Score
To unify the distance metrics (where lower is a better match) with similarity scores (where higher is a better match), distance is mapped to a similarity score between 0.0 and 1.0:
$$\text{Similarity} = \max\left(0.0, \min\left(1.0, 1.0 - \frac{\text{Distance}}{100.0}\right)\right)$$

## Matching Rules
- If the normalized similarity is greater than or equal to the configured threshold, the match is accepted, and student details are retrieved using `StudentRepository`.
- If similarity is below the threshold, the result is discarded, and the face is marked as `"Unknown"`.
