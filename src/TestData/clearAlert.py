from openJson import jsonR

# Test file that takes in a json file and outputs information onto console
# jsonR stands for json reader

print(jsonR('src/testdata/ddAllertsPayload1.json').loadJson())
print(jsonR('src/testdata/ddAllertsPayload1.json').dumpsJson())

