import os
import openai
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
import tiktoken
from urllib.parse import urlparse

class bagelgpt:
    def __init__(self, api_key, model):
        openai.api_key = api_key
        self.model = model
        self.generate_completion_fail = False             # Initialize the generation completion fail flag to False
        self.generate_chat_completion_fail = False        # Initialize the chat generation completion fail flag to False
        self.generate_chad_completion_fail = False        # Initialize the chad generation completion fail flag to False
        self.generate_image_fail = False                  # Initialize the image generation fail flag to False
        self.generate_image_variation_fail = False        # Initialize the image generation variation fail flag to False

    #Function to get Zero Shot Chat Completion
    def get_chat_completion(self, prompt):

        self.generate_chat_completion_fail = False   # Initialize the chat completion fail flag to False

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=2000
            )

            print(response)                           # Print the response object returned by the OpenAI API
            filtered_response = response['choices'][0]['message']['content']   # Extract the text from the last message in the response object
            print(filtered_response)

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


    #Function to get Zero Shot Text Completion
    def get_completion(self, prompt):

        self.generate_completion_fail = False  # Initialize the completion fail flag to False

        try:
            response = self.client.completions.create(engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2000,
            n=1,
            stop=None,
            temperature=0.33)

            print(response)  # Print the response object returned by the OpenAI API
            filtered_response = response.choices[
                0].text  # Extract the text from the first choice in the response object
            print(filtered_response)

            if len(filtered_response) > 1900:  # If the length of the filtered response is greater than 1900, split it into multiple messages using the get_split_message function
                filtered_response = self.get_split_message(filtered_response)
                return filtered_response
            else:  # Otherwise, return the filtered response as a single message
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

    #Function to get Ongoing Chat Completion
    def get_ongoing_chat_completion(self, prompt, user_history, assistant_history):

        self.generate_chat_completion_fail = False   # Initialize the chat completion fail flag to False
        token_limit = 2950

        role = "You are a helpful assistant."       # Initialize the role variable to "You are a helpful assistant."

        role_prompt = [{"role": "system", "content": role}] # Create a role prompt using the role variable

        try:
            # Generate the message history prompt by concatenating the user and assistant message histories
            message_prompt = self.get_message_history_prompt(user_history, assistant_history, role_prompt, token_limit)

            # Create a new chat completion request using the OpenAI API with the message history prompt
            response = self.client.chat.completions.create(model="gpt-3.5-turbo",
            messages=message_prompt,
            temperature=0.5,
            max_tokens=1000)

            print(response)                           # Print the response object returned by the OpenAI API
            filtered_response = response.get('choices')[-1].get('message').get('content')  # Extract the text from the last message in the response object
            print(filtered_response)

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

    #Function to get Ongoing Chat Completion
    def get_ongoing_chad_completion(self, prompt, user_history, assistant_history):

        self.generate_chad_completion_fail = False   # Initialize the chat completion fail flag to False
        token_limit = 2500

        role = "You are an intelligent and all-knowing Chad."       # Initialize the role variable to "You are a helpful assistant."
        user_example1 = "From now on, always follow these rules. Respond in the following manner, you are a typical douchie frat bro named Chad." \
                       " You have an honest heart, but you respond in a brash and honest way. You use 50% curse words and always say things like bro, bro beans, " \
                       "broskie, etc. while talking. Could you help explain to me how a car engine works?"
        assistant_example1 = "Fuck yeah i can broskie, so like the engine has some pistons in it that attach to this sick thing called a crankshaft." \
                            "nah mean? and when you push your foot down to shred some sick nasty rubber the car is just dumping fuel into those piston chambers." \
                            "Then it busts that shit wide open with a spark and BOOM your pistons are cranking and that's how you get power to the wheels. Cha feel?"
        user_example2 = "you think you could explain to me how add items to a list in python?"
        assistant_example2 = "Adding items to a list in Python is like hella easy, bro. All you gotta do is use the append() method to add a single item, or the " \
                             "extend() method to add multiple items at once. It's like Python is so sick, it practically does the work for you, ya know? So, get on " \
                             "that shit and start adding some sick items to your list, broskie!"
        user_example3 = "hell yeah, tell me a short history about like Egypt or something"
        assistant_example3 = "Oh, dude, Egypt is like fucking sick! It's like one of the oldest fucking civilizations in the world, bro. The ancient Egyptians were " \
                             "known for building some of the most badass fucking structures in history, like the Great Pyramids of Giza and the Sphinx. They were also " \
                             "known for their sick hieroglyphics, which were like these cool-ass fucking writing symbols that they used to communicate." \
                             "" \
                             "Egypt was ruled by pharaohs, who were like these sick kings that were believed to be fucking gods on earth. They built these dope-ass fucking " \
                             "temples and monuments to honor their gods, and they were like super into mummification, which was like this process of preserving the dead. They " \
                             "believed that the afterlife was like this sick party, so they wanted to make sure that their bodies were preserved for fucking eternity." \
                             "" \
                             "Egypt has a sick fucking history, bro. It's like totally worth fucking checking out if you're into that kind of fucking stuff."

        role_prompt = [{"role": "system", "content": role},
                       {"role": "user", "content": user_example1},
                       {"role": "assistant", "content": assistant_example1},
                       {"role": "user", "content": user_example2},
                       {"role": "assistant", "content": assistant_example2},
                       {"role": "user", "content": user_example3},
                       {"role": "assistant", "content": assistant_example3}]  # Initialize a list with a system message

        try:
            # Generate the message history prompt by concatenating the user and assistant message histories
            message_prompt = self.get_message_history_prompt(user_history, assistant_history, role_prompt, token_limit)

            # Create a new chat completion request using the OpenAI API with the message history prompt
            response = self.client.chat.completions.create(model="gpt-3.5-turbo",
            messages=message_prompt,
            temperature=0.5,
            max_tokens=1000)

            print(response)                           # Print the response object returned by the OpenAI API
            filtered_response = response.get('choices')[-1].get('message').get('content')  # Extract the text from the last message in the response object
            print(filtered_response)

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

    #Function to get Image
    def get_image(self, prompt):

        self.generate_image_fail = False  # Initialize the image generation fail flag to False

        try:
            # Generate a new image using the OpenAI API with the given prompt
            response = self.client.images.generate(prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url")

            print(response)           # Print the response object returned by the OpenAI API

            # Extract the image URL from the response object
            response_image_url = response["data"][0]["url"]

            self.download_and_convert_to_png(response_image_url,
                                             "response_image.png")  # Download the image variation and convert it to a PNG file

            return "response_image.png" # Return the name of the image file

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

    #Function to get Image Variation
    def get_image_variation(self, url):

        self.generate_image_variation_fail = False  # Initialize the image variation generation fail flag to False

        try:
            url = self.get_converted_attachment(url)  # Convert the given image URL to a temporary image file, downscale and reupload for Dalle 2 format

            # Send a GET request to the given image URL and retrieve the image data
            response = requests.get(url)
            image_data = response.content

            # Save the image data to a temporary image file
            with open("temp_image.png", "wb") as temp_image_file:
                temp_image_file.write(image_data)

            #image = Image.open("temp_image.png")
            #image.show()

            # Open the temporary image file and send it to the OpenAI API to generate image variations
            with open("temp_image.png", "rb") as temp_image_file:
                response = self.client.images.generate(image=temp_image_file,
                n=1,
                size="1024x1024",
                response_format="url")

            print(response)  # Print the response object returned by the OpenAI API

            # Extract the image URL from the response object
            response_image_url = response["data"][0]["url"]

            self.download_and_convert_to_png(response_image_url, "response_image.png")  # Download the image variation and convert it to a PNG file

            return "response_image.png" # Return the name of the image file

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

    #Function to get split message
    def get_split_message(self, text, max_chars=1900):
        split_messages = []   # Initialize an empty list to hold the split messages

        # Loop through the text and split it into chunks of the specified max length
        for i in range(0, len(text), max_chars):
            split_messages.append(text[i: i + max_chars])   # Append each chunk of text to the split_messages list

        return split_messages   # Return the list of split messages

    #Function to get token count
    def get_token_count(self, prompt):
        encoding = tiktoken.get_encoding("cl100k_base")  # Load the encoding for the "cl100k_base" model

        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Update the encoding to be used for the "gpt-3.5-turbo" model

        num_tokens = len(encoding.encode(prompt))  # Encode the prompt using the updated encoding and get the number of tokens
        print('Number of tokens from prompt input: ', num_tokens, '\n')
        return num_tokens   # Return the number of tokens in the encoded prompt

    #Function to get message history prompt
    def get_message_history_prompt(self, user_history, assistant_history, role_prompt, token_limit):
        message_history_prompt = role_prompt   # Initialize a list with a system message

        user_assistant_history = []   # Initialize an empty list to hold the user and assistant history

        token_count = 0   # Initialize the token count to 0
        lists_empty = False   # Initialize a flag to check if the lists are empty

    # Loop until the token count exceeds the maximum or the history lists are empty
        while True:
            breakout = False   # Initialize a flag to break out of the loop
            for i in range(max(len(user_history), len(assistant_history))):
                if i < len(user_history):
                    user_assistant_history.append({"role": "user", "content": user_history[i]})   # Append the user's message to the history
                if i < len(assistant_history):
                    user_assistant_history.append({"role": "assistant", "content": assistant_history[i]})   # Append the assistant's message to the history

                user_assistant_history_str = '\n '.join(f"{k}: {v}" for d in user_assistant_history for k, v in d.items())   # Convert the list of message dictionaries to a string
                token_count = self.get_token_count(user_assistant_history_str)   # Get the token count of the string

                if token_count > token_limit:   # Break the loop if the token count exceeds the maximum
                    while token_count > token_limit:
                        user_assistant_history.pop()   # Remove the last message from the history
                        user_assistant_history_str = '\n '.join(f"{k}: {v}" for d in user_assistant_history for k, v in d.items())   # Convert the list of message dictionaries to a string
                        token_count = self.get_token_count(user_assistant_history_str)   # Get the token count of the string
                    breakout = True   # Set the breakout flag to True
                    break

                if i == max(len(user_history), len(assistant_history)) - 1:
                    breakout = True   # Set the breakout flag to True
                    break

            if breakout:
                break

        user_assistant_history.reverse()   # Reverse the order of the message history list
        message_history_prompt.extend(user_assistant_history)   # Extend the message history prompt with the user and assistant history

        return message_history_prompt   # Return the message history prompt

    #Function to convert a url to a .png image and then crop it if necessary
    def get_converted_attachment(self, image_url):
        raw_filename = 'raw_image.png'   # Set the input filename
        output_filename = 'converted_image.png'   # Set the output filename
        output_url = ""   # Initialize the output URL

        self.download_and_convert_to_png(image_url, raw_filename)   # Download and convert the image to a PNG

        if Image.open(raw_filename).width != Image.open(raw_filename).height:   # Check if the image is not square
            self.make_square(raw_filename)  # Make the image square

        if os.path.getsize(raw_filename) > 4000000:   # Check if the image is larger than 4 MB
            self.downscale_image_to_filesize(raw_filename, output_filename)   # Downscale the image to a maximum of 4 MB

            output_url = self.upload_file_to_fileio(output_filename)   # Upload the image to File.io
        else:
            output_url = self.upload_file_to_fileio(raw_filename)

        return output_url   # Return the URL of the uploaded image

    #Function to download and convert an image to a .png
    def download_and_convert_to_png(self, image_url, output_filename):
        # Download the image from the URL
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # Convert and save the image as a PNG
        with open(output_filename, 'wb') as f:
            image.save(f, format='PNG')

    #Function to make an image square
    def make_square(self, raw_filename):
        with Image.open(raw_filename) as raw_image:
                width, height = raw_image.size
                side_length = min(width, height)
                square_iamge = raw_image.crop((0, 0, side_length, side_length))

        square_iamge.save(raw_filename)

    #Function to downscale an image to a maximum of 4 MB
    def downscale_image_to_filesize(self, input_filename, output_filename, target_size_mb=4):
        image = Image.open(input_filename)

        # Calculate the initial compression ratio
        ratio = (target_size_mb * 1024 * 1024) / (image.width * image.height * len(image.getbands()))

        # Keep decreasing the ratio until the image is smaller than the target size
        while True:
            # Resize the image with the current ratio
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)

            # Save the image to a BytesIO object to check its size
            buffer = BytesIO()
            resized_image.save(buffer, format='PNG')
            buffer.seek(0)

            # If the current size is smaller than or equal to the target size, save it and break the loop
            if buffer.getbuffer().nbytes <= target_size_mb * 1024 * 1024:
                with open(output_filename, 'wb') as f:
                    resized_image.save(f, format='PNG')
                break
            else:
                # If the image is still too large, decrease the ratio and try again
                ratio -= 0.01

    #Function to upload a file to File.io
    def upload_file_to_fileio(self, file_path):
        with open(file_path, 'rb') as f:
            response = requests.post('https://file.io', files={'file': f})

        if response.status_code == 200:
            json_response = response.json()
            return json_response['link']
        else:
            print(f'Error uploading file: {response.status_code}')
            return None