from utils.setting import response_prefix, user_prefix, system_prefix
from utils.setting import deliminator
from typing import List, Dict

class ChatParser:
    def __init__(self, logger):
        self.logger = logger

    def parse(self, text:str, allow_system:bool = True) -> List[Dict]:
        delim = f"{deliminator}"

        if delim in text:
            list_to_return = []
            last_role = None
            text_list = text.split(delim)
            self.logger.debug("number of text_list: %s", len(text_list))
            system_content = ""

            for i, txt in enumerate(text_list):

                if system_prefix in txt:
                    if allow_system:
                        system_content = txt.replace(system_prefix, "")
                        last_role = "system"

                    else:
                        if last_role == "user":
                            list_to_return[-1]["content"] += txt
                        else:
                            list_to_return.append({
                                "role": "user",
                                "content": txt
                            })
                            last_role = "user"

                elif user_prefix in txt and last_role != "user":
                    content = txt.replace(user_prefix, "")

                    list_to_return.append({
                        "role": "user",
                        "content": content
                    })
                    last_role = "user"

                elif user_prefix in txt and last_role == "user":
                    content = txt.replace(user_prefix, "")
                    list_to_return[-1]["content"] += content
                    last_role = "user"

                elif response_prefix in txt and last_role != "assistant":
                    content = txt.replace(response_prefix, "")
                    list_to_return.append({
                        "role": "assistant",
                        "content": content
                    })
                    last_role = "assistant"

                elif response_prefix in txt and last_role == "assistant":
                    content = txt.replace(response_prefix, "")
                    list_to_return[-1]["content"] += content
                    last_role = "assistant"

                elif last_role == "user":
                    list_to_return[-1]["content"] += txt
                    last_role = "user"

                else:
                    list_to_return.append({
                        "role": "user",
                        "content": txt
                    })
                    last_role = "user"

            if system_content:
                list_to_return.insert(0, {
                    "role": "system",
                    "content": system_content
                })

            self.logger.debug(f"{len(list_to_return)} messages parsed")
            len_user = len([m for m in list_to_return if m['role'] == 'user'])
            len_assistant = len([m for m in list_to_return if m['role'] == 'assistant'])
            len_system = len([m for m in list_to_return if m['role'] == 'system'])
            self.logger.debug(f"User: {len_user}, Assistant: {len_assistant}, System: {len_system}")


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
                c['content'] = c['content'].replace(user_prefix, "")
                chat_str += f"{user_prefix} {c['content']}\n"
            elif c["role"] == "assistant":
                c['content'] = c['content'].replace(response_prefix, "")
                chat_str += f"{response_prefix} {c['content']}\n"
            elif c["role"] == "system":
                c['content'] = c['content'].replace(system_prefix, "")
                chat_str += f"{system_prefix} {c['content']}\n"
            
            chat_str += deliminator + "\n"

        # remove the last deliminator and the newline character
        chat_str = chat_str[:-len(deliminator)-1]

        return chat_str