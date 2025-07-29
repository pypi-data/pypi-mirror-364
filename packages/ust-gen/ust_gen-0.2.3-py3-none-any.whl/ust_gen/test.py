from ust_gen.interface import generate_from_file
import json

result = generate_from_file("requirements.pdf")  # or .xlsx

print(json.dumps(result, indent=4))
