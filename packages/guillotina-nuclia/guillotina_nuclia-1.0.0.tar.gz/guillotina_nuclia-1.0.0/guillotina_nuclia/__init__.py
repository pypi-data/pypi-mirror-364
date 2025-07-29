from guillotina import configure

import os


app_settings = {
    "load_utilities": {
        "nuclia": {
            "provides": "guillotina_nuclia.utility.INucliaUtility",
            "factory": "guillotina_nuclia.utility.NucliaUtility",
            "settings": {
                "generative_model": os.environ.get("GENERATIVE_MODEL", "chatgpt4o"),
                "nua_key": os.environ.get("NUA_KEY"),
                "max_tokens": os.environ.get("MAX_TOKENS"),
            },
        }
    }
}


def includeme(root, settings):
    configure.scan("guillotina_nuclia.install")
    configure.scan("guillotina_nuclia.utility")
    configure.scan("guillotina_nuclia.api")
    configure.scan("guillotina_nuclia.content")
    configure.scan("guillotina_nuclia.interfaces")
    configure.scan("guillotina_nuclia.permissions")
