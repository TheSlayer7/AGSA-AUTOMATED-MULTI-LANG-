"""
Performance optimization migration for chat models.
This adds database indexes for faster queries.
"""

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_chat_session_user_status ON chat_chatsession(user_profile_id, status);",
            reverse_sql="DROP INDEX IF EXISTS idx_chat_session_user_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_chat_message_session_timestamp ON chat_chatmessage(session_id, timestamp);",
            reverse_sql="DROP INDEX IF EXISTS idx_chat_message_session_timestamp;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_user_profile_phone ON api_userprofile(phone_number);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_profile_phone;"
        ),
    ]
