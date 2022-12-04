
import sys
sys.path.append("..")
from app import queryutils

def main():
    tokenizer = queryutils.Tokenizer()
    tokens = tokenizer.tokenize('( << { SNOMED:12345 | abcd }) and ({ LOINC:666 | efgh } before { LOINC:777 | efgh }) or ({ LOINC:888} >= 2.0)')
    # for token in tokens:
    #     print(token)

    tokens = tokenizer.parse()
    for token in tokens:
        print(token)

if __name__=='__main__':
    main()
