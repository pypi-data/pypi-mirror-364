from typing_extensions import List, Dict, Any


def convert_openai_tools_to_openapi(
    tools: List[Dict[str, Any]],
    title: str = "Converted Tool API",
    version: str = "1.0.0"
) -> Dict[str, Any]:
    """
    Convert OpenAI tool schemas into a complete OpenAPI 3.1 specification.

    :param tools: List of OpenAI tool calling schemas
    :param title: API title
    :param version: API version
    :return: OpenAPI spec as dict
    """
    paths = {}

    def convert_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively convert OpenAI parameter schema into OpenAPI schema.
        Supports: type, properties, items, oneOf, anyOf, enum, description, format
        """
        if not isinstance(schema, dict):
            return schema

        result = {}

        # Simple keywords to copy
        for key in [
            "type", "description", "format", "enum", "nullable",
            "minLength", "maxLength", "minimum", "maximum", "default", "examples"
        ]:
            if key in schema:
                result[key] = schema[key]

        # Nested schemas
        if "properties" in schema:
            result["properties"] = {
                k: convert_schema(v) for k, v in schema["properties"].items()
            }
        if "required" in schema:
            result["required"] = schema["required"]
        if "items" in schema:
            result["items"] = convert_schema(schema["items"])
        for logic in ["oneOf", "anyOf", "allOf"]:
            if logic in schema:
                result[logic] = [convert_schema(s) for s in schema[logic]]
        if "additionalProperties" in schema:
            result["additionalProperties"] = convert_schema(schema["additionalProperties"])

        return result

    for tool in tools:
        func = tool.get("function", {})
        name = func.get("name", "unnamedFunction")
        description = func.get("description", "")
        parameters = func.get("parameters", {"type": "object"})

        path = f"/{name}"
        paths[path] = {
            "post": {
                "operationId": name,
                "description": description,
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": convert_schema(parameters)
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {}
                            }
                        }
                    }
                }
            }
        }

    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version
        },
        "paths": paths,
        "components": {}
    }

    return openapi_spec


if __name__ == "__main__":
  tools = [
    {
        "function": {
            "name": "drawOverlay",
            "description": "Draw technical overlays on chart",
            "parameters": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["line", "rectangle", "arrow"]
                    },
                    "style": {
                        "type": "object",
                        "properties": {
                            "color": {"type": "string"},
                            "lineWidth": {"type": "number"},
                            "dashed": {"type": "boolean"}
                        }
                    },
                    "points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {"type": "integer"},
                                "value": {"type": "number"}
                            },
                            "required": ["timestamp", "value"]
                        }
                    },
                    "config": {
                        "oneOf": [
                            {"type": "string"},
                            {
                                "type": "object",
                                "properties": {"advanced": {"type": "boolean"}}
                            }
                        ]
                    }
                },
                "required": ["type", "points"]
            }
        }
    }
  ]

  openapi_spec = convert_openai_tools_to_openapi(tools)
  import json
  print(json.dumps(openapi_spec, indent=2))
