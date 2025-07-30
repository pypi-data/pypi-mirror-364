import pytest
import asyncio

from universal_mcp.utils.testing import (
    AutomationTestCase, 
    execute_automation_test,
    create_app_with_integration
)
from universal_mcp_outlook.app import OutlookApp


@pytest.fixture
def outlook_app():
    return create_app_with_integration("outlook", OutlookApp)


@pytest.fixture
def outlook_test_case(outlook_app):
    return AutomationTestCase(
        app="outlook",
        app_instance=outlook_app,
        tools=["user_send_mail", "user_list_message", "get_user_id"],
        tasks=[
            "Get the user id.",
            "Send an email to example@gmail.com saying subject: Hello and message: Hey Agentr",
            "List last 3 email in my inbox."
        ],
        validate_query = (
            "Based on the conversation history, verify: "
            "1. Was a user Id retrieved? "
            "2. Was the email sent successfully (check for success response)? "
            "3. Were exactly 3 emails listed from the inbox (check if response shows 3 numbered items)? "
            "4. Does the sent email content 'Hey Agentr' appear in any of the listed email previews?"
        )
    )


@pytest.mark.asyncio
async def test_outlook_tools(outlook_test_case):
    """Test Outlook integration with specific tools."""
    await execute_automation_test(outlook_test_case)


 