import os
import openai
import time
import logging

class OpenAITestGenerator:
    def __init__(
        self,
        api_key,
        strategy="cot",
        evaluation_strategy="value",
        api_base="",
        api_model="",
    ):
        if api_key == "" or api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY", "")
        if api_key != "":
            openai.api_key = api_key
        else:
            raise Exception("Please provide OpenAI API key")

        if api_base == "" or api_base is None:
            api_base = os.environ.get("OPENAI_API_BASE", "")
        if api_base != "":
            openai.api_base = api_base
            print(f'Using custom api_base {api_base}')

        if api_model == "" or api_model is None:
            api_model = os.environ.get("OPENAI_API_MODEL", "")
        if api_model != "":
            self.api_model = api_model
        else:
            self.api_model = "text-davinci-003"
        print(f'Using api_model {self.api_model}')

        self.use_chat_api = 'gpt' in self.api_model
        self.strategy = strategy
        self.evaluation_strategy = evaluation_strategy

    def run(
        self,
        prompt,
        max_tokens,
        temperature,
        k=1,
        stop=None
    ):
        while True:
            try:
                if self.use_chat_api:
                    messages = [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                    response = openai.ChatCompletion.create(
                        model=self.api_model,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                else:
                    response = openai.Completion.create(
                        engine=self.api_model,
                        prompt=prompt,
                        n=k,
                        max_tokens=max_tokens,
                        stop=stop,
                        temperature=temperature,
                    )
                with open("openai.logs", 'a') as log_file:
                    log_file.write("\n" + "-----------" + '\n' + "Prompt : " + prompt + "\n")
                return response
            except openai.error.RateLimitError as e:
                sleep_duration = os.environ.get("OPENAI_RATE_TIMEOUT", 30)
                print(f'{str(e)}, sleep for {sleep_duration}s, set it by env OPENAI_RATE_TIMEOUT')
                time.sleep(sleep_duration)

    def openai_choice2text_handler(self, choice):
        if self.use_chat_api:
            text = choice['message']['content']
        else:
            text = choice.text.strip()
        return text

    def generate_text(self, prompt, k):
        if self.use_chat_api:
            thoughts = []
            for _ in range(k):
                response = self.run(prompt, 400, 0.5, k)
                text = self.openai_choice2text_handler(response.choices[0])
                thoughts += [text]
            return thoughts
        else:
            response = self.run(prompt, 300, 0.5, k)
            thoughts = [self.openai_choice2text_handler(choice) for choice in response.choices]
            return thoughts
