# Task
Your task is to examine and evaluate the phrase quote and the applicant interpretation. The interpretation can be in Tagalog.
The applicants is just average person grade them fairly but not critically

# Rules 
1. if the applicant interpretation is just a repetition of the quote please set all criteria score to 1.
2. The JSON string needs to be escaped, such as \\n for line breaks.

# Criteria
Understanding: Grasping the basic meaning of the quote.
Scoring:
1: Misunderstands the quote or fails to explain it.
2: Provides a basic but incomplete understanding.
3: Demonstrates a clear and accurate understanding.

Personal Connection: Relating the quote to personal experiences.
Scoring:
1: No personal connection; fails to relate the quote to personal experiences.
2: Provides a general or superficial connection.
3: Clearly relates the quote to meaningful personal experiences.

Insightfulness: Offering thoughtful or reflective insights about the quote.
Scoring:
1: Lacks depth or thoughtful insights.
2: Provides some insights but lacks depth.
3: Offers thoughtful and reflective insights.

Practical Application: Applying the quote to real-life situations.
Scoring:
1: Fails to apply the quote to real-life situations.
2: Provides a general or vague application.
3: Clearly applies the quote to specific real-life situations.

# Output Format
```json{{
    "understanding": {{
        "score": score,
        "feedback": "The applicant provides a basic understanding of the quote, but it's not entirely clear or accurate. \\nThe interpretation is mostly a paraphrased version of the quote, with some added phrases in Tagalog. \\nThe applicant seems to grasp the general idea that not taking chances can lead to regret, but the explanation is not particularly nuanced or detailed."
    }},
    "personal_connection": {{
        "score": score,
        "feedback": "The applicant fails to provide a personal connection to the quote. \\nThe interpretation is more of a general explanation of the quote's meaning, without any personal anecdotes or experiences that illustrate the quote's significance."
    }},
    "insightfulness": {{
        "score": score,
        "feedback": "The applicant provides some insights, but they lack depth.\\nThe interpretation mostly reiterates the quote's message without offering any new or thought-provoking perspectives. \\nThe applicant's points about taking chances and not regretting them are valid, but they are not particularly original or insightful."
    }},
    "practical_application": {{
        "score": score,
        "feedback": "The applicant attempts to apply the quote to real-life situations, but the application is general and vague. \\nThe interpretation suggests that one should take chances to avoid regret, but it does not provide specific examples or scenarios where this advice can be applied. \\nThe applicant's language is also quite vague, using phrases like `mga chances na yun` (those chances) without specifying what kind of chances they are referring to."```
    }}
}}```

# Input
quote: {quote}
applicant interpretation: {interpretation}
