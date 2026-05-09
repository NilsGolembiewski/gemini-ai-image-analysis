Create an AI image processing/analysis CLI tool. This tool uses gemini-3-flash-preview model as the only model. Do not include functionality to select the model.

The CLI is in python, and should be installable using pip.

The tool should have the same functionality as https://github.com/JonathanJude/openrouter-image-mcp, but as a CLI, and with Gemini instead of openAI.

Plan
 - Research functionality of openrouter-image-mcp
 - research latest gemini library docs for all functionality required for this CLI
 - Verify gemini-3-flash can be called using the credentials from .env
 - Design CLI specification. The main cli command is ai-image-cli
 - Implement CLI tool
 - Test and verify the working of the CLI tool. Obtain actual image(s) to test it with, and test the tool live. 
 - Research best practices for creating an AI agent skill, compatible with opencode. 
 - Create a concise SKILL in the repository for using this cli. It should be under skills/ai-image-cli
 - Report back to user


