this json is a complete analysis of the model's performance on concepts and the patterns used in the solutions to solve the problems.

the orginal json has 4 keys:

- model_progression
- pattern_insights
- concept_pattern_correlations
- concept_difficulty_matrix
- pattern_effectiveness

each of these keys has a dictionary with the model names as the keys.

## model_progression
for each model, there exsits a dictionary with the following keys:

### capability_level
- total_combinations: total number of concept combinations attempted by the model
- difficulty_distribution: number of concept combinations attempted by the model at each difficulty level
- difficulty_percentage: percentage of concept combinations attempted by the model at each difficulty level

### performance_by_difficulty
the difficulty levels are the main keys (very easy, easy, medium, hard, very hard). if the model did not attempt any concept combinations at a certain difficulty level, that difficulty level will not be a key in the dictionary.
each difficulty level has a dictionary with the following keys:
- success_rate: average success rate of the model at the difficulty level
- num_combinations: number of concept combinations attempted by the model at the difficulty level
- concepts: the dictionary of concepts attempted by the model at the difficulty level. the keys are the concepts and the values are the number of times the concept was attempted at the difficulty level.
- successful_patterns: the dictionary of patterns used by the model at the difficulty level. the keys are the patterns and the values are the number of times the pattern was used at the difficulty level.
- failed_patterns: the dictionary of patterns not used by the model at the difficulty level. the keys are the patterns and the values are the number of times the pattern was not used at the difficulty level.

- concept_progression

### concept_progression
the keys are the concepts and the values are the dictionaries with the following keys:
- difficulties_reached: the list of difficulty levels that the model has reached for the concept
- success_by_difficulty: the dictionary of success rates of the model at the difficulty level for the concept. the keys are the difficulty levels and the values are the success rates.
- patterns_by_difficulty: the dictionary of patterns used by the model at the difficulty level for the concept. the keys are the difficulty levels and the values are the patterns.


## concept_pattern_correlations
for each model, there exists a dictionary with the following keys:
each key is a concept and the value is a dictionary with the following keys:
- total_patterns: total number of patterns used by the model for the concept
- pattern_insights: the list of patterns used by the model for the concept. each pattern has the following keys:
    - pattern: the pattern used to solve the concept
    - usage_count: the number of times the pattern was used for the concept
    - success_ratio: the success rate of the model for the pattern
    - by_difficulty: the dictionary of success rates of the model at the difficulty level for the pattern. the keys are the difficulty levels and the values are the success rates. for each difficulty level, there exists a dictionary with the following keys:
        - usage_count: the number of times the pattern was used at the difficulty level
        - success_ratio: the success rate of the model for the pattern at the difficulty level
- difficulty_distribution: the dictionary of difficulty levels that the model has reached for the concept. the keys are the difficulty levels and the values are the number of times the model has reached the difficulty level.
