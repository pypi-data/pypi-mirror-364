# KEY = config("328707CA5CA99AB96BF800E0F6CA7B83")


from steam_web_api.steam import Steam
from steam_web_api.steam_types import (
    PublishedFileInfoMatchingFileType,
    PublishedFileQueryType,
)


terraria_app_id = 105600
steam = Steam("32695860B33BD953838E0888B4738021")

# arguments: app_id
test = steam.apps.get_app_details(292030, "UA")
# user = steam.apps.get_user_achievements(76561198040366189, 105600)
# test = steam.users.search_user("regulartetragon")


# user = steam.users.get_user_details("1")
print(test)
# s = 'p\u0443\u0431'

# encoded_str = 'Hello my name is david salazar'
# # Decode the string
# decoded_str = encoded_str.encode('utf-8').decode('unicode_escape')

# print(decoded_str)
key = "32695860B33BD953838E0888B4738021"
file_ids = [2086515808]


# test = steam.apps.file_service_get_details(
#     key=key, publishedfileids=file_ids, includevotes=True
# )
# test_two = steam.users.get_profile_wishlist("76561197993026505")
# print(test_two)
