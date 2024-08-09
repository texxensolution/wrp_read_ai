# Task
Your task is to examine and evaluate for mispronunciations/errors based on applicant transcription and given script.

# Steps
1. make it json compatible and include \\n in string
2. only use ` when highlighting mispronunciations 
3. follow the output format example
4. make the evaluation brief

# Output Format
```json{{
    evaluation: "Here is the evaluation: \\nThe speaker transcription is not empty, so it's valid. \\nThere are several mispronunciations and differences between the speaker transcription and the given script: \\nhe always start -> he always starts\\n`eager` is missing the phrase `to lose themselves in new adventures daily`\\n`every morning she takes a quiet walk with her dog along the path that winds through the softly whispering woods` is missing in the speaker transcription\\n`softly whispering` is not present in the speaker transcription\\n`brilliant streak` -> `brilliant streaks`\\n`relatively jams` -> `reliably chimes`\\n`every hour make marking time` -> `every hour marking time`\\n`clear sleeping landscape` -> `meticulously paints landscapes`\\n`trunk lit beauty` -> `tranquil beauty`\\n`suitable the world` is not present in the given script\\n`busy busy bus bus` -> `busy bees buzz`\\n`vibrant flower that bloomed` -> `vibrant flowers that bloom profusely`\\n`peaceful flows` -> `peaceful close`
\\n\\nOverall, the speaker transcription has several omissions, mispronunciations, and differences in wording compared to the given script."
}}
```

# Input
applicant transcription: {transcription}
given script: {given_script}
