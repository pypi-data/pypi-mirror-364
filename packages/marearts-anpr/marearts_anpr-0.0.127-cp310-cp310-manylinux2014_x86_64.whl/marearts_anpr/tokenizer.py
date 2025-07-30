

from typing import List, Union
import numpy as np
import json

class CustomTokenizer:
    def __init__(self, vocab: Union[str, List[str]], max_len=20, pad_token="<PAD>", bos_token="<BOS>", sep_token="<SEP>"):
        if isinstance(vocab, str):
            with open(vocab, 'r') as f:
                self.vocab = {word.strip(): i for i, word in enumerate(f.readlines())}
        elif isinstance(vocab, list):
            self.vocab = {word: i for i, word in enumerate(vocab)}
        else:
            raise ValueError("vocab must be either a filepath (str) or a list of words")

        self.pad_token = pad_token
        self.bos_token = bos_token
        self.eos_token = self.sep_token = sep_token
        self.max_len = max_len
        self.inv_vocab = {v: k for k, v in self.vocab.items()}

        # Define a dictionary mapping token types to their IDs
        self.sep_token_id = self.eos_token_id = self.convert_tokens_to_ids([self.eos_token])[0]
        self.bos_token_id = self.convert_tokens_to_ids([self.bos_token])[0]
        self.pad_token_id = self.convert_tokens_to_ids([self.pad_token])[0]

    def save_vocab_to_json(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.vocab, f)
        print(f"Vocabulary saved to {filepath}")

    def save_settings_to_json(self, filepath: str):
        settings = {
            'max_len': self.max_len,
            'pad_token': self.pad_token,
            'bos_token': self.bos_token,
            'eos_token': self.eos_token,
            'sep_token': self.sep_token
        }
        with open(filepath, 'w') as f:
            json.dump(settings, f)
        print(f"Settings saved to {filepath}")

    def tokenize(self, text: str):
        tokens = [c for c in text if c in self.vocab]
        tokens = [self.bos_token] + tokens + [self.sep_token]
        return tokens

    def convert_tokens_to_ids(self, tokens):
        return [self.vocab.get(token, self.vocab.get(self.pad_token)) for token in tokens]
    
    def convert_ids_to_tokens(self, ids):
        return [self.inv_vocab.get(id, self.pad_token) for id in ids]

    def batch_encode_plus(self, batch_text, return_tensors='pt', padding='max_length', truncation=True):
        batch_input_ids = []
        batch_attention_mask = []
        for text in batch_text:
            encoding = self.encode_plus(text, return_tensors, padding, truncation)
            batch_input_ids.append(encoding['input_ids'].squeeze(0)) # add squeeze here
            batch_attention_mask.append(encoding['attention_mask'].squeeze(0)) # add squeeze here
        
        # if return_tensors == 'pt':
        #     batch_input_ids = torch.stack(batch_input_ids)
        #     batch_attention_mask = torch.stack(batch_attention_mask)
        if return_tensors == 'pt':
            batch_input_ids = np.vstack(batch_input_ids)
            batch_attention_mask = np.vstack(batch_attention_mask)

        return {'input_ids': batch_input_ids, 'attention_mask': batch_attention_mask}


    def encode_plus(self, text, return_tensors='pt', padding='max_length', truncation=True):
        # Tokenization
        tokens = self.tokenize(text)
        
        # Truncate to self.max_len if required
        if truncation and len(tokens) > self.max_len:
            tokens = tokens[:self.max_len]
        
        # Convert tokens to ids
        input_ids = self.convert_tokens_to_ids(tokens)

        # Attention mask (1 for tokens, 0 for padding)
        attention_mask = [1 if id != self.vocab.get(self.pad_token) else 0 for id in input_ids]

        # Padding to self.max_len if required
        if padding == 'max_length' and len(input_ids) < self.max_len:
            padding_length = self.max_len - len(input_ids)
            # Pad input_ids
            input_ids = input_ids + [self.vocab[self.pad_token]] * padding_length
            # Pad attention_mask
            attention_mask = attention_mask + [0] * padding_length

        # Return as PyTorch tensors if required
        # if return_tensors == 'pt':
        #     input_ids = torch.tensor([input_ids])
        #     attention_mask = torch.tensor([attention_mask])
        if return_tensors == 'pt':
            input_ids = np.array([input_ids])
            attention_mask = np.array([attention_mask])

        # Return dictionary
        return {'input_ids': input_ids, 'attention_mask': attention_mask}

    def batch_decode(self, batch_ids, skip_special_tokens=True):
    
        if not isinstance(batch_ids, list):
            batch_ids = batch_ids.tolist()  # convert tensor to list only if it's not already a list

        batch_sentences = []
        for ids in batch_ids:
            tokens = [self.inv_vocab.get(id_item, self.pad_token) for id_item in ids]
            if skip_special_tokens:
                tokens = [token for token in tokens if token not in [self.pad_token, self.bos_token, self.eos_token, self.sep_token]]
            sentence = ''.join(tokens)
            batch_sentences.append(sentence)
        return batch_sentences

    def decode(self, ids, skip_special_tokens=True):
        # ids = ids.tolist() if isinstance(ids, torch.Tensor) else ids  # convert tensor to list if needed
        if isinstance(ids, np.ndarray):
            ids = ids.tolist()
        tokens = [self.inv_vocab.get(id_item, self.pad_token) for id_item in ids]
        if skip_special_tokens:
            tokens = [token for token in tokens if token not in [self.pad_token, self.bos_token, self.eos_token, self.sep_token]]
        sentence = ''.join(tokens)
        return sentence
    
def main():
    vocab = ["<PAD>", "<BOS>", "<SEP>", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    with open('vocab.txt', 'w') as f:
        for token in vocab:
            f.write(token + '\n')

    # Initialize your custom tokenizer
    tokenizer = CustomTokenizer(vocab='vocab.txt')

    
    # Test strings with only numeric characters
    text = "1234567890"

    # 1. Test conversion from text to ids
    encoded = tokenizer.encode_plus(text)
    
    # 2. Test conversion from ids to text
    decoded = tokenizer.batch_decode(encoded['input_ids']) # ensure we have a batch dimension

    # 3. Test batch conversion from text to ids
    batch_text = ["1234567890", "0987654321"]
    batch_encoded = tokenizer.batch_encode_plus(batch_text)

    # 4. Test batch conversion from ids to text
    batch_decoded = tokenizer.batch_decode(batch_encoded['input_ids'])


if __name__ == '__main__':
    main()
