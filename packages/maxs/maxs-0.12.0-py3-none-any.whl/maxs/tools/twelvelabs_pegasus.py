"""TwelveLabs Pegasus video language model tool for Strands Agents.

This module provides access to TwelveLabs Pegasus 1.2 model through Amazon Bedrock,
allowing you to generate text descriptions, summaries, and insights from video content
using natural language processing and computer vision.
"""

import json
import logging
import os
import base64
from typing import Any, Optional

import boto3
from strands import tool

logger = logging.getLogger(__name__)

# TwelveLabs Pegasus model IDs by region
PEGASUS_MODEL_IDS = {
    "us-west-2": "us.twelvelabs.pegasus-1-2-v1:0",
    "eu-west-1": "eu.twelvelabs.pegasus-1-2-v1:0"
}

def get_aws_region() -> str:
    """Get AWS region from environment or default."""
    return os.environ.get("AWS_REGION", "us-west-2")

def get_model_id(region: str) -> str:
    """Get the appropriate model ID for the region."""
    return PEGASUS_MODEL_IDS.get(region, PEGASUS_MODEL_IDS["us-west-2"])

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
def twelvelabs_pegasus(
    input_prompt: str,
    label: str,
    s3_uri: Optional[str] = None,
    s3_bucket_owner: Optional[str] = None,
    local_file_path: Optional[str] = None
) -> str:
    """
    Generate text descriptions, summaries, and insights from video content using TwelveLabs Pegasus 1.2 model.
    Supports natural language video analysis, timeline breakdown, and content understanding through Amazon Bedrock.

    Args:
        input_prompt: The prompt or question about the video content
            Examples: 
            - "Describe what happens in this video with timestamps"
            - "Generate a 3-sentence summary of the main events"
            - "What products are shown in this marketing video?"
            - "Create chapter titles for this educational content"
        label: Human-readable description of the video analysis operation
        s3_uri: S3 URI of the video content (e.g., s3://bucket/video.mp4)
        s3_bucket_owner: AWS account ID of the S3 bucket owner (required for S3 input)
        local_file_path: Local file path to read and encode as base64 (alternative to S3)

    Returns:
        String with video analysis results and insights

    Environment Variables:
        AWS_REGION: AWS region (default: us-west-2 for Pegasus availability)
        AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, etc.)
        BYPASS_TOOL_CONSENT: Set to "true" to skip confirmation prompts

    Examples:
        # Analyze video timeline
        twelvelabs_pegasus(
            input_prompt="Tell me about this video with timestamps",
            s3_uri="s3://my-bucket/presentation.mp4",
            s3_bucket_owner="123456789012",
            label="Analyze quarterly presentation video"
        )

        # Generate video summary
        twelvelabs_pegasus(
            input_prompt="Create a 2-sentence summary of this customer feedback",
            local_file_path="/path/to/feedback.mp4",
            label="Summarize customer feedback video"
        )
    """
    
    print(f"🎯 **{label}**")
    print(f"💭 Prompt: {input_prompt}")
    
    region = get_aws_region()
    model_id = get_model_id(region)
    print(f"🌍 Region: {region}")
    print(f"🤖 Model: {model_id}")
    
    # Validate input requirements
    if not s3_uri and not local_file_path:
        return "❌ **Error:** Either s3_uri or local_file_path is required for video input"
    
    if s3_uri and not s3_bucket_owner:
        return "❌ **Error:** s3_bucket_owner is required when using s3_uri"
    
    # Check region availability
    if region not in PEGASUS_MODEL_IDS:
        available_regions = ", ".join(PEGASUS_MODEL_IDS.keys())
        return f"❌ **Error:** Pegasus model not available in region {region}. Available regions: {available_regions}"
    
    # Ask for confirmation
    BYPASS_CONSENT = os.environ.get("BYPASS_TOOL_CONSENT", "").lower() == "true"
    if not BYPASS_CONSENT:
        confirm = input(f"🤔 Analyze video content using TwelveLabs Pegasus model? [y/*] ")
        if confirm.lower() != "y":
            return f"⏹️ **Operation canceled by user.** Reason: {confirm}"
    
    try:
        client = create_bedrock_client()
        
        # Build the request body properly
        request_body = {
            "inputPrompt": input_prompt
        }
        
        # Add media source
        if s3_uri and s3_bucket_owner:
            request_body["mediaSource"] = {
                "s3Location": {
                    "uri": s3_uri,
                    "bucketOwner": s3_bucket_owner
                }
            }
            print(f"📁 S3 Input: {s3_uri}")
        elif local_file_path:
            print(f"📂 Reading and encoding local file: {local_file_path}")
            base64_content = read_file_as_base64(local_file_path)
            request_body["mediaSource"] = {
                "base64String": base64_content
            }
            print(f"✅ File encoded successfully")
        
        print(f"🔍 Analyzing video content with Pegasus...")
        
        # Invoke the model with proper request body
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json"
        )
        
        # Parse response
        response_data = json.loads(response['body'].read())
        
        # Format the response
        result = f"✅ **Pegasus Video Analysis Complete!**\n\n"
        
        # Handle different response formats
        if "outputText" in response_data:
            result += f"📄 **Analysis:**\n{response_data['outputText']}\n\n"
        elif "response" in response_data:
            result += f"📄 **Analysis:**\n{response_data['response']}\n\n"
        elif "text" in response_data:
            result += f"📄 **Analysis:**\n{response_data['text']}\n\n"
        else:
            # Fallback: show the full response if format is unexpected
            result += f"📄 **Raw Response:**\n{json.dumps(response_data, indent=2)}\n\n"
        
        # Add metadata if present
        if "metadata" in response_data:
            result += f"📊 **Metadata:**\n"
            for key, value in response_data["metadata"].items():
                result += f"  - {key}: {value}\n"
            result += "\n"
        
        # Add usage information if present
        if "usage" in response_data:
            result += f"💰 **Usage Information:**\n"
            for key, value in response_data["usage"].items():
                result += f"  - {key}: {value}\n"
        
        return result.strip()
        
    except Exception as ex:
        logger.warning(f"Pegasus video analysis call threw exception: {type(ex).__name__}")
        return f"❌ **Pegasus video analysis failed:** {str(ex)}"
