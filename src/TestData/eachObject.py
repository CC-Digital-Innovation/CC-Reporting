import dd, pure, unity
import json

# Tests for dataclasses made from the json data to see if they are working correctly

# print(dd.jsonDat, pure.jsonDat, unity.jsonDat)
# print(dd.ddObject, pure.pureObject, unity.unityObject)
# print(dd.ddObject.alert_list[0])
# print(pure.pureObject[0])
# print(unity.unityObject.entries[0].content)

# print(dd.ddObject.alert_list[0].to_dict())
# print(pure.pureObject[0].to_dict())
# print(unity.unityObject.entries[0].content.to_dict())

# for each in dd.ddObject.alert_list:
#     print(each.to_dict())
# for each in pure.pureObject:
#     print(each.to_dict())
# for each in unity.unityObject.entries:
#     print(each.content.to_dict())
for each in dd.ddObject.alert_list:
    print(json.dumps(each.to_dict(), indent = 4))
for each in pure.pureObject:
    print(json.dumps(each.to_dict(), indent = 4))
for each in unity.unityObject.entries:
    print(json.dumps(each.content.to_dict(), indent = 4))