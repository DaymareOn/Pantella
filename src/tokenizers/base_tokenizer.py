import logging
class base_Tokenizer(): # Tokenizes(only availble for counting the tokens in a string presently for local_models), and parses and formats messages for use with the language model
    def __init__(self,config):
        self.config = config

        # Prommpt Parsing Stuff
        self.BOS_token = self.config.BOS_token # Beginning of string token
        self.EOS_token = self.config.EOS_token # End of string token
        self.message_signifier = config.message_signifier # Signifies the start of a message
        self.message_seperator = config.message_seperator # Seperates messages
        self.message_format = config.message_format # Format of a message. A string of messages formatted like this is what is sent to the language model, typically following by the start of a message from the assistant to generate a response

    def named_parse(self, msg, name): # Parses a string into a message format with the name of the speaker
        if not name:
            name = "[name]"
        if not msg:
            return self.start_message(name) + self.end_message(name)
        parsed_msg = self.message_format
        parsed_msg = parsed_msg.replace("[BOS_token]",self.BOS_token)
        parsed_msg = parsed_msg.replace("[name]",name)
        parsed_msg = parsed_msg.replace("[message_signifier]",self.message_signifier)
        parsed_msg = parsed_msg.replace("[content]",msg)
        parsed_msg = parsed_msg.replace("[EOS_token]",self.EOS_token)
        parsed_msg = parsed_msg.replace("[message_seperator]",self.message_seperator)
        return parsed_msg

    def start_message(self, name): # Returns the start of a message with the name of the speaker
        parsed_msg = self.message_format
        parsed_msg = parsed_msg.split("[content]")[0]
        parsed_msg = parsed_msg.replace("[BOS_token]",self.BOS_token)
        parsed_msg = parsed_msg.replace("[name]",name)
        parsed_msg = parsed_msg.replace("[message_signifier]",self.message_signifier)
        parsed_msg = parsed_msg.replace("[EOS_token]",self.EOS_token)
        parsed_msg = parsed_msg.replace("[message_seperator]",self.message_seperator)
        return parsed_msg

    def end_message(self, name=""): # Returns the end of a message with the name of the speaker (Incase the message format chosen requires the name be on the end for some reason, but it's optional to include the name in the end message)
        parsed_msg = self.message_format
        parsed_msg = parsed_msg.split("[content]")[1]
        parsed_msg = parsed_msg.replace("[BOS_token]",self.BOS_token)
        parsed_msg = parsed_msg.replace("[name]",name)
        parsed_msg = parsed_msg.replace("[message_signifier]",self.message_signifier)
        parsed_msg = parsed_msg.replace("[EOS_token]",self.EOS_token)
        parsed_msg = parsed_msg.replace("[message_seperator]",self.message_seperator)
        return parsed_msg

    def get_string_from_messages(self, messages): # Returns a formatted string from a list of messages
        context = ""
        for message in messages:
            context += self.named_parse(message["content"],message["role"])
        return context

    def num_tokens_from_messages(self, messages): # Returns the number of tokens used by a list of messages
        """Returns the number of tokens used by a list of messages"""
        context = self.get_string_from_messages(messages)
        context += self.start_message(self.config.assistant_name) # Simulate the assistant replying to add a little more to the token count to be safe (this is a bit of a hack, but it should work 99% of the time I think) TODO: Determine if needed
        return self.get_token_count(context)
        
    def get_token_count(self, string):
        logging.info(f"base_Tokenizer.get_token_count() called with string: {string}")
        logging.info(f"You should override this method in your tokenizer class! Please do so! I'm going to crash until you do actually, just to encourage you to do so! <3")
        exit()