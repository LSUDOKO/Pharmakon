"""DH2027 word count for main.tex: abstract, body text, headings and figure/table captions.
Excludes tables, TikZ, references, the GenAI disclosure, data-availability note and appendix tables."""
import re, sys
s = open(sys.argv[1] if len(sys.argv) > 1 else "main.tex", encoding="utf-8").read()
s = s[s.index("\\noindent\\colorbox"):s.index("\\section*{Data and code availability}")]
caps = re.findall(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", s)
s = re.sub(r"\\begin\{(table|figure)\}.*?\\end\{\1\}", " ", s, flags=re.S)
s = " ".join([s] + caps)
s = re.sub(r"%.*", " ", s)
s = re.sub(r"\\(cite[tp]?|label|ref|url|href|doi|includegraphics|texttt)\*?(\[[^]]*\])*\{[^}]*\}", " X ", s)
s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
s = re.sub(r"[{}$\\~^_&]", " ", s)
words = [w for w in s.split() if re.search(r"\w", w)]
print(len(words))
