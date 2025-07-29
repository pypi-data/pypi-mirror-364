"""TwelveLabs Marengo video embedding tool for Strands Agents.

This module provides access to TwelveLabs Marengo Embed 2.7 model through Amazon Bedrock,
allowing you to generate vector embeddings from video, text, audio, or image inputs.
These embeddings can be used for similarity search, clustering, and other ML tasks.
"""

import json
import logging
import os
import base64
from typing import Any, Optional

import boto3
from strands import tool

logger = logging.getLogger(__name__)

# TwelveLabs Marengo model IDs
MARENGO_MODEL_IDS = {
    "us-east-1": "twelvelabs.marengo-embed-2-7-v1:0",
    "eu-west-1": "eu.twelvelabs.marengo-embed-2-7-v1:0", 
    "ap-northeast-2": "ap.twelvelabs.marengo-embed-2-7-v1:0"
}

def get_aws_region() -> str:
    """Get AWS region from environment or default."""
    return os.environ.get("AWS_REGION", "us-east-1")

def get_model_id(region: str) -> str:
    """Get the appropriate model ID for the region."""
    return MARENGO_MODEL_IDS.get(region, MARENGO_MODEL_IDS["us-east-1"])

def read_file_as_base64(file_path: str) -> str:
    """Read a file and return as base64 encoded string."""
    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
            return base64.b64encode(file_content).decode('utf-8')
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {str(e)}")

def create_bedrock_client():
    """Create and return a Bedrock Runtime client."""
    region = get_aws_region()
    return boto3.client("bedrock-runtime", region_name=region)

@tool
def twelvelabs_marengo(
    input_type: str,
    output_s3_uri: str,
    label: str,
    s3_uri: Optional[str] = None,
    s3_bucket_owner: Optional[str] = None,
    local_file_path: Optional[str] = None,
    text_content: Optional[str] = None,
    embedding_option: str = "visual-text"
) -> str:
    """
    Generate vector embeddings from video, text, audio, or image content using TwelveLabs Marengo Embed 2.7 model.
    Supports similarity search, clustering, and content classification through Amazon Bedrock.

    Args:
        input_type: Type of input content to generate embeddings from
            - "video": Video content analysis
            - "text": Text content embeddings
            - "audio": Audio content analysis
            - "image": Image content analysis
        output_s3_uri: S3 URI where embedding results will be stored
        label: Human-readable description of the embedding operation
        s3_uri: S3 URI of the input content (e.g., s3://bucket/video.mp4)
        s3_bucket_owner: AWS account ID of the S3 bucket owner (required for S3 input)
        local_file_path: Local file path to read and encode as base64 (alternative to S3)
        text_content: Text content for text embeddings (when input_type is 'text')
        embedding_option: Type of embedding to generate (default: visual-text)
            - "visual-text": Combined visual and text embeddings
            - "visual": Visual-only embeddings
            - "text": Text-only embeddings
            - "audio": Audio-only embeddings

    Returns:
        String with job details and status information

    Environment Variables:
        AWS_REGION: AWS region (default: us-east-1)
        AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)
        BYPASS_TOOL_CONSENT: Set to "true" to skip confirmation prompts

    Examples:
        # Generate video embeddings from S3
        twelvelabs_marengo(
            input_type="video",
            s3_uri="s3://my-bucket/marketing-video.mp4",
            s3_bucket_owner="123456789012",
            output_s3_uri="s3://my-results-bucket/embeddings/",
            label="Generate video embeddings for search system"
        )

        # Generate text embeddings
        twelvelabs_marengo(
            input_type="text",
            text_content="Product demonstration video showing new features",
            output_s3_uri="s3://my-results-bucket/text-embeddings/",
            label="Generate text embeddings for product descriptions"
        )
    """
    
    print(f"🎯 **{label}**")
    print(f"📊 Input Type: {input_type}")
    print(f"🔧 Embedding Option: {embedding_option}")
    
    region = get_aws_region()
    model_id = get_model_id(region)
    print(f"🌍 Region: {region}")
    print(f"🤖 Model: {model_id}")
    
    # Validate input requirements
    if input_type == "text" and not text_content:
        return "❌ **Error:** text_content is required when input_type is 'text'"
    
    if input_type != "text" and not s3_uri and not local_file_path:
        return "❌ **Error:** Either s3_uri or local_file_path is required for non-text input types"
    
    if s3_uri and not s3_bucket_owner:
        return "❌ **Error:** s3_bucket_owner is required when using s3_uri"
    
    # Check region availability
    if region not in MARENGO_MODEL_IDS:
        available_regions = ", ".join(MARENGO_MODEL_IDS.keys())
        return f"❌ **Error:** Marengo model not available in region {region}. Available regions: {available_regions}"
    
    # Ask for confirmation
    BYPASS_CONSENT = os.environ.get("BYPASS_TOOL_CONSENT", "").lower() == "true"
    if not BYPASS_CONSENT:
        confirm = input(f"🤔 Generate embeddings using TwelveLabs Marengo model? [y/*] ")
        if confirm.lower() != "y":
            return f"⏹️ **Operation canceled by user.** Reason: {confirm}"
    
    try:
        client = create_bedrock_client()
        
        # Build the model input
        model_input = {
            "inputType": input_type,
            "embeddingOption": embedding_option
        }
        
        # Add media source based on input type
        if s3_uri and s3_bucket_owner:
            model_input["mediaSource"] = {
                "s3Location": {
                    "uri": s3_uri,
                    "bucketOwner": s3_bucket_owner
                }
            }
            print(f"📁 S3 Input: {s3_uri}")
        elif local_file_path:
            print(f"📂 Reading local file: {local_file_path}")
            base64_content = read_file_as_base64(local_file_path)
            model_input["mediaSource"] = {
                "base64String": base64_content
            }
            print(f"✅ File encoded successfully")
        elif text_content:
            model_input["textContent"] = text_content
            preview = text_content[:100] + "..." if len(text_content) > 100 else text_content
            print(f"📝 Text Preview: {preview}")
        
        # Build the complete request body (NOW PROPERLY USED!)
        request_body = {
            "modelId": model_id,
            "modelInput": model_input,
            "outputDataConfig": {
                "s3OutputDataConfig": {
                    "s3Uri": output_s3_uri
                }
            }
        }
        
        print(f"🚀 Starting async embedding generation...")
        
        # Start async invocation using the complete request_body
        response = client.start_async_invoke(**request_body)
        
        # Format success response
        result = f"✅ **Marengo Embedding Job Started Successfully!**\n\n"
        
        if "invocationArn" in response:
            result += f"📋 **Job ARN:** {response['invocationArn']}\n"
        
        result += f"📤 **Output Location:** {output_s3_uri}\n"
        result += f"🔧 **Embedding Type:** {embedding_option}\n"
        result += f"📊 **Input Type:** {input_type}\n\n"
        
        result += f"⏳ **Note:** This is an async operation.\n"
        result += f"📁 Check the S3 output location for results when processing completes.\n"
        result += f"🔍 You can monitor job status using AWS CLI or Console."
        
        return result
        
    except Exception as ex:
        logger.warning(f"Marengo embedding call threw exception: {type(ex).__name__}")
        return f"❌ **Marengo embedding generation failed:** {str(ex)}"
