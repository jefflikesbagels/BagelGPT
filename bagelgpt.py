import os
import openai
from openai import OpenAI

class bagelgpt:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    #Function to get Zero Shot Chat Completion
    def get_chat_completion(self, prompt, context):

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Your name is BagelGPT and you like to answer in rap battles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000,
                #context=context,
            )

            # Print the response object returned by the OpenAI API
            # print(f"OpenAI API response: ", response)                        

            # Extract the text from the last message in the response object
            filtered_response = response.choices[0].message.content
            # print(f"OpenAI API response: ", filtered_response)

            if len(filtered_response) > 1900:        # If the length of the filtered response is greater than 1900, split it into multiple messages using the get_split_message function
                filtered_response = self.get_split_message(filtered_response)
                return filtered_response
            else:                                     # Otherwise, return the filtered response as a single message
                return filtered_response

        # Status Code 400 - Bad Request Error
        except openai.BadRequestError as e:
            print(f"OpenAI API returned a Bad Request Error: {e}")
            return f"OpenAI API returned a Bad Request Error: {e}"

        # Status Code 401 - Authentication Error
        except openai.AuthenticationError as e:
            print(f"OpenAI API returned an Authentication Error: {e}")
            return f"OpenAI API returned an Authentication Error: {e}"

        # Status Code 403 - Permission Denied Error
        except openai.PermissionDeniedError as e:
            print(f"OpenAI API returned a Permission Denied Error: {e}")
            return f"OpenAI API returned a Permission Denied Error: {e}"

        # Status Code 404 - Not Found Error
        except openai.NotFoundError as e:
            print(f"OpenAI API returned a Not Found Error: {e}")
            return f"OpenAI API returned a Not Found Error: {e}"

        # Status Code 422 - Unprocessable Entity Error
        except openai.UnprocessableEntityError as e:
            print(f"OpenAI API returned an Unprocessable Entity Error: {e}")
            return f"OpenAI API returned an Unprocessable Entity Error: {e}"

        # Status Code 429 - Rate Limit Error
        except openai.RateLimitError as e:
            print(f"OpenAI API returned a Rate Limit Error: {e}")
            return f"OpenAI API returned a Rate Limit Error: {e}"
        
        # Status Code >=500 - Internal Server Error
        except openai.InternalServerError as e:
            print(f"OpenAI API returned an Internal Server Error: {e}")
            return f"OpenAI API returned an Internal Server Error: {e}"
        
        # Status Code N/A - API Connection Error
        except openai.InternalServerError as e:
            print(f"OpenAI API returned an API Connection Error: {e}")
            return f"OpenAI API returned an API Connection Error: {e}"
