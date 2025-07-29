from olla_cli.utils.messages import MessageBuilder

def test_message_builder_system_message():
    builder = MessageBuilder()
    builder.add_system_message("System prompt")
    messages = builder.build_chat_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "System prompt"

def test_message_builder_user_message():
    builder = MessageBuilder()
    builder.add_user_message("User prompt")
    messages = builder.build_chat_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "User prompt"

def test_message_builder_assistant_message():
    builder = MessageBuilder()
    builder.add_assistant_message("Assistant response")
    messages = builder.build_chat_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert messages[0]["content"] == "Assistant response"

def test_message_builder_chaining():
    builder = MessageBuilder()
    messages = (
        builder.add_system_message("System prompt")
        .add_user_message("User prompt")
        .add_assistant_message("Assistant response")
        .build_chat_messages()
    )
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
