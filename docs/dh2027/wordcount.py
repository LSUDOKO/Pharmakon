"""DH2027 word count: body text, headings and figure captions inside <main class="count">.
Excludes chart labels, tables, references and the GenAI disclosure (per the call)."""
import html, re, sys
s = open(sys.argv[1] if len(sys.argv) > 1 else "paper.html", encoding="utf-8").read()
main = re.search(r'<main class="count">(.*?)</main>', s, re.S).group(1)
main = re.sub(r'<div class="chart">.*?</div>\s*<figcaption>', '<figcaption>', main, flags=re.S)  # drop chart labels
text = html.unescape(re.sub(r"<[^>]+>", " ", main))
words = re.findall(r"[\w’'–\-.,%()≤]+", text)
words = [w for w in words if re.search(r"\w", w)]
print(len(words))
