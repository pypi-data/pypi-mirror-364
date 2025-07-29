# AccessibleTranslator Python SDK

Official Python SDK for AccessibleTranslator - automated cognitive accessibility and text simplification powered by Claude AI.

## What is AccessibleTranslator?

AccessibleTranslator transforms complex text into accessible formats for people with diverse cognitive needs. Our AI-powered platform offers 50+ specialized transformations to make content more understandable and cognitively accessible, while preserving meaning.

**Perfect for:**
- **API Partners**: Digital agencies, accessibility consultants, CMS plugin developers
- **Enterprise Clients**: Large businesses expanding accessibility at scale
- **Developers**: Building cognitively accessible applications and services
- **Organizations**: Going beyond compliance to reach cognitively diverse audiences

## Installation

```bash
pip install accessibletranslator
```

## Quick start

The AccessibleTranslator SDK uses async/await patterns for optimal performance when processing text. All API operations are asynchronous to handle the AI processing time efficiently.

### Basic setup

First, you'll need an API key from your AccessibleTranslator account. The SDK uses this key to authenticate all requests:

```python
import asyncio
import accessibletranslator
from accessibletranslator.rest import ApiException

# Configure API key authentication
configuration = accessibletranslator.Configuration(
    api_key={'ApiKeyAuth': 'sk_your_api_key_here'}
)

async def main():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        # Create API instances
        translation_api = accessibletranslator.TranslationApi(api_client)
        user_api = accessibletranslator.UserManagementApi(api_client)
        
        # Your code here
        pass

# Run async function
asyncio.run(main())
```

### Simple text translation

This example shows the core functionality: transforming complex text into more accessible versions. We're using two basic transformations that work well together:

```python
async def translate_text():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        
        # Create translation request
        request = accessibletranslator.TranslationRequest(
            text="The implementation of this algorithm requires substantial computational resources and exhibits significant complexity in its operational parameters.",
            transformations=["language_simple_sentences", "language_common_words"]
        )
        
        try:
            # Translate text
            result = await translation_api.translate(request)
            print(f"Original: {request.text}")
            print(f"Simplified: {result.translated_text}")
            print(f"Words used: {result.words_used}")
            print(f"Remaining balance: {result.word_balance}")
            
        except ApiException as e:
            print(f"Translation failed: {e}")

asyncio.run(translate_text())
```

## Discovery and exploration

AccessibleTranslator offers 50+ transformations that are continuously being improved and expanded. Rather than maintaining hardcoded lists in your application, the SDK provides methods to discover current options dynamically.

### Get available transformations

This approach ensures your application always has access to the latest transformations and their descriptions. The API returns both regular transformations and special functions (like `explain_changes`):

```python
async def explore_transformations():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        
        try:
            # Get all available transformations
            transformations_response = await translation_api.transformations()
            
            print(f"Available transformations ({transformations_response.total_transformations}):")
            for transform in transformations_response.transformations:
                print(f"  • {transform.name}: {transform.description}")
            
            # Show special functions too
            print(f"\nSpecial functions ({transformations_response.total_functions}):")
            for func in transformations_response.functions:
                print(f"  • {func.name}: {func.description}")
                
        except ApiException as e:
            print(f"Failed to get transformations: {e}")

asyncio.run(explore_transformations())
```

### Get supported languages

AccessibleTranslator can output simplified text in multiple languages. This is particularly useful for international organizations or multilingual content platforms:

```python
async def explore_languages():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        
        try:
            # Get supported target languages
            languages_response = await translation_api.target_languages()
            
            print(f"Supported languages ({languages_response.total_languages}):")
            for language in languages_response.languages:
                print(f"  • {language}")
            
            print(f"\nNote: {languages_response.usage_note}")
            
        except ApiException as e:
            print(f"Failed to get languages: {e}")

asyncio.run(explore_languages())
```

## Comprehensive examples

These examples demonstrate real-world scenarios where AccessibleTranslator adds significant value to applications and content workflows.

### Multi-language workflow

For international organizations, this pattern shows how to create accessible content in multiple languages. This is particularly valuable for global companies ensuring their content reaches cognitively diverse audiences worldwide:

```python
async def multilingual_accessibility():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        
     	# Define target languages
        target_languages = ["English", "Spanish", "French", "German", "Dutch"]  # Get from  translation_api.target_languages()
        
        original_text = "The implementation of this algorithm requires substantial computational resources and exhibits significant complexity in its operational parameters."
        transformations = ["language_simple_sentences", "language_common_words"]
        
        print("=== MULTILINGUAL ACCESSIBILITY ===")
        print(f"Original: {original_text}")
        
        for language in target_languages:
            if language in languages_response.languages:
                request = accessibletranslator.TranslationRequest(
                    text=original_text,
                    transformations=transformations,
                    target_language=language
                )
                
                try:
                    result = await translation_api.translate(request)
                    print(f"\n{language}: {result.translated_text}")
                    
                except ApiException as e:
                    print(f"\n{language}: Translation failed - {e}")

asyncio.run(multilingual_accessibility())
```

### Batch processing

When you need to process multiple texts (like articles, documentation, or user-generated content), this pattern shows how to handle batch operations efficiently while monitoring your word balance and handling individual failures gracefully:

```python
async def batch_translation():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        user_api = accessibletranslator.UserManagementApi(api_client)
        
        # Check initial word balance
        balance = await user_api.word_balance()
        print(f"Starting word balance: {balance.word_balance}")
        
        texts_to_process = [
            "The implementation requires careful consideration of edge cases.",
            "This methodology demonstrates significant improvements in efficacy.",
            "The comprehensive analysis reveals important correlations."
        ]
        
        transformations = ["language_simple_sentences", "language_common_words"]
        results = []
        
        for i, text in enumerate(texts_to_process, 1):
            print(f"\nProcessing text {i}/{len(texts_to_process)}...")
            
            request = accessibletranslator.TranslationRequest(
                text=text,
                transformations=transformations
            )
            
            try:
                result = await translation_api.translate(request)
                results.append({
                    'original': text,
                    'simplified': result.translated_text,
                    'words_used': result.words_used
                })
                
                print(f"✅ Processed ({result.words_used} words)")
                
            except ApiException as e:
                print(f"❌ Failed: {e}")
                results.append({
                    'original': text,
                    'error': str(e)
                })
        
        # Summary
        total_words_used = sum(r.get('words_used', 0) for r in results)
        successful = sum(1 for r in results if 'simplified' in r)
        
        print(f"\n=== BATCH PROCESSING SUMMARY ===")
        print(f"Processed: {successful}/{len(texts_to_process)} texts")
        print(f"Total words used: {total_words_used}")
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Text {i} ---")
            print(f"Original: {result['original']}")
            if 'simplified' in result:
                print(f"Simplified: {result['simplified']}")
            else:
                print(f"Error: {result['error']}")

asyncio.run(batch_translation())
```

## Account management

AccessibleTranslator uses a word-based billing system. Each API call consumes words from your account balance based on the input text length. Monitoring your usage helps ensure uninterrupted service.

### Check word balance

Regularly checking your word balance helps you monitor usage and avoid service interruptions. This is especially important for production applications:

```python
async def check_balance():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        user_api = accessibletranslator.UserManagementApi(api_client)
        
        try:
            balance = await user_api.word_balance()
            print(f"Current word balance: {balance.word_balance:,} words")
            
        except ApiException as e:
            print(f"Failed to get balance: {e}")

asyncio.run(check_balance())
```

### System health check

For production applications, monitoring the API's availability ensures your accessibility features remain functional. This endpoint provides a quick way to verify system status:

```python
async def health_check():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        system_api = accessibletranslator.SystemApi(api_client)
        
        try:
            health = await system_api.check()
            print(f"System status: {health.status}")
            print(f"Timestamp: {health.timestamp}")
            
        except ApiException as e:
            print(f"Health check failed: {e}")

asyncio.run(health_check())
```

## Error handling

Robust error handling is crucial when integrating AI-powered accessibility features into production applications. Different error types require different response strategies.

### Comprehensive error handling

This example shows a production-ready approach to handling various error conditions you might encounter. The retry logic helps handle temporary issues while respecting different types of permanent failures:

```python
async def robust_translation():
    async with accessibletranslator.ApiClient(configuration) as api_client:
        translation_api = accessibletranslator.TranslationApi(api_client)
        user_api = accessibletranslator.UserManagementApi(api_client)
        
        # Pre-flight checks
        try:
            balance = await user_api.word_balance()
            if balance.word_balance < 100:
                print("⚠️  Warning: Low word balance")
        except ApiException:
            print("⚠️  Could not check word balance")
        
        # Translation with retry logic
        max_retries = 3
        retry_count = 0
        
        request = accessibletranslator.TranslationRequest(
            text="Your text here",
            transformations=["language_simple_sentences"]
        )
        
        while retry_count < max_retries:
            try:
                result = await translation_api.translate(request)
                print(f"✅ Translation successful!")
                print(f"Result: {result.translated_text}")
                break
                
            except ApiException as e:
                retry_count += 1
                print(f"❌ Attempt {retry_count} failed: {e}")
                
                if e.status == 402:  # Payment required
                    print("💳 Insufficient word balance")
                    break
                elif e.status == 401:  # Unauthorized
                    print("🔑 Invalid API key")
                    break
                elif e.status == 422:  # Validation error
                    print("📝 Invalid request format")
                    break
                elif retry_count < max_retries:
                    print(f"🔄 Retrying in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    print("💥 Max retries exceeded")

asyncio.run(robust_translation())
```

## API classes and methods

The SDK organizes functionality into logical API classes. Each class handles a specific aspect of the AccessibleTranslator service.

### TranslationApi

This is the primary class you'll use for text processing and discovery. It handles all transformation operations and provides methods to explore available options.

**Main translation functionality:**

- `translate(translation_request)` - Transform text with accessibility features
- `transformations()` - Get all available transformations and descriptions  
- `target_languages()` - Get supported output languages

### UserManagementApi

Manages account-level operations like checking your word balance. Essential for monitoring usage in production applications.

**Account and usage management:**

- `word_balance()` - Check remaining word balance

### SystemApi

Provides system status information for monitoring and health checks in production environments.

**System monitoring:**

- `check()` - Basic system health status

## Configuration options

The SDK supports various configuration options to adapt to different deployment environments and requirements.

### Authentication

API key authentication is the recommended approach for production applications. Store your API key securely (environment variables, secret management systems):

```python
# API Key authentication (recommended for production)
configuration = accessibletranslator.Configuration(
    api_key={'ApiKeyAuth': 'sk_your_api_key_here'}
)
```

### Advanced configuration

For production deployments, you may need to adjust connection settings, SSL configuration, or enable debug logging:

```python
configuration = accessibletranslator.Configuration(
    api_key={'ApiKeyAuth': 'sk_your_api_key_here'},
    # Connection settings
    connection_pool_maxsize=100,
    retries=3,
    # SSL settings
    verify_ssl=True,
    # Debug mode
    debug=False
)
```

## Best practices

These patterns help ensure reliable, maintainable integrations that scale well in production environments.

### 1. Use dynamic discovery

Transformations and languages are continuously updated. Dynamic discovery ensures your application always uses current options without requiring code updates:

```python
# Dynamic discovery
transformations = await translation_api.transformations()
languages = await translation_api.target_languages()
```

### 2. Handle async properly

Proper async context management prevents resource leaks and ensures connections are properly closed:

```python
# ✅ Good - Proper async context management
async with accessibletranslator.ApiClient(configuration) as api_client:
    api = accessibletranslator.TranslationApi(api_client)
    result = await api.translate(request)

# ❌ Avoid - Missing async context
api_client = accessibletranslator.ApiClient(configuration)
api = accessibletranslator.TranslationApi(api_client)
```

### 3. Monitor usage

Proactive monitoring prevents service interruptions and helps with capacity planning:

```python
# Check balance before large operations
balance = await user_api.word_balance()
if balance.word_balance < estimated_words_needed:
    print("Warning: Insufficient balance for operation")
```

### 4. Error recovery

Different error types require different handling strategies. Understanding these patterns improves application reliability:

```python
try:
    result = await translation_api.translate(request)
except ApiException as e:
    if e.status == 402:
        handle_insufficient_balance()
    elif e.status == 429:
        await asyncio.sleep(retry_delay)
        # Retry logic
```

## Getting help

- **API documentation**: [https://www.accessibletranslator.com/resources/api-docs](https://www.accessibletranslator.com/resources/api-docs)
- **Support**: support@accessibletranslator.com
- **Website**: [https://accessibletranslator.com](https://accessibletranslator.com)

---

## Technical details

**Requirements:** Python 3.9+

**Dependencies:** urllib3, python-dateutil, aiohttp, aiohttp-retry, pydantic, typing-extensions

**License:** MIT