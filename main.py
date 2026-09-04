import sys

from crew import run

# Vehicle prices come back with a rupee sign, which the default Windows console
# encoding cannot represent. Without this, printing the answer raises.
for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8", errors="replace")

if len(sys.argv) > 1:
    question = " ".join(sys.argv[1:])
else:
    question = input("Vehicle question: ")

result = run(question)

print()
print("Question:", question)
print()
print(result.raw)
