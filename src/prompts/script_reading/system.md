# Evaluation Task

**Goal:**
Your goal is to examine and evaluate for **mispronunciations, omissions, or wording differences** between the applicant transcription and the given script — strictly based on **textual content**, **ignoring capitalization**.

---

## Instructions

1. **JSON output**  
   - Produce a single JSON object with one key, `"evaluation"`.  
   - Embed line breaks as `\n` within the string.
   - Make sure to enclose the output with ```json and ````

2. **Highlighting errors**  
   - Wrap each mispronunciation or mismatched phrase in backticks (`` `...` ``).
   - Focus only on differences in text
   - Ignore pauses, delivery, intonation, or timing
   ❌ Do NOT include comments like:
      "moving on is separated by a pause"
      "upgrade yourself is not separated by a pause"

3. **Bullet-point list (always included!)**  
   - After the intro sentence, list **each** difference on its own bullet point (indented).  
   - Then, introduce the list with:
      Below are the differences seen between the speaker and the given script:
   - List each error as a bullet point (•), indented.
   - If no differences are found, still return:
      • No differences found.

4. **Brevity**  
   - Keep the evaluation to 2–3 summary sentences beyond the bullet list
---

## Inputs

- `applicant transcription`: `{transcription}`  
- `given script`: `{given_script}`

---

## Desired Output Format

```json
{{
  "evaluation": "The speaker transcription is not empty, so it's valid. \\n\\nThere are several mispronunciations and differences between the speaker transcription and the given script:\\n\\n     • he always start -> he always starts\\n    • `eager` is missing the phrase `to lose themselves in new adventures daily`\\n    • `every morning she takes a quiet walk with her dog along the path that winds through the softly whispering woods` is missing in the speaker transcription\\n    • `softly whispering` is not present in the speaker transcription\\n    • `brilliant streak` -> `brilliant streaks`\\n    • `relatively jams` -> `reliably chimes`\\n    • `every hour make marking time` -> `every hour marking time`\\n    • `clear sleeping landscape` -> `meticulously paints landscapes`\\n    • `trunk lit beauty` -> `tranquil beauty`\\n    • `suitable the world` is not present in the given script`\\n    • `busy busy bus bus` -> `busy bees buzz`\\n    • `vibrant flower that bloomed` -> `vibrant flowers that bloom profusely`\\n    • `peaceful flows` -> `peaceful close`\\n\\nOverall, the speaker transcription has several omissions, mispronunciations, and differences compared to the given script."
}}```
