import requests
import json
import os
import re
from typing import Any, List, Dict, Union
from faker import Faker
from .key import API_KEYS
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from googletrans import Translator

fake = Faker()

current_key_index = 0

def _get_next_api_key():
    global current_key_index
    if not API_KEYS:
        raise ValueError("there is a problem with the AI")
    
    key = API_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    return key

def _make_gemini_request(prompt: str) -> str:
    global current_key_index
    
    original_key_index = current_key_index
    attempts = 0
    
    while attempts < len(API_KEYS):
        api_key = _get_next_api_key()
        
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            
            elif response.status_code in [429, 403]:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', '').lower()
                
                if 'quota' in error_message or 'rate' in error_message or 'limit' in error_message:
                    print(f"API key {current_key_index} exceeded limit, trying next key...")
                    attempts += 1
                    continue
                else:
                    raise Exception(f"API request failed with status {response.status_code}: {error_message}")
            
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if attempts == len(API_KEYS) - 1:  # Last attempt
                raise Exception(f"All API keys failed. Last error: {str(e)}")
            attempts += 1
            continue
        except (KeyError, IndexError, ValueError) as e:
            raise Exception(f"Error processing API response: {str(e)}")
    
    raise Exception("All API keys have exceeded their limits or failed. Please check your API keys and try again later.")

def isContext(variable, prompt):    
    full_prompt = f"Evaluate if the variable '{variable}' satisfies the condition: {prompt}. Return only 'True' or 'False' as a string."
    payload = {
        "contents": [{
            "parts": [{
                "text": full_prompt
            }]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    global current_key_index
    original_key_index = current_key_index
    attempts = 0
    
    while attempts < len(API_KEYS):
        api_key = _get_next_api_key()
        
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}",
                headers=headers,
                data=json.dumps(payload)
            )
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                
                if response_text == "True":
                    return True
                elif response_text == "False":
                    return False
                else:
                    raise ValueError(f"Please tell Darrien there is a problem with my AI: {response_text}")
            
            elif response.status_code in [429, 403]:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', '').lower()
                
                if 'quota' in error_message or 'rate' in error_message or 'limit' in error_message:
                    print(f"API key {current_key_index} exceeded limit, trying next key...")
                    attempts += 1
                    continue
                else:
                    raise Exception(f"API request failed with status {response.status_code}: {error_message}")
            
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            if attempts == len(API_KEYS) - 1:  # Last attempt
                raise Exception(f"All API keys failed. Last error: {str(e)}")
            attempts += 1
            continue
        except (KeyError, IndexError, ValueError) as e:
            raise Exception(f"Error processing API response: {str(e)}")
    
    raise Exception("All API keys have exceeded their limits or failed. Please check your API keys and try again later.")

def configure_api_keys(api_keys: List[str]):
    global API_KEYS
    if not api_keys:
        raise ValueError("Please provide at least one API key")
    
    for i, key in enumerate(api_keys):
        if not key or key.strip() == "":
            raise ValueError(f"API key {i+1} is empty")
        if key == "YOUR_API_KEY_1_HERE":
            raise ValueError(f"Please replace placeholder API key {i+1} with your actual API key")
    
    API_KEYS.clear()
    API_KEYS.extend(api_keys)
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_file_path = os.path.join(current_dir, 'key.py')
        
        if not os.path.exists(key_file_path):
            key_file_path = os.path.join(os.path.dirname(__file__), 'key.py')
        
        with open(key_file_path, 'w') as f:
            f.write("# API Keys configuration - Add your API keys here\n")
            f.write("API_KEYS = [\n")
            for key in api_keys:
                f.write(f'    "{key}",\n')
            f.write("]\n")
    except Exception as e:
        print(f"⚠️  Warning: Could not update key.py file: {e}")

def get_api_key_status():
    return {
        "total_keys": len(API_KEYS),
        "current_key_index": current_key_index,
        "keys_configured": all(key != "YOUR_API_KEY_1_HERE" for key in API_KEYS),
        "keys": [key[:10] + "..." if key != "YOUR_API_KEY_1_HERE" else "NOT_CONFIGURED" for key in API_KEYS]
    }

def summarizeText(text: str, max_length: int = 100, method: str = "auto") -> str:
    if max_length < 1:
        raise ValueError("max_length must be at least 1")

    def manual_summary(text, max_length):
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            sentences = list(parser.document.sentences)
            if len(sentences) <= 1:
                # Fallback: take first N words
                words = text.split()
                return " ".join(words[:max_length])
            summarizer = TextRankSummarizer()
            n_sentences = max(1, min(len(sentences), max_length // 20))
            summary = summarizer(parser.document, n_sentences)
            return " ".join(str(sentence) for sentence in summary)
        except Exception as e:
            return None

    if method == "manual":
        result = manual_summary(text, max_length)
        if result:
            return result
        else:
            raise Exception("Manual summarization failed. For best results, use longer text with multiple sentences. Manual mode uses the TextRank/PageRank algorithm.")
    elif method == "llm":
        prompt = f"Summarize the following text to approximately {max_length} words. Ensure the summary is concise, retains key points, and is grammatically correct:\n\n{text}. Do not add additional text or explanations, just return the summary."
        return _make_gemini_request(prompt)
    else:
        result = manual_summary(text, max_length)
        if result:
            return result
        prompt = f"Summarize the following text to approximately {max_length} words. Ensure the summary is concise, retains key points, and is grammatically correct:\n\n{text}. Do not add additional text or explanations, just return the summary."
        return _make_gemini_request(prompt)

def translateText(text: str, target_language: str, method: str = "auto") -> str:
    def manual_translate(text, target_language):
        try:
            translator = Translator()
            result = translator.translate(text, dest=target_language.lower())
            return result.text
        except Exception as e:
            return None
    
    if method == "manual":
        result = manual_translate(text, target_language)
        if result:
            return result
        else:
            raise Exception("Manual translation failed.")
    elif method == "llm":
        prompt = f"Translate the following text to {target_language}. Ensure the translation is accurate and natural:\n\n{text}. Make sure to only print the result of the translation without any additional text."
        return _make_gemini_request(prompt)
    else:
        result = manual_translate(text, target_language)
        if result:
            return result
        prompt = f"Translate the following text to {target_language}. Ensure the translation is accurate and natural:\n\n{text}. Make sure to only print the result of the translation without any additional text."
        return _make_gemini_request(prompt)

def extractEntities(data: Any) -> List[Dict[str, str]]:
    if isinstance(data, (list, dict)):
        input_text = json.dumps(data)
    else:
        input_text = str(data)
    
    prompt = f"Extract named entities (people, places, organizations, etc.) from the following text. Return a valid JSON list of objects with 'entity' and 'type' fields only, e.g., '[{{\"entity\": \"John Doe\", \"type\": \"Person\"}}]'. Do not include any additional text or explanations:\n\n{input_text}"
    response = _make_gemini_request(prompt)
    
    try:
        entities = json.loads(response)
        if not isinstance(entities, list):
            raise ValueError("API response is not a list")
        return entities
    except json.JSONDecodeError:
        json_match = re.search(r'(\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\])', response, re.DOTALL)
        if json_match:
            try:
                entities = json.loads(json_match.group(1))
                if not isinstance(entities, list):
                    raise ValueError("Extracted content is not a list")
                return entities
            except json.JSONDecodeError:
                raise Exception("Failed to parse API response as JSON after extraction attempt")
        raise Exception("Failed to parse API response as JSON")

def extractContext(data: Any, extract_type: str) -> List[str]:
    if isinstance(data, (list, dict)):
        input_text = json.dumps(data)
    else:
        input_text = str(data)
    
    prompt = f"Extract all {extract_type} from the following text/data. Return only a valid JSON array of strings, e.g., ['item1', 'item2']. Do not include any additional text or explanations:\n\n{input_text}"
    response = _make_gemini_request(prompt)
    
    try:
        # Try to parse as JSON array
        result = json.loads(response)
        if not isinstance(result, list):
            raise ValueError("API response is not a list")
        return result
    except json.JSONDecodeError:
        # Try to extract JSON array from response
        json_match = re.search(r'(\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\])', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if not isinstance(result, list):
                    raise ValueError("Extracted content is not a list")
                return result
            except json.JSONDecodeError:
                raise Exception("Failed to parse API response as JSON after extraction attempt")
        raise Exception("Failed to parse API response as JSON")

# Data Generation Functions using Faker
def generate_comment() -> str:
    return fake.text(max_nb_chars=200)

def generate_email_from_username(username: str) -> str:
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'example.com']
    domain = fake.random_element(domains)
    return f"{username}@{domain}"

def generate_fullname() -> str:
    return fake.name()

def generate_paragraph(sentences: int = 3) -> str:
    return fake.text(max_nb_chars=sentences * 100)

def generate_sentence() -> str:
    return fake.sentence()

def generate_username_from_fullname(fullname: str) -> str:
    username = re.sub(r'[^a-zA-Z0-9]', '', fullname.lower())
    if len(username) < 3:
        username += str(fake.random_number(digits=3))
    return username

# Additional useful function
def analyzeSentiment(text: str) -> Dict[str, Union[str, float]]:
    prompt = f"Analyze the sentiment of this text and return a JSON object with 'sentiment' (positive/negative/neutral), 'confidence' (0-1), and 'emotion' (happy, sad, angry, etc.): {text}. Return only valid JSON, no additional text."
    response = _make_gemini_request(prompt)
    
    try:
        result = json.loads(response)
        if not isinstance(result, dict):
            raise ValueError("API response is not a dictionary")
        return result
    except json.JSONDecodeError:
        # Try to extract JSON object from response
        json_match = re.search(r'(\{[^}]*\})', response, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group(1))
                if not isinstance(result, dict):
                    raise ValueError("Extracted content is not a dictionary")
                return result
            except json.JSONDecodeError:
                raise Exception("Failed to parse API response as JSON after extraction attempt")
        raise Exception("Failed to parse API response as JSON")

def autoTag(text: str, max_tags: int = 5) -> list:
    prompt = (
        f"Generate up to {max_tags} relevant tags for the following text. "
        "Return only a valid JSON array of strings, e.g., ['tag1', 'tag2']. "
        "Do not include any additional text or explanations.\n\n{text}"
    )
    response = _make_gemini_request(prompt)
    try:
        tags = json.loads(response)
        if not isinstance(tags, list):
            raise ValueError("API response is not a list")
        return tags
    except json.JSONDecodeError:
        json_match = re.search(r'(\[.*?\])', response, re.DOTALL)
        if json_match:
            try:
                tags = json.loads(json_match.group(1))
                if not isinstance(tags, list):
                    raise ValueError("Extracted content is not a list")
                return tags
            except json.JSONDecodeError:
                raise Exception("Failed to parse API response as JSON after extraction attempt")
        raise Exception("Failed to parse API response as JSON")


def contextualCompare(a: str, b: str, context: str = "general") -> bool:
    prompt = (
        f"Compare the following two items in the context of '{context}'. "
        "Return only 'True' if they are contextually similar/equivalent, or 'False' if not. "
        f"Item 1: {a}\nItem 2: {b}"
    )
    response = _make_gemini_request(prompt)
    response_text = response.strip().lower()
    if response_text == "true":
        return True
    elif response_text == "false":
        return False
    else:
        raise Exception(f"Unexpected LLM response: {response_text}")

def info():
    print("=" * 80)
    print("AKIHIRO LIBRARY - COMPLETE FUNCTION")
    print("=" * 80)
    print()
    
    # 1. isContext
    print("1️⃣ CONTEXTUAL EVALUATION (isContext)")
    print("-" * 50)
    print("Evaluate if a variable satisfies a condition using natural language.")
    print()
    print("📝 Usage:")
    print("   result = isContext(variable, condition)")
    print()
    print("💡 Examples:")
    print("   isContext('John Doe', 'is a person\\'s name') → True")
    print("   isContext(42, 'is a positive number') → True")
    print("   isContext('user@example.com', 'is a valid email') → True")
    print("   isContext([1,2,3], 'contains only numbers') → True")
    print()
    
    # 2. extractContext
    print("2️⃣ CONTEXT EXTRACTION (extractContext)")
    print("-" * 50)
    print("Extract specific information from data using natural language queries.")
    print()
    print("📝 Usage:")
    print("   result = extractContext(data, 'what_to_extract')")
    print()
    print("💡 Examples:")
    print("   extractContext('I have red and blue balloons', 'colors') → ['red', 'blue']")
    print("   extractContext('John works with Sarah', 'names') → ['John', 'Sarah']")
    print("   extractContext('I have 5 apples and 3 oranges', 'numbers') → ['5', '3']")
    print()
    
    # 3. summarizeText
    print("3️⃣ TEXT SUMMARIZATION (summarizeText)")
    print("-" * 50)
    print("Generate concise summaries from long text with customizable length.")
    print()
    print("📝 Usage:")
    print("   summary = summarizeText(text, max_length=100)")
    print()
    print("💡 Examples:")
    print("   summarizeText('Long article text...', max_length=30)")
    print("   → 'AI revolutionizes problem-solving through machine learning...'")
    print()
    
    # 4. translateText
    print("4️⃣ TEXT TRANSLATION (translateText)")
    print("-" * 50)
    print("Translate text to different languages with natural accuracy.")
    print()
    print("📝 Usage:")
    print("   translated = translateText(text, 'target_language')")
    print()
    print("💡 Examples:")
    print("   translateText('Hello world', 'Spanish') → 'Hola mundo'")
    print("   translateText('Thank you', 'Japanese') → 'ありがとう'")
    print("   translateText('I love programming', 'German') → 'Ich liebe das Programmieren'")
    print()
    
    # 5. extractEntities
    print("5️⃣ ENTITY EXTRACTION (extractEntities)")
    print("-" * 50)
    print("Extract and classify named entities from text or structured data.")
    print()
    print("📝 Usage:")
    print("   entities = extractEntities(data)")
    print()
    print("💡 Examples:")
    print("   extractEntities('John works at Google in New York')")
    print("   → [{'entity': 'John', 'type': 'Person'}, {'entity': 'Google', 'type': 'Organization'}]")
    print()
    
    # 6. analyzeSentiment
    print("6️⃣ SENTIMENT ANALYSIS (analyzeSentiment)")
    print("-" * 50)
    print("Analyze the emotional tone and sentiment of text.")
    print()
    print("📝 Usage:")
    print("   sentiment = analyzeSentiment(text)")
    print()
    print("💡 Examples:")
    print("   analyzeSentiment('I love this product!')")
    print("   → {'sentiment': 'positive', 'confidence': 0.95, 'emotion': 'happy'}")
    print()
    
    # 7. Data Generation Functions
    print("7️⃣ DATA GENERATION FUNCTIONS")
    print("-" * 50)
    print("Generate realistic fake data for testing and development.")
    print()
    print("📝 Usage:")
    print("   generate_comment() → Random comment text")
    print("   generate_email_from_username('john_doe') → 'john_doe@gmail.com'")
    print("   generate_fullname() → 'Dr. John Smith'")
    print("   generate_paragraph(sentences=3) → Random paragraph")
    print("   generate_sentence() → Random sentence")
    print("   generate_username_from_fullname('John Smith') → 'johnsmith'")
    print()
    
    print("ADVANCED USAGE")
    print("-" * 50)
    print("Error Handling:")
    print("   try:")
    print("       result = isContext('test', 'condition')")
    print("   except Exception as e:")
    print("       print(f'Error: {e}')")
    print()
    print("Batch Processing:")
    print("   for text in texts:")
    print("       sentiment = analyzeSentiment(text)")
    print("       print(f'Sentiment: {sentiment}')")
    print()
    
    print("📦 INSTALLATION")
    print("-" * 50)
    print("   pip install akihiro")
    print()
    
    print("📚 DOCUMENTATION")
    print("-" * 50)
    print("   Full documentation: https://github.com/Akihiro2004/akihiro")
    print("   PyPI: https://pypi.org/project/akihiro/")
    print()
    
    print("🎯 QUICK START")
    print("-" * 50)
    print("   from akihiro import isContext, extractContext, analyzeSentiment")
    print("   ")
    print("   # Check condition")
    print("   result = isContext('John Doe', 'is a person\\'s name')")
    print("   ")
    print("   # Extract data")
    print("   colors = extractContext('red and blue items', 'colors')")
    print("   ")
    print("   # Analyze sentiment")
    print("   sentiment = analyzeSentiment('I love this!')")
    print()
    