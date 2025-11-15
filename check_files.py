import json

f1 = json.load(open('Data/knowledge_base.json'))
f2 = json.load(open('Capstone/Data/knowledge_base.json'))

prog1 = sum(1 for i in f1 if 'program' in i)
prog2 = sum(1 for i in f2 if 'program' in i)

print(f'Data/ has {prog1} program keys')
print(f'Capstone/Data/ has {prog2} program keys')
print(f'Files identical: {f1 == f2}')
