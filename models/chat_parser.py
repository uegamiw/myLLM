from utils.setting import response_prefix, user_prefix, system_prefix
from utils.setting import deliminator
from typing import List, Dict

class ChatParser:
    def __init__(self, logger):
        self.logger = logger

    def parse(self, text:str) -> List[Dict]:
        print("text: ", text, "delim: ", deliminator)
        delim = f"\n{deliminator}\n"

        if delim in text:
            list_to_return = []
            last_role = None
            text_list = text.split(delim)
            self.logger.debug("number of text_list: %s", len(text_list))
            system_content = ""

            for i, txt in enumerate(text_list):

                if txt.startswith(system_prefix):
                    system_content = txt[len(system_prefix):]
                    last_role = "system"

                elif txt.startswith(user_prefix) and last_role != "user":
                    list_to_return.append({
                        "role": "user",
                        "content": txt[len(user_prefix):]
                    })
                    last_role = "user"

                elif txt.startswith(user_prefix) and last_role == "user":
                    list_to_return[-1]["content"] += txt[len(user_prefix):]
                    last_role = "user"

                elif txt.startswith(response_prefix) and last_role != "assistant":
                    list_to_return.append({
                        "role": "assistant",
                        "content": txt[len(response_prefix):]
                    })
                    last_role = "assistant"

                elif txt.startswith(response_prefix) and last_role == "assistant":
                    list_to_return[-1]["content"] += txt[len(response_prefix):]
                    last_role = "assistant"

                elif last_role == "assistant":
                    list_to_return.append({
                        "role": "user",
                        "content": txt
                    })
                    last_role = "user"

                elif last_role == "user":
                    list_to_return[-1]["content"] += txt
                    last_role = "user"

                else:
                    print("ELSE++++++++++++")
                    print(f"*** {i=}, {txt=}")

            if system_content:
                # place the system content at the first index
                list_to_return.insert(0, {
                    "role": "system",
                    "content": system_content
                })

            self.logger.debug("list_to_return: %s", list_to_return)

            return list_to_return


        else:
            self.logger.debug('single text')
            return [{
                "role": "user",
                "content": text
            }]

    def to_str(self, chat:list) -> str:
        chat_str = ""
        for c in chat:
            if c["role"] == "user":
                chat_str += f"{user_prefix} {c['content']}\n"
            elif c["role"] == "assistant":
                chat_str += f"{response_prefix} {c['content']}\n"
            elif c["role"] == "system":
                chat_str += f"{system_prefix} {c['content']}\n"
            
            chat_str += deliminator + "\n"

        # remove the last deliminator and the newline character
        chat_str = chat_str[:-len(deliminator)-1]

        return chat_str