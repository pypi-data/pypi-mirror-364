import tempfile
from pathlib import Path
from enum import Enum
from flamapy.metamodels.configuration_metamodel.models import Configuration
from flamapy.interfaces.python.flamapy_feature_model import FLAMAFeatureModel
from flamapy.core.discover import DiscoverMetamodels
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)


class FlamapyOperations(str, Enum):
    ATOMIC_SETS = "atomic_sets"
    AVERAGE_BRANCHING_FACTOR = "average_branching_factor"
    COMMONALITY = "commonality"
    CONFIGURATIONS = "configurations"
    CONFIGURATIONS_NUMBER = "configurations_number"
    CORE_FEATURES = "core_features"
    COUNT_LEAFS = "count_leafs"
    DEAD_FEATURES = "dead_features"
    ESTIMATED_NUMBER_OF_CONFIGURATIONS = "estimated_number_of_configurations"
    FALSE_OPTIONAL_FEATURES = "false_optional_features"
    FEATURE_ANCESTORS = "feature_ancestors"
    FEATURE_INCLUSION_PROBABILITY = "feature_inclusion_probability"
    FILTER = "filter"
    HOMOGENEITY = "homogeneity"
    LEAF_FEATURES = "leaf_features"
    MAX_DEPTH = "max_depth"
    SAMPLING = "sampling"
    SATISFIABILITY = "satisfiability"
    SATISFIABLE_CONFIGURATION = "satisfiable_configuration"
    UNIQUE_FEATURES = "unique_features"
    VARIABILITY = "variability"
    VARIANT_FEATURES = "variant_features"


class UVLContent(BaseModel):
    content: str = Field(description="UVL (universal variability language) feature model content")


class UVLContentWithConfig(BaseModel):
    content: str = Field(description="UVL (universal variability language) feature model content")
    config_file: str = Field(description="Configuration content or parameter (e.g., feature name, list of features).")


class UVLContentWithSimpleConfig(BaseModel):
    content: str = Field(description="UVL (universal variability language) feature model content")
    selected_features: List[str] = Field(
        description="A list of feature names to be considered 'selected' in the configuration.")


def _create_temp_file(content: str, suffix: str = ".uvl") -> str:
    """Create a temporary file with content and return its path"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix) as temp_file:
        temp_file.write(content)
        return temp_file.name


def _cleanup_temp_file(file_path: str):
    """Clean up temporary file"""
    try:
        Path(file_path).unlink()
    except Exception:
        pass


def _run_facade_operation(content: str, operation_method: str, *args) -> Any:
    """Run operation using the simple facade interface"""
    temp_file = _create_temp_file(content)
    try:
        fm = FLAMAFeatureModel(temp_file)
        method = getattr(fm, operation_method)
        result = method(*args)
        return result
    except Exception as e:
        raise Exception(f"Error executing {operation_method}: {str(e)}")
    finally:
        _cleanup_temp_file(temp_file)


def _run_framework_operation(content: str, operation_name: str, **kwargs) -> Any:
    """Run operation using the core framework interface with optional parameters"""
    temp_file = _create_temp_file(content)
    try:
        dm = DiscoverMetamodels()
        op = dm.use_operation_from_file(operation_name, temp_file)

        # If operation requires execution
        if hasattr(op, 'execute'):
            # Set parameters if any were passed
            for key, value in kwargs.items():
                if hasattr(op, key):
                    setattr(op, key, value)

            op.execute()
            return op.get_result()

        # If result is already final
        return op
    except Exception as e:
        raise Exception(f"Error executing {operation_name}: {str(e)}")
    finally:
        _cleanup_temp_file(temp_file)


async def serve() -> None:
    server = Server("mcp-flamapy")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=FlamapyOperations.ATOMIC_SETS,
                description="Identifies atomic sets, which are groups of features that always appear together in all valid configurations.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.AVERAGE_BRANCHING_FACTOR,
                description="Calculates the average number of child features per parent feature, indicating model complexity.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.COMMONALITY,
                description="Measures the frequency of a feature in valid configurations, expressed as a percentage.",
                inputSchema=UVLContentWithConfig.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.CONFIGURATIONS,
                description="Generates all possible valid configurations from the feature model.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.CONFIGURATIONS_NUMBER,
                description="Returns the total number of valid configurations for the feature model.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.CORE_FEATURES,
                description="Identifies features that are present in all valid configurations (mandatory features).",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.COUNT_LEAFS,
                description="Counts the number of leaf features (features with no children) in the model.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.DEAD_FEATURES,
                description="Identifies features that cannot be included in any valid configuration, often indicating model errors.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.ESTIMATED_NUMBER_OF_CONFIGURATIONS,
                description="Estimates the total number of configurations by considering all feature combinations, ignoring constraints.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.FALSE_OPTIONAL_FEATURES,
                description="Identifies features that seem optional but are mandatory due to model constraints.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.FEATURE_ANCESTORS,
                description="Returns all ancestor features for a given feature in the model hierarchy.",
                inputSchema=UVLContentWithConfig.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.FEATURE_INCLUSION_PROBABILITY,
                description="Calculates the probability of each feature being included in a random valid configuration.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.FILTER,
                description="Filters and selects a subset of configurations based on specified criteria.",
                inputSchema=UVLContentWithConfig.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.HOMOGENEITY,
                description="Measures the similarity of configurations. A higher value (closer to 1) indicates more similar configurations.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.LEAF_FEATURES,
                description="Identifies all leaf features in the model (features with no children).",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.MAX_DEPTH,
                description="Finds the maximum depth of the feature tree, indicating the longest path from root to leaf.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.SAMPLING,
                description="Generates a sample of valid configurations from the feature model.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.SATISFIABILITY,
                description="Checks if the feature model is valid and can produce at least one valid configuration.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.SATISFIABLE_CONFIGURATION,
                description="Checks if a given configuration of selected features is valid according to the model's constraints.",
                inputSchema=UVLContentWithSimpleConfig.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.UNIQUE_FEATURES,
                description="Identifies features that are part of a unique variability point.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.VARIABILITY,
                description="Calculates the ratio of variant features to the total number of features.",
                inputSchema=UVLContent.model_json_schema()
            ),
            Tool(
                name=FlamapyOperations.VARIANT_FEATURES,
                description="Identifies features that are neither core nor dead (i.e., truly optional).",
                inputSchema=UVLContent.model_json_schema()
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case FlamapyOperations.ATOMIC_SETS:
                return [TextContent(
                    type="text",
                    text=_run_facade_operation(arguments.get("content"), "atomic_sets")
                )]
            case FlamapyOperations.AVERAGE_BRANCHING_FACTOR:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "average_branching_factor"))
                )]
            case FlamapyOperations.COMMONALITY:
                return [TextContent(
                    type="text",
                    text=str(
                        _run_facade_operation(arguments.get("content"), "commonality", arguments.get("config_file")))
                )]
            case FlamapyOperations.CONFIGURATIONS:
                configs = _run_facade_operation(arguments.get("content"), "configurations")
                return [TextContent(
                    type="text",
                    text=str(configs)
                )]
            case FlamapyOperations.CONFIGURATIONS_NUMBER:
                return [TextContent(
                    type="text",
                    text=str(_run_framework_operation(arguments.get("content"), "PySATConfigurationsNumber"))
                )]
            case FlamapyOperations.CORE_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "core_features"))
                )]
            case FlamapyOperations.COUNT_LEAFS:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "count_leafs"))
                )]
            case FlamapyOperations.DEAD_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "dead_features"))
                )]
            case FlamapyOperations.ESTIMATED_NUMBER_OF_CONFIGURATIONS:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "estimated_number_of_configurations"))
                )]
            case FlamapyOperations.FALSE_OPTIONAL_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "false_optional_features"))
                )]
            case FlamapyOperations.FEATURE_ANCESTORS:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "feature_ancestors",
                                                   arguments.get("config_file")))
                )]
            case FlamapyOperations.FEATURE_INCLUSION_PROBABILITY:
                probabilities = _run_framework_operation(arguments.get("content"), "FeatureInclusionProbability")
                formatted_probabilities = {feature: round(prob, 4) for feature, prob in probabilities.items()}
                return [TextContent(
                    type="text",
                    text=str(formatted_probabilities)
                )]
            case FlamapyOperations.FILTER:
                config_file = _create_temp_file(arguments.get("config_file"), ".csvconf")
                try:
                    filtered_configs = _run_facade_operation(arguments.get("content"), "filter", config_file)
                    return [TextContent(
                        type="text",
                        text=str(filtered_configs)
                    )]
                finally:
                    _cleanup_temp_file(config_file)
            case FlamapyOperations.HOMOGENEITY:
                return [TextContent(
                    type="text",
                    text=str(_run_framework_operation(arguments.get("content"), "Homogeneity"))
                )]
            case FlamapyOperations.LEAF_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "leaf_features"))
                )]
            case FlamapyOperations.MAX_DEPTH:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "max_depth"))
                )]
            case FlamapyOperations.SAMPLING:
                samples = _run_framework_operation(arguments.get("content"), "Sampling")
                return [TextContent(
                    type="text",
                    text=str(samples)
                )]
            case FlamapyOperations.SATISFIABILITY:
                return [TextContent(
                    type="text",
                    text=str(_run_facade_operation(arguments.get("content"), "satisfiable"))
                )]
            case FlamapyOperations.SATISFIABLE_CONFIGURATION:
                config_temp_file_path = None
                try:
                    config_lines = [f"{feature_name},True" for feature_name in arguments.get("selected_features")]
                    config_content = "\n".join(config_lines)

                    # Create the temporary file with the correctly formatted configuration
                    config_temp_file_path = _create_temp_file(config_content, suffix=".csvconf")

                    result = _run_facade_operation(arguments.get("content"), "satisfiable_configuration",
                                                   config_temp_file_path, False)
                    return [TextContent(
                        type="text",
                        text=str(result)
                    )]
                except Exception as e:
                    raise Exception(f"Failed to check configuration satisfiability: {str(e)}")
                finally:
                    if config_temp_file_path:
                        _cleanup_temp_file(config_temp_file_path)
            case FlamapyOperations.UNIQUE_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_framework_operation(arguments.get("content"), "UniqueFeatures"))
                )]
            case FlamapyOperations.VARIABILITY:
                variability_ratio = _run_framework_operation(arguments.get("content"), "Variability")
                return [TextContent(
                    type="text",
                    text=str(round(float(variability_ratio), 2))
                )]
            case FlamapyOperations.VARIANT_FEATURES:
                return [TextContent(
                    type="text",
                    text=str(_run_framework_operation(arguments.get("content"), "VariantFeatures"))
                )]
            case _:
                raise ValueError(f"Unknown tool name: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
