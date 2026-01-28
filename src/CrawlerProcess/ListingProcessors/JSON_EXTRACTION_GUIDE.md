# JSON Extraction & Listing Processors - Complete Guide for Dummies

## The Problem We're Solving

**Old way (Bad ❌):**
- Use CSS selectors like `a.product-link` to find products
- Problem: When website changes HTML structure, selectors break
- Problem: Have to find right CSS classes for each site
- Not scalable

**New way (Good ✅):**
- Extract JSON data that sites embed in HTML
- JSON data is structured and reliable
- No CSS class dependencies
- Easy to extend to new sites

---

## How Modern Websites Work

### Example: MercadoLibre

**What you see in browser:**
```
[Product 1] [Product 2] [Product 3]
```

**What's actually in the HTML:**
```html
<script>
  melidata("add","event_data",{
    "results": ["MLC123", "MLC456", "MLC789"],
    "printed_result": [
      {"item_id": "MLC123", "price": 5000},
      {"item_id": "MLC456", "price": 10000},
      {"item_id": "MLC789", "price": 15000}
    ]
  });
</script>
```

**How we extract it:**
```python
# Step 1: Find the JSON using regex
pattern = r'melidata\("add","event_data",(\{.*?\})\);'
json_data = extract_json(html, pattern)

# Step 2: Navigate the structure
product_ids = json_data["results"]  # ["MLC123", "MLC456", "MLC789"]

# Step 3: Build URLs
for id in product_ids:
    url = f"https://listado.mercadolibre.cl/{id}"
```

---

## The Clean Architecture

### Layer 1: Base Class (AbstractListingProcessor)

```
Purpose: Define the INTERFACE that all processors must follow
Think of it like: "All website processors must have an extract_product_urls() method"

Code:
    class AbstractListingProcessor(ABC):
        def extract_product_urls(self, html_content):
            # Must be implemented by each website
            pass
```

### Layer 2: Specific Processors (One per Website)

```
Purpose: Implement HOW to extract from each specific website

Examples:
    - MercadoLibreProcessor: Knows MercadoLibre's JSON structure
    - FalabellaProcessor: Knows Falabella's JSON structure
    - ParisProcessor: Knows Paris's JSON structure
```

### Layer 3: Factory (ListingProcessorFactory)

```
Purpose: Act as a manager that gives you the right processor

Think of it like a VENDING MACHINE:
    - You ask: "Give me a processor for MERCADOLIBRE"
    - Factory responds: "Here's MercadoLibreProcessor!"
    - You ask: "Give me a processor for PARIS"
    - Factory responds: "Here's ParisProcessor!"
```

### Layer 4: Crawler (Updated)

```
Purpose: Use the factory to get processors, no hardcoding needed

Before (Bad):
    if source == "MERCADOLIBRE":
        # MercadoLibre specific code
    elif source == "FALABELLA":
        # Falabella specific code
    # Gets messy fast!

After (Good):
    processor = factory.get_processor(source)
    urls = processor.extract_product_urls(html)
    # Clean and simple!
```

---

## How to Add a New Website (Step-by-Step)

### Example: Adding Support for PARIS

**Step 1: Inspect the website**
- Open Paris.com in browser
- Right-click → Inspect → Search for <script> tags
- Find where JSON data is embedded
- Look for patterns like:
  - `window.__INITIAL_STATE__ = {...}`
  - `window.__DATA__ = {...}`
  - `<script id="apollo">...</script>`

**Step 2: Write down the JSON pattern**
```python
# Example: Paris might embed data like:
<script id="apollo">
  window.__APOLLO_STATE__ = {"products": [{"id": "P123", "url": "/paris-product-123"}]}
</script>

# So the regex pattern would be:
pattern = r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});'
```

**Step 3: Create ParisProcessor.py**
```python
from src.CrawlerProcess.ListingProcessors.AbstractListingProcessor import AbstractListingProcessor

class ParisProcessor(AbstractListingProcessor):
    def extract_product_urls(self, html_content):
        # Find the JSON
        json_pattern = r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});'
        data = self._extract_json_from_html(html_content, json_pattern)
        
        if not data:
            return []
        
        # Extract URLs from the data
        urls = []
        products = data.get("products", [])
        for product in products:
            url = product.get("url")
            if url:
                urls.append(f"https://www.paris.com{url}")
        
        return urls
```

**Step 4: Register the processor**
```python
# In ListingProcessorFactory.initialize_default_processors():
cls.register_processor("PARIS", ParisProcessor(debug_mode=debug_mode))
```

**That's it! No changes needed to Crawler.py**

---

## Can We Do This Automatically?

### Short Answer: No, but it's easier than you think

### Long Answer:

**Why not automatic:**
- Each website has DIFFERENT JSON structures
- MercadoLibre uses `melidata()` calls
- Falabella uses `window.__INITIAL_STATE__`
- Paris uses `window.__APOLLO_STATE__`
- We can't guess the pattern without seeing the site

**But here's the good news:**
1. Inspecting takes **5 minutes** (right-click → inspect → find JSON)
2. Once you know the pattern, processor is **20 lines of code**
3. Adding new sites is **EASY and FAST**

**Could we make a smart detector?**
- We could try multiple common patterns automatically
- Try: `window.__.*__`, `melidata()`, `apollo`, etc.
- Would catch 80% of sites
- Still needs manual review for edge cases

Example auto-detector:
```python
COMMON_PATTERNS = [
    r'melidata\("add","event_data",(\{.*?\})\);',  # MercadoLibre
    r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});',   # Many sites
    r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});',    # GraphQL sites
    r'<script id="apollo">(\{.*?\})</script>',       # Apollo
]

def auto_find_json(html):
    for pattern in COMMON_PATTERNS:
        data = extract_json(html, pattern)
        if data:
            return data
    return None
```

---

## Quick Reference: How to Find JSON Patterns

### For any website, follow these steps:

1. **Open site in browser**
   ```
   Right-click → Inspect → Press Ctrl+F
   ```

2. **Search for common patterns in HTML:**
   ```
   - window.__
   - <script type="application/json"
   - melidata(
   - apollo
   - __INITIAL_STATE__
   - __DATA__
   ```

3. **Once found, extract the pattern:**
   ```javascript
   // If you see:
   <script>
     window.__INITIAL_STATE__ = {"products": [...]}
   </script>
   
   // The regex pattern is:
   r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'
   ```

4. **Create processor, register it, done!**

---

## Example: Full Workflow

### Scenario: You want to add RIPLEY

```
1. Go to ripley.com
2. Open browser DevTools
3. Find: "ripley" + "search results" page
4. Inspect HTML, find JSON
5. See: window.__RIPLEY_DATA__ = {...}

6. Create src/CrawlerProcess/ListingProcessors/RipleyProcessor.py
7. Write 20 lines of extraction code
8. Add to factory: cls.register_processor("RIPLEY", RipleyProcessor())
9. Add "RIPLEY" to your NavRules.JSON
10. Done! Crawler now supports Ripley

Total time: 10 minutes
```

---

## Architecture Diagram

```
                    Crawler.py
                        |
                        v
        ListingProcessorFactory
        /      /      |       \      \
       /      /       |        \      \
      v      v        v         v      v
  MercadoLibre  Falabella   Paris   Ripley   ...
  Processor     Processor   Processor Processor
       |             |         |        |
       |             |         |        |
       └─────────────┴─────────┴────────┘
               |
               v
       Extract Product URLs
               |
               v
       Add to Crawler Queue
```

---

## Why This Design is Great

✅ **Easy to extend**: Add new site in 10 minutes
✅ **Clean code**: No big if/else statements
✅ **Maintainable**: Changes isolated to specific processor
✅ **Testable**: Each processor can be tested independently  
✅ **Scalable**: Can handle 20+ websites easily
✅ **Fallback**: CSS selector processor for emergency cases

---

## Summary

1. **JSON extraction** = More reliable than CSS selectors
2. **Pattern finding** = 5 minutes per new website
3. **Processor creation** = 20 lines of code
4. **Factory pattern** = No changes to main Crawler code
5. **Easy scaling** = Add sites without touching existing code

You now have a **professional, enterprise-grade web scraping architecture!**
