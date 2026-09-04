import sys

from crew import run

if len(sys.argv) > 1:
    question = " ".join(sys.argv[1:])
else:
    question = input("Vehicle question: ")

result = run(question)

print()
print("Question:", question)
print()
print(result.raw)
