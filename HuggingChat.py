from hugchat import hugchat
from hugchat.login import Login


email = "mihorag447@vikinoko.com"
passwd = "IamstewpedW!23@"
# Log in to huggingface and grant authorization to huggingchat
sign = Login(email, passwd)
cookies = sign.login()

# # Save cookies to the local directory
cookie_path_dir = "App/utils/cookies"
sign.saveCookiesToDir(cookie_path_dir)

# Load cookies when you restart your program:
# sign = login(email, None)
cookies = sign.loadCookiesFromDir(cookie_path_dir)
print(cookies.get_dict())

# Create a ChatBot
chatbot = hugchat.ChatBot(
    cookies={
        "hf-chat": "831aa60e-832c-4bc8-9609-feee1a63cabd",
        "token": "kybodoshVPnQLMIerSDRJjgLMnsoldLxjyoYHTdTsNWGXmOmdiGmQqjIXHDbwulMYnRqpnHkhwTcebrfTMxwXcVjLOfcPShwAJGzWwDTXjnxewKGgHICpagCZhnotfKA",
    },
    system_prompt="You are  a true creative master genius and a great story teller that keeps the viewer/listener engauged. Make sure that you narrate the sequence of events properly so that the listener can understand. Use smart/insiteful quotes from the book. Don't speak to the viewers just tell the story accurately. Each scene should carry one topic and if the narration is long add more image_prompts, by default a short naration should have  2 image_prompts",
)

model_index = 0
models = chatbot.get_available_llm_models()
print(chatbot.active_model)
if not chatbot.active_model.name == "CohereForAI/c4ai-command-r-plus":
    for model in models:
        print(model.name, "switching..")
        if model.name == "CohereForAI/c4ai-command-r-plus":
            model_index = models.index(model)
            chatbot.switch_llm(model_index)
            break
print(chatbot.current_conversation.system_prompt)
