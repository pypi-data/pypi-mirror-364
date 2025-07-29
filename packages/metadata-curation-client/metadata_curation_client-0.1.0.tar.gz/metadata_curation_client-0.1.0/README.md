# Metadata Curation Client

API client for external partners to integrate with metadata curation platforms.

## Installation

```bash
pip install metadata-curation-client
```

## Basic Usage

```python
from metadata_curation_client import CurationAPIClient, PropertyType

# Initialize client
client = CurationAPIClient("http://localhost:8000")

# Create source
source = client.create_source({
    "name": "My Archive",
    "description": "Digital editions from our collection"
})

# Create controlled vocabulary property
language_prop = client.create_property({
    "technical_name": "language",
    "name": "Language", 
    "type": PropertyType.CONTROLLED_VOCABULARY,
    "source_id": source["id"],
    "property_options": [{"name": "English"}, {"name": "German"}]
})

# Create free text property
description_prop = client.create_property({
    "technical_name": "description",
    "name": "Description", 
    "type": PropertyType.FREE_TEXT,
    "source_id": source["id"]
})

# Create edition
edition = client.create_edition({
    "source_id": source["id"],
    "source_internal_id": "my_001"
})

# Create properties for each type
genre_prop = client.create_property({
    "technical_name": "genre",
    "name": "Genre", 
    "type": PropertyType.CONTROLLED_VOCABULARY,
    "source_id": source["id"],
    "property_options": [
        {"name": "Poetry"}, {"name": "Prose"}, {"name": "Drama"}
    ]
})

has_annotations_prop = client.create_property({
    "technical_name": "has_annotations",
    "name": "Has Annotations", 
    "type": PropertyType.BINARY,
    "source_id": source["id"]
})

year_prop = client.create_property({
    "technical_name": "publication_year",
    "name": "Publication Year", 
    "type": PropertyType.NUMERICAL,
    "source_id": source["id"]
})

description_prop = client.create_property({
    "technical_name": "description",
    "name": "Description", 
    "type": PropertyType.FREE_TEXT,
    "source_id": source["id"]
})

# Example 1: CONTROLLED_VOCABULARY suggestion
# First get the property option ID
properties = client.get_properties()
genre_prop = next(p for p in properties if p["technical_name"] == "genre")
poetry_option = next(opt for opt in genre_prop["property_options"] if opt["name"] == "Poetry")

client.create_suggestion({
    "source_id": source["id"],
    "edition_id": edition["id"],
    "property_id": genre_prop["id"],
    "property_option_id": poetry_option["id"]
})

# Example 2: BINARY suggestion (uses property_option_id)
# Binary properties always have options with ID 1 (true/1) and ID 2 (false/0)
# Get the "true" option (usually ID 1)
binary_props = client.get_properties()
has_annotations_prop = next(p for p in binary_props if p["technical_name"] == "has_annotations")
true_option = next(opt for opt in has_annotations_prop["property_options"] if opt["name"] == "1")

client.create_suggestion({
    "source_id": source["id"],
    "edition_id": edition["id"],
    "property_id": has_annotations_prop["id"],
    "property_option_id": true_option["id"]  # For "yes"/"true" value
})

# Example 3: NUMERICAL suggestion (uses custom_value)
client.create_suggestion({
    "source_id": source["id"],
    "edition_id": edition["id"],
    "property_id": year_prop["id"],
    "custom_value": "2025"  # Note: numerical values are sent as strings
})

# Example 4: FREE_TEXT suggestion (uses custom_value)
client.create_suggestion({
    "source_id": source["id"],
    "edition_id": edition["id"],
    "property_id": description_prop["id"],
    "custom_value": "This is a detailed description of the edition."
})

# Mark ingestion complete
client.mark_ingestion_complete(source["id"])
```

## Property Types

- `PropertyType.CONTROLLED_VOCABULARY` - Predefined options
- `PropertyType.FREE_TEXT` - Free text
- `PropertyType.BINARY` - True/false values
- `PropertyType.NUMERICAL` - Numeric values

## API Reference

See the docstrings in `curation_api_client.py` for detailed method documentation.

## Enhanced Integration with SourceManager

For more sophisticated integrations, we also provide a higher-level abstraction in `source_manager.py` that mirrors some of the conveniences of our internal extractors:

```python
from metadata_curation_client import CurationAPIClient, PropertyType, SourceManager, PropertyBuilder

# Initialize client and create source
client = CurationAPIClient("http://localhost:8000")
source = client.get_source_by_technical_name("my_data_source")
if not source:
    source = client.create_source({
        "name": "My Data Source",
        "description": "My collection of digital editions",
        "technical_name": "my_data_source"
    })

# Define properties using helper builders
property_definitions = [
    PropertyBuilder.controlled_vocabulary(
        "example_genre", "Genre", ["Poetry", "Prose", "Drama"]
    ),
    PropertyBuilder.binary(
        "example_has_annotations", "Has Annotations"
    ),
    PropertyBuilder.numerical(
        "example_year", "Publication Year"
    )
]

# Initialize the source manager - this will:
# - Fetch all existing data
# - Build lookup tables
# - Create any missing properties
manager = SourceManager(client, source['id'], property_definitions)

# Efficiently get or create edition using lookup tables
edition = manager.get_or_create_edition("book_001")

# Create suggestions in a batch with validation and deduplication
manager.create_suggestions_batch(
    edition["id"],
    {
        "example_genre": "Poetry",
        "example_has_annotations": True,
        "example_year": 2022
    }
)

# Mark ingestion complete (updates timestamp)
manager.finish_ingestion()
```

### Benefits of the SourceManager

The `SourceManager` provides several advantages for more complex integrations:

1. **Reduced API Calls**: Prefetches data to minimize API requests
2. **Lookup Tables**: Maintains efficient in-memory lookups for editions, properties, and suggestions
3. **Automatic Property Creation**: Creates properties from definitions as needed
4. **Validation**: Automatically validates values based on property types
5. **Deduplication**: Avoids creating duplicate suggestions
6. **Builder Helpers**: Provides convenient builder classes for creating properties and sources
7. **Timestamp Management**: Automatically updates the last ingestion timestamp

For a complete example, see `example_with_source_manager.py`.

### Choosing the Right Approach

- **Basic API Client**: For simple integrations or when you need complete control over the process
- **SourceManager**: For more complex integrations where efficiency and convenience are priorities

Both approaches use the same underlying API endpoints and data models, so you can choose the one that best fits your needs or even mix them as required.
