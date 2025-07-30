import re

# Covers most emojis, CJK characters, and symbols
double_width_pattern = re.compile(
    r'[\u2e80-\u2eff\u3000-\u303f\u3400-\u4dbf'
    r'\U00004e00-\U00009fff\U0001f300-\U0001f6ff'
    r'\U0001f900-\U0001f9ff\U0001fa70-\U0001faff]',
    re.UNICODE
)

text = "Hello 😊 世界"
matches = double_width_pattern.findall(text)
print(matches)  # Output: ['😊', '世', '界']
